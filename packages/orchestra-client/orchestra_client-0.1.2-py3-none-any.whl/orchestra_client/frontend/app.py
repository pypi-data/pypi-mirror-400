#!/usr/bin/env python3
"""Unified UI - Session picker and monitor combined"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import requests
from textual.app import App, ComposeResult
from textual.widgets import (
    Static,
    Label,
    TabbedContent,
    TabPane,
    ListView,
    ListItem,
    Tabs,
    RichLog,
)
from textual.containers import Container, Horizontal
from textual.binding import Binding

from orchestra_client.frontend.widgets.hud import HUD
from orchestra_client.frontend.widgets.messages_tab import MessagesTab
from orchestra_client.frontend.state import AppState
from orchestra_client.lib.message import load_messages
from orchestra_client.lib.logger import get_logger
from orchestra_client.lib.config import load_config, get_auth_headers
from orchestra_client.lib.helpers.process import check_dependencies
from orchestra_client.lib.helpers.tmux import (
    respawn_pane,
    PANE_AGENT,
)
from orchestra_client.lib.helpers.file_ops import ensure_orchestra_directory

logger = get_logger(__name__)

ORCHESTRA_HOST = os.environ.get("ORCHESTRA_HOST", "orchestra.fulcrumresearch.ai")
# Use https for non-localhost (e.g., ngrok)
_protocol = "http" if ORCHESTRA_HOST.startswith("localhost") else "https"
BACKEND_URL = f"{_protocol}://{ORCHESTRA_HOST}"


class UnifiedApp(App):
    """Unified app combining session picker and monitor"""

    CSS = """
    Screen {
        background: $background;
    }

    #header {
        height: 1;
        background: $panel;
        dock: top;
        padding: 0 1;
    }

    #hud {
        height: 1;
        padding: 0;
        color: $primary;
        text-align: center;
        width: 100%;
    }

    #main-content {
        height: 1fr;
    }

    #left-pane {
        width: 30%;
        background: $background;
        padding: 1;
    }

    #right-pane {
        width: 1fr;
        background: $background;
        padding: 1;
    }

    #session-card {
        border: round $panel;
        background: $background;
        height: 1fr;
        width: 1fr;
        padding: 0;
    }

    #diff-card {
        border: round $panel;
        background: $background;
        height: 1fr;
        width: 1fr;
        padding: 0;
    }

    TabbedContent {
        height: 1fr;
        padding: 0;
    }

    Tabs {
        background: transparent;
        width: 100%;
        padding: 0;
    }

    Tab {
        padding: 0 1;
        margin: 0;
    }

    Tab.-active {
        text-style: bold;
    }

    Tab.-active:focus-within {
        background: $primary 25%;
    }

    TabPane {
        padding: 1;
        background: $background;
        layout: vertical;
    }

    #sidebar-title {
        color: $success;
        text-style: bold;
        margin-bottom: 0;
        height: 1;
        width: 100%;
        padding: 0 1;
    }

    #status-indicator {
        color: $warning;
        text-style: italic;
        margin-bottom: 1;
        height: 1;
        width: 100%;
        padding: 0 1;
    }

    #sessions-header {
        color: $secondary;
        text-style: bold;
        margin-bottom: 1;
        height: 1;
        width: 100%;
        padding: 0 1;
    }

    ListView {
        height: 1fr;
        width: 1fr;
        padding: 0;
        margin: 0;
        border: none;
    }

    ListView > .list-view--container {
        padding: 0;
        margin: 0;
    }

    ListItem {
        color: $foreground;
        background: $background;
        width: 100%;
        padding: 0;
        margin: 0;
        layout: horizontal;
        height: 1;
    }

    ListItem Label {
        width: 1fr;
        padding: 0 1;
        height: 1;
        text-wrap: nowrap;
        overflow: hidden;
    }

    ListItem .indicator { width: 1; height: 1; background: transparent; }

    ListItem.-highlight {
        background: $primary 25%;
    }

    ListItem.-highlight Label {
        color: $text;
        text-style: bold;
    }

    RichLog {
        background: $background;
        color: $foreground;
        overflow-x: hidden;
        overflow-y: auto;
        width: 100%;
        height: 1fr;
        text-wrap: wrap;
    }
"""

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+r", "refresh", "Refresh", priority=True),
        Binding("ctrl+d", "delete_session", "Delete", priority=True),
        Binding("enter", "select_session", "Select", show=False),
        Binding("up", "cursor_up", show=False),
        Binding("down", "cursor_down", show=False),
        Binding("k", "scroll_tab_up", "Scroll Tab Up", show=False),
        Binding("j", "scroll_tab_down", "Scroll Tab Down", show=False),
        Binding("left", "prev_tab", show=False),
        Binding("right", "next_tab", show=False),
        Binding("h", "prev_tab", show=False),
        Binding("l", "next_tab", show=False),
    ]

    def __init__(self, shutdown_callback=None):
        super().__init__()
        project_dir = Path.cwd().resolve()
        self.state = AppState(project_dir)
        self.shutdown_callback = shutdown_callback

        config = load_config()
        self.theme = config.get("ui_theme", "textual-light")

    def compose(self) -> ComposeResult:
        config = load_config()
        require_docker = config.get("use_docker", False)
        success, missing = check_dependencies(require_docker=require_docker)

        if not success:
            print("\n Missing dependencies:")
            for dep in missing:
                print(f"  - {dep}")
            print()

        with Container(id="header"):
            self.hud = HUD(id="hud")
            yield self.hud

        with Horizontal(id="main-content"):
            with Container(id="left-pane"):
                yield Static("Orchestra", id="sidebar-title")
                self.status_indicator = Static("", id="status-indicator")
                yield self.status_indicator
                with Container(id="session-card"):
                    yield Static("Sessions", id="sessions-header")
                    self.session_list = ListView(id="session-list")
                    yield self.session_list

            with Container(id="right-pane"):
                with Container(id="diff-card"):
                    with TabbedContent(initial="messages-tab"):
                        with TabPane("Messages", id="messages-tab"):
                            self.messages_tab = MessagesTab()
                            yield self.messages_tab

    async def on_ready(self) -> None:
        """Load sessions from backend and refresh list"""
        self.state.load()

        if not self.state.root_session:
            self.status_indicator.update("No sessions found. Create one via backend API.")
            logger.warning("No root session found")
        else:
            self.state.active_session_name = self.state.root_session.session_name
            self.hud.set_session(self.state.root_session.session_name)

        await self.action_refresh()
        self.set_focus(self.session_list)

        ensure_orchestra_directory(self.state.project_dir)

        # Poll for session updates every 5 seconds
        self.set_interval(5, self.action_refresh)

    async def action_refresh(self) -> None:
        """Refresh the session list from backend"""
        self.state.load()

        index = self.session_list.index if self.session_list.index is not None else 0
        current_session = self.state.get_session_by_index(index)
        selected_name = current_session.session_name if current_session else None

        self.session_list.clear()

        root = self.state.root_session
        if not root:
            return

        label_text = f"{root.session_name} ({root.agent_type})"
        self.session_list.append(
            ListItem(
                Horizontal(
                    Static("", classes="indicator"),
                    Label(label_text, markup=True),
                )
            )
        )

        for child in root.children:
            label_text = f"  {child.session_name} ({child.agent_type})"
            self.session_list.append(
                ListItem(
                    Horizontal(
                        Static("", classes="indicator"),
                        Label(label_text, markup=True),
                    )
                )
            )

        if selected_name:
            new_index = self.state.get_index_by_session_name(selected_name)
            self.session_list.index = new_index if new_index is not None else 0

    def action_cursor_up(self) -> None:
        self.session_list.action_cursor_up()

    def action_cursor_down(self) -> None:
        self.session_list.action_cursor_down()

    def action_select_session(self) -> None:
        """Select the currently highlighted session and connect to it"""
        session = self.state.get_session_by_index(self.session_list.index)
        if session:
            self.state.set_active_session(session.session_name)
            self.hud.set_session(session.session_name)
            self.messages_tab.refresh_messages()
            # Connect to the selected session's Claude
            respawn_pane(PANE_AGENT, f"uv run orchestra connect {session.session_name}")

    def action_scroll_tab_up(self) -> None:
        tabs = self.query_one(TabbedContent)
        active_pane = tabs.get_pane(tabs.active)
        if active_pane:
            for widget in active_pane.query(RichLog):
                widget.scroll_relative(y=-1)

    def action_scroll_tab_down(self) -> None:
        tabs = self.query_one(TabbedContent)
        active_pane = tabs.get_pane(tabs.active)
        if active_pane:
            for widget in active_pane.query(RichLog):
                widget.scroll_relative(y=1)

    def action_prev_tab(self) -> None:
        tabs = self.query_one(Tabs)
        tabs.action_previous_tab()

    def action_next_tab(self) -> None:
        tabs = self.query_one(Tabs)
        tabs.action_next_tab()

    async def _delete_session_task(self, session_name: str) -> None:
        """Delete session via backend API"""
        try:
            resp = await asyncio.to_thread(
                requests.delete, f"{BACKEND_URL}/agents/{session_name}",
                headers=get_auth_headers()
            )
            resp.raise_for_status()
            logger.info(f"Deleted session: {session_name}")
        except requests.RequestException as e:
            logger.error(f"Failed to delete session: {e}")

        await self.action_refresh()
        self.status_indicator.update("")

    def action_delete_session(self) -> None:
        """Delete the currently selected session"""
        index = self.session_list.index
        if index is None:
            return

        session = self.state.get_session_by_index(index)
        if not session:
            return

        if session == self.state.root_session:
            self.status_indicator.update("Cannot delete root session")
            return

        self.status_indicator.update("Deleting session...")
        asyncio.create_task(self._delete_session_task(session.session_name))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.action_select_session()

    def action_quit(self) -> None:
        self.status_indicator.update("Quitting...")
        logger.info("Shutting down Orchestra...")
        asyncio.create_task(self._shutdown_task())

    async def _shutdown_task(self) -> None:
        if self.shutdown_callback:
            await asyncio.to_thread(self.shutdown_callback)
        self.exit()

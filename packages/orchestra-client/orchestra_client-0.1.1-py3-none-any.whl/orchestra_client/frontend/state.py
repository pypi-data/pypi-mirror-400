"""Application state management for Orchestra UI"""

import os
from pathlib import Path
from typing import Optional, List

import requests

from orchestra_client.lib.session import Session
from orchestra_client.lib.config import get_auth_headers

ORCHESTRA_HOST = os.environ.get("ORCHESTRA_HOST", "orchestra.fulcrumresearch.ai")
# Use https for non-localhost (e.g., ngrok)
_protocol = "http" if ORCHESTRA_HOST.startswith("localhost") else "https"
BACKEND_URL = f"{_protocol}://{ORCHESTRA_HOST}"


def fetch_sessions_from_api() -> List[Session]:
    """Fetch sessions from backend API and convert to Session objects."""
    try:
        resp = requests.get(f"{BACKEND_URL}/agents", headers=get_auth_headers())
        resp.raise_for_status()
        sessions_data = resp.json().get("sessions", [])

        # First pass: create all sessions
        sessions_by_name = {}
        for data in sessions_data:
            session = Session.from_dict(data)
            sessions_by_name[session.session_name] = session

        # Second pass: rebuild parent-child relationships
        for session in sessions_by_name.values():
            if session.parent_session_name:
                parent = sessions_by_name.get(session.parent_session_name)
                if parent and session not in parent.children:
                    parent.children.append(session)

        return list(sessions_by_name.values())
    except requests.RequestException:
        return []


class AppState:
    """Centralized application state for the Orchestra UI.

    Holds all session data and provides methods to access and manipulate it.
    No UI logic - just data management.
    """

    def __init__(self, project_dir: Path):
        """Initialize app state.

        Args:
            project_dir: The project directory path (kept for compatibility)
        """
        self.root_session: Optional[Session] = None
        self.root_session_name: Optional[str] = None
        self.active_session_name: Optional[str] = None
        self.paired_session_name: Optional[str] = None
        self.project_dir = project_dir

    def load(self, root_session_name: str = None) -> None:
        """Load sessions from backend API.

        Args:
            root_session_name: Optional root session name to filter by
        """
        sessions = fetch_sessions_from_api()

        if root_session_name:
            # Find specific root session
            for session in sessions:
                if session.session_name == root_session_name:
                    self.root_session = session
                    return
        else:
            # Find first root session (no parent)
            for session in sessions:
                if session.parent_session_name is None:
                    self.root_session = session
                    return

        self.root_session = None

    def get_active_session(self) -> Optional[Session]:
        """Get the currently active session.

        Returns:
            The active Session object or None
        """
        if not self.active_session_name or not self.root_session:
            return None

        # Check root
        if self.root_session.session_name == self.active_session_name:
            return self.root_session

        # Check children
        for child in self.root_session.children:
            if child.session_name == self.active_session_name:
                return child

        return None

    def set_active_session(self, session_name: str) -> None:
        """Set the active session by name.

        Args:
            session_name: The session name to set as active
        """
        self.active_session_name = session_name

    def get_paired_session(self) -> Optional[Session]:
        """Get the currently paired session.

        Returns:
            The paired Session object or None
        """
        if not self.paired_session_name or not self.root_session:
            return None

        # Check root
        if self.root_session.session_name == self.paired_session_name:
            return self.root_session

        # Check children
        for child in self.root_session.children:
            if child.session_name == self.paired_session_name:
                return child

        return None

    def set_paired_session(self, session_name: Optional[str]) -> None:
        """Set the paired session by name.

        Args:
            session_name: The session name to set as paired, or None to clear
        """
        self.paired_session_name = session_name

    def get_session_by_index(self, index: int) -> Optional[Session]:
        """Get session by list index (0 = root, 1+ = children).

        Args:
            index: The list index

        Returns:
            Session at that index, or None if invalid
        """
        if not self.root_session:
            return None

        if index == 0:
            return self.root_session
        else:
            child_index = index - 1
            if 0 <= child_index < len(self.root_session.children):
                return self.root_session.children[child_index]
        return None

    def remove_child(self, session_name: str) -> bool:
        """Remove a child session by name.

        Args:
            session_name: The session name to remove

        Returns:
            True if removed, False if not found
        """
        if not self.root_session:
            return False

        for i, child in enumerate(self.root_session.children):
            if child.session_name == session_name:
                self.root_session.children.pop(i)
                return True
        return False

    def get_index_by_session_name(self, session_name: str) -> Optional[int]:
        """Get list index for a session name (0 = root, 1+ = children).

        Args:
            session_name: The session name to find

        Returns:
            List index, or None if not found
        """
        if not self.root_session:
            return None

        if self.root_session.session_name == session_name:
            return 0

        for i, child in enumerate(self.root_session.children):
            if child.session_name == session_name:
                return i + 1

        return None

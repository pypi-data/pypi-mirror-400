#!/usr/bin/env python3
"""Launcher for Orchestra's tmux workspace."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import requests

from orchestra_client.lib.helpers.tmux import build_tmux_cmd, run_local_tmux_command
from orchestra_client.lib.config import get_tmux_server_name, get_auth_headers


TMUX_BIN = shutil.which("tmux") or "tmux"
ORCHESTRA_HOST = os.environ.get("ORCHESTRA_HOST", "orchestra.fulcrumresearch.ai")
# Use https for non-localhost (e.g., ngrok)
_protocol = "http" if ORCHESTRA_HOST.startswith("localhost") else "https"
BACKEND_URL = f"{_protocol}://{ORCHESTRA_HOST}"


def get_root_session() -> dict | None:
    """Fetch sessions from API and return the root session (no parent)."""
    try:
        resp = requests.get(f"{BACKEND_URL}/agents", headers=get_auth_headers())
        resp.raise_for_status()
        sessions = resp.json().get("sessions", [])

        # Find root session (no parent)
        for session in sessions:
            if session.get("parent_id") is None:
                return session
        return None
    except requests.RequestException as e:
        print(f"Failed to fetch sessions from backend: {e}", file=sys.stderr)
        return None


def create_root_session(name: str = "main") -> dict | None:
    """Create a root designer session via the API."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/agents",
            json={"name": name, "agent_type": "designer"},
            headers=get_auth_headers(),
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Failed to create root session: {e}", file=sys.stderr)
        return None


def main() -> int:
    """Launch Orchestra tmux workspace."""
    try:
        # Setup session names
        repo = Path.cwd().name.replace(" ", "-").replace(":", "-") or "workspace"
        session = f"coral-{repo}"
        target = f"{session}:main"

        check_result = run_local_tmux_command("has-session", "-t", session)
        if check_result.returncode == 0:
            # Session exists - try to attach to it
            run_local_tmux_command("attach-session", "-t", session)
            return 0

        # Kill old session
        run_local_tmux_command("kill-session", "-t", session)

        # Get or create root session from API
        root_session = get_root_session()
        if not root_session:
            print("No root session found. Creating one...")
            root_session = create_root_session("main")
            if not root_session:
                print("Failed to create root session. Is the backend running?", file=sys.stderr)
                return 1
            print(f"Created root session: {root_session['session_name']}")
        else:
            print(f"Connecting to root session: {root_session['session_name']}")

        session_name = root_session["session_name"]

        # Create new session with config
        run_local_tmux_command(
            "new-session",
            "-d",
            "-s",
            session,
            "-n",
            "main",
            ";",
            "set",
            "-t",
            session,
            "status",
            "off",
            ";",
            "set",
            "-t",
            session,
            "-g",
            "mouse",
            "on",
            ";",
            "bind-key",
            "-n",
            "C-s",
            "select-pane",
            "-t",
            ":.+",
        )

        # Get window width and calculate split
        result = run_local_tmux_command("display-message", "-t", target, "-p", "#{window_width}")
        width = 200  # Default width
        if result.returncode == 0 and result.stdout.strip():
            try:
                width = int(result.stdout.strip())
            except ValueError:
                pass  # Use default width if conversion fails
        left_size = max(width * 50 // 100, 1)

        # Create 3-pane layout
        run_local_tmux_command("split-window", "-t", target, "-h", "-b", "-l", str(left_size))
        run_local_tmux_command("split-window", "-t", f"{target}.0", "-v", "-l", "8")

        # Use uv run to ensure correct environment in new tmux panes
        run_cmd = "uv run"

        # Initialize panes
        run_local_tmux_command("send-keys", "-t", f"{target}.0", f"{run_cmd} orchestra-ui", "C-m")
        run_local_tmux_command("send-keys", "-t", f"{target}.1", f"{run_cmd} orchestra connect --terminal {session_name}", "C-m")
        # Connect to root session via backend WebSocket proxy
        run_local_tmux_command(
            "send-keys",
            "-t",
            f"{target}.2",
            f"{run_cmd} orchestra connect {session_name}",
            "C-m",
        )
        run_local_tmux_command("select-pane", "-t", f"{target}.0")

        # Attach to orchestra session
        if os.environ.get("TMUX"):
            # Already in tmux - unset TMUX to allow nested attach
            env = os.environ.copy()
            env.pop("TMUX", None)
            return subprocess.run(
                build_tmux_cmd("attach-session", "-t", session),
                env=env
            ).returncode

        return subprocess.run(build_tmux_cmd("attach-session", "-t", session)).returncode

    except subprocess.CalledProcessError as e:
        print(f"tmux error: {e.stderr or e}", file=sys.stderr)
        return e.returncode or 1


if __name__ == "__main__":
    sys.exit(main())

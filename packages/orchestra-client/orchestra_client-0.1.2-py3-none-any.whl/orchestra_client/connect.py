#!/usr/bin/env python3
"""CLI client for connecting to sessions via Orchestra backend."""

import argparse
import os
import sys
from pathlib import Path

import requests

from orchestra_client.lib.config import get_auth_headers


def fetch_ssh_key(session_name: str, server_url: str) -> dict:
    """Fetch SSH key for a session from the backend."""
    # Convert ws:// to http:// for the API call
    http_url = server_url.replace("wss://", "https://").replace("ws://", "http://")
    resp = requests.get(
        f"{http_url}/sessions/{session_name}/ssh-key",
        headers=get_auth_headers(),
    )
    resp.raise_for_status()
    return resp.json()


def connect(session_name: str, server_url: str, terminal: bool = False) -> int:
    """Connect to a session via SSH through the Orchestra proxy.

    Args:
        session_name: Name of the session to connect to
        server_url: Orchestra backend WebSocket URL (ws:// or wss://)
        terminal: If True, open plain shell. If False, attach to tmux.

    Returns:
        Exit code from SSH (or 1 on error)
    """
    # Fetch SSH key from backend
    try:
        ssh_key = fetch_ssh_key(session_name, server_url)
    except requests.RequestException as e:
        print(f"Failed to fetch SSH key: {e}", file=sys.stderr)
        return 1

    # Save private key to ~/.ssh/orchestra-<session>.pem
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    key_path = ssh_dir / f"orchestra-{session_name}.pem"
    key_path.write_text(ssh_key["private_key"])
    key_path.chmod(0o600)

    # Build SSH command using orchestra ssh-proxy as ProxyCommand
    ssh_cmd = [
        "ssh",
        "-i", str(key_path),
        "-o", f"ProxyCommand=orchestra ssh-proxy {session_name} --server {server_url}",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "LogLevel=ERROR",
        "root@orchestra",  # hostname doesn't matter, proxy routes by session_name
    ]

    if not terminal:
        # Attach to Claude's tmux session
        ssh_cmd.extend(["-t", "tmux attach -t orchestra"])

    # Replace current process with SSH
    os.execvp("ssh", ssh_cmd)


def main():
    parser = argparse.ArgumentParser(
        description="Connect to a session via Orchestra backend"
    )
    parser.add_argument(
        "session_name",
        help="The session name to connect to"
    )
    orchestra_host = os.environ.get("ORCHESTRA_HOST", "orchestra.fulcrumresearch.ai")
    # Use wss:// for non-localhost (e.g., ngrok)
    protocol = "ws" if orchestra_host.startswith("localhost") else "wss"
    parser.add_argument(
        "--server",
        default=f"{protocol}://{orchestra_host}",
        help=f"Orchestra backend WebSocket URL (default: {protocol}://{orchestra_host})"
    )
    parser.add_argument(
        "--terminal", "-t",
        action="store_true",
        help="Open a shell terminal instead of connecting to Claude"
    )

    args = parser.parse_args()

    return connect(args.session_name, args.server, args.terminal)


if __name__ == "__main__":
    sys.exit(main())

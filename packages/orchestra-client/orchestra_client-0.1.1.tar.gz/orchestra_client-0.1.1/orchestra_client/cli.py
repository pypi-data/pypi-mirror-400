#!/usr/bin/env python3
"""Orchestra Client CLI."""

import argparse
import asyncio
import os
import sys

from orchestra_client.connect import connect
from orchestra_client.ssh_proxy import ssh_proxy
from orchestra_client.launch import main as launch_main
from orchestra_client.maestro import main as maestro_main


def main():
    parser = argparse.ArgumentParser(
        prog="orchestra",
        description="Orchestra Client - Connect to Orchestra sessions",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # launch (default when no command given)
    launch_parser = subparsers.add_parser(
        "launch",
        help="Launch Orchestra tmux workspace (default)",
    )

    # ui
    ui_parser = subparsers.add_parser(
        "ui",
        help="Launch Orchestra TUI",
    )

    # connect
    connect_parser = subparsers.add_parser(
        "connect",
        help="Connect to a session via SSH proxy",
    )
    connect_parser.add_argument(
        "session_name",
        help="The session name to connect to",
    )
    connect_parser.add_argument(
        "--server",
        default=None,
        help="Orchestra backend WebSocket URL (default: ws://$ORCHESTRA_HOST)",
    )
    connect_parser.add_argument(
        "--terminal", "-t",
        action="store_true",
        help="Open a shell terminal instead of connecting to Claude",
    )

    # ssh-proxy (used as SSH ProxyCommand)
    ssh_proxy_parser = subparsers.add_parser(
        "ssh-proxy",
        help="SSH proxy bridge (used as ProxyCommand)",
    )
    ssh_proxy_parser.add_argument(
        "session_name",
        help="The session name to connect to",
    )
    ssh_proxy_parser.add_argument(
        "--server",
        default=None,
        help="Orchestra backend WebSocket URL (default: ws://$ORCHESTRA_HOST)",
    )

    args = parser.parse_args()

    # Default to launch if no command given
    if args.command is None:
        args.command = "launch"

    if args.command == "launch":
        return launch_main()

    elif args.command == "ui":
        return maestro_main()

    elif args.command == "connect":
        orchestra_host = os.environ.get("ORCHESTRA_HOST", "orchestra.fulcrumresearch.ai")
        protocol = "ws" if orchestra_host.startswith("localhost") else "wss"
        server = args.server or f"{protocol}://{orchestra_host}"
        return connect(args.session_name, server, args.terminal)

    elif args.command == "ssh-proxy":
        orchestra_host = os.environ.get("ORCHESTRA_HOST", "orchestra.fulcrumresearch.ai")
        protocol = "ws" if orchestra_host.startswith("localhost") else "wss"
        server = args.server or f"{protocol}://{orchestra_host}"
        return asyncio.run(ssh_proxy(args.session_name, server))

    return 0


if __name__ == "__main__":
    sys.exit(main())

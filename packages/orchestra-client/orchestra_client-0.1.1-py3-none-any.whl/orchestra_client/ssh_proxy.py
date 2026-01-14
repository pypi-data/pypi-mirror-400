"""SSH proxy - bridges stdin/stdout to WebSocket tunnel.

Used as SSH ProxyCommand to connect through Orchestra server.
"""

import asyncio
import os
import sys
from urllib.parse import quote

import websockets

from orchestra_client.lib.config import get_orchestra_password


async def stdin_to_ws(ws):
    """Forward stdin to WebSocket."""
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin.buffer)

    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            await ws.send(data)
    except Exception:
        pass


async def ws_to_stdout(ws):
    """Forward WebSocket to stdout."""
    try:
        async for message in ws:
            if isinstance(message, bytes):
                os.write(sys.stdout.fileno(), message)
            else:
                os.write(sys.stdout.fileno(), message.encode())
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception:
        pass


async def ssh_proxy(session_name: str, server_url: str) -> int:
    """Bridge stdin/stdout to WebSocket SSH tunnel.

    Args:
        session_name: Name of the session to connect to
        server_url: Orchestra backend WebSocket URL (ws:// or wss://)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Build URL with auth
    url = f"{server_url}/sessions/{session_name}/connect"
    password = get_orchestra_password()
    if password:
        url += f"?password={quote(password)}"

    try:
        async with websockets.connect(url) as ws:
            # Run both directions concurrently
            stdin_task = asyncio.create_task(stdin_to_ws(ws))
            stdout_task = asyncio.create_task(ws_to_stdout(ws))

            done, pending = await asyncio.wait(
                [stdin_task, stdout_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        return 0

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        return 1
    except ConnectionRefusedError:
        print(f"Cannot connect to Orchestra backend at {server_url}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

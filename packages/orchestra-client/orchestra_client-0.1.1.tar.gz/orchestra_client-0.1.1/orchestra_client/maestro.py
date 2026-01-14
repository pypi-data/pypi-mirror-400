#!/usr/bin/env python3
"""Orchestra UI entry point"""

import os
from pathlib import Path

from orchestra_client.frontend.app import UnifiedApp
from orchestra_client.lib.logger import get_logger
from orchestra_client.lib.helpers.tmux import build_tmux_cmd, execute_local

logger = get_logger(__name__)


def main():
    """Entry point for the unified UI"""
    os.environ.setdefault("TERM", "xterm-256color")
    os.environ.setdefault("TMUX_TMPDIR", "/tmp")

    logger.info("Starting Orchestra UI...")

    # Clear the message queue on startup
    messages_file = Path.cwd() / ".orchestra" / "messages.jsonl"
    if messages_file.exists():
        messages_file.unlink()
        logger.debug("Cleared messages queue")

    def cleanup():
        """Clean up on exit"""
        # Remove doc injection
        claude_path = Path.cwd() / ".claude" / "CLAUDE.md"
        if claude_path.exists():
            content = claude_path.read_text()
            if "@orchestra.md" in content:
                claude_path.write_text(content.replace("@orchestra.md", ""))

        logger.info("Shutting down tmux server")
        try:
            execute_local(build_tmux_cmd("kill-server"))
        except Exception as e:
            logger.debug(f"Error killing tmux server: {e}")

    try:
        UnifiedApp(shutdown_callback=cleanup).run()
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        cleanup()
        raise


if __name__ == "__main__":
    main()

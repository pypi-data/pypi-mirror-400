"""File and directory utilities"""

from pathlib import Path

from orchestra_client.lib.logger import get_logger
from orchestra_client.lib.config import get_orchestra_home

logger = get_logger(__name__)


# Sessions file path (shared constant)
SESSIONS_FILE = get_orchestra_home() / "sessions.json"

# Architecture template for new projects
ARCHITECTURE_MD_TEMPLATE = """# Project Architecture

This document provides an overview of the project structure and key components.

## Overview

TODO: Add project overview

## Key Components

TODO: Document key components
"""


def ensure_orchestra_directory(project_dir: Path) -> None:
    """Ensure .orchestra/ directory exists with docs/architecture.md template,
    and create a .gitignore file inside .orchestra/ to manage what gets committed.

    Args:
        project_dir: Path to the project directory
    """
    orchestra_dir = project_dir / ".orchestra"
    orchestra_dir.mkdir(exist_ok=True)

    # Create .gitignore inside .orchestra/ to ignore most content but preserve docs and markdown files
    gitignore_path = orchestra_dir / ".gitignore"
    gitignore_content = "*"
    if not gitignore_path.exists():
        gitignore_path.write_text(gitignore_content)
        logger.info(f"Created .gitignore at {gitignore_path}")

    # Create docs directory
    docs_dir = orchestra_dir / "docs"
    docs_dir.mkdir(exist_ok=True)

    architecture_md = docs_dir / "architecture.md"

    # Create architecture.md with template if it doesn't exist
    if not architecture_md.exists():
        architecture_md.write_text(ARCHITECTURE_MD_TEMPLATE)
        logger.info(f"Created architecture.md with template at {architecture_md}")

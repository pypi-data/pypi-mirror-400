"""Global configuration for Orchestra"""

import getpass
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict


def get_orchestra_home() -> Path:
    """Get the Orchestra home directory.

    Checks for ORCHESTRA_HOME_DIR environment variable first.
    If not set, defaults to ~/.orchestra2

    Returns:
        Path to the Orchestra home directory
    """
    home_dir = os.environ.get("ORCHESTRA_HOME_DIR")
    if home_dir:
        return Path(home_dir).expanduser()
    return Path.home() / ".orchestra2"


CONFIG_FILE = get_orchestra_home() / "config" / "settings.json"

DEFAULT_CONFIG = {
    "use_docker": True,
    "mcp_port": 8765,
    "monitor_port": 8081,
    "ui_theme": "textual-dark",
    "tmux_server_name": "coral",
}

# Default tmux configuration for all Orchestra sessions
DEFAULT_TMUX_CONF = """# Orchestra tmux configuration

# Disable status bar
set-option -g status off

# Enable scrollback buffer with 10000 lines
set-option -g history-limit 10000

# Enable mouse support for scrolling
set-option -g mouse on

# Ensure proper color support
set-option -g default-terminal "screen-256color"

# Disable all default key bindings to avoid conflicts
unbind-key -a

# Ctrl+S for pane switching
bind-key -n C-s select-pane -t :.+

# Ctrl+\\ for detaching without killing session
bind-key -n C-\\\\ detach-client

# Re-enable mouse wheel scrolling bindings for copy mode
bind-key -n WheelUpPane if-shell -F -t = "#{mouse_any_flag}" "send-keys -M" "if -Ft= '#{pane_in_mode}' 'send-keys -M' 'copy-mode -e; send-keys -M'"
bind-key -n WheelDownPane select-pane -t= \\; send-keys -M

# Copy mode usage:
# Mouse wheel up to scroll
# Press 'q' or Esc to exit copy mode
"""


def load_config() -> Dict[str, Any]:
    """Load global configuration"""
    orchestra_config = get_orchestra_home() / "config" / "settings.json"
    if orchestra_config.exists():
        try:
            with open(orchestra_config, "r") as f:
                config = json.load(f)
                return {**DEFAULT_CONFIG, **config}
        except (json.JSONDecodeError, IOError):
            pass

    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save global configuration"""
    orchestra_config = get_orchestra_home() / "config" / "settings.json"
    orchestra_config.parent.mkdir(parents=True, exist_ok=True)
    with open(orchestra_config, "w") as f:
        json.dump(config, f, indent=2)


def ensure_config_dir() -> Path:
    """Ensure $ORCHESTRA_HOME/config/ directory exists with default config files.

    Creates the config directory and writes default config files ONLY if they don't exist.
    Never overwrites existing user configs.

    Returns:
        Path to the config directory
    """
    config_dir = get_orchestra_home() / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create tmux.conf if it doesn't exist
    tmux_conf_path = config_dir / "tmux.conf"
    if not tmux_conf_path.exists():
        tmux_conf_path.write_text(DEFAULT_TMUX_CONF)

    return config_dir


def get_tmux_config_path() -> Path:
    """Get path to tmux.conf for all Orchestra sessions.

    Ensures config directory exists before returning path.

    Returns:
    """
    ensure_config_dir()
    return get_orchestra_home() / "config" / "tmux.conf"


def get_tmux_server_name() -> str:
    """Get configured tmux server name.

    Returns:
        Configured tmux server name (defaults to "coral")
    """
    config = load_config()
    return config.get("tmux_server_name", "coral")


def get_orchestra_password() -> str | None:
    """Get Orchestra password from saved config, prompting if not set.

    Returns:
        Password string or None if user cancels prompt
    """
    config = load_config()
    password = config.get("password")

    if not password:
        password = getpass.getpass("Orchestra password: ")
        if password:
            config["password"] = password
            save_config(config)

    return password or None


def get_user_token() -> str:
    """Get or generate a unique user token for session isolation.

    Generates a UUID on first call and stores it in config.
    Returns the same token on subsequent calls.

    Returns:
        User token string (UUID)
    """
    config = load_config()
    token = config.get("user_token")

    if not token:
        token = str(uuid.uuid4())
        config["user_token"] = token
        save_config(config)

    return token


def get_auth_headers() -> dict:
    """Get authentication headers for HTTP requests.

    Returns:
        Dict with X-Orchestra-Password and X-Orchestra-User-Token headers
    """
    headers = {"X-Orchestra-User-Token": get_user_token()}
    password = get_orchestra_password()
    if password:
        headers["X-Orchestra-Password"] = password
    return headers



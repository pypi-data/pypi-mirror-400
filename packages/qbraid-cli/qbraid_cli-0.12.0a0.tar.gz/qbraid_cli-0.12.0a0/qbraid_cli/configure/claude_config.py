# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Utility functions for managing Claude Desktop configuration.

This module provides cross-platform support for locating and updating
the claude_desktop_config.json file used by Claude Desktop.
"""

import json
import os
import platform
import shutil
from pathlib import Path
from typing import Optional


def get_claude_config_path() -> Optional[Path]:
    """
    Get the path to the Claude Desktop configuration file.

    Returns the platform-specific path to claude_desktop_config.json:
    - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
    - Windows: %APPDATA%\\Claude\\claude_desktop_config.json
    - Linux: ~/.config/Claude/claude_desktop_config.json

    Returns:
        Path to the config file if it exists, None otherwise
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        config_path = Path.home() / "Library" / "Application Support" / "Claude"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            return None
        config_path = Path(appdata) / "Claude"
    elif system == "Linux":
        config_path = Path.home() / ".config" / "Claude"
    else:
        return None

    config_file = config_path / "claude_desktop_config.json"
    return config_file if config_file.exists() else None


def load_claude_config() -> dict:
    """
    Load the Claude Desktop configuration file.

    Returns:
        Configuration dictionary. If file doesn't exist, returns empty dict.

    Raises:
        json.JSONDecodeError: If config file exists but contains invalid JSON
        OSError: If there are permission issues reading the file
    """
    config_path = get_claude_config_path()

    if config_path is None or not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_claude_config(config: dict) -> Path:
    """
    Save the Claude Desktop configuration file.

    Creates the configuration directory if it doesn't exist.

    Args:
        config: Configuration dictionary to save

    Returns:
        Path to the saved configuration file

    Raises:
        OSError: If there are permission issues or the platform is unsupported
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise OSError("APPDATA environment variable not set")
        config_dir = Path(appdata) / "Claude"
    elif system == "Linux":
        config_dir = Path.home() / ".config" / "Claude"
    else:
        raise OSError(f"Unsupported platform: {system}")

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "claude_desktop_config.json"

    # Write config with pretty formatting
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add trailing newline

    return config_file


def add_qbraid_mcp_server(overwrite: bool = False) -> tuple[bool, str]:
    """
    Add qBraid MCP server configuration to Claude Desktop config.

    Args:
        overwrite: If True, overwrite existing qbraid entry

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Get the full path to qbraid executable
    qbraid_path = shutil.which("qbraid")
    if not qbraid_path:
        return (
            False,
            "Could not find qbraid executable in PATH. "
            "Please ensure qbraid-cli is installed and accessible.",
        )

    try:
        config = load_claude_config()
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in Claude config file: {e}"
    except OSError as e:
        return False, f"Error reading Claude config file: {e}"

    # Initialize mcpServers section if it doesn't exist
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Determine server name
    server_name = "qbraid"

    # Check if server already exists
    if server_name in config["mcpServers"] and not overwrite:
        return (
            False,
            f"MCP server '{server_name}' already exists in config. "
            "Use --overwrite to replace it.",
        )

    # Build server configuration with full path to qbraid
    server_config = {"command": qbraid_path, "args": ["mcp", "serve"]}

    # Add server to config
    config["mcpServers"][server_name] = server_config

    # Save config
    try:
        config_path = save_claude_config(config)
        action = "Updated" if server_name in config["mcpServers"] else "Added"
        return True, f"{action} MCP server '{server_name}' in [cyan]{config_path}[/cyan]"
    except OSError as e:
        return False, f"Error saving Claude config file: {e}"


def remove_qbraid_mcp_server() -> tuple[bool, str]:
    """
    Remove qBraid MCP server configuration from Claude Desktop config.

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        config = load_claude_config()
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in Claude config file: {e}"
    except OSError as e:
        return False, f"Error reading Claude config file: {e}"

    if "mcpServers" not in config:
        return False, "No mcpServers section found in Claude config"

    server_name = "qbraid"

    if server_name not in config["mcpServers"]:
        return False, f"MCP server '{server_name}' not found in config"

    # Remove server
    del config["mcpServers"][server_name]

    # Save config
    try:
        config_path = save_claude_config(config)
        return True, f"Removed MCP server '{server_name}' from [cyan]{config_path}[/cyan]"
    except OSError as e:
        return False, f"Error saving Claude config file: {e}"


def get_qbraid_mcp_server_config() -> Optional[dict]:
    """
    Get qBraid MCP server configuration from Claude Desktop config.

    Returns:
        Server configuration dict if found, None otherwise
    """
    try:
        config = load_claude_config()
    except (json.JSONDecodeError, OSError):
        return None

    if "mcpServers" not in config:
        return None

    return config["mcpServers"].get("qbraid")

"""Path utilities for Janet CLI."""

import re
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir


def get_config_dir() -> Path:
    """Get configuration directory path."""
    config_dir = Path(user_config_dir("janet-cli", appauthor=False))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_dir() -> Path:
    """Get data directory path."""
    data_dir = Path(user_data_dir("janet-cli", appauthor=False))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_file() -> Path:
    """Get configuration file path."""
    return get_config_dir() / "config.json"


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.

    Replaces invalid characters with hyphens and limits length.

    Args:
        name: String to sanitize

    Returns:
        Sanitized filename-safe string
    """
    # Replace invalid filesystem characters with hyphens
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "-", name)

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(". ")

    # Replace multiple consecutive hyphens with single hyphen
    sanitized = re.sub(r"-+", "-", sanitized)

    # Limit length to 255 characters (filesystem limit)
    if len(sanitized) > 255:
        sanitized = sanitized[:255].rstrip("-")

    return sanitized if sanitized else "unnamed"


def expand_path(path: str) -> Path:
    """
    Expand user home directory and resolve path.

    Args:
        path: Path string (may contain ~)

    Returns:
        Resolved absolute Path
    """
    return Path(path).expanduser().resolve()

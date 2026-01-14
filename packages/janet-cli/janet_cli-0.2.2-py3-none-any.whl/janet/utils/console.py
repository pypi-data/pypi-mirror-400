"""Rich console utilities for beautiful terminal output."""

from rich.console import Console
from rich.theme import Theme

# Custom theme for Janet CLI
janet_theme = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "yellow",
        "error": "bold red",
        "highlight": "bold magenta",
        "dim": "dim",
    }
)

# Global console instance
console = Console(theme=janet_theme)


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"✓ {message}", style="success")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"✗ {message}", style="error")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"⚠ {message}", style="warning")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"ℹ {message}", style="info")

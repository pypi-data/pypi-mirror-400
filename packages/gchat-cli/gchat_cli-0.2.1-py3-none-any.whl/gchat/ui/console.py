"""Rich console configuration."""

from rich.console import Console
from rich.theme import Theme

# Custom theme for consistent styling
GCHAT_THEME = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "account": "magenta",
        "space": "blue",
        "sender": "cyan",
        "timestamp": "dim",
    }
)

console = Console(theme=GCHAT_THEME)


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[success]✓[/success] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[error]✗[/error] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]![/warning] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[info]ℹ[/info] {message}")

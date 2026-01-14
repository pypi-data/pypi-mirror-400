"""
CLI output formatting utilities.

This module provides rich, user-friendly terminal output using the Rich library.
Includes formatted messages for success, errors, warnings, and information.

Features:
    - Color-coded output (green=success, red=error, yellow=warning, blue=info)
    - Styled tables for structured data
    - Progress indicators
    - Panels for grouped information
    - Consistent formatting across all CLI commands
"""

from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Initialize Rich console for styled output
console = Console()


# ============================================================================
# OUTPUT FUNCTIONS
# ============================================================================


def success(message: str, detail: Optional[str] = None) -> None:
    """Print success message in green.

    Args:
        message: Main success message
        detail: Optional additional detail to display below message

    Example:
        >>> success("Credentials encrypted successfully", "Profile: production")
        ✓ Credentials encrypted successfully
          Profile: production
    """
    text = Text()
    text.append("✓ ", style="bold green")
    text.append(message, style="green")
    console.print(text)

    if detail:
        console.print(f"  {detail}", style="dim green")


def error(message: str, detail: Optional[str] = None, exit_code: int = 1) -> None:
    """Print error message in red and exit.

    Args:
        message: Main error message
        detail: Optional additional detail (e.g., exception message)
        exit_code: Exit code (default: 1)

    Example:
        >>> error("Failed to decrypt credentials", "Invalid password")
        ✗ Failed to decrypt credentials
          Invalid password
        [Exits with code 1]
    """
    text = Text()
    text.append("✗ ", style="bold red")
    text.append(message, style="red")
    console.print(text)

    if detail:
        console.print(f"  {detail}", style="dim red")

    raise SystemExit(exit_code)


def warning(message: str, detail: Optional[str] = None) -> None:
    """Print warning message in yellow.

    Args:
        message: Main warning message
        detail: Optional additional detail

    Example:
        >>> warning("Profile already exists", "Will overwrite existing credentials")
        ⚠ Profile already exists
          Will overwrite existing credentials
    """
    text = Text()
    text.append("⚠ ", style="bold yellow")
    text.append(message, style="yellow")
    console.print(text)

    if detail:
        console.print(f"  {detail}", style="dim yellow")


def info(message: str, detail: Optional[str] = None) -> None:
    """Print info message in blue.

    Args:
        message: Main info message
        detail: Optional additional detail

    Example:
        >>> info("Loading credentials", "Profile: production")
        ℹ Loading credentials
          Profile: production
    """
    text = Text()
    text.append("ℹ ", style="bold blue")
    text.append(message, style="blue")
    console.print(text)

    if detail:
        console.print(f"  {detail}", style="dim blue")


def print_message(message: str, style: str = "") -> None:
    """Print plain message with optional style.

    Args:
        message: Message to print
        style: Optional Rich style string (e.g., "bold", "dim", "cyan")

    Example:
        >>> print_message("Processing...", style="dim")
        Processing...
    """
    console.print(message, style=style)


def print_panel(
    title: str,
    content: str,
    style: str = "blue",
    border_style: str = "blue",
) -> None:
    """Print content in a styled panel.

    Args:
        title: Panel title
        content: Panel content
        style: Content text style
        border_style: Border color style

    Example:
        >>> print_panel("Configuration", "Region: eu-west-1\\nProfile: prod", style="cyan")
        ╭─── Configuration ────╮
        │ Region: eu-west-1    │
        │ Profile: prod        │
        ╰──────────────────────╯
    """
    panel = Panel(
        content,
        title=title,
        border_style=border_style,
        title_align="left",
    )
    console.print(panel)


def print_table(
    title: str,
    headers: list[str],
    rows: list[list[str]],
    caption: Optional[str] = None,
) -> None:
    """Print data in a formatted table.

    Args:
        title: Table title
        headers: Column headers
        rows: Table rows (list of lists)
        caption: Optional table caption/footer

    Example:
        >>> print_table(
        ...     "Stored Profiles",
        ...     ["Profile", "Created"],
        ...     [["production", "2024-01-15"], ["staging", "2024-01-16"]]
        ... )
        ┏━━━━━━━━━━━┳━━━━━━━━━━━━┓
        ┃ Profile   ┃ Created    ┃
        ┡━━━━━━━━━━━╇━━━━━━━━━━━━┩
        │ production│ 2024-01-15 │
        │ staging   │ 2024-01-16 │
        └───────────┴────────────┘
    """
    table = Table(title=title, caption=caption, show_header=True, header_style="bold cyan")

    # Add columns
    for header in headers:
        table.add_column(header, style="white")

    # Add rows
    for row in rows:
        table.add_row(*row)

    console.print(table)


def print_separator(char: str = "─", length: int = 60) -> None:
    """Print a horizontal separator line.

    Args:
        char: Character to use for separator
        length: Length of separator

    Example:
        >>> print_separator()
        ────────────────────────────────────────────────────────────
    """
    console.print(char * length, style="dim")


def print_header(title: str) -> None:
    """Print a formatted section header.

    Args:
        title: Header title

    Example:
        >>> print_header("Credential Configuration")

        ═══════════════════════════════════════════
        Credential Configuration
        ═══════════════════════════════════════════
    """
    console.print()
    console.print("═" * 60, style="cyan")
    console.print(f"  {title}", style="bold cyan")
    console.print("═" * 60, style="cyan")
    console.print()


def confirm(message: str, default: bool = False) -> bool:
    """Prompt user for yes/no confirmation.

    Args:
        message: Confirmation question
        default: Default value if user just presses Enter

    Returns:
        True if user confirms, False otherwise

    Example:
        >>> if confirm("Delete profile 'production'?"):
        ...     print("Deleting...")
        Delete profile 'production'? [y/N]: y
        Deleting...
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = console.input(f"[yellow]{message}{suffix}[/yellow]").strip().lower()

    if not response:
        return default

    return response in ("y", "yes")


def prompt(message: str, default: Optional[str] = None, password: bool = False) -> str:
    """Prompt user for input.

    Args:
        message: Prompt message
        default: Default value if user just presses Enter
        password: If True, hide input (for passwords)

    Returns:
        User input string

    Example:
        >>> name = prompt("Enter profile name", default="default")
        Enter profile name [default]: production
        >>> # Returns: "production"
    """
    suffix = f" [{default}]: " if default else ": "
    prompt_text = f"[cyan]{message}{suffix}[/cyan]"

    if password:
        response = console.input(prompt_text, password=True).strip()
    else:
        response = console.input(prompt_text).strip()

    if not response and default:
        return default

    return response


# ============================================================================
# OUTPUT HELPER CLASS (FOR COMPATIBILITY)
# ============================================================================


class ComplianceOutput:
    """
    Helper class for output operations.

    This class wraps the module-level output functions in a class interface
    for convenience and compatibility with existing code.
    """

    @staticmethod
    def success(message: str, detail: Optional[str] = None) -> None:
        """Print success message."""
        success(message, detail)

    @staticmethod
    def error(message: str, detail: Optional[str] = None, exit_code: int = 1) -> None:
        """Print error message."""
        error(message, detail, exit_code)

    @staticmethod
    def warning(message: str, detail: Optional[str] = None) -> None:
        """Print warning message."""
        warning(message, detail)

    @staticmethod
    def info(message: str, detail: Optional[str] = None) -> None:
        """Print info message."""
        info(message, detail)

    @staticmethod
    def print_message(message: str, style: str = "") -> None:
        """Print plain message."""
        print_message(message, style)

    @staticmethod
    def prompt(message: str, default: Optional[str] = None) -> str:
        """Prompt user for input."""
        return prompt(message, default, password=False)

    @staticmethod
    def prompt_password(message: str) -> str:
        """Prompt user for password (hidden input)."""
        return prompt(message, password=True)

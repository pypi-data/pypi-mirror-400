"""
CLI banner and branding utilities.

This module provides ASCII art branding for the Complio CLI.
The banner displays when launching the CLI to provide visual identity.
"""

from rich.console import Console
from rich.text import Text

console = Console()


def print_banner() -> None:
    """Print the Complio ASCII art banner.

    Displays a stylized "COMPLIO" logo with tagline in cyan/blue colors.

    Example:
        >>> print_banner()
         ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ██╗ ██████╗
        ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██║██╔═══██╗
        ██║     ██║   ██║██╔████╔██║██████╔╝██║     ██║██║   ██║
        ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██║██║   ██║
        ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗██║╚██████╔╝
         ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝ ╚═════╝
    """
    banner = """
 ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ██╗ ██████╗
██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██║██╔═══██╗
██║     ██║   ██║██╔████╔██║██████╔╝██║     ██║██║   ██║
██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██║██║   ██║
╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗██║╚██████╔╝
 ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝ ╚═════╝
"""

    # Print banner in cyan/blue gradient
    text = Text(banner)
    text.stylize("bold cyan")
    console.print(text)

    # Print tagline
    tagline = Text()
    tagline.append("Automated ", style="dim white")
    tagline.append("ISO 27001 compliance testing", style="bold cyan")
    tagline.append(" for AWS infrastructure.", style="dim white")

    console.print(tagline)
    console.print()


def print_simple_banner() -> None:
    """Print a simpler, more compact Complio banner.

    Alternative banner for smaller terminals or less verbose output.

    Example:
        >>> print_simple_banner()
        ╔═══════════════════════════════════════════════════════════╗
        ║  COMPLIO - Compliance-as-Code Platform                    ║
        ║  Automated ISO 27001 compliance testing for AWS           ║
        ╚═══════════════════════════════════════════════════════════╝
    """
    text = Text()
    text.append("\n╔═══════════════════════════════════════════════════════════╗\n", style="cyan")
    text.append("║  ", style="cyan")
    text.append("COMPLIO", style="bold cyan")
    text.append(" - Compliance-as-Code Platform", style="white")
    text.append("                    ║\n", style="cyan")
    text.append("║  Automated ISO 27001 compliance testing for AWS           ║\n", style="cyan")
    text.append("╚═══════════════════════════════════════════════════════════╝\n", style="cyan")

    console.print(text)


def print_minimal_banner() -> None:
    """Print minimal banner for compact display.

    Example:
        >>> print_minimal_banner()
        COMPLIO v0.1.0 - Compliance-as-Code Platform
    """
    text = Text()
    text.append("COMPLIO", style="bold cyan")
    text.append(" v0.1.0", style="dim cyan")
    text.append(" - Compliance-as-Code Platform\n", style="white")
    console.print(text)

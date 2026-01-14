"""
License deactivation command for Complio.

This command removes the locally cached license, requiring re-activation
on next use. The license remains valid and can be reactivated.
"""

import click
import structlog
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from complio.licensing.validator import LicenseValidator

logger = structlog.get_logger(__name__)
console = Console()


@click.command()
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def deactivate(ctx: click.Context, yes: bool) -> None:
    """
    Deactivate the current license.

    This removes the license from this machine but does not invalidate
    the license key. You can reactivate the same license key later using
    the activate command.

    Example:
        complio deactivate
        complio deactivate --yes  # Skip confirmation
    """
    logger.info("deactivate_command_started")

    # Get validator to check current license
    validator = LicenseValidator()
    license_data = validator.get_license_info()

    if license_data is None:
        console.print(
            "\n[yellow]ℹ No license is currently activated.[/yellow]\n"
        )
        logger.info("deactivate_no_license_found")
        return

    # Show current license info
    console.print()
    console.print(
        Panel(
            f"[bold]Current License:[/bold]\n\n"
            f"Tier: {license_data.tier.upper()}\n"
            f"Email: {license_data.email}\n\n"
            "[yellow]This will remove the license from this machine.[/yellow]\n"
            "[dim]The license key remains valid and can be reactivated.[/dim]",
            title="⚠️  Deactivate License",
            border_style="yellow",
            padding=(1, 2),
        )
    )

    # Confirm unless --yes flag provided
    if not yes:
        if not click.confirm("\nAre you sure you want to deactivate this license?"):
            console.print("\n[cyan]Deactivation cancelled.[/cyan]\n")
            logger.info("deactivate_cancelled")
            return

    # Remove license cache file
    try:
        cache_path = Path.home() / ".complio" / "license.json"

        if cache_path.exists():
            cache_path.unlink()
            logger.info("license_cache_removed", path=str(cache_path))

        console.print()
        console.print(
            Panel(
                "[bold green]✅ License deactivated successfully[/bold green]\n\n"
                "The license has been removed from this machine.\n\n"
                "[bold]To reactivate:[/bold]\n"
                "[cyan]complio activate --license-key YOUR-KEY[/cyan]\n\n"
                "[dim]Note: Your license key remains valid and can be used\n"
                "on this or other machines.[/dim]",
                title="License Deactivated",
                border_style="green",
                padding=(1, 2),
            )
        )

        logger.info("license_deactivated_successfully")

    except Exception as e:
        console.print(
            f"\n❌ Error removing license: {str(e)}\n",
            style="bold red"
        )
        logger.error("deactivate_failed", error=str(e))
        raise click.Abort()


__all__ = ["deactivate"]

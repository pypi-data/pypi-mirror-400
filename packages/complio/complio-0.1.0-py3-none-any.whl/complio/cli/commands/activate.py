"""
License activation command for Complio.

This command activates a license key and stores it locally for offline validation.
"""

import click
import structlog
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from complio.licensing.exceptions import (
    InvalidLicenseError,
    LicenseAPIError,
    LicenseExpiredError,
)
from complio.licensing.validator import LicenseValidator

logger = structlog.get_logger(__name__)
console = Console()


@click.command()
@click.option(
    "--license-key",
    "-k",
    required=True,
    prompt="Enter your license key",
    help="License key in format COMPL-XXXX-XXXX-XXXX-XXXX",
)
@click.pass_context
def activate(ctx: click.Context, license_key: str) -> None:
    """
    Activate a Complio license.

    Validates the license key with the licensing API and stores it locally
    for offline validation. Early Access founders receive special recognition.

    Example:
        complio activate --license-key COMPL-A3F2-9B4C-D8E1-7F2A
    """
    logger.info("activate_command_started", key_masked=_mask_key(license_key))

    try:
        # Validate and activate license
        validator = LicenseValidator()

        console.print("\n🔐 Validating license key...", style="cyan")

        license_info = validator.activate(license_key)

        logger.info(
            "license_activated_successfully",
            tier=license_info.tier,
            early_access=license_info.early_access,
            founder=license_info.is_founder()
        )

        # Display appropriate success message based on tier
        if license_info.is_founder():
            _display_founder_activation(license_info)
        elif license_info.tier == "early_access":
            _display_early_access_activation(license_info)
        elif license_info.tier == "pro":
            _display_pro_activation(license_info)
        elif license_info.tier == "enterprise":
            _display_enterprise_activation(license_info)
        else:
            _display_standard_activation(license_info)

    except InvalidLicenseError as e:
        console.print(f"\n❌ {str(e)}", style="bold red")
        logger.error("license_activation_failed", error="invalid_license")
        raise click.Abort()

    except LicenseExpiredError as e:
        console.print(f"\n❌ {str(e)}", style="bold red")
        console.print(
            "\n💡 Please contact support@compl.io to renew your license.",
            style="yellow"
        )
        logger.error("license_activation_failed", error="expired")
        raise click.Abort()

    except LicenseAPIError as e:
        console.print(f"\n❌ {str(e)}", style="bold red")
        console.print(
            "\n💡 Please check your internet connection and try again.",
            style="yellow"
        )
        logger.error("license_activation_failed", error="api_error")
        raise click.Abort()

    except Exception as e:
        console.print(
            f"\n❌ Unexpected error during activation: {str(e)}",
            style="bold red"
        )
        logger.error("license_activation_failed", error=str(e))
        raise click.Abort()


def _display_founder_activation(license_info) -> None:
    """Display celebration message for founder licenses."""
    console.print()
    console.print(
        Panel(
            "[bold cyan]🎉 WELCOME, FOUNDER! 🎉[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_info.tier.upper()}\n"
            f"[bold]Price:[/bold] €{license_info.locked_price}/month [green](locked forever)[/green]\n"
            f"[bold]Email:[/bold] {license_info.email}\n"
            f"[bold]Status:[/bold] 🏆 [bold yellow]FOUNDER BADGE[/bold yellow]\n\n"
            "[bold green]You're one of the first 50 customers![/bold green]\n"
            f"[bold]Annual Savings:[/bold] €{license_info.get_savings():,.0f}/year\n\n"
            "[dim]Your founder price is locked in forever. Even when we raise\n"
            "prices to €299/month, you'll always pay €99/month.[/dim]",
            title="✨ License Activated ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    # Features table
    _display_features_table(license_info)

    # Coming soon
    _display_coming_soon()

    console.print(
        "\n✅ License activated successfully! Run [bold cyan]complio scan[/bold cyan] to get started.\n",
        style="green"
    )


def _display_early_access_activation(license_info) -> None:
    """Display message for early access (non-founder) licenses."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]🚀 EARLY ACCESS ACTIVATED[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_info.tier.upper()}\n"
            f"[bold]Email:[/bold] {license_info.email}\n"
            f"[bold]Expires:[/bold] {_format_expiry(license_info.expires)}\n\n"
            "[green]You have access to all current and upcoming features![/green]",
            title="✨ License Activated ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    _display_features_table(license_info)
    _display_coming_soon()

    console.print(
        "\n✅ License activated successfully! Run [bold cyan]complio scan[/bold cyan] to get started.\n",
        style="green"
    )


def _display_pro_activation(license_info) -> None:
    """Display message for pro licenses."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]⚡ PRO LICENSE ACTIVATED[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_info.tier.upper()}\n"
            f"[bold]Email:[/bold] {license_info.email}\n"
            f"[bold]Company:[/bold] {license_info.company or 'N/A'}\n"
            f"[bold]Expires:[/bold] {_format_expiry(license_info.expires)}\n\n"
            "[green]Full access to professional features![/green]",
            title="✨ License Activated ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    _display_features_table(license_info)

    console.print(
        "\n✅ License activated successfully! Run [bold cyan]complio scan[/bold cyan] to get started.\n",
        style="green"
    )


def _display_enterprise_activation(license_info) -> None:
    """Display message for enterprise licenses."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]🏢 ENTERPRISE LICENSE ACTIVATED[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_info.tier.upper()}\n"
            f"[bold]Email:[/bold] {license_info.email}\n"
            f"[bold]Company:[/bold] {license_info.company or 'N/A'}\n"
            f"[bold]Expires:[/bold] {_format_expiry(license_info.expires)}\n\n"
            "[green]Full access to all enterprise features![/green]",
            title="✨ License Activated ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    _display_features_table(license_info)

    console.print(
        "\n✅ License activated successfully!\n",
        style="green"
    )


def _display_standard_activation(license_info) -> None:
    """Display message for standard/unknown tiers."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]LICENSE ACTIVATED[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_info.tier.upper()}\n"
            f"[bold]Email:[/bold] {license_info.email}\n"
            f"[bold]Expires:[/bold] {_format_expiry(license_info.expires)}",
            title="✨ License Activated ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def _display_features_table(license_info) -> None:
    """Display table of active features."""
    console.print("\n[bold]Active Features:[/bold]")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Feature", style="cyan")

    # Group features for display
    feature_display = {
        "scanning": "✅ Compliance Scanning",
        "basic_tests": "✅ Basic Compliance Tests",
        "advanced_tests": "✅ Advanced Compliance Tests",
        "markdown_reports": "✅ Markdown Reports",
        "json_reports": "✅ JSON Reports",
        "pdf_reports": "✅ PDF Reports",
        "email_notifications": "✅ Email Notifications",
        "multi_profile": "✅ Multi-Profile Support",
        "multi_region": "✅ Multi-Region Support",
        "parallel_execution": "✅ Parallel Test Execution",
        "multi_cloud": "✅ Multi-Cloud Support",
        "soc2_framework": "✅ SOC 2 Framework",
        "api_access": "✅ API Access",
        "sso": "✅ SSO Integration",
        "multi_user": "✅ Multi-User Support",
        "audit_logs": "✅ Audit Logs",
        "custom_tests": "✅ Custom Tests",
    }

    for feature in license_info.features:
        if feature in feature_display:
            table.add_row(feature_display[feature])

    console.print(table)


def _display_coming_soon() -> None:
    """Display coming soon features."""
    console.print("\n[bold]Coming in Next 6 Weeks:[/bold]")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Feature", style="yellow")

    coming_soon = [
        "🚀 10+ Additional Compliance Tests",
        "🚀 PDF Report Generation with Charts",
        "🚀 Email Notifications & Scheduling",
        "🚀 SOC 2 Compliance Framework",
        "🚀 Historical Trend Analysis",
        "🚀 CI/CD Integration",
    ]

    for feature in coming_soon:
        table.add_row(feature)

    console.print(table)


def _format_expiry(expires) -> str:
    """Format expiry date for display."""
    if expires is None:
        return "[green]Lifetime[/green]"
    return expires.strftime("%Y-%m-%d")


def _mask_key(license_key: str) -> str:
    """Mask license key for logging."""
    parts = license_key.split("-")
    if len(parts) >= 2:
        return "-".join(["****"] * (len(parts) - 1) + [parts[-1]])
    return "****"


__all__ = ["activate"]

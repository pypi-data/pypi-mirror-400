"""
License information command for Complio.

This command displays the current license status and provides upgrade
messaging for free tier users.
"""

import click
import structlog
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from complio.licensing.validator import DEV_MODE, LicenseValidator

logger = structlog.get_logger(__name__)
console = Console()


@click.command(name="license")
@click.pass_context
def license_info(ctx: click.Context) -> None:
    """
    Show license information and status.

    Displays the current license tier, active features, and upgrade
    options. Free tier users see the Early Access offer.

    Example:
        complio license
    """
    logger.info("license_info_command_started")

    validator = LicenseValidator()
    tier = validator.get_current_tier()
    license_data = validator.get_license_info()

    # DEV MODE warning
    if DEV_MODE:
        _display_dev_mode_warning()

    # Display based on tier
    if tier == "free":
        _display_free_tier(validator)
    elif tier == "early_access" and license_data and license_data.is_founder():
        _display_founder_license(license_data)
    elif tier == "early_access":
        _display_early_access_license(license_data)
    elif tier == "pro":
        _display_pro_license(license_data)
    elif tier == "enterprise":
        _display_enterprise_license(license_data)
    else:
        _display_unknown_tier(tier)


def _display_dev_mode_warning() -> None:
    """Display warning when DEV_MODE is active."""
    console.print()
    console.print(
        Panel(
            "[bold yellow]⚠️  DEV MODE ACTIVE ⚠️[/bold yellow]\n\n"
            "All licensing checks are bypassed.\n"
            "You have Early Access tier with all features enabled.\n\n"
            "[dim]To disable: unset COMPLIO_DEV_MODE[/dim]",
            border_style="yellow",
            padding=(1, 2),
        )
    )


def _display_free_tier(validator: LicenseValidator) -> None:
    """Display free tier with upgrade offer."""
    console.print()
    console.print(
        Panel(
            "[bold]Current License:[/bold] FREE TIER\n\n"
            "❌ No compliance scanning available\n"
            "❌ No reports\n"
            "❌ No test execution\n\n"
            "[yellow]Upgrade to unlock full compliance testing![/yellow]",
            title="🔒 License Status",
            border_style="yellow",
            padding=(1, 2),
        )
    )

    # Display Early Access offer
    console.print("\n" + "═" * 70)
    console.print(
        "[bold cyan]🎯 EARLY ACCESS OFFER - LIMITED TO 50 FOUNDERS[/bold cyan]"
    )
    console.print("═" * 70 + "\n")

    # Pricing comparison
    pricing_table = Table(show_header=True, box=None)
    pricing_table.add_column("", style="bold")
    pricing_table.add_column("Early Access", style="green", justify="center")
    pricing_table.add_column("Regular Price", style="red", justify="center")

    pricing_table.add_row(
        "Monthly Price",
        "[bold green]€99[/bold green]",
        "[bold red strikethrough]€299[/bold red strikethrough]"
    )
    pricing_table.add_row(
        "Annual Cost",
        "[green]€1,188[/green]",
        "[red strikethrough]€3,588[/red strikethrough]"
    )
    pricing_table.add_row(
        "Annual Savings",
        "[bold green]€2,400 💰[/bold green]",
        "—"
    )
    pricing_table.add_row(
        "Price Guarantee",
        "[bold green]Locked Forever 🔒[/bold green]",
        "Subject to increase"
    )

    console.print(pricing_table)

    # What you get today
    console.print("\n[bold]✨ What You Get TODAY:[/bold]")
    today_features = Table(show_header=False, box=None, padding=(0, 2))
    today_features.add_column("Feature", style="cyan")

    today_features.add_row("✅ All 4 ISO 27001 compliance tests")
    today_features.add_row("✅ S3 Encryption scanning")
    today_features.add_row("✅ EC2 Security Groups scanning")
    today_features.add_row("✅ IAM Password Policy scanning")
    today_features.add_row("✅ CloudTrail Logging scanning")
    today_features.add_row("✅ Parallel test execution (4x faster)")
    today_features.add_row("✅ JSON & Markdown reports")
    today_features.add_row("✅ Cryptographically signed evidence")
    today_features.add_row("✅ Rich CLI with progress bars")
    today_features.add_row("✅ Multi-profile & multi-region support")

    console.print(today_features)

    # What's coming soon
    console.print("\n[bold]🚀 Coming in Next 6 Weeks:[/bold]")
    coming_features = Table(show_header=False, box=None, padding=(0, 2))
    coming_features.add_column("Feature", style="yellow")

    coming_features.add_row("📈 10+ additional compliance tests")
    coming_features.add_row("📊 PDF report generation with charts")
    coming_features.add_row("📧 Email notifications & scheduling")
    coming_features.add_row("🛡️  SOC 2 compliance framework")
    coming_features.add_row("📉 Historical trend analysis")
    coming_features.add_row("🔄 CI/CD integration")
    coming_features.add_row("🌍 Multi-cloud support (Azure, GCP)")

    console.print(coming_features)

    # Founder benefits
    console.print("\n[bold]🏆 Founder Benefits:[/bold]")
    founder_table = Table(show_header=False, box=None, padding=(0, 2))
    founder_table.add_column("Benefit", style="yellow")

    founder_table.add_row("💰 Price locked at €99/month forever")
    founder_table.add_row("🏆 Founder badge on profile")
    founder_table.add_row("🎯 Priority feature requests")
    founder_table.add_row("💬 Direct Slack channel access")
    founder_table.add_row("♾️  Lifetime updates included")

    console.print(founder_table)

    # Call to action
    console.print("\n" + "═" * 70)
    console.print(
        "[bold green]📧 Get Your License Key:[/bold green]\n"
        "   Visit: [cyan]https://compl.io/early-access[/cyan]\n"
        "   Email: [cyan]founders@compl.io[/cyan]\n\n"
        "[bold yellow]💡 Already have a key?[/bold yellow]\n"
        "   Run: [cyan]complio activate --license-key YOUR-KEY[/cyan]\n"
    )
    console.print("═" * 70 + "\n")


def _display_founder_license(license_data) -> None:
    """Display founder license status with celebration."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]🏆 FOUNDER LICENSE 🏆[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_data.tier.upper()}\n"
            f"[bold]Email:[/bold] {license_data.email}\n"
            f"[bold]Price:[/bold] €{license_data.locked_price}/month [green](locked forever)[/green]\n"
            f"[bold]Expires:[/bold] {_format_expiry(license_data.expires)}\n"
            f"[bold]Status:[/bold] ✅ [bold green]ACTIVE[/bold green]\n\n"
            f"[bold yellow]You're one of the first 50 customers![/bold yellow]\n"
            f"[bold]Annual Savings:[/bold] €{license_data.get_savings():,.0f}/year 💰",
            title="✨ License Status ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    _display_active_features(license_data)
    _display_coming_features()


def _display_early_access_license(license_data) -> None:
    """Display early access license status."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]🚀 EARLY ACCESS LICENSE[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_data.tier.upper()}\n"
            f"[bold]Email:[/bold] {license_data.email}\n"
            f"[bold]Expires:[/bold] {_format_expiry(license_data.expires)}\n"
            f"[bold]Status:[/bold] ✅ [bold green]ACTIVE[/bold green]",
            title="✨ License Status ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    _display_active_features(license_data)
    _display_coming_features()


def _display_pro_license(license_data) -> None:
    """Display pro license status."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]⚡ PRO LICENSE[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_data.tier.upper()}\n"
            f"[bold]Email:[/bold] {license_data.email}\n"
            f"[bold]Company:[/bold] {license_data.company or 'N/A'}\n"
            f"[bold]Expires:[/bold] {_format_expiry(license_data.expires)}\n"
            f"[bold]Status:[/bold] ✅ [bold green]ACTIVE[/bold green]",
            title="✨ License Status ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    _display_active_features(license_data)


def _display_enterprise_license(license_data) -> None:
    """Display enterprise license status."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]🏢 ENTERPRISE LICENSE[/bold cyan]\n\n"
            f"[bold]Tier:[/bold] {license_data.tier.upper()}\n"
            f"[bold]Email:[/bold] {license_data.email}\n"
            f"[bold]Company:[/bold] {license_data.company or 'N/A'}\n"
            f"[bold]Expires:[/bold] {_format_expiry(license_data.expires)}\n"
            f"[bold]Status:[/bold] ✅ [bold green]ACTIVE[/bold green]",
            title="✨ License Status ✨",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    _display_active_features(license_data)


def _display_unknown_tier(tier: str) -> None:
    """Display unknown tier status."""
    console.print()
    console.print(
        Panel(
            f"[bold]Current License:[/bold] {tier.upper()}\n\n"
            "[yellow]Unknown license tier[/yellow]\n"
            "Please contact support@compl.io for assistance.",
            title="⚠️  License Status",
            border_style="yellow",
            padding=(1, 2),
        )
    )


def _display_active_features(license_data) -> None:
    """Display table of active features."""
    console.print("\n[bold]✅ Active Features:[/bold]")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Feature", style="green")

    feature_display = {
        "scanning": "Compliance Scanning",
        "basic_tests": "Basic Compliance Tests",
        "advanced_tests": "Advanced Compliance Tests",
        "markdown_reports": "Markdown Reports",
        "json_reports": "JSON Reports",
        "pdf_reports": "PDF Reports",
        "email_notifications": "Email Notifications",
        "multi_profile": "Multi-Profile Support",
        "multi_region": "Multi-Region Support",
        "parallel_execution": "Parallel Test Execution",
        "multi_cloud": "Multi-Cloud Support",
        "soc2_framework": "SOC 2 Framework",
        "api_access": "API Access",
        "sso": "SSO Integration",
        "multi_user": "Multi-User Support",
        "audit_logs": "Audit Logs",
        "custom_tests": "Custom Tests",
    }

    for feature in license_data.features:
        if feature in feature_display:
            table.add_row(f"✅ {feature_display[feature]}")

    console.print(table)


def _display_coming_features() -> None:
    """Display coming soon features."""
    console.print("\n[bold]🚀 Coming in Next 6 Weeks:[/bold]")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Feature", style="yellow")

    coming = [
        "10+ Additional Compliance Tests",
        "PDF Report Generation with Charts",
        "Email Notifications & Scheduling",
        "SOC 2 Compliance Framework",
        "Historical Trend Analysis",
        "CI/CD Integration",
    ]

    for feature in coming:
        table.add_row(f"🚀 {feature}")

    console.print(table)
    console.print()


def _format_expiry(expires) -> str:
    """Format expiry date for display."""
    if expires is None:
        return "[green]Lifetime[/green]"
    return expires.strftime("%Y-%m-%d")


__all__ = ["license_info"]

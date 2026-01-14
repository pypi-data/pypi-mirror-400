"""
History command for viewing and comparing past scans.

This module implements CLI commands for managing scan history:
- complio history: View recent scans
- complio compare: Compare two scans

Example:
    $ complio history
    $ complio history --limit 20
    $ complio compare scan_20260107_162335_abc123 scan_20260106_143022_xyz789
"""

from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from complio.utils.history import (
    clear_old_history,
    compare_scans,
    get_scan_by_id,
    get_scan_history,
)
from complio.utils.logger import get_logger


@click.command()
@click.option(
    "--limit",
    "-n",
    default=10,
    type=int,
    help="Maximum number of scans to display",
    show_default=True,
)
@click.option(
    "--details",
    is_flag=True,
    default=False,
    help="Show detailed information for each scan",
)
def history(limit: int, details: bool) -> None:
    """View scan history.

    Displays a list of recent compliance scans with summary information.
    Use this to track compliance trends over time and reference past results.

    Examples:

        # View last 10 scans
        $ complio history

        # View last 20 scans
        $ complio history --limit 20

        # View with detailed test results
        $ complio history --details

    Scan results are stored locally in ~/.complio/history/
    """
    console = Console()
    logger = get_logger(__name__)

    try:
        # Get scan history
        scans = get_scan_history(limit=limit)

        if not scans:
            console.print("\n[yellow]No scan history found[/yellow]")
            console.print("\n[dim]Run 'complio scan' to create your first scan[/dim]\n")
            return

        # Display scans in table
        table = Table(
            title=f"Scan History (Last {len(scans)} scans)",
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("Scan ID", style="cyan", no_wrap=True)
        table.add_column("Timestamp", style="green")
        table.add_column("Region", style="yellow")
        table.add_column("Score", style="magenta", justify="right")
        table.add_column("Status", style="bold")
        table.add_column("Tests", justify="right")

        for scan in scans:
            scan_id = scan["scan_id"]
            timestamp = scan["timestamp"][:19]  # Remove microseconds
            region = scan["region"]
            score = scan["summary"]["overall_score"]
            status = scan["summary"]["compliance_status"]
            total_tests = scan["summary"]["total_tests"]
            passed = scan["summary"]["passed_tests"]
            failed = scan["summary"]["failed_tests"]

            # Color code status
            if status == "COMPLIANT":
                status_display = f"[green]✅ {status}[/green]"
            else:
                status_display = f"[red]❌ {status}[/red]"

            # Color code score
            if score >= 90:
                score_display = f"[green]{score}%[/green]"
            elif score >= 70:
                score_display = f"[yellow]{score}%[/yellow]"
            else:
                score_display = f"[red]{score}%[/red]"

            tests_display = f"{passed}/{total_tests}"
            if failed > 0:
                tests_display += f" ([red]{failed} failed[/red])"

            table.add_row(
                scan_id,
                timestamp,
                region,
                score_display,
                status_display,
                tests_display,
            )

        console.print()
        console.print(table)
        console.print()

        # Show detailed results if requested
        if details:
            console.print("[bold cyan]Detailed Test Results:[/bold cyan]\n")
            for scan in scans:
                console.print(f"[bold]{scan['scan_id']}[/bold]")
                console.print(f"  Timestamp: {scan['timestamp']}")
                console.print(f"  Region: {scan['region']}")
                console.print(f"  Score: {scan['summary']['overall_score']}%")
                console.print("  Test Results:")

                for test_result in scan.get("test_results", []):
                    status_emoji = {
                        "passed": "✅",
                        "warning": "⚠️",
                        "failed": "❌",
                        "error": "🚫",
                    }.get(test_result["status"], "❓")

                    console.print(
                        f"    {status_emoji} {test_result['test_name']}: "
                        f"{test_result['score']}% "
                        f"({test_result['findings_count']} findings)"
                    )
                console.print()

        # Show helpful tips
        console.print("[dim]💡 Tip: Use 'complio compare <scan_id1> <scan_id2>' to compare two scans[/dim]\n")

        logger.info("history_viewed", scan_count=len(scans))

    except Exception as e:
        logger.error("history_command_failed", error=str(e))
        console.print(f"\n[red]❌ Failed to retrieve scan history: {str(e)}[/red]\n")
        raise click.Abort()


@click.command()
@click.argument("scan_id_1")
@click.argument("scan_id_2")
@click.option(
    "--detailed",
    is_flag=True,
    default=False,
    help="Show test-by-test comparison",
)
def compare(scan_id_1: str, scan_id_2: str, detailed: bool) -> None:
    """Compare two scans to track compliance changes.

    Compares two compliance scans and shows the differences in scores,
    test results, and overall compliance status. Use this to track
    improvement or identify regressions.

    Arguments:

        SCAN_ID_1    First scan ID (newer scan)

        SCAN_ID_2    Second scan ID (older scan for comparison)

    Examples:

        # Compare two scans
        $ complio compare scan_20260107_162335_abc123 scan_20260106_143022_xyz789

        # Compare with detailed test breakdown
        $ complio compare scan_20260107_... scan_20260106_... --detailed

    Note: Scan IDs can be found using 'complio history'
    """
    console = Console()
    logger = get_logger(__name__)

    try:
        # Get comparison data
        comparison = compare_scans(scan_id_1, scan_id_2)

        scan1 = comparison["scan1"]
        scan2 = comparison["scan2"]
        diff = comparison["differences"]

        # Display comparison header
        console.print("\n[bold cyan]Scan Comparison[/bold cyan]\n")

        # Comparison table
        table = Table(show_header=True, header_style="bold")
        table.add_column("Metric", style="cyan")
        table.add_column("Scan 1 (Newer)", style="green", justify="right")
        table.add_column("Scan 2 (Older)", style="yellow", justify="right")
        table.add_column("Change", style="magenta", justify="right")

        # Scan IDs
        table.add_row(
            "Scan ID",
            scan1["scan_id"][:25] + "...",
            scan2["scan_id"][:25] + "...",
            "-",
        )

        # Timestamps
        table.add_row(
            "Timestamp",
            scan1["timestamp"][:19],
            scan2["timestamp"][:19],
            "-",
        )

        # Overall Score
        score_change = diff["score_change"]
        if score_change > 0:
            score_display = f"[green]+{score_change}%[/green]"
            score_emoji = "📈"
        elif score_change < 0:
            score_display = f"[red]{score_change}%[/red]"
            score_emoji = "📉"
        else:
            score_display = "[dim]No change[/dim]"
            score_emoji = "➡️"

        table.add_row(
            "Overall Score",
            f"{scan1['score']}%",
            f"{scan2['score']}%",
            f"{score_emoji} {score_display}",
        )

        # Passed Tests
        passed_change = diff["passed_change"]
        if passed_change > 0:
            passed_display = f"[green]+{passed_change}[/green]"
        elif passed_change < 0:
            passed_display = f"[red]{passed_change}[/red]"
        else:
            passed_display = "[dim]No change[/dim]"

        table.add_row(
            "Passed Tests",
            str(scan1["passed"]),
            str(scan2["passed"]),
            passed_display,
        )

        # Failed Tests
        failed_change = diff["failed_change"]
        if failed_change < 0:
            failed_display = f"[green]{failed_change}[/green]"
        elif failed_change > 0:
            failed_display = f"[red]+{failed_change}[/red]"
        else:
            failed_display = "[dim]No change[/dim]"

        table.add_row(
            "Failed Tests",
            str(scan1["failed"]),
            str(scan2["failed"]),
            failed_display,
        )

        console.print(table)
        console.print()

        # Summary message
        direction = diff["score_change_direction"]
        if direction == "improved":
            console.print(
                f"[bold green]✅ Compliance has improved by {abs(score_change)}%[/bold green]\n"
            )
        elif direction == "declined":
            console.print(
                f"[bold red]⚠️ Compliance has declined by {abs(score_change)}%[/bold red]\n"
            )
        else:
            console.print("[bold]➡️ No change in compliance score[/bold]\n")

        # Detailed comparison if requested
        if detailed:
            console.print("[bold cyan]Test-by-Test Comparison:[/bold cyan]\n")
            console.print("[dim]Note: Detailed test comparison requires scan details[/dim]\n")

            # Get full scan details
            scan1_full = get_scan_by_id(scan_id_1)
            scan2_full = get_scan_by_id(scan_id_2)

            if scan1_full and scan2_full:
                # Build test result maps
                test_map_1 = {
                    t["test_id"]: t for t in scan1_full.get("test_results", [])
                }
                test_map_2 = {
                    t["test_id"]: t for t in scan2_full.get("test_results", [])
                }

                all_tests = set(test_map_1.keys()) | set(test_map_2.keys())

                for test_id in sorted(all_tests):
                    test1 = test_map_1.get(test_id)
                    test2 = test_map_2.get(test_id)

                    if test1 and test2:
                        score_diff = test1["score"] - test2["score"]
                        if score_diff != 0:
                            if score_diff > 0:
                                change = f"[green]+{score_diff}%[/green]"
                            else:
                                change = f"[red]{score_diff}%[/red]"
                            console.print(
                                f"  • {test1['test_name']}: "
                                f"{test1['score']}% → {test2['score']}% ({change})"
                            )
                    elif test1:
                        console.print(
                            f"  • [green]NEW:[/green] {test1['test_name']} ({test1['score']}%)"
                        )
                    elif test2:
                        console.print(
                            f"  • [red]REMOVED:[/red] {test2['test_name']} ({test2['score']}%)"
                        )

                console.print()

        logger.info(
            "scans_compared",
            scan_id_1=scan_id_1,
            scan_id_2=scan_id_2,
            score_change=score_change,
        )

    except ValueError as e:
        logger.error("compare_failed", error=str(e))
        console.print(f"\n[red]❌ {str(e)}[/red]")
        console.print("\n[dim]💡 Tip: Use 'complio history' to see available scan IDs[/dim]\n")
        raise click.Abort()
    except Exception as e:
        logger.error("compare_command_failed", error=str(e))
        console.print(f"\n[red]❌ Failed to compare scans: {str(e)}[/red]\n")
        raise click.Abort()


@click.command(name="clear-history")
@click.option(
    "--days",
    "-d",
    default=30,
    type=int,
    help="Keep scans from last N days (default: 30)",
    show_default=True,
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Skip confirmation prompt",
)
def clear_history_cmd(days: int, force: bool) -> None:
    """Clear old scan history to free up disk space.

    Removes scan history files older than the specified number of days.
    This helps manage disk space while retaining recent compliance data.

    Examples:

        # Clear scans older than 30 days
        $ complio clear-history

        # Keep only last 7 days of scans
        $ complio clear-history --days 7

        # Clear without confirmation
        $ complio clear-history --days 30 --force

    Note: This action cannot be undone.
    """
    console = Console()
    logger = get_logger(__name__)

    try:
        # Get current scan count
        scans = get_scan_history(limit=1000)
        total_scans = len(scans)

        if total_scans == 0:
            console.print("\n[yellow]No scan history to clear[/yellow]\n")
            return

        # Confirmation unless --force
        if not force:
            console.print(f"\n[yellow]⚠️ This will delete scans older than {days} days[/yellow]")
            console.print(f"Current total scans: {total_scans}\n")

            if not click.confirm("Are you sure?", default=False):
                console.print("\n[dim]Operation cancelled[/dim]\n")
                return

        # Clear old history
        deleted_count = clear_old_history(keep_days=days)

        if deleted_count > 0:
            console.print(
                f"\n[green]✅ Deleted {deleted_count} old scan(s)[/green]"
            )
            remaining = total_scans - deleted_count
            console.print(f"[dim]Remaining scans: {remaining}[/dim]\n")
            logger.info("history_cleared", deleted_count=deleted_count, days=days)
        else:
            console.print(
                f"\n[dim]No scans older than {days} days found[/dim]\n"
            )

    except Exception as e:
        logger.error("clear_history_failed", error=str(e))
        console.print(f"\n[red]❌ Failed to clear history: {str(e)}[/red]\n")
        raise click.Abort()

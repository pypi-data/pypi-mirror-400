"""
Scan command for running compliance tests.

This module implements the 'complio scan' CLI command for executing
compliance tests and generating reports.

Example:
    $ complio scan
    $ complio scan --test s3_encryption
    $ complio scan --region us-west-2 --output report.json
"""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from complio.cli.output import ComplianceOutput
from complio.connectors.aws.client import AWSConnector
from complio.core.registry import TestRegistry
from complio.core.runner import TestRunner
from complio.licensing.exceptions import FeatureNotAvailableError
from complio.licensing.validator import LicenseValidator
from complio.reporters.generator import ReportGenerator
from complio.utils.errors import handle_aws_error, validate_profile_exists, validate_region_format
from complio.utils.history import save_scan_to_history
from complio.utils.logger import get_logger


# ============================================================================
# ARGUMENT VALIDATION CALLBACKS
# ============================================================================


def validate_region_param(ctx, param, value):
    """Validate region parameter format and emptiness."""
    if value is None:
        return None

    # Check for empty string
    if isinstance(value, str) and value.strip() == "":
        raise click.BadParameter(
            "Region cannot be empty. "
            "Valid regions: us-east-1, eu-west-1, eu-west-3, etc."
        )

    # Validate format
    if not validate_region_format(value):
        raise click.BadParameter(
            f"'{value}' is not a valid AWS region format. "
            "Expected format: us-east-1, eu-west-3, ap-southeast-2, etc."
        )

    return value


def validate_profile_param(ctx, param, value):
    """Validate profile parameter exists and is not empty."""
    if value is None or value == "default":
        return value

    # Check for empty string
    if isinstance(value, str) and value.strip() == "":
        raise click.BadParameter("Profile name cannot be empty")

    # Verify profile exists (warning only, let boto3 handle actual failure)
    if not validate_profile_exists(value):
        import configparser
        import os
        try:
            config = configparser.ConfigParser()
            config.read(os.path.expanduser('~/.aws/credentials'))
            available = ", ".join(config.sections()) if config.sections() else "none"
            raise click.BadParameter(
                f"Profile '{value}' not found in ~/.aws/credentials. "
                f"Available profiles: {available}"
            )
        except:
            pass  # Let boto3 handle validation

    return value


@click.command()
@click.option(
    "--profile",
    default="default",
    callback=validate_profile_param,
    help="AWS credentials profile to use",
    show_default=True,
)
@click.option(
    "--region",
    default=None,
    callback=validate_region_param,
    help="AWS region to scan (uses profile's region if not specified)",
)
@click.option(
    "--regions",
    default=None,
    help="Comma-separated list of regions to scan (e.g., 'us-east-1,eu-west-1')",
)
@click.option(
    "--all-regions",
    is_flag=True,
    default=False,
    help="Scan all available AWS regions (takes longer)",
)
@click.option(
    "--test",
    "test_id",
    default=None,
    help="Run specific test only (e.g., 's3_encryption')",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Save report to file (auto-detects format from extension: .json, .md)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "markdown"], case_sensitive=False),
    default=None,
    help="Report format (auto-detected from --output if not specified)",
)
@click.option(
    "--parallel",
    is_flag=True,
    default=False,
    help="Run tests in parallel (faster but uses more resources)",
)
@click.option(
    "--list-tests",
    is_flag=True,
    default=False,
    help="List all available tests and exit",
)
@click.pass_context
def scan(
    ctx: click.Context,
    profile: str,
    region: Optional[str],
    regions: Optional[str],
    all_regions: bool,
    test_id: Optional[str],
    output: Optional[Path],
    output_format: Optional[str],
    parallel: bool,
    list_tests: bool,
) -> None:
    """Run compliance tests on AWS infrastructure.

    Executes ISO 27001 compliance tests against your AWS environment
    and generates detailed reports with findings and remediation steps.

    Examples:

        # Run all tests on default profile
        $ complio scan

        # Run specific test
        $ complio scan --test s3_encryption

        # Scan specific region
        $ complio scan --region us-west-2

        # Scan multiple regions
        $ complio scan --regions us-east-1,eu-west-1,ap-southeast-2

        # Scan all AWS regions
        $ complio scan --all-regions

        # Save report to file
        $ complio scan --output report.json
        $ complio scan --output report.md --format markdown

        # Run tests in parallel (faster)
        $ complio scan --parallel

        # List all available tests
        $ complio scan --list-tests
    """
    console = Console()
    output_helper = ComplianceOutput()
    logger = get_logger(__name__)

    # List tests and exit if requested
    if list_tests:
        _list_available_tests(console)
        return

    # ========================================================================
    # LICENSE VALIDATION - GATE SCANNING FEATURE
    # ========================================================================

    # Check if scanning is allowed under current license
    try:
        validator = LicenseValidator()
        validator.require_feature("scanning", required_tier="early_access")

        # Log license tier for debugging
        tier = validator.get_current_tier()
        logger.info("license_check_passed", tier=tier, feature="scanning")

    except FeatureNotAvailableError as e:
        # Display upgrade message
        console.print(str(e), style="yellow")
        logger.warning("scanning_blocked_by_license", tier=validator.get_current_tier())
        raise click.Abort()

    # ========================================================================

    # Validate mutually exclusive region options
    region_options_count = sum([
        region is not None,
        regions is not None,
        all_regions,
    ])

    if region_options_count > 1:
        output_helper.error("Options --region, --regions, and --all-regions are mutually exclusive")
        output_helper.info("Use only one of these options at a time")
        raise click.Abort()

    # Determine regions to scan
    scan_regions = []

    if all_regions:
        # Get all AWS regions from the validation function
        scan_regions = [
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "eu-north-1",
            "ap-south-1", "ap-northeast-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2",
            "ca-central-1", "sa-east-1",
        ]
        output_helper.info(f"Scanning all {len(scan_regions)} AWS regions (this may take a while)")
    elif regions:
        # Parse comma-separated list
        scan_regions = [r.strip() for r in regions.split(",")]
        # Validate each region
        for r in scan_regions:
            if not validate_region_format(r):
                output_helper.error(f"Invalid region format: '{r}'")
                output_helper.info("Valid format: us-east-1, eu-west-3, ap-southeast-2, etc.")
                raise click.Abort()
            if not _validate_aws_region(r):
                output_helper.error(f"Unknown AWS region: '{r}'")
                output_helper.info("Valid regions: us-east-1, us-west-2, eu-west-1, eu-west-3, etc.")
                raise click.Abort()
        output_helper.info(f"Scanning {len(scan_regions)} regions: {', '.join(scan_regions)}")
    else:
        # Single region mode (existing behavior)
        scan_region = region
        if not scan_region:
            # Try to get region from AWS config/profile
            try:
                import boto3
                session = boto3.Session(profile_name=profile)
                scan_region = session.region_name
                if scan_region:
                    output_helper.info(f"Using region from AWS config: {scan_region}")
                else:
                    # Fall back to us-east-1 if no region in config
                    from complio.config.settings import get_settings
                    settings = get_settings()
                    scan_region = settings.default_region
                    output_helper.info(f"No region in AWS config, using default: {scan_region}")
            except Exception:
                # If boto3 fails, use default
                from complio.config.settings import get_settings
                settings = get_settings()
                scan_region = settings.default_region
                output_helper.info(f"Using default region: {scan_region}")

        # Validate region
        if not _validate_aws_region(scan_region):
            output_helper.error(f"Invalid AWS region: {scan_region}")
            output_helper.info("Valid regions include: us-east-1, us-west-2, eu-west-1, eu-west-3, eu-north-1, etc.")
            raise click.Abort()

        # Convert single region to list for unified processing
        scan_regions = [scan_region]

    # ========================================================================
    # MULTI-REGION SCANNING LOOP
    # ========================================================================

    # Store results from all regions
    all_regional_results = []
    failed_regions = []

    # Determine which tests to run (before region loop)
    if test_id:
        # Run single test
        registry = TestRegistry()
        if not registry.test_exists(test_id):
            output_helper.error(f"Test '{test_id}' not found")
            available_tests = registry.get_test_ids()
            output_helper.info(f"Available tests: {', '.join(available_tests)}")
            raise click.Abort()

        test_ids = [test_id]
        output_helper.info(f"Running single test: {test_id}")
    else:
        # Run all tests
        registry = TestRegistry()
        test_ids = registry.get_test_ids()
        output_helper.info(f"Running {len(test_ids)} compliance tests")

    # Loop through each region
    for region_index, scan_region in enumerate(scan_regions, 1):
        try:
            # Show region progress for multi-region scans
            if len(scan_regions) > 1:
                console.print(f"\n[bold cyan]Region {region_index}/{len(scan_regions)}: {scan_region}[/bold cyan]\n")

            # Initialize AWS connector with standard credentials (no password needed)
            # Reads from ~/.aws/credentials automatically
            connector = AWSConnector(
                profile_name=profile,
                region=scan_region,
                password=None,  # Use standard AWS credential chain
            )

            output_helper.success(f"Connecting to AWS region: {scan_region}")

            if not connector.connect():
                output_helper.error(f"Failed to connect to AWS region {scan_region}")
                failed_regions.append(scan_region)
                continue  # Skip to next region

            # Validate credentials (only once for first region)
            if region_index == 1:
                account_info = connector.validate_credentials()
                account_id = account_info.get("account_id", "unknown")
                output_helper.info(f"Connected to AWS Account: {account_id}")

            # Execute tests with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                progress_task = progress.add_task(
                    "[cyan]Running compliance tests...",
                    total=len(test_ids),
                )

                # Define progress callback to update Rich progress bar
                def progress_callback(test_name: str, current: int, total: int, scope: str = "regional") -> None:
                    """Update progress bar after each test completes with scope information."""
                    # Create scope label
                    if scope == "global":
                        scope_label = "[dim cyan](Global - All Regions)[/dim cyan]"
                    else:
                        scope_label = f"[dim cyan](Regional - {scan_region} only)[/dim cyan]"

                    description = f"[cyan]Test {current}/{total}:[/cyan] {test_name} {scope_label}"
                    progress.update(progress_task, completed=current, description=description)

                # Initialize test runner with progress callback
                runner = TestRunner(
                    connector=connector,
                    max_workers=4,
                    progress_callback=progress_callback,
                )

                # Run tests
                results = runner.run_tests(test_ids, parallel=parallel)

                # Ensure progress is at 100%
                progress.update(progress_task, completed=len(test_ids))

            # Store results with region info
            all_regional_results.append({
                "region": scan_region,
                "results": results,
            })

            # For single region, display results immediately
            if len(scan_regions) == 1:
                # Generate and display scan ID for reference
                from complio.reporters.generator import generate_scan_id
                scan_id = generate_scan_id()
                console.print(f"\n📋 Scan ID: [cyan]{scan_id}[/cyan]")
                console.print("   [dim]Reference this ID when contacting support[/dim]\n")

                # Save scan to history for later reference
                try:
                    history_path = save_scan_to_history(scan_id, results, scan_region)
                    logger.info("scan_saved_to_history", scan_id=scan_id, path=str(history_path))
                except Exception as e:
                    logger.warning("failed_to_save_history", scan_id=scan_id, error=str(e))
                    # Don't fail the scan if history saving fails

                # Display results summary
                _display_results_summary(console, results)

                # Display detailed findings
                _display_findings(console, results)
            else:
                # For multi-region, show brief summary per region
                console.print(f"\n[bold]Results for {scan_region}:[/bold]")
                console.print(f"  Score: {results.overall_score}%")
                console.print(f"  Passed: {results.passed_tests}/{results.total_tests}")
                console.print(f"  Failed: {results.failed_tests}")

        except Exception as e:
            # Log error but continue with other regions
            logger.error("region_scan_failed", region=scan_region, error=str(e))
            output_helper.error(f"Scan failed for region {scan_region}: {str(e)}")
            failed_regions.append(scan_region)
            continue

    # ========================================================================
    # MULTI-REGION RESULTS AGGREGATION
    # ========================================================================

    # If multiple regions, display aggregated results
    if len(scan_regions) > 1:
        console.print(f"\n[bold cyan]Multi-Region Scan Summary[/bold cyan]\n")

        # Display summary table
        from rich.table import Table
        summary_table = Table(title="Regional Results", show_header=True)
        summary_table.add_column("Region", style="cyan")
        summary_table.add_column("Score", style="magenta", justify="right")
        summary_table.add_column("Passed", style="green", justify="right")
        summary_table.add_column("Failed", style="red", justify="right")
        summary_table.add_column("Status", style="bold")

        for regional_data in all_regional_results:
            region = regional_data["region"]
            results = regional_data["results"]

            score_display = f"{results.overall_score}%"
            if results.overall_score >= 90:
                score_display = f"[green]{score_display}[/green]"
            elif results.overall_score >= 70:
                score_display = f"[yellow]{score_display}[/yellow]"
            else:
                score_display = f"[red]{score_display}[/red]"

            status = "✅ COMPLIANT" if results.overall_score >= 90 else "❌ NON-COMPLIANT"

            summary_table.add_row(
                region,
                score_display,
                str(results.passed_tests),
                str(results.failed_tests),
                status,
            )

        console.print(summary_table)
        console.print()

        if failed_regions:
            console.print(f"[yellow]⚠️ Failed to scan {len(failed_regions)} region(s): {', '.join(failed_regions)}[/yellow]\n")

        # Calculate aggregate statistics
        total_regions_scanned = len(all_regional_results)
        avg_score = sum(r["results"].overall_score for r in all_regional_results) / total_regions_scanned if total_regions_scanned > 0 else 0
        worst_region = min(all_regional_results, key=lambda r: r["results"].overall_score) if total_regions_scanned > 0 else None
        best_region = max(all_regional_results, key=lambda r: r["results"].overall_score) if total_regions_scanned > 0 else None

        console.print(f"[bold]Aggregate Statistics:[/bold]")
        console.print(f"  Total Regions Scanned: {total_regions_scanned}")
        console.print(f"  Average Score: {avg_score:.1f}%")
        if worst_region:
            console.print(f"  Worst Region: {worst_region['region']} ({worst_region['results'].overall_score}%)")
        if best_region:
            console.print(f"  Best Region: {best_region['region']} ({best_region['results'].overall_score}%)")
        console.print()

        # Use the worst region's results for final status determination
        if worst_region:
            results = worst_region["results"]
    else:
        # Single region - results already displayed above
        results = all_regional_results[0]["results"] if all_regional_results else None

    if not results:
        output_helper.error("All region scans failed")
        raise click.Abort()

    try:

        # Save or display report
        if output:
            # Auto-detect format from extension if not specified
            if not output_format:
                ext = output.suffix.lower()
                if ext == ".json":
                    output_format = "json"
                elif ext in [".md", ".markdown"]:
                    output_format = "markdown"
                else:
                    output_format = "json"  # default

            generator = ReportGenerator()
            generator.save_report(results, output, output_format)
            output_helper.success(f"Report saved to: {output}")
        else:
            # Display markdown report to console
            generator = ReportGenerator()
            if output_format == "json":
                console.print(generator.generate_json(results))
            else:
                console.print(generator.generate_markdown(results))

        # Exit with appropriate code
        if results.overall_score < 70:
            output_helper.warning(
                f"Compliance score ({results.overall_score}%) is below threshold"
            )
            raise click.exceptions.Exit(1)
        elif results.overall_score < 90:
            output_helper.warning(
                f"Compliance score ({results.overall_score}%) needs improvement"
            )
            raise click.exceptions.Exit(0)
        else:
            output_helper.success(f"Compliance score: {results.overall_score}% - PASSED!")
            raise click.exceptions.Exit(0)

    except click.exceptions.Exit:
        # Let Exit exceptions pass through to Click
        raise
    except (click.exceptions.Abort, FeatureNotAvailableError):
        # Let these exceptions pass through
        raise
    except Exception as e:
        # Try to provide user-friendly error messages for AWS errors
        from botocore.exceptions import BotoCoreError, ClientError
        if isinstance(e, (BotoCoreError, ClientError)):
            logger.error("scan_command_failed_aws_error", error=str(e))
            handle_aws_error(e)  # This will exit with user-friendly message
        else:
            # Other errors - show technical message with help
            logger.error("scan_command_failed", error=str(e))
            output_helper.error(f"Scan failed: {str(e)}")
            click.echo("\nFor help: https://docs.complio.tech/troubleshooting", err=True)
            click.echo("Support: support@complio.tech", err=True)
            raise click.Abort()


def _validate_aws_region(region: str) -> bool:
    """Validate that the provided region is a valid AWS region.

    Args:
        region: AWS region name to validate

    Returns:
        True if valid region, False otherwise
    """
    # List of valid AWS regions (as of 2024)
    # This is more reliable than trying to call AWS APIs which may fail due to credentials
    VALID_REGIONS = {
        # US regions
        "us-east-1", "us-east-2", "us-west-1", "us-west-2",
        # EU regions
        "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "eu-central-2",
        "eu-north-1", "eu-south-1", "eu-south-2",
        # Asia Pacific regions
        "ap-south-1", "ap-south-2", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
        "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-4",
        "ap-east-1",
        # Canada
        "ca-central-1",
        # South America
        "sa-east-1",
        # Middle East
        "me-south-1", "me-central-1",
        # Africa
        "af-south-1",
        # China (requires special account)
        "cn-north-1", "cn-northwest-1",
        # GovCloud
        "us-gov-east-1", "us-gov-west-1",
    }

    return region in VALID_REGIONS


def _list_available_tests(console: Console) -> None:
    """Display list of available tests."""
    registry = TestRegistry()

    table = Table(title="Available Compliance Tests", show_header=True)
    table.add_column("Test ID", style="cyan")
    table.add_column("Test Name", style="green")
    table.add_column("ISO 27001 Control", style="yellow")

    # Temporary connector for getting test names (won't be used)
    from complio.connectors.aws.client import AWSConnector
    temp_connector = AWSConnector("temp", "us-east-1")

    test_info = {
        "s3_encryption": "A.10.1.1",
        "ec2_security_groups": "A.13.1.1",
        "iam_password_policy": "A.9.4.3",
        "cloudtrail_logging": "A.12.4.1",
        # Phase 1: 8 New Tests
        "ebs_encryption": "A.8.24",
        "rds_encryption": "A.8.24",
        "secrets_manager_encryption": "A.8.24",
        "s3_public_access_block": "A.8.11",
        "cloudtrail_log_validation": "A.8.15",
        "cloudtrail_encryption": "A.8.15",
        "vpc_flow_logs": "A.8.16",
        "nacl_security": "A.8.20",
        # Phase 2: 8 New Tests
        "redshift_encryption": "A.8.24",
        "efs_encryption": "A.8.24",
        "dynamodb_encryption": "A.8.24",
        "elasticache_encryption": "A.8.24",
        "kms_key_rotation": "A.8.24",
        "access_key_rotation": "A.8.5",
        "mfa_enforcement": "A.8.5",
        "root_account_protection": "A.8.2",
        # Phase 3 Week 1: 6 Easy Tests
        "s3_versioning": "A.8.13",
        "backup_encryption": "A.8.24",
        "cloudwatch_retention": "A.8.15",
        "sns_encryption": "A.8.24",
        "cloudwatch_logs_encryption": "A.8.24",
        "vpn_security": "A.8.22",
        # Phase 3 Week 2: 9 Medium Tests (complete)
        "nacl_configuration": "A.8.20",
        "alb_nlb_security": "A.8.22",
        "cloudfront_https": "A.8.24",
        "transit_gateway_security": "A.8.22",
        "vpc_endpoints_security": "A.8.22",
        "network_firewall": "A.8.20",
        "direct_connect_security": "A.8.22",
        "cloudwatch_alarms": "A.8.16",
        "config_enabled": "A.8.16",
        # Phase 3 Week 3: 5 Hard Tests (complete!)
        "waf_configuration": "A.8.20",
        "api_gateway_security": "A.8.22",
        "guardduty_enabled": "A.8.16",
        "security_hub_enabled": "A.8.16",
        "eventbridge_rules": "A.8.16",
    }

    for test_id in registry.get_test_ids():
        test_class = registry.get_test(test_id)
        test_instance = test_class(temp_connector)
        control = test_info.get(test_id, "N/A")

        table.add_row(test_id, test_instance.test_name, control)

    console.print(table)


def _display_results_summary(console: Console, results) -> None:
    """Display test results summary table."""
    table = Table(title="Scan Results Summary", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Tests", str(results.total_tests))
    table.add_row("Passed", f"✅ {results.passed_tests}")
    table.add_row("Failed", f"❌ {results.failed_tests}")
    table.add_row("Errors", f"⚠️ {results.error_tests}")
    table.add_row("Overall Score", f"{results.overall_score}%")
    table.add_row("Execution Time", f"{results.execution_time:.2f}s")

    console.print()
    console.print(table)
    console.print()


def _display_findings(console: Console, results) -> None:
    """Display findings by severity."""
    # Count findings by severity (using strings since use_enum_values=True)
    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for test_result in results.test_results:
        for finding in test_result.findings:
            if finding.severity in severity_counts:
                severity_counts[finding.severity] += 1

    # Display critical and high findings
    critical_and_high = []
    for test_result in results.test_results:
        for finding in test_result.findings:
            if finding.severity in ["critical", "high"]:
                critical_and_high.append((test_result.test_name, finding))

    if critical_and_high:
        console.print("[bold red]🚨 Critical & High Severity Findings:[/bold red]")
        console.print()

        for test_name, finding in critical_and_high:
            severity_color = "red" if finding.severity == "critical" else "orange1"
            console.print(f"[{severity_color}]● {finding.severity}:[/{severity_color}] {finding.title}")
            console.print(f"  Test: {test_name}")
            console.print(f"  Resource: {finding.resource_id}")
            console.print()

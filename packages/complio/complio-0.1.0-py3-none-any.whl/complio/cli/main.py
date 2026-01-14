"""
Complio CLI - Main entry point.

This module defines the main CLI application and command groups.
All CLI commands are registered here and dispatched to their respective handlers.

Usage:
    complio --help
    complio configure
    complio list-profiles
    complio remove-profile <name>
    complio scan --region <region>
"""

import sys
from pathlib import Path
from typing import Optional

import click

from complio.cli import output
from complio.cli.banner import print_banner

# CLI version (sync with pyproject.toml)
VERSION = "0.1.0"


# ============================================================================
# MAIN CLI GROUP
# ============================================================================


@click.group(invoke_without_command=True)
@click.version_option(version=VERSION, prog_name="complio")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Complio - Compliance-as-Code Platform

    Automated ISO 27001 infrastructure compliance testing for AWS environments.

    \b
    AWS Credentials:
      Complio uses standard AWS CLI credentials from ~/.aws/credentials
      Configure with: aws configure
      Or optionally use: complio configure (with encryption)

    \b
    Common Commands:
      configure        (Optional) Set up AWS credentials with encryption
      license          Show license information and pricing
      activate         Activate a license key
      scan             Run compliance tests
      history          View past scan results
      compare          Compare two scans
      list-profiles    Show all stored credential profiles
      remove-profile   Delete a credential profile
      deactivate       Deactivate the current license

    \b
    Examples:
      # Configure AWS credentials (recommended)
      aws configure
      complio scan

      # Check license status
      complio license

      # Activate license
      complio activate --license-key YOUR-KEY

      # Run compliance scan with specific region
      complio scan --region eu-west-3

      # Run compliance scan with AWS CLI profile
      complio scan --profile production

    For more information, visit: https://compl.io
    """
    # Ensure context object exists for passing data between commands
    ctx.ensure_object(dict)

    # Show banner when no subcommand is provided
    if ctx.invoked_subcommand is None:
        print_banner()
        output.print_message("")
        click.echo(ctx.get_help())


# ============================================================================
# CONFIGURE COMMAND
# ============================================================================


@cli.command()
@click.option(
    "--profile",
    "-p",
    default="default",
    help="Profile name for credentials (default: 'default')",
    show_default=True,
)
@click.option(
    "--access-key",
    "-a",
    help="AWS Access Key ID (will prompt if not provided)",
)
@click.option(
    "--secret-key",
    "-s",
    help="AWS Secret Access Key (will prompt if not provided)",
)
@click.option(
    "--session-token",
    "-t",
    help="AWS Session Token for temporary credentials (optional)",
)
@click.option(
    "--password",
    help="Encryption password (will prompt if not provided)",
)
def configure(
    profile: str,
    access_key: Optional[str],
    secret_key: Optional[str],
    session_token: Optional[str],
    password: Optional[str],
) -> None:
    """
    Configure AWS credentials with secure encryption (OPTIONAL).

    NOTE: Complio can use standard AWS CLI credentials from ~/.aws/credentials.
    If you already have AWS CLI configured (aws configure), you can skip this
    command and use --profile to select your AWS CLI profile.

    This command provides an ALTERNATIVE way to store credentials with additional
    encryption. It stores them in ~/.complio/credentials.enc with AES-256 encryption.

    \b
    Security Features:
      • AES-256 encryption (Fernet)
      • PBKDF2 key derivation (480,000 iterations)
      • Secure file permissions (chmod 600)
      • Zero credential logging

    \b
    Examples:
      # Use AWS CLI credentials (recommended)
      aws configure
      complio scan

      # OR use encrypted Complio credentials
      complio configure
      complio scan --password YOUR_PASSWORD

      # Specify profile name
      complio configure --profile production

      # Non-interactive mode (for automation)
      complio configure --access-key AKIA... --secret-key ... --password ...

    \b
    Note: Credentials are stored locally and never sent to external servers.
    """
    from complio.utils.crypto import CredentialManager
    from complio.utils.exceptions import ComplioError

    try:
        output.print_header("AWS Credential Configuration")

        # Initialize credential manager
        manager = CredentialManager()

        # Check if profile already exists
        existing_profiles = manager.list_profiles()
        if profile in existing_profiles:
            output.warning(
                f"Profile '{profile}' already exists",
                "Continuing will overwrite existing credentials",
            )
            if not output.confirm("Continue?", default=False):
                output.info("Configuration cancelled")
                sys.exit(0)
            output.print_message("")

        # Track if we're in interactive mode (any value was missing)
        interactive_mode = not access_key or not secret_key or not password

        # Interactive prompts for missing values
        if not access_key:
            output.info("AWS credentials can be found in AWS Console → IAM → Security Credentials")
            access_key = output.prompt("AWS Access Key ID")

        if not secret_key:
            secret_key = output.prompt("AWS Secret Access Key", password=True)

        # Optional session token (only ask if in interactive mode)
        if not session_token and interactive_mode:
            if output.confirm("Using temporary credentials (session token)?", default=False):
                session_token = output.prompt("AWS Session Token", password=True)

        # Encryption password
        if not password:
            output.print_message("")
            output.info(
                "Choose a strong encryption password",
                "Minimum 8 characters, use letters, numbers, and symbols",
            )
            password = output.prompt("Encryption password", password=True)
            password_confirm = output.prompt("Confirm password", password=True)

            if password != password_confirm:
                output.error("Passwords do not match", "Please try again")

        # Encrypt and store credentials
        output.print_message("")
        output.info(f"Encrypting credentials for profile '{profile}'...")

        manager.encrypt_credentials(
            access_key=access_key,
            secret_key=secret_key,
            password=password,
            profile_name=profile,
            session_token=session_token,
        )

        output.print_message("")
        output.success(
            f"Credentials configured successfully",
            f"Profile: {profile}",
        )

        # Show credential file location
        cred_path = manager.credentials_path
        output.info(f"Credentials stored at: {cred_path}")

        # Security reminder
        output.print_message("")
        output.print_panel(
            "Security Reminder",
            "• Keep your encryption password safe - it cannot be recovered\n"
            "• Never commit credentials.enc to version control\n"
            "• Use different passwords for different environments",
            style="yellow",
            border_style="yellow",
        )

    except ComplioError as e:
        output.error(
            "Configuration failed",
            f"{e.message}",
        )
    except KeyboardInterrupt:
        output.print_message("\n")
        output.warning("Configuration cancelled by user")
        sys.exit(130)
    except Exception as e:
        output.error(
            "Unexpected error during configuration",
            f"{type(e).__name__}: {str(e)}",
        )


# ============================================================================
# LIST PROFILES COMMAND
# ============================================================================


@cli.command(name="list-profiles")
def list_profiles() -> None:
    """
    List all stored credential profiles.

    Shows all credential profiles that have been configured and stored
    in the encrypted credentials file.

    \b
    Examples:
      complio list-profiles

    \b
    Output shows:
      • Profile names
      • Storage location
      • Total count
    """
    from complio.utils.crypto import CredentialManager
    from complio.utils.exceptions import ComplioError

    try:
        manager = CredentialManager()
        profiles = manager.list_profiles()

        if not profiles:
            output.info(
                "No credential profiles configured",
                "Run 'complio configure' to set up credentials",
            )
            return

        output.print_header("Stored Credential Profiles")

        # Create table data
        rows = [[profile] for profile in sorted(profiles)]
        output.print_table(
            title=f"Profiles ({len(profiles)} total)",
            headers=["Profile Name"],
            rows=rows,
            caption=f"Credentials stored at: {manager.credentials_path}",
        )

        output.print_message("")
        output.info(
            "To use a profile, specify it with --profile flag",
            "Example: complio scan --profile production",
        )

    except ComplioError as e:
        output.error(
            "Failed to list profiles",
            f"{e.message}",
        )
    except Exception as e:
        output.error(
            "Unexpected error while listing profiles",
            f"{type(e).__name__}: {str(e)}",
        )


# ============================================================================
# REMOVE PROFILE COMMAND
# ============================================================================


@cli.command(name="remove-profile")
@click.argument("profile_name")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Skip confirmation prompt",
)
def remove_profile(profile_name: str, force: bool) -> None:
    """
    Remove a credential profile.

    Permanently deletes the specified credential profile from encrypted storage.
    This action cannot be undone.

    \b
    Arguments:
      PROFILE_NAME    Name of the profile to remove

    \b
    Examples:
      # Remove profile with confirmation
      complio remove-profile staging

      # Remove profile without confirmation
      complio remove-profile staging --force

    \b
    Warning: This permanently deletes the credentials. They cannot be recovered.
    """
    from complio.utils.crypto import CredentialManager
    from complio.utils.exceptions import ComplioError, CredentialNotFoundError

    try:
        manager = CredentialManager()

        # Check if profile exists
        existing_profiles = manager.list_profiles()
        if profile_name not in existing_profiles:
            output.error(
                f"Profile '{profile_name}' not found",
                f"Available profiles: {', '.join(existing_profiles) if existing_profiles else 'none'}",
            )

        # Confirmation (unless --force)
        if not force:
            output.warning(
                f"This will permanently delete profile '{profile_name}'",
                "This action cannot be undone",
            )
            if not output.confirm("Are you sure?", default=False):
                output.info("Profile removal cancelled")
                sys.exit(0)

        # Delete profile
        manager.delete_profile(profile_name)

        output.success(
            f"Profile '{profile_name}' removed successfully",
        )

        # Show remaining profiles
        remaining = manager.list_profiles()
        if remaining:
            output.info(
                f"Remaining profiles: {', '.join(remaining)}",
            )
        else:
            output.info("No profiles remaining")

    except CredentialNotFoundError as e:
        output.error(
            f"Profile '{profile_name}' not found",
            f"{e.message}",
        )
    except ComplioError as e:
        output.error(
            f"Failed to remove profile '{profile_name}'",
            f"{e.message}",
        )
    except Exception as e:
        output.error(
            "Unexpected error while removing profile",
            f"{type(e).__name__}: {str(e)}",
        )


# ============================================================================
# SCAN COMMAND
# ============================================================================

# Import and register scan command
from complio.cli.commands.scan import scan

cli.add_command(scan)


# ============================================================================
# LICENSE COMMANDS
# ============================================================================

# Import and register license commands
from complio.cli.commands.activate import activate
from complio.cli.commands.license_info import license_info
from complio.cli.commands.deactivate import deactivate

cli.add_command(activate)
cli.add_command(license_info)
cli.add_command(deactivate)


# ============================================================================
# HISTORY COMMANDS
# ============================================================================

# Import and register history commands
from complio.cli.commands.history import history, compare, clear_history_cmd

cli.add_command(history)
cli.add_command(compare)
cli.add_command(clear_history_cmd)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main() -> None:
    """Main entry point for CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        output.print_message("\n")
        output.warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        output.error(
            "Unexpected error",
            f"{type(e).__name__}: {str(e)}",
        )


if __name__ == "__main__":
    main()

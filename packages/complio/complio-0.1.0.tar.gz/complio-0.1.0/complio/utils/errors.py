"""
User-friendly error message translation for Complio.

This module translates technical AWS and system errors into actionable,
user-friendly messages with clear next steps.

Example:
    >>> from complio.utils.errors import handle_aws_error
    >>> try:
    >>>     connector.connect()
    >>> except Exception as e:
    >>>     handle_aws_error(e)
"""

import configparser
import os
import sys
from typing import NoReturn

import click
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    PartialCredentialsError,
    ProfileNotFound,
)


def handle_aws_error(error: Exception) -> NoReturn:
    """Translate technical AWS errors to user-friendly messages.

    This function catches common AWS errors and displays helpful messages
    with actionable next steps instead of technical stack traces.

    Args:
        error: The exception that was raised

    Raises:
        SystemExit: Always exits with code 1 after displaying the error

    Example:
        >>> try:
        >>>     session = boto3.Session(profile_name="nonexistent")
        >>> except Exception as e:
        >>>     handle_aws_error(e)
        >>> # Displays: "❌ AWS profile 'nonexistent' not found"
        >>> # Then lists available profiles
    """

    if isinstance(error, NoCredentialsError):
        click.echo("❌ AWS credentials not found", err=True)
        click.echo("\nTo configure AWS credentials:", err=True)
        click.echo("  1. Run: aws configure", err=True)
        click.echo("  2. Enter your Access Key ID and Secret Access Key", err=True)
        click.echo("\nFor help: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html", err=True)
        sys.exit(1)

    elif isinstance(error, PartialCredentialsError):
        click.echo("❌ Incomplete AWS credentials", err=True)
        click.echo("\nYour AWS credentials are missing required information.", err=True)
        click.echo("Run: aws configure", err=True)
        sys.exit(1)

    elif isinstance(error, ProfileNotFound):
        # Extract profile name from error message
        profile = str(error).split("'")[1] if "'" in str(error) else "unknown"
        click.echo(f"❌ AWS profile '{profile}' not found", err=True)
        click.echo(f"\nAvailable profiles in ~/.aws/credentials:", err=True)
        try:
            config = configparser.ConfigParser()
            config.read(os.path.expanduser('~/.aws/credentials'))
            if config.sections():
                for prof in config.sections():
                    click.echo(f"  • {prof}", err=True)
            else:
                click.echo("  (No profiles configured)", err=True)
                click.echo("\nRun 'aws configure' to create a profile", err=True)
        except Exception:
            click.echo("  (Unable to read credentials file)", err=True)
        sys.exit(1)

    elif isinstance(error, EndpointConnectionError):
        click.echo("❌ Cannot connect to AWS", err=True)
        click.echo("\nPossible causes:", err=True)
        click.echo("  • No internet connection", err=True)
        click.echo("  • Invalid region specified", err=True)
        click.echo("  • Corporate firewall blocking AWS", err=True)
        sys.exit(1)

    elif isinstance(error, ClientError):
        error_code = error.response.get('Error', {}).get('Code', 'Unknown')
        error_message = error.response.get('Error', {}).get('Message', '')

        if error_code == 'UnauthorizedOperation':
            click.echo("❌ Insufficient AWS permissions", err=True)
            click.echo("\nYour AWS user needs the 'SecurityAudit' policy.", err=True)
            click.echo("Contact your AWS administrator to grant permissions.", err=True)

        elif error_code == 'InvalidClientTokenId':
            click.echo("❌ Invalid AWS credentials", err=True)
            click.echo("\nYour Access Key ID is not recognized by AWS.", err=True)
            click.echo("Run 'aws configure' to update your credentials.", err=True)

        elif error_code == 'SignatureDoesNotMatch':
            click.echo("❌ Invalid AWS credentials", err=True)
            click.echo("\nYour Secret Access Key is incorrect.", err=True)
            click.echo("Run 'aws configure' to update your credentials.", err=True)

        elif error_code == 'AccessDenied':
            click.echo("❌ Access denied", err=True)
            click.echo(f"\n{error_message}", err=True)
            click.echo("\nYour AWS user needs additional permissions.", err=True)
            click.echo("Contact your AWS administrator.", err=True)

        elif error_code == 'InvalidRegion':
            click.echo("❌ Invalid AWS region", err=True)
            click.echo("\nValid regions: us-east-1, eu-west-1, eu-west-3, etc.", err=True)

        else:
            click.echo(f"❌ AWS Error: {error_code}", err=True)
            if error_message:
                click.echo(f"\n{error_message}", err=True)
            click.echo(f"\nFor help: https://docs.complio.tech/errors", err=True)

        sys.exit(1)

    else:
        # Unknown error - show technical message but add help
        click.echo(f"❌ Unexpected error: {str(error)}", err=True)
        click.echo(f"\nFor help: https://docs.complio.tech/troubleshooting", err=True)
        click.echo(f"Support: support@complio.tech", err=True)
        sys.exit(1)


def validate_region_format(region: str) -> bool:
    """Validate AWS region format.

    Args:
        region: Region string to validate

    Returns:
        True if valid format, False otherwise

    Example:
        >>> validate_region_format("us-east-1")
        True
        >>> validate_region_format("invalid")
        False
    """
    import re
    # AWS region format: 2 letters, dash, direction/location, dash, number
    # Examples: us-east-1, eu-west-3, ap-southeast-2
    pattern = r'^[a-z]{2}-[a-z]+-\d+$'
    return bool(re.match(pattern, region))


def validate_profile_exists(profile: str) -> bool:
    """Check if AWS profile exists in credentials file.

    Args:
        profile: Profile name to check

    Returns:
        True if profile exists, False otherwise

    Example:
        >>> validate_profile_exists("default")
        True
    """
    if profile == "default":
        return True  # Default profile is implicit

    try:
        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~/.aws/credentials'))
        return profile in config.sections()
    except Exception:
        return True  # If can't read file, let boto3 handle it

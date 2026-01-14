"""
Configuration management for Complio.

This module provides centralized configuration using Pydantic Settings.
Supports environment variables, defaults, and validation.

Configuration Sources (priority order):
1. Environment variables (COMPLIO_*)
2. Configuration file (~/.complio/config.yaml)
3. Default values

Example:
    >>> from complio.config.settings import get_settings
    >>> settings = get_settings()
    >>> print(settings.default_region)
    'us-east-1'
"""

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ============================================================================
# CONSTANTS
# ============================================================================

# Application version
VERSION = "0.1.0"

# Default configuration directory
DEFAULT_CONFIG_DIR = Path.home() / ".complio"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
DEFAULT_CREDENTIALS_FILE = DEFAULT_CONFIG_DIR / "credentials.enc"
DEFAULT_LOG_DIR = DEFAULT_CONFIG_DIR / "logs"
DEFAULT_REPORT_DIR = DEFAULT_CONFIG_DIR / "reports"

# Valid AWS regions (as of 2024)
VALID_AWS_REGIONS: List[str] = [
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "af-south-1",
    "ap-east-1",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-southeast-3",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ca-central-1",
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-south-1",
    "eu-north-1",
    "me-south-1",
    "sa-east-1",
]

# Valid output formats
VALID_OUTPUT_FORMATS: List[str] = ["json", "markdown", "pdf", "html"]

# Valid log levels
VALID_LOG_LEVELS: List[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


# ============================================================================
# SETTINGS MODEL
# ============================================================================


class ComplioSettings(BaseSettings):
    """Application settings with validation and defaults.

    Settings can be configured via:
    - Environment variables (COMPLIO_DEFAULT_REGION, etc.)
    - Configuration file (~/.complio/config.yaml)
    - Default values (defined here)

    Attributes:
        default_region: Default AWS region for scans
        default_profile: Default credential profile name
        default_output_format: Default report format
        log_level: Logging level
        log_to_file: Enable file logging
        log_dir: Directory for log files
        log_max_bytes: Max log file size before rotation
        log_backup_count: Number of backup log files to keep
        config_dir: Configuration directory path
        credentials_file: Path to encrypted credentials
        report_dir: Directory for generated reports
        aws_timeout: Timeout for AWS API calls (seconds)
        max_concurrent_tests: Maximum concurrent compliance tests
        enable_colors: Enable colored terminal output
        verbose: Enable verbose output

    Example:
        >>> settings = ComplioSettings()
        >>> print(settings.default_region)
        'us-east-1'

        >>> # Override with environment variable
        >>> import os
        >>> os.environ['COMPLIO_DEFAULT_REGION'] = 'eu-west-1'
        >>> settings = ComplioSettings()
        >>> print(settings.default_region)
        'eu-west-1'
    """

    model_config = SettingsConfigDict(
        env_prefix="COMPLIO_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application Version
    VERSION: str = Field(
        default=VERSION,
        description="Application version",
    )

    # AWS Configuration
    default_region: str = Field(
        default="us-east-1",
        description="Default AWS region for compliance scans",
    )
    default_profile: str = Field(
        default="default",
        description="Default credential profile name",
    )
    aws_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Timeout for AWS API calls in seconds",
    )

    # Output Configuration
    default_output_format: str = Field(
        default="json",
        description="Default format for compliance reports",
    )
    enable_colors: bool = Field(
        default=True,
        description="Enable colored terminal output",
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose output",
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_to_file: bool = Field(
        default=True,
        description="Enable logging to file",
    )
    log_dir: Path = Field(
        default=DEFAULT_LOG_DIR,
        description="Directory for log files",
    )
    log_max_bytes: int = Field(
        default=10_000_000,  # 10 MB
        ge=1_000_000,  # Min 1 MB
        le=100_000_000,  # Max 100 MB
        description="Maximum log file size before rotation",
    )
    log_backup_count: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of backup log files to keep",
    )

    # Directory Configuration
    config_dir: Path = Field(
        default=DEFAULT_CONFIG_DIR,
        description="Configuration directory path",
    )
    credentials_file: Path = Field(
        default=DEFAULT_CREDENTIALS_FILE,
        description="Path to encrypted credentials file",
    )
    report_dir: Path = Field(
        default=DEFAULT_REPORT_DIR,
        description="Directory for generated reports",
    )

    # Test Execution Configuration
    max_concurrent_tests: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of concurrent compliance tests",
    )

    # Validation
    @field_validator("default_region")
    @classmethod
    def validate_region(cls, v: str) -> str:
        """Validate AWS region.

        Args:
            v: Region string to validate

        Returns:
            Validated region string

        Raises:
            ValueError: If region is invalid
        """
        if v not in VALID_AWS_REGIONS:
            raise ValueError(
                f"Invalid AWS region: {v}. Must be one of: {', '.join(VALID_AWS_REGIONS)}"
            )
        return v

    @field_validator("default_output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """Validate output format.

        Args:
            v: Format string to validate

        Returns:
            Validated format string (lowercase)

        Raises:
            ValueError: If format is invalid
        """
        v_lower = v.lower()
        if v_lower not in VALID_OUTPUT_FORMATS:
            raise ValueError(
                f"Invalid output format: {v}. Must be one of: {', '.join(VALID_OUTPUT_FORMATS)}"
            )
        return v_lower

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level.

        Args:
            v: Log level string to validate

        Returns:
            Validated log level string (uppercase)

        Raises:
            ValueError: If log level is invalid
        """
        v_upper = v.upper()
        if v_upper not in VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of: {', '.join(VALID_LOG_LEVELS)}"
            )
        return v_upper

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist.

        Creates:
        - Configuration directory
        - Log directory
        - Report directory

        Sets appropriate permissions (700 for directories).

        Example:
            >>> settings = ComplioSettings()
            >>> settings.ensure_directories()
            >>> assert settings.log_dir.exists()
        """
        for directory in [self.config_dir, self.log_dir, self.report_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            # Set directory permissions to 700 (rwx------)
            directory.chmod(0o700)


# ============================================================================
# SINGLETON SETTINGS INSTANCE
# ============================================================================

_settings: Optional[ComplioSettings] = None


def get_settings() -> ComplioSettings:
    """Get application settings singleton.

    Returns cached settings instance if available, otherwise creates new one.
    This ensures consistent settings across the application.

    Returns:
        ComplioSettings instance

    Example:
        >>> settings = get_settings()
        >>> print(settings.default_region)
        'us-east-1'

        >>> # Subsequent calls return same instance
        >>> settings2 = get_settings()
        >>> assert settings is settings2
    """
    global _settings
    if _settings is None:
        _settings = ComplioSettings()
        # Ensure required directories exist
        _settings.ensure_directories()
    return _settings


def reset_settings() -> None:
    """Reset settings singleton.

    Useful for testing to force re-initialization of settings.

    Example:
        >>> reset_settings()
        >>> settings = get_settings()  # Creates new instance
    """
    global _settings
    _settings = None

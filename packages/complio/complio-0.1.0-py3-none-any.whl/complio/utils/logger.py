"""
Structured logging with credential filtering.

This module provides secure, structured logging for Complio with automatic
credential redaction. All sensitive data is filtered before being written to logs.

Security Features:
    - Automatic credential redaction (AWS keys, secrets, passwords)
    - Structured JSON logging for machine parsing
    - Log rotation to prevent disk fill
    - Separate console and file logging
    - Configurable log levels
    - Context binding for request tracking

Example:
    >>> from complio.utils.logger import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("test_started", test_name="s3_encryption", region="us-east-1")
    >>> # Credentials automatically redacted:
    >>> logger.info("aws_response", access_key="AKIAIOSFODNN7EXAMPLE")
    >>> # Logged as: access_key="[REDACTED_AWS_ACCESS_KEY]"
"""

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.processors import JSONRenderer
from structlog.stdlib import add_log_level, filter_by_level

from complio.config.settings import get_settings

# ============================================================================
# CREDENTIAL PATTERNS (for redaction)
# ============================================================================

# AWS Access Key patterns
AWS_ACCESS_KEY_PATTERN = re.compile(r"(AKIA[0-9A-Z]{16})", re.IGNORECASE)
AWS_SECRET_KEY_PATTERN = re.compile(r"([A-Za-z0-9/+=]{40})", re.IGNORECASE)
AWS_SESSION_TOKEN_PATTERN = re.compile(r"(FwoGZXIvYXdzE[A-Za-z0-9/+=]{100,})", re.IGNORECASE)

# Generic password patterns
PASSWORD_PATTERN = re.compile(
    r'(password["\s:=]+)([^"\s,}]+)',
    re.IGNORECASE
)

# API keys and tokens
API_KEY_PATTERN = re.compile(
    r'(["\s](api[_-]?key|token|secret)["\s:=]+)([^"\s,}]+)',
    re.IGNORECASE
)

# Private IP addresses (optional - may want to keep these)
PRIVATE_IP_PATTERN = re.compile(
    r'\b(?:10|172\.(?:1[6-9]|2[0-9]|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b'
)

# Email addresses (optional - may want to keep these)
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


# ============================================================================
# CREDENTIAL FILTERING PROCESSOR
# ============================================================================


def filter_credentials(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Filter sensitive credentials from log events.

    This processor scans all log event data and redacts any credentials,
    passwords, API keys, or other sensitive information.

    Redaction Rules:
        - AWS Access Keys (AKIA...) → [REDACTED_AWS_ACCESS_KEY]
        - AWS Secret Keys (40 chars) → [REDACTED_AWS_SECRET_KEY]
        - AWS Session Tokens → [REDACTED_AWS_SESSION_TOKEN]
        - AWS Account IDs (12 digits) → ****1234 (last 4 digits only)
        - User IDs → ****W53X (last 4 chars only)
        - Passwords → [REDACTED_PASSWORD]
        - API Keys/Tokens → [REDACTED_API_KEY]

    Args:
        logger: Logger instance
        method_name: Log method name (info, error, etc.)
        event_dict: Log event dictionary

    Returns:
        Event dictionary with credentials redacted

    Example:
        >>> event = {"msg": "Connected", "access_key": "AKIAIOSFODNN7EXAMPLE"}
        >>> filtered = filter_credentials(None, "info", event)
        >>> print(filtered["access_key"])
        '[REDACTED_AWS_ACCESS_KEY]'
    """
    # Process all values in the event dict
    for key, value in event_dict.items():
        if isinstance(value, str):
            # Redact AWS Access Keys
            value = AWS_ACCESS_KEY_PATTERN.sub("[REDACTED_AWS_ACCESS_KEY]", value)

            # Redact AWS Secret Keys (be careful with this - 40 chars is common)
            # Only redact if key name suggests it's a secret
            if any(secret_key in key.lower() for secret_key in ["secret", "password", "token"]):
                if len(value) >= 40:
                    value = "[REDACTED_AWS_SECRET_KEY]"

            # Redact AWS Session Tokens
            value = AWS_SESSION_TOKEN_PATTERN.sub("[REDACTED_AWS_SESSION_TOKEN]", value)

            # Mask AWS Account IDs (show last 4 digits only)
            if any(acct_key in key.lower() for acct_key in ["account_id", "account"]):
                if value.isdigit() and len(value) == 12:
                    value = f"****{value[-4:]}"

            # Mask User IDs (show last 4 chars only)
            if any(user_key in key.lower() for user_key in ["user_id", "userid"]):
                if len(value) > 4:
                    value = f"****{value[-4:]}"

            # Redact passwords
            value = PASSWORD_PATTERN.sub(r'\1[REDACTED_PASSWORD]', value)

            # Redact API keys
            value = API_KEY_PATTERN.sub(r'\1[REDACTED_API_KEY]', value)

            # Update the value
            event_dict[key] = value

        elif isinstance(value, dict):
            # Recursively filter nested dicts
            event_dict[key] = _filter_dict(value)

        elif isinstance(value, list):
            # Filter lists
            event_dict[key] = [_filter_value(item) for item in value]

    return event_dict


def _filter_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively filter credentials from dictionary.

    Args:
        data: Dictionary to filter

    Returns:
        Filtered dictionary
    """
    filtered = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Check for sensitive keys
            if any(sensitive in key.lower() for sensitive in [
                "password", "secret", "token", "key", "credential"
            ]):
                filtered[key] = "[REDACTED]"
            else:
                # Still scan for patterns
                filtered[key] = AWS_ACCESS_KEY_PATTERN.sub("[REDACTED_AWS_ACCESS_KEY]", value)
                filtered[key] = AWS_SESSION_TOKEN_PATTERN.sub("[REDACTED_AWS_SESSION_TOKEN]", filtered[key])
        elif isinstance(value, dict):
            filtered[key] = _filter_dict(value)
        elif isinstance(value, list):
            filtered[key] = [_filter_value(item) for item in value]
        else:
            filtered[key] = value
    return filtered


def _filter_value(value: Any) -> Any:
    """Filter a single value.

    Args:
        value: Value to filter

    Returns:
        Filtered value
    """
    if isinstance(value, str):
        value = AWS_ACCESS_KEY_PATTERN.sub("[REDACTED_AWS_ACCESS_KEY]", value)
        value = AWS_SESSION_TOKEN_PATTERN.sub("[REDACTED_AWS_SESSION_TOKEN]", value)
        return value
    elif isinstance(value, dict):
        return _filter_dict(value)
    elif isinstance(value, list):
        return [_filter_value(item) for item in value]
    else:
        return value


# ============================================================================
# LOGGER SETUP
# ============================================================================


def setup_logging() -> None:
    """Configure structured logging for the application.

    Sets up:
    - Console handler with colored output (if enabled)
    - File handler with rotation (if enabled)
    - Credential filtering processor
    - JSON formatting for file logs
    - Structured event dict format

    Called automatically when getting a logger.

    Example:
        >>> setup_logging()
        >>> logger = logging.getLogger("complio")
        >>> logger.info("Application started")
    """
    settings = get_settings()

    # Get log level
    log_level = getattr(logging, settings.log_level)

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
    )

    # Silence noisy libraries
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Build processor chain
    shared_processors = [
        structlog.stdlib.add_logger_name,
        add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        filter_credentials,  # CRITICAL: Filter credentials before any output
    ]

    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            filter_by_level,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set up file logging if enabled
    if settings.log_to_file:
        # Ensure log directory exists
        settings.log_dir.mkdir(parents=True, exist_ok=True)
        settings.log_dir.chmod(0o700)

        log_file = settings.log_dir / "complio.log"

        # Create rotating file handler
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        # Use JSON formatter for file logs
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=JSONRenderer(),
                foreign_pre_chain=shared_processors,
            )
        )

        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)

        # Set file permissions to 600
        log_file.chmod(0o600)


# Track if logging has been set up
_logging_configured = False


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Structured logger with credential filtering

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_login", user_id=123, ip="10.0.0.1")
        >>> logger.error("auth_failed", error="Invalid password")
    """
    global _logging_configured
    if not _logging_configured:
        setup_logging()
        _logging_configured = True

    return structlog.get_logger(name)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def log_function_call(logger: structlog.stdlib.BoundLogger, function_name: str, **kwargs: Any) -> None:
    """Log a function call with parameters.

    Automatically filters sensitive parameters.

    Args:
        logger: Logger instance
        function_name: Name of function being called
        **kwargs: Function parameters

    Example:
        >>> logger = get_logger(__name__)
        >>> log_function_call(logger, "connect_to_aws", region="us-east-1", profile="prod")
    """
    logger.debug(
        "function_call",
        function=function_name,
        **kwargs
    )


def log_aws_api_call(
    logger: structlog.stdlib.BoundLogger,
    service: str,
    operation: str,
    region: str,
    **kwargs: Any
) -> None:
    """Log an AWS API call.

    Args:
        logger: Logger instance
        service: AWS service name (e.g., 's3', 'ec2')
        operation: API operation (e.g., 'list_buckets')
        region: AWS region
        **kwargs: Additional context

    Example:
        >>> logger = get_logger(__name__)
        >>> log_aws_api_call(logger, "s3", "list_buckets", "us-east-1")
    """
    logger.debug(
        "aws_api_call",
        service=service,
        operation=operation,
        region=region,
        **kwargs
    )


def log_test_result(
    logger: structlog.stdlib.BoundLogger,
    test_name: str,
    passed: bool,
    **kwargs: Any
) -> None:
    """Log a compliance test result.

    Args:
        logger: Logger instance
        test_name: Name of compliance test
        passed: Whether test passed
        **kwargs: Additional context (findings, resources, etc.)

    Example:
        >>> logger = get_logger(__name__)
        >>> log_test_result(logger, "s3_encryption", True, bucket_count=5)
    """
    log_level = "info" if passed else "warning"
    getattr(logger, log_level)(
        "compliance_test_result",
        test_name=test_name,
        passed=passed,
        **kwargs
    )

"""
Custom exceptions for Complio.

This module defines all custom exceptions used throughout the application.
All exceptions inherit from ComplioError for easy catching of all application errors.
"""

from typing import Optional


class ComplioError(Exception):
    """Base exception for all Complio errors.

    All custom exceptions should inherit from this class to allow
    catching all application-specific errors.
    """

    def __init__(self, message: str, details: Optional[dict[str, str]] = None) -> None:
        """Initialize ComplioError.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CryptoError(ComplioError):
    """Base exception for cryptography-related errors."""
    pass


class EncryptionError(CryptoError):
    """Raised when encryption operations fail.

    Examples:
        - Encryption algorithm failure
        - Invalid encryption key
        - Corrupted data during encryption
    """
    pass


class DecryptionError(CryptoError):
    """Raised when decryption operations fail.

    Examples:
        - Invalid decryption key (wrong password)
        - Corrupted encrypted data
        - Tampered encrypted file
        - Invalid token format
    """
    pass


class CredentialError(ComplioError):
    """Base exception for credential-related errors."""
    pass


class InvalidCredentialsError(CredentialError):
    """Raised when AWS credentials are invalid or malformed.

    Examples:
        - Empty access key or secret key
        - Invalid access key format (not AKIA...)
        - Credentials that don't match AWS format requirements
    """
    pass


class CredentialStorageError(CredentialError):
    """Raised when credential storage operations fail.

    Examples:
        - Unable to create credentials directory
        - Insufficient permissions to write credentials file
        - Disk full when saving credentials
    """
    pass


class CredentialNotFoundError(CredentialError):
    """Raised when attempting to load non-existent credentials.

    Examples:
        - Credentials file doesn't exist
        - Profile name not found in credentials file
    """
    pass


class InvalidPasswordError(CredentialError):
    """Raised when password validation fails.

    Examples:
        - Password too short (< 8 characters)
        - Password doesn't meet complexity requirements
        - Wrong password during decryption
    """
    pass


class ValidationError(ComplioError):
    """Raised when input validation fails.

    Examples:
        - Invalid AWS region
        - Malformed account ID
        - Invalid file path
    """
    pass


class AWSError(ComplioError):
    """Base exception for AWS-related errors."""
    pass


class AWSCredentialsError(AWSError):
    """Raised when AWS API rejects credentials.

    Examples:
        - Invalid access key or secret key
        - Expired temporary credentials
        - Insufficient IAM permissions
    """
    pass


class AWSConnectionError(AWSError):
    """Raised when unable to connect to AWS API.

    Examples:
        - Network timeout
        - DNS resolution failure
        - AWS service unavailable
    """
    pass


class InvalidRegionError(AWSError):
    """Raised when AWS region is invalid.

    Examples:
        - Non-existent region name
        - Region not enabled for account
    """
    pass

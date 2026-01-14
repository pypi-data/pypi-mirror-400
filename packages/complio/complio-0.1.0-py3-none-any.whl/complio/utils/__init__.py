"""Utility modules for Complio."""

from complio.utils.crypto import CredentialManager
from complio.utils.exceptions import (
    AWSConnectionError,
    AWSCredentialsError,
    AWSError,
    ComplioError,
    CredentialError,
    CredentialNotFoundError,
    CredentialStorageError,
    CryptoError,
    DecryptionError,
    EncryptionError,
    InvalidCredentialsError,
    InvalidPasswordError,
    InvalidRegionError,
    ValidationError,
)
from complio.utils.logger import get_logger, setup_logging

__all__ = [
    # Crypto
    "CredentialManager",
    # Logging
    "get_logger",
    "setup_logging",
    # Exceptions - Base
    "ComplioError",
    "CryptoError",
    "CredentialError",
    "AWSError",
    # Exceptions - Crypto
    "EncryptionError",
    "DecryptionError",
    # Exceptions - Credentials
    "InvalidCredentialsError",
    "InvalidPasswordError",
    "CredentialStorageError",
    "CredentialNotFoundError",
    # Exceptions - AWS
    "AWSConnectionError",
    "AWSCredentialsError",
    "InvalidRegionError",
    # Exceptions - Validation
    "ValidationError",
]

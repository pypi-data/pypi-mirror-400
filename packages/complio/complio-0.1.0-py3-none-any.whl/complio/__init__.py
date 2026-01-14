"""
Complio - Compliance-as-Code Platform

Automated ISO 27001 infrastructure compliance testing for AWS.

Example:
    >>> from complio import CredentialManager
    >>> manager = CredentialManager()
    >>> manager.encrypt_credentials(
    ...     access_key="AKIAIOSFODNN7EXAMPLE",
    ...     secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    ...     password="StrongPassword123!",
    ...     profile_name="production"
    ... )
"""

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
from complio.config.settings import ComplioSettings, get_settings
from complio.connectors.aws.client import AWSConnector

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Credential Management
    "CredentialManager",
    # Configuration
    "ComplioSettings",
    "get_settings",
    # AWS Connector
    "AWSConnector",
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

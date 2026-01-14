"""
Base connector interface for cloud providers.

This module defines the abstract base class for cloud provider connectors.
All cloud connectors (AWS, Azure, GCP) should inherit from CloudConnector.

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> connector = AWSConnector(profile_name="production")
    >>> connector.connect()
    >>> connector.validate_credentials()
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class CloudConnector(ABC):
    """Abstract base class for cloud provider connectors.

    All cloud provider implementations must inherit from this class
    and implement the required methods.

    Attributes:
        profile_name: Name of the credential profile to use
        region: Cloud provider region
        connected: Whether connector is currently connected

    Example:
        >>> class MyCloudConnector(CloudConnector):
        ...     def connect(self) -> bool:
        ...         # Implementation
        ...         pass
        ...     def disconnect(self) -> None:
        ...         # Implementation
        ...         pass
    """

    def __init__(self, profile_name: str, region: str) -> None:
        """Initialize cloud connector.

        Args:
            profile_name: Credential profile name
            region: Cloud provider region

        Example:
            >>> connector = MyCloudConnector("production", "us-east-1")
        """
        self.profile_name = profile_name
        self.region = region
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to cloud provider.

        Returns:
            True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection fails

        Example:
            >>> connector.connect()
            True
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from cloud provider.

        Closes any open connections and cleans up resources.

        Example:
            >>> connector.disconnect()
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> Dict[str, Any]:
        """Validate credentials with cloud provider.

        Returns:
            Dictionary with validation result:
                {
                    "valid": True/False,
                    "account_id": "123456789012",
                    "user_arn": "arn:aws:iam::...",
                    "error": "..." (if validation failed)
                }

        Raises:
            ValueError: If credentials are invalid

        Example:
            >>> result = connector.validate_credentials()
            >>> print(result["account_id"])
            '123456789012'
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection is working.

        Returns:
            True if connection is healthy, False otherwise

        Example:
            >>> if connector.test_connection():
            ...     print("Connection is healthy")
        """
        pass

    def __enter__(self) -> "CloudConnector":
        """Context manager entry.

        Example:
            >>> with connector:
            ...     # Use connector
            ...     pass
        """
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.disconnect()

"""
AWS connector using boto3.

This module provides AWS connectivity using standard AWS credentials (from
~/.aws/credentials, environment variables, or IAM roles) via boto3 SDK.

Security Features:
    - Uses boto3's standard credential chain
    - Reads from ~/.aws/credentials (same as AWS CLI)
    - Supports environment variables and IAM roles
    - Optional encrypted credential storage (legacy mode)
    - STS validation before use
    - Configurable timeouts
    - Automatic retry with exponential backoff
    - No credential logging

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> # Uses credentials from ~/.aws/credentials (no password needed)
    >>> connector = AWSConnector(profile_name="default", region="us-east-1")
    >>> connector.connect()
    >>> # Validate credentials
    >>> result = connector.validate_credentials()
    >>> print(result["account_id"])
    '123456789012'
    >>> # Get AWS clients
    >>> s3 = connector.get_client("s3")
    >>> ec2 = connector.get_client("ec2")
"""

from typing import Any, Dict, Optional

import boto3
from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

from complio.config.settings import get_settings
from complio.connectors.base import CloudConnector
from complio.utils.crypto import CredentialManager
from complio.utils.exceptions import AWSConnectionError, AWSCredentialsError, CredentialNotFoundError
from complio.utils.logger import get_logger, log_aws_api_call

logger = get_logger(__name__)


class AWSConnector(CloudConnector):
    """AWS cloud connector using boto3.

    Manages AWS connections using standard AWS credentials (from ~/.aws/credentials,
    environment variables, or IAM roles). Optionally supports encrypted credential
    storage for legacy compatibility.

    Attributes:
        profile_name: Credential profile name (from ~/.aws/credentials)
        region: AWS region
        password: Optional password for encrypted credentials (legacy mode)
        session: Boto3 session (created on connect)
        connected: Connection status

    Example:
        >>> # Standard usage (reads from ~/.aws/credentials)
        >>> connector = AWSConnector("default", "us-east-1")
        >>> connector.connect()
        >>> s3_client = connector.get_client("s3")
        >>> buckets = s3_client.list_buckets()
    """

    def __init__(
        self,
        profile_name: str,
        region: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Initialize AWS connector.

        Args:
            profile_name: Name of credential profile (from ~/.aws/credentials)
            region: AWS region (defaults to settings.default_region)
            password: Optional password for encrypted credentials (legacy mode only)

        Example:
            >>> # Uses standard AWS credentials (no password)
            >>> connector = AWSConnector("default", "us-east-1")
        """
        settings = get_settings()
        region = region or settings.default_region

        super().__init__(profile_name=profile_name, region=region)

        self.password = password
        self.session: Optional[Session] = None
        self._clients: Dict[str, Any] = {}
        self._account_id: Optional[str] = None
        self._user_arn: Optional[str] = None

    def connect(self) -> bool:
        """Connect to AWS using standard AWS credentials.

        Uses boto3's default credential chain (reads from ~/.aws/credentials, environment
        variables, EC2 instance metadata, etc). Falls back to encrypted credentials if
        password is explicitly provided.

        Returns:
            True if connection successful

        Raises:
            AWSCredentialsError: If credentials cannot be loaded or are invalid
            AWSConnectionError: If connection fails

        Example:
            >>> connector.connect()
            True
        """
        logger.info("connecting_to_aws", profile=self.profile_name, region=self.region)

        try:
            # If password is provided, use encrypted credentials (legacy mode)
            if self.password:
                logger.debug("using_encrypted_credentials", profile=self.profile_name)
                manager = CredentialManager()

                # Decrypt credentials
                try:
                    credentials = manager.decrypt_credentials(
                        password=self.password,
                        profile_name=self.profile_name
                    )
                except CredentialNotFoundError as e:
                    raise AWSCredentialsError(
                        f"Profile '{self.profile_name}' not found in encrypted storage.",
                        details={"profile": self.profile_name}
                    ) from e

                # Create boto3 session with explicit credentials
                self.session = boto3.Session(
                    aws_access_key_id=credentials["access_key"],
                    aws_secret_access_key=credentials["secret_key"],
                    aws_session_token=credentials.get("session_token"),
                    region_name=self.region
                )
            else:
                # Use standard AWS credential chain (default behavior)
                # This reads from:
                # 1. ~/.aws/credentials (AWS config file)
                # 2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                # 3. IAM role (for EC2 instances)
                # 4. Other boto3 credential providers
                logger.debug("using_standard_aws_credentials", profile=self.profile_name)

                # Create boto3 session using profile from ~/.aws/credentials
                self.session = boto3.Session(
                    profile_name=self.profile_name if self.profile_name != "default" else None,
                    region_name=self.region
                )

            self.connected = True
            logger.info("aws_connection_established", profile=self.profile_name, region=self.region)

            return True

        except AWSCredentialsError:
            raise
        except Exception as e:
            logger.error("aws_connection_failed", error=str(e), profile=self.profile_name)
            raise AWSConnectionError(
                f"Failed to connect to AWS: {str(e)}",
                details={"profile": self.profile_name, "region": self.region}
            ) from e

    def disconnect(self) -> None:
        """Disconnect from AWS.

        Clears session and cached clients.

        Example:
            >>> connector.disconnect()
        """
        self.session = None
        self._clients = {}
        self.connected = False
        logger.info("aws_disconnected", profile=self.profile_name)

    def get_client(self, service_name: str, region: Optional[str] = None) -> Any:
        """Get boto3 client for AWS service.

        Creates and caches boto3 clients with proper configuration.

        Args:
            service_name: AWS service name (e.g., 's3', 'ec2', 'iam')
            region: AWS region (uses connector region if not specified)

        Returns:
            Boto3 client for the specified service

        Raises:
            AWSConnectionError: If not connected

        Example:
            >>> s3 = connector.get_client("s3")
            >>> buckets = s3.list_buckets()
        """
        if not self.connected or not self.session:
            raise AWSConnectionError(
                "Not connected to AWS. Call connect() first.",
                details={"profile": self.profile_name}
            )

        region = region or self.region
        cache_key = f"{service_name}:{region}"

        # Return cached client if available
        if cache_key in self._clients:
            return self._clients[cache_key]

        # Create new client with configuration
        settings = get_settings()

        client_config = Config(
            region_name=region,
            retries={
                "max_attempts": 3,
                "mode": "adaptive"
            },
            connect_timeout=settings.aws_timeout,
            read_timeout=settings.aws_timeout,
        )

        try:
            client = self.session.client(service_name, config=client_config)
            self._clients[cache_key] = client

            logger.debug("aws_client_created", service=service_name, region=region)

            return client

        except Exception as e:
            logger.error("aws_client_creation_failed", service=service_name, error=str(e))
            raise AWSConnectionError(
                f"Failed to create {service_name} client: {str(e)}",
                details={"service": service_name, "region": region}
            ) from e

    def validate_credentials(self) -> Dict[str, Any]:
        """Validate AWS credentials using STS GetCallerIdentity.

        Returns:
            Dictionary with validation result:
                {
                    "valid": True,
                    "account_id": "123456789012",
                    "user_arn": "arn:aws:iam::123456789012:user/admin",
                    "user_id": "AIDAI..."
                }

        Raises:
            AWSCredentialsError: If credentials are invalid
            AWSConnectionError: If not connected

        Example:
            >>> result = connector.validate_credentials()
            >>> print(f"Connected to account: {result['account_id']}")
        """
        if not self.connected:
            raise AWSConnectionError(
                "Not connected to AWS. Call connect() first.",
                details={"profile": self.profile_name}
            )

        logger.info("validating_aws_credentials", profile=self.profile_name)

        try:
            sts = self.get_client("sts")
            log_aws_api_call(logger, "sts", "get_caller_identity", self.region)

            response = sts.get_caller_identity()

            result = {
                "valid": True,
                "account_id": response["Account"],
                "user_arn": response["Arn"],
                "user_id": response["UserId"],
            }

            # Cache for future use
            self._account_id = result["account_id"]
            self._user_arn = result["user_arn"]

            logger.info(
                "aws_credentials_valid",
                account_id=result["account_id"],
                user_id=result["user_id"]
            )

            return result

        except (ClientError, NoCredentialsError, PartialCredentialsError) as e:
            logger.error("aws_credential_validation_failed", error=str(e))
            raise AWSCredentialsError(
                f"AWS credential validation failed: {str(e)}",
                details={"profile": self.profile_name}
            ) from e

    def test_connection(self) -> bool:
        """Test if AWS connection is working.

        Performs a simple STS call to verify connectivity.

        Returns:
            True if connection is healthy, False otherwise

        Example:
            >>> if connector.test_connection():
            ...     print("AWS connection is healthy")
        """
        try:
            self.validate_credentials()
            return True
        except Exception as e:
            logger.warning("aws_connection_test_failed", error=str(e))
            return False

    def get_account_id(self) -> str:
        """Get AWS account ID.

        Returns:
            AWS account ID

        Raises:
            AWSConnectionError: If credentials haven't been validated

        Example:
            >>> account_id = connector.get_account_id()
            >>> print(account_id)
            '123456789012'
        """
        if not self._account_id:
            # Validate to get account ID
            self.validate_credentials()

        if not self._account_id:
            raise AWSConnectionError(
                "Account ID not available. Validate credentials first.",
                details={"profile": self.profile_name}
            )

        return self._account_id

    def list_regions(self, service: str = "ec2") -> list[str]:
        """List available AWS regions for a service.

        Args:
            service: AWS service name (default: ec2)

        Returns:
            List of region names

        Example:
            >>> regions = connector.list_regions()
            >>> print(regions)
            ['us-east-1', 'us-west-2', 'eu-west-1', ...]
        """
        try:
            client = self.get_client(service)
            regions = client.describe_regions()["Regions"]
            return [region["RegionName"] for region in regions]
        except Exception as e:
            logger.warning("failed_to_list_regions", error=str(e))
            # Return default list if API call fails
            from complio.config.settings import VALID_AWS_REGIONS
            return VALID_AWS_REGIONS

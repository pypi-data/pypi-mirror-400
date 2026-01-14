"""
Test registry for managing compliance tests.

This module provides a registry of all available compliance tests,
allowing for easy discovery and execution.

Example:
    >>> from complio.core.registry import TestRegistry
    >>> registry = TestRegistry()
    >>> tests = registry.get_all_tests()
    >>> print(f"Available tests: {len(tests)}")
"""

from typing import Dict, List, Type

from complio.tests_library.base import ComplianceTest
from complio.tests_library.infrastructure.s3_encryption import S3EncryptionTest
from complio.tests_library.infrastructure.ec2_security_groups import EC2SecurityGroupTest
from complio.tests_library.infrastructure.iam_password_policy import IAMPasswordPolicyTest
from complio.tests_library.infrastructure.cloudtrail_logging import CloudTrailLoggingTest
from complio.tests_library.infrastructure.ebs_encryption import EBSEncryptionTest
from complio.tests_library.infrastructure.rds_encryption import RDSEncryptionTest
from complio.tests_library.infrastructure.secrets_manager_encryption import SecretsManagerEncryptionTest
from complio.tests_library.infrastructure.s3_public_access import S3PublicAccessBlockTest
from complio.tests_library.infrastructure.cloudtrail_log_validation import CloudTrailLogValidationTest
from complio.tests_library.infrastructure.cloudtrail_encryption import CloudTrailEncryptionTest
from complio.tests_library.infrastructure.vpc_flow_logs import VPCFlowLogsTest
from complio.tests_library.infrastructure.nacl_security import NACLSecurityTest

# Phase 2: Storage Tests
from complio.tests_library.storage.redshift_encryption import RedshiftEncryptionTest
from complio.tests_library.storage.efs_encryption import EFSEncryptionTest
from complio.tests_library.storage.dynamodb_encryption import DynamoDBEncryptionTest
from complio.tests_library.storage.elasticache_encryption import ElastiCacheEncryptionTest

# Phase 2: Security Tests
from complio.tests_library.security.kms_key_rotation import KMSKeyRotationTest

# Phase 2: Identity Tests
from complio.tests_library.identity.access_key_rotation import AccessKeyRotationTest
from complio.tests_library.identity.mfa_enforcement import MFAEnforcementTest
from complio.tests_library.identity.root_account_protection import RootAccountProtectionTest

# Phase 3 Week 1: Easy Tests (6 tests)
from complio.tests_library.storage.s3_versioning import S3VersioningTest
from complio.tests_library.storage.backup_encryption import BackupEncryptionTest
from complio.tests_library.logging.cloudwatch_retention import CloudWatchRetentionTest
from complio.tests_library.logging.sns_encryption import SNSEncryptionTest
from complio.tests_library.logging.cloudwatch_logs_encryption import CloudWatchLogsEncryptionTest
from complio.tests_library.network.vpn_security import VPNSecurityTest

# Phase 3 Week 2: Medium Tests (9 tests - complete)
from complio.tests_library.network.nacl_configuration import NACLConfigurationTest
from complio.tests_library.network.alb_nlb_security import ALBNLBSecurityTest
from complio.tests_library.network.cloudfront_https import CloudFrontHTTPSTest
from complio.tests_library.network.transit_gateway_security import TransitGatewaySecurityTest
from complio.tests_library.network.vpc_endpoints_security import VPCEndpointsSecurityTest
from complio.tests_library.network.network_firewall import NetworkFirewallTest
from complio.tests_library.network.direct_connect_security import DirectConnectSecurityTest
from complio.tests_library.logging.cloudwatch_alarms import CloudWatchAlarmsTest
from complio.tests_library.logging.config_enabled import ConfigEnabledTest

# Phase 3 Week 3: Hard Tests (5 tests - complete!)
from complio.tests_library.network.waf_configuration import WAFConfigurationTest
from complio.tests_library.network.api_gateway_security import APIGatewaySecurityTest
from complio.tests_library.logging.guardduty_enabled import GuardDutyEnabledTest
from complio.tests_library.logging.security_hub_enabled import SecurityHubEnabledTest
from complio.tests_library.logging.eventbridge_rules import EventBridgeRulesTest


class TestRegistry:
    """Registry of all available compliance tests.

    This class maintains a catalog of all compliance tests,
    organized by category and ISO 27001 control.

    Attributes:
        tests: Dictionary of test_id -> test class mappings

    Example:
        >>> registry = TestRegistry()
        >>> test_class = registry.get_test("s3_encryption")
        >>> print(test_class.__name__)
        'S3EncryptionTest'
    """

    def __init__(self) -> None:
        """Initialize the test registry."""
        self._tests: Dict[str, Type[ComplianceTest]] = {}
        self._register_tests()

    def _register_tests(self) -> None:
        """Register all available compliance tests."""
        # Infrastructure Tests
        self._tests["s3_encryption"] = S3EncryptionTest
        self._tests["ec2_security_groups"] = EC2SecurityGroupTest
        self._tests["iam_password_policy"] = IAMPasswordPolicyTest
        self._tests["cloudtrail_logging"] = CloudTrailLoggingTest

        # Phase 1: 8 New Tests
        self._tests["ebs_encryption"] = EBSEncryptionTest
        self._tests["rds_encryption"] = RDSEncryptionTest
        self._tests["secrets_manager_encryption"] = SecretsManagerEncryptionTest
        self._tests["s3_public_access_block"] = S3PublicAccessBlockTest
        self._tests["cloudtrail_log_validation"] = CloudTrailLogValidationTest
        self._tests["cloudtrail_encryption"] = CloudTrailEncryptionTest
        self._tests["vpc_flow_logs"] = VPCFlowLogsTest
        self._tests["nacl_security"] = NACLSecurityTest

        # Phase 2: 8 New Tests (Storage, Security, Identity)
        self._tests["redshift_encryption"] = RedshiftEncryptionTest
        self._tests["efs_encryption"] = EFSEncryptionTest
        self._tests["dynamodb_encryption"] = DynamoDBEncryptionTest
        self._tests["elasticache_encryption"] = ElastiCacheEncryptionTest
        self._tests["kms_key_rotation"] = KMSKeyRotationTest
        self._tests["access_key_rotation"] = AccessKeyRotationTest
        self._tests["mfa_enforcement"] = MFAEnforcementTest
        self._tests["root_account_protection"] = RootAccountProtectionTest

        # Phase 3 Week 1: 6 Easy Tests (Storage, Logging, Network)
        self._tests["s3_versioning"] = S3VersioningTest
        self._tests["backup_encryption"] = BackupEncryptionTest
        self._tests["cloudwatch_retention"] = CloudWatchRetentionTest
        self._tests["sns_encryption"] = SNSEncryptionTest
        self._tests["cloudwatch_logs_encryption"] = CloudWatchLogsEncryptionTest
        self._tests["vpn_security"] = VPNSecurityTest

        # Phase 3 Week 2: 9 Medium Tests (Network + Logging - complete)
        self._tests["nacl_configuration"] = NACLConfigurationTest
        self._tests["alb_nlb_security"] = ALBNLBSecurityTest
        self._tests["cloudfront_https"] = CloudFrontHTTPSTest
        self._tests["transit_gateway_security"] = TransitGatewaySecurityTest
        self._tests["vpc_endpoints_security"] = VPCEndpointsSecurityTest
        self._tests["network_firewall"] = NetworkFirewallTest
        self._tests["direct_connect_security"] = DirectConnectSecurityTest
        self._tests["cloudwatch_alarms"] = CloudWatchAlarmsTest
        self._tests["config_enabled"] = ConfigEnabledTest

        # Phase 3 Week 3: 5 Hard Tests (Network + Logging - complete!)
        self._tests["waf_configuration"] = WAFConfigurationTest
        self._tests["api_gateway_security"] = APIGatewaySecurityTest
        self._tests["guardduty_enabled"] = GuardDutyEnabledTest
        self._tests["security_hub_enabled"] = SecurityHubEnabledTest
        self._tests["eventbridge_rules"] = EventBridgeRulesTest

    def get_test(self, test_id: str) -> Type[ComplianceTest]:
        """Get a test class by ID.

        Args:
            test_id: Test identifier (e.g., "s3_encryption")

        Returns:
            Test class

        Raises:
            KeyError: If test_id not found

        Example:
            >>> registry = TestRegistry()
            >>> test_class = registry.get_test("s3_encryption")
        """
        if test_id not in self._tests:
            raise KeyError(f"Test '{test_id}' not found. Available tests: {list(self._tests.keys())}")
        return self._tests[test_id]

    def get_all_tests(self) -> Dict[str, Type[ComplianceTest]]:
        """Get all registered tests.

        Returns:
            Dictionary of test_id -> test class mappings

        Example:
            >>> registry = TestRegistry()
            >>> tests = registry.get_all_tests()
            >>> print(f"Total tests: {len(tests)}")
        """
        return self._tests.copy()

    def get_test_ids(self) -> List[str]:
        """Get list of all test IDs.

        Returns:
            List of test identifiers

        Example:
            >>> registry = TestRegistry()
            >>> test_ids = registry.get_test_ids()
            >>> print(test_ids)
            ['s3_encryption', 'ec2_security_groups', ...]
        """
        return list(self._tests.keys())

    def get_tests_by_category(self, category: str) -> Dict[str, Type[ComplianceTest]]:
        """Get tests filtered by category.

        Args:
            category: Category name (e.g., "infrastructure", "access_control")

        Returns:
            Dictionary of matching tests

        Example:
            >>> registry = TestRegistry()
            >>> infra_tests = registry.get_tests_by_category("infrastructure")
        """
        # For now, all tests are in infrastructure category
        # This can be extended when we have more categories
        if category == "infrastructure":
            return self._tests.copy()
        return {}

    def test_exists(self, test_id: str) -> bool:
        """Check if a test exists in the registry.

        Args:
            test_id: Test identifier

        Returns:
            True if test exists, False otherwise

        Example:
            >>> registry = TestRegistry()
            >>> registry.test_exists("s3_encryption")
            True
            >>> registry.test_exists("nonexistent_test")
            False
        """
        return test_id in self._tests

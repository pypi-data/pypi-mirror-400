"""
KMS key rotation compliance test.

Checks that all customer-managed KMS keys have automatic rotation enabled.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: Cryptographic keys must be rotated regularly

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.security.kms_key_rotation import KMSKeyRotationTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = KMSKeyRotationTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

from typing import Any, Dict

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Severity,
    TestResult,
    TestStatus,
)


class KMSKeyRotationTest(ComplianceTest):
    """Test for KMS key rotation compliance.

    Verifies that all customer-managed KMS keys have automatic rotation enabled.
    AWS-managed keys are automatically rotated and are skipped.

    Compliance Requirements:
        - Customer-managed keys must have KeyRotationEnabled=True
        - AWS-managed keys are automatically rotated (not checked)
        - Keys without rotation enabled are non-compliant

    Scoring:
        - 100% if all customer-managed keys have rotation enabled
        - Proportional score based on compliant/total ratio
        - 0% if no keys have rotation enabled

    Example:
        >>> test = KMSKeyRotationTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize KMS key rotation test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="kms_key_rotation",
            test_name="KMS Key Rotation Check",
            description="Verify all customer-managed KMS keys have automatic rotation enabled",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute KMS key rotation compliance test.

        Returns:
            TestResult with findings for keys without rotation

        Example:
            >>> test = KMSKeyRotationTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            100.0
        """
        result = TestResult(
            test_id=self.test_id,
            test_name=self.test_name,
            status=TestStatus.PASSED,
            passed=True,
            score=100.0,
        )

        try:
            # Get KMS client
            kms_client = self.connector.get_client("kms")

            # List all keys
            self.logger.info("listing_kms_keys")
            key_ids = []

            # Handle pagination
            paginator = kms_client.get_paginator("list_keys")
            for page in paginator.paginate():
                for key in page.get("Keys", []):
                    key_ids.append(key["KeyId"])

            if not key_ids:
                self.logger.info("no_kms_keys_found")
                result.metadata["message"] = "No KMS keys found in region"
                return result

            self.logger.info("kms_keys_found", count=len(key_ids))

            # Filter customer-managed keys and check rotation
            customer_managed_keys = []
            rotation_enabled_count = 0

            for key_id in key_ids:
                try:
                    # Describe key to get metadata
                    key_metadata_response = kms_client.describe_key(KeyId=key_id)
                    key_metadata = key_metadata_response.get("KeyMetadata", {})

                    # Skip AWS-managed keys (they are automatically rotated)
                    key_manager = key_metadata.get("KeyManager")
                    if key_manager == "AWS":
                        self.logger.debug("skipping_aws_managed_key", key_id=key_id)
                        continue

                    # Skip keys that are not enabled
                    key_state = key_metadata.get("KeyState")
                    if key_state not in ["Enabled", "Disabled"]:
                        # Skip keys in PendingDeletion, PendingImport, etc.
                        self.logger.debug("skipping_key_in_state", key_id=key_id, state=key_state)
                        continue

                    # This is a customer-managed key
                    customer_managed_keys.append(key_id)
                    result.resources_scanned += 1

                    # Get key alias for better reporting
                    key_alias = "no-alias"
                    try:
                        aliases_response = kms_client.list_aliases(KeyId=key_id)
                        aliases = aliases_response.get("Aliases", [])
                        if aliases:
                            key_alias = aliases[0].get("AliasName", "no-alias")
                    except Exception:
                        pass

                    # Check rotation status
                    try:
                        rotation_response = kms_client.get_key_rotation_status(KeyId=key_id)
                        rotation_enabled = rotation_response.get("KeyRotationEnabled", False)
                    except ClientError as e:
                        error_code = e.response.get("Error", {}).get("Code")
                        if error_code == "UnsupportedOperationException":
                            # Asymmetric keys don't support automatic rotation
                            self.logger.debug("key_rotation_not_supported", key_id=key_id)
                            rotation_enabled = False
                        else:
                            raise

                    # Get key details
                    key_arn = key_metadata.get("Arn")
                    creation_date = key_metadata.get("CreationDate")
                    description = key_metadata.get("Description", "")
                    key_usage = key_metadata.get("KeyUsage", "unknown")
                    key_spec = key_metadata.get("KeySpec", "unknown")

                    # Create evidence
                    evidence = self.create_evidence(
                        resource_id=key_id,
                        resource_type="kms_key",
                        data={
                            "key_id": key_id,
                            "key_arn": key_arn,
                            "key_alias": key_alias,
                            "rotation_enabled": rotation_enabled,
                            "key_state": key_state,
                            "key_manager": key_manager,
                            "key_usage": key_usage,
                            "key_spec": key_spec,
                            "description": description,
                            "creation_date": creation_date.isoformat() if creation_date else None,
                        }
                    )
                    result.add_evidence(evidence)

                    if rotation_enabled:
                        rotation_enabled_count += 1
                        self.logger.debug(
                            "kms_key_rotation_enabled",
                            key_id=key_id,
                            key_alias=key_alias
                        )
                    else:
                        # Create finding for key without rotation
                        finding = self.create_finding(
                            resource_id=key_id,
                            resource_type="kms_key",
                            severity=Severity.HIGH,
                            title="KMS key automatic rotation not enabled",
                            description=f"Customer-managed KMS key '{key_alias}' ({key_id}) does not have "
                                        f"automatic rotation enabled. Key is {key_state.lower()} and used for {key_usage}. "
                                        "Without rotation, compromised keys remain valid indefinitely. "
                                        "ISO 27001 A.8.24 requires regular key rotation to minimize risk.",
                            remediation=(
                                f"Enable automatic key rotation for KMS key '{key_id}':\n\n"
                                "Using AWS CLI:\n"
                                f"aws kms enable-key-rotation --key-id {key_id}\n\n"
                                "Or use AWS Console:\n"
                                "1. Go to AWS KMS → Customer managed keys\n"
                                f"2. Select key '{key_alias}' ({key_id})\n"
                                "3. Go to 'Key rotation' tab\n"
                                "4. Enable 'Automatic key rotation'\n"
                                "5. Click 'Save'\n\n"
                                "Note: KMS automatically rotates the key material every year.\n"
                                "Existing ciphertext can still be decrypted with old key material.\n"
                                "Asymmetric keys do not support automatic rotation."
                            ),
                            evidence=evidence
                        )
                        result.add_finding(finding)

                        self.logger.warning(
                            "kms_key_rotation_disabled",
                            key_id=key_id,
                            key_alias=key_alias,
                            key_state=key_state
                        )

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code")
                    if error_code in ["AccessDeniedException", "NotFoundException"]:
                        self.logger.warning("key_access_denied", key_id=key_id, error_code=error_code)
                        continue
                    else:
                        raise

            total_customer_keys = len(customer_managed_keys)

            if total_customer_keys == 0:
                self.logger.info("no_customer_managed_keys_found")
                result.metadata["message"] = "No customer-managed KMS keys found in region"
                return result

            # Calculate compliance score
            result.score = (rotation_enabled_count / total_customer_keys) * 100

            # Determine pass/fail
            result.passed = rotation_enabled_count == total_customer_keys
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_keys_scanned": len(key_ids),
                "customer_managed_keys": total_customer_keys,
                "rotation_enabled": rotation_enabled_count,
                "rotation_disabled": total_customer_keys - rotation_enabled_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "kms_key_rotation_test_completed",
                total_customer_keys=total_customer_keys,
                rotation_enabled=rotation_enabled_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("kms_key_rotation_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("kms_key_rotation_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_kms_key_rotation_test(connector: AWSConnector) -> TestResult:
    """Run KMS key rotation compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_kms_key_rotation_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = KMSKeyRotationTest(connector)
    return test.execute()

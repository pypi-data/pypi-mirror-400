"""
Secrets Manager encryption compliance test.

Checks that all secrets use customer-managed KMS keys for encryption.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: Sensitive data must be encrypted with customer-controlled keys

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.secrets_manager_encryption import SecretsManagerEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = SecretsManagerEncryptionTest(connector)
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


class SecretsManagerEncryptionTest(ComplianceTest):
    """Test for Secrets Manager encryption compliance.

    Verifies that all secrets use customer-managed KMS keys for encryption
    rather than the default AWS-managed key.

    Compliance Requirements:
        - All secrets should use customer-managed KMS keys
        - AWS-managed keys provide less control over rotation and access
        - Secrets without custom KMS keys are flagged as medium severity

    Scoring:
        - 100% if all secrets use customer-managed keys
        - Proportional score based on compliant/total ratio
        - 0% if no secrets use customer-managed keys

    Example:
        >>> test = SecretsManagerEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize Secrets Manager encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="secrets_manager_encryption",
            test_name="Secrets Manager KMS Encryption Check",
            description="Verify all secrets use customer-managed KMS keys for encryption",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute Secrets Manager encryption compliance test.

        Returns:
            TestResult with findings for secrets using AWS-managed keys

        Example:
            >>> test = SecretsManagerEncryptionTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            85.0
        """
        result = TestResult(
            test_id=self.test_id,
            test_name=self.test_name,
            status=TestStatus.PASSED,
            passed=True,
            score=100.0,
        )

        try:
            # Get Secrets Manager client
            sm_client = self.connector.get_client("secretsmanager")

            # List all secrets
            self.logger.info("listing_secrets")
            secrets = []
            paginator = sm_client.get_paginator("list_secrets")

            for page in paginator.paginate():
                secrets.extend(page.get("SecretList", []))

            if not secrets:
                self.logger.info("no_secrets_found")
                result.metadata["message"] = "No secrets found in region"
                return result

            self.logger.info("secrets_found", count=len(secrets))

            # Check each secret for customer-managed KMS key
            compliant_count = 0
            total_count = len(secrets)

            for secret in secrets:
                secret_name = secret["Name"]
                secret_arn = secret["ARN"]
                kms_key_id = secret.get("KmsKeyId")
                result.resources_scanned += 1

                # Check if using customer-managed key
                # If KmsKeyId is not present or is alias/aws/secretsmanager, it's using AWS-managed key
                using_customer_key = (
                    kms_key_id is not None and
                    "alias/aws/secretsmanager" not in str(kms_key_id) and
                    kms_key_id != ""
                )

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=secret_name,
                    resource_type="secrets_manager_secret",
                    data={
                        "secret_name": secret_name,
                        "secret_arn": secret_arn,
                        "kms_key_id": kms_key_id,
                        "using_customer_managed_key": using_customer_key,
                        "last_changed_date": secret.get("LastChangedDate").isoformat() if secret.get("LastChangedDate") else None,
                        "last_accessed_date": secret.get("LastAccessedDate").isoformat() if secret.get("LastAccessedDate") else None,
                    }
                )
                result.add_evidence(evidence)

                if using_customer_key:
                    compliant_count += 1
                    self.logger.debug(
                        "secret_using_customer_key",
                        secret_name=secret_name,
                        kms_key_id=kms_key_id
                    )
                else:
                    # Create finding for secret using AWS-managed key
                    finding = self.create_finding(
                        resource_id=secret_name,
                        resource_type="secrets_manager_secret",
                        severity=Severity.MEDIUM,
                        title="Secret using AWS-managed KMS key",
                        description=f"Secret '{secret_name}' is using the default AWS-managed KMS key instead of a "
                                    "customer-managed key. This reduces control over key rotation, access policies, "
                                    "and audit trails. ISO 27001 A.8.24 recommends customer-controlled encryption keys.",
                        remediation=(
                            "Update the secret to use a customer-managed KMS key:\n"
                            "1. Create a customer-managed KMS key (if not already created):\n"
                            "   aws kms create-key --description 'Secrets Manager encryption key'\n"
                            "2. Update the secret to use the customer-managed key:\n"
                            f"   aws secretsmanager update-secret --secret-id {secret_name} "
                            "--kms-key-id <your-kms-key-id>\n\n"
                            "Note: Ensure your IAM roles/users have permission to use the KMS key.\n"
                            "Add a key policy that allows the Secrets Manager service to use the key."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "secret_using_aws_managed_key",
                        secret_name=secret_name,
                        kms_key_id=kms_key_id
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (compliant_count / total_count) * 100

            # Determine pass/fail
            result.passed = compliant_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_secrets": total_count,
                "secrets_with_customer_keys": compliant_count,
                "secrets_with_aws_managed_keys": total_count - compliant_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "secrets_manager_encryption_test_completed",
                total=total_count,
                compliant=compliant_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("secrets_manager_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("secrets_manager_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_secrets_manager_encryption_test(connector: AWSConnector) -> TestResult:
    """Run Secrets Manager encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_secrets_manager_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = SecretsManagerEncryptionTest(connector)
    return test.execute()

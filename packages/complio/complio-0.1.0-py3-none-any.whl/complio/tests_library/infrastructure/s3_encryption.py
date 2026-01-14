"""
S3 bucket encryption compliance test.

Checks that all S3 buckets have default encryption enabled.

ISO 27001 Control: A.10.1.1 - Cryptographic Controls
Requirement: All data at rest must be encrypted

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.s3_encryption import S3EncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = S3EncryptionTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

from typing import Any, Dict, List

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Severity,
    TestResult,
    TestStatus,
)


class S3EncryptionTest(ComplianceTest):
    """Test for S3 bucket encryption compliance.

    Verifies that all S3 buckets have default encryption enabled.

    Compliance Requirements:
        - All S3 buckets must have default encryption configured
        - Encryption can be SSE-S3, SSE-KMS, or SSE-C
        - Buckets without encryption are non-compliant

    Scoring:
        - 100% if all buckets are encrypted
        - Proportional score based on encrypted/total ratio
        - 0% if no buckets are encrypted

    Example:
        >>> test = S3EncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize S3 encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="s3_encryption",
            test_name="S3 Bucket Encryption Check",
            description="Verify all S3 buckets have default encryption enabled (scans all regions)",
            control_id="A.10.1.1",
            connector=connector,
            scope="global",
        )

    def execute(self) -> TestResult:
        """Execute S3 encryption compliance test.

        Returns:
            TestResult with findings for non-encrypted buckets

        Example:
            >>> test = S3EncryptionTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            85.5
        """
        result = TestResult(
            test_id=self.test_id,
            test_name=self.test_name,
            status=TestStatus.PASSED,
            passed=True,
            score=100.0,
        )

        try:
            # Get S3 client
            s3_client = self.connector.get_client("s3")

            # List all buckets
            self.logger.info("listing_s3_buckets")
            response = s3_client.list_buckets()
            buckets = response.get("Buckets", [])

            if not buckets:
                self.logger.info("no_s3_buckets_found")
                result.metadata["message"] = "No S3 buckets found in account"
                return result

            self.logger.info("s3_buckets_found", count=len(buckets))

            # Check each bucket for encryption
            encrypted_count = 0
            total_count = len(buckets)

            for bucket in buckets:
                bucket_name = bucket["Name"]
                result.resources_scanned += 1

                # Check encryption status
                encryption_status = self._check_bucket_encryption(s3_client, bucket_name)

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=bucket_name,
                    resource_type="s3_bucket",
                    data={
                        "bucket_name": bucket_name,
                        "encryption": encryption_status,
                        "creation_date": bucket["CreationDate"].isoformat(),
                    }
                )
                result.add_evidence(evidence)

                if encryption_status["enabled"]:
                    encrypted_count += 1
                    self.logger.debug(
                        "bucket_encrypted",
                        bucket=bucket_name,
                        algorithm=encryption_status.get("algorithm")
                    )
                else:
                    # Create finding for non-encrypted bucket
                    finding = self.create_finding(
                        resource_id=bucket_name,
                        resource_type="s3_bucket",
                        severity=Severity.HIGH,
                        title="S3 bucket encryption not enabled",
                        description=f"Bucket '{bucket_name}' does not have default encryption enabled. "
                                    "This violates ISO 27001 A.10.1.1 requirement for data-at-rest encryption.",
                        remediation=(
                            "Enable default encryption for the bucket:\n"
                            "1. Go to AWS Console → S3 → Select bucket\n"
                            "2. Go to Properties → Default encryption\n"
                            "3. Enable either SSE-S3 or SSE-KMS encryption\n"
                            "Or use AWS CLI:\n"
                            f"aws s3api put-bucket-encryption --bucket {bucket_name} "
                            "--server-side-encryption-configuration '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"AES256\"}}]}'"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "bucket_not_encrypted",
                        bucket=bucket_name
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (encrypted_count / total_count) * 100

            # Determine pass/fail
            result.passed = encrypted_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_buckets": total_count,
                "encrypted_buckets": encrypted_count,
                "non_encrypted_buckets": total_count - encrypted_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "s3_encryption_test_completed",
                total=total_count,
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except Exception as e:
            self.logger.error("s3_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result

    def _check_bucket_encryption(self, s3_client: Any, bucket_name: str) -> Dict[str, Any]:
        """Check if bucket has encryption enabled.

        Args:
            s3_client: Boto3 S3 client
            bucket_name: Name of the bucket to check

        Returns:
            Dictionary with encryption status:
                {
                    "enabled": True/False,
                    "algorithm": "AES256" | "aws:kms",
                    "kms_key_id": "..." (if SSE-KMS)
                }

        Example:
            >>> status = self._check_bucket_encryption(s3_client, "my-bucket")
            >>> print(status["enabled"])
            True
        """
        try:
            response = s3_client.get_bucket_encryption(Bucket=bucket_name)

            # Extract encryption configuration
            rules = response.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])

            if not rules:
                return {"enabled": False}

            # Get first rule (usually only one)
            rule = rules[0]
            sse_default = rule.get("ApplyServerSideEncryptionByDefault", {})

            encryption_status = {
                "enabled": True,
                "algorithm": sse_default.get("SSEAlgorithm"),
            }

            # Add KMS key ID if using KMS
            if sse_default.get("SSEAlgorithm") == "aws:kms":
                encryption_status["kms_key_id"] = sse_default.get("KMSMasterKeyID")

            return encryption_status

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")

            if error_code == "ServerSideEncryptionConfigurationNotFoundError":
                # No encryption configured
                return {"enabled": False}
            elif error_code == "NoSuchBucket":
                # Bucket doesn't exist (race condition)
                self.logger.warning("bucket_not_found", bucket=bucket_name)
                return {"enabled": False, "error": "Bucket not found"}
            elif error_code == "AccessDenied":
                # No permission to check encryption
                self.logger.warning("encryption_check_access_denied", bucket=bucket_name)
                return {
                    "enabled": False,
                    "error": "Access denied - insufficient permissions"
                }
            else:
                # Other error
                self.logger.error(
                    "encryption_check_error",
                    bucket=bucket_name,
                    error_code=error_code,
                    error=str(e)
                )
                return {"enabled": False, "error": str(e)}

        except Exception as e:
            self.logger.error(
                "encryption_check_unexpected_error",
                bucket=bucket_name,
                error=str(e)
            )
            return {"enabled": False, "error": str(e)}


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_s3_encryption_test(connector: AWSConnector) -> TestResult:
    """Run S3 encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_s3_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = S3EncryptionTest(connector)
    return test.run()

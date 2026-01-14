"""
S3 bucket versioning compliance test.

Checks that all S3 buckets have versioning enabled for data recovery.

ISO 27001 Control: A.8.13 - Information backup
Requirement: S3 buckets must have versioning enabled

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.storage.s3_versioning import S3VersioningTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = S3VersioningTest(connector)
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


class S3VersioningTest(ComplianceTest):
    """Test for S3 bucket versioning compliance.

    Verifies that all S3 buckets have versioning enabled to protect
    against accidental deletion and provide data recovery capabilities.

    Compliance Requirements:
        - All S3 buckets must have versioning enabled (Status='Enabled')
        - MFA Delete is recommended for additional protection (bonus check)
        - Versioning protects against accidental deletion and modification

    Scoring:
        - 100% if all buckets have versioning enabled
        - Proportional score based on compliant/total ratio
        - 0% if no buckets have versioning enabled

    Example:
        >>> test = S3VersioningTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize S3 versioning test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="s3_versioning",
            test_name="S3 Bucket Versioning Check",
            description="Verify all S3 buckets have versioning enabled for data recovery",
            control_id="A.8.13",
            connector=connector,
            scope="global",
        )

    def execute(self) -> TestResult:
        """Execute S3 bucket versioning compliance test.

        Returns:
            TestResult with findings for buckets without versioning

        Example:
            >>> test = S3VersioningTest(connector)
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
            # Get S3 client
            s3_client = self.connector.get_client("s3")

            # List all buckets
            self.logger.info("listing_s3_buckets")
            buckets_response = s3_client.list_buckets()
            buckets = buckets_response.get("Buckets", [])

            if not buckets:
                self.logger.info("no_s3_buckets_found")
                result.metadata["message"] = "No S3 buckets found in account"
                return result

            self.logger.info("s3_buckets_found", count=len(buckets))

            # Check versioning for each bucket
            versioning_enabled_count = 0

            for bucket in buckets:
                bucket_name = bucket["Name"]
                result.resources_scanned += 1

                try:
                    # Get bucket versioning configuration
                    versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)

                    # Check versioning status
                    versioning_status = versioning_response.get("Status", "Disabled")
                    mfa_delete = versioning_response.get("MFADelete", "Disabled")

                    versioning_enabled = versioning_status == "Enabled"

                    # Create evidence
                    evidence = self.create_evidence(
                        resource_id=bucket_name,
                        resource_type="s3_bucket",
                        data={
                            "bucket_name": bucket_name,
                            "versioning_status": versioning_status,
                            "mfa_delete": mfa_delete,
                            "creation_date": bucket.get("CreationDate").isoformat() if bucket.get("CreationDate") else None,
                        }
                    )
                    result.add_evidence(evidence)

                    if versioning_enabled:
                        versioning_enabled_count += 1
                        self.logger.debug(
                            "bucket_versioning_enabled",
                            bucket=bucket_name,
                            mfa_delete=mfa_delete
                        )
                    else:
                        # Create finding for bucket without versioning
                        finding = self.create_finding(
                            resource_id=bucket_name,
                            resource_type="s3_bucket",
                            severity=Severity.MEDIUM,
                            title="S3 bucket versioning not enabled",
                            description=f"S3 bucket '{bucket_name}' does not have versioning enabled "
                                        f"(current status: {versioning_status}). Without versioning, objects "
                                        "can be permanently deleted or overwritten accidentally. Versioning "
                                        "protects against unintended user actions, application failures, and "
                                        "provides the ability to recover previous versions. "
                                        "ISO 27001 A.8.13 requires proper backup and recovery capabilities.",
                            remediation=(
                                f"Enable versioning for S3 bucket '{bucket_name}':\n\n"
                                "Using AWS CLI:\n"
                                f"aws s3api put-bucket-versioning --bucket {bucket_name} \\\n"
                                "  --versioning-configuration Status=Enabled\n\n"
                                "Or use AWS Console:\n"
                                "1. Go to AWS S3 console\n"
                                f"2. Select bucket '{bucket_name}'\n"
                                "3. Go to 'Properties' tab\n"
                                "4. Under 'Bucket Versioning', click 'Edit'\n"
                                "5. Select 'Enable'\n"
                                "6. Click 'Save changes'\n\n"
                                "Optional: Enable MFA Delete for additional protection:\n"
                                f"aws s3api put-bucket-versioning --bucket {bucket_name} \\\n"
                                "  --versioning-configuration Status=Enabled,MFADelete=Enabled \\\n"
                                "  --mfa \"arn:aws:iam::ACCOUNT-ID:mfa/root-account-mfa-device XXXXXX\"\n\n"
                                "Note: MFA Delete requires root account credentials.\n"
                                "Consider lifecycle policies to manage versioned objects and costs."
                            ),
                            evidence=evidence
                        )
                        result.add_finding(finding)

                        self.logger.warning(
                            "bucket_versioning_disabled",
                            bucket=bucket_name,
                            status=versioning_status
                        )

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code")
                    if error_code in ["NoSuchBucket", "AccessDenied"]:
                        self.logger.warning(
                            "bucket_versioning_check_error",
                            bucket=bucket_name,
                            error_code=error_code
                        )
                        continue
                    else:
                        raise

            # Calculate compliance score
            result.score = (versioning_enabled_count / len(buckets)) * 100

            # Determine pass/fail
            result.passed = versioning_enabled_count == len(buckets)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_buckets": len(buckets),
                "versioning_enabled": versioning_enabled_count,
                "versioning_disabled": len(buckets) - versioning_enabled_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "s3_versioning_test_completed",
                total_buckets=len(buckets),
                versioning_enabled=versioning_enabled_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("s3_versioning_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("s3_versioning_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_s3_versioning_test(connector: AWSConnector) -> TestResult:
    """Run S3 bucket versioning compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_s3_versioning_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = S3VersioningTest(connector)
    return test.execute()

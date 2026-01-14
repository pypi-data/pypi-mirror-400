"""
S3 public access block compliance test.

Checks that S3 public access block is enabled at both account and bucket levels.

ISO 27001 Control: A.8.11 - Secure configuration
Requirement: Data must be protected from unauthorized public access

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.s3_public_access import S3PublicAccessBlockTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = S3PublicAccessBlockTest(connector)
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


class S3PublicAccessBlockTest(ComplianceTest):
    """Test for S3 public access block compliance.

    Verifies that S3 public access block is enabled at both account-level
    and individual bucket levels to prevent unintended public data exposure.

    Compliance Requirements:
        - Account-level public access block should be enabled
        - All four settings should be enabled (Block Public ACLs, Ignore Public ACLs,
          Block Public Policy, Restrict Public Buckets)
        - Buckets without all four settings enabled are non-compliant

    Scoring:
        - Account-level check contributes 30% of score
        - Bucket-level checks contribute 70% of score
        - All four settings must be enabled for full compliance

    Example:
        >>> test = S3PublicAccessBlockTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize S3 public access block test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="s3_public_access_block",
            test_name="S3 Public Access Block Check",
            description="Verify S3 public access block is enabled at account and bucket levels",
            control_id="A.8.11",
            connector=connector,
            scope="global",
        )

    def execute(self) -> TestResult:
        """Execute S3 public access block compliance test.

        Returns:
            TestResult with findings for misconfigured public access blocks

        Example:
            >>> test = S3PublicAccessBlockTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            95.0
        """
        result = TestResult(
            test_id=self.test_id,
            test_name=self.test_name,
            status=TestStatus.PASSED,
            passed=True,
            score=100.0,
        )

        try:
            # Get S3 and S3Control clients
            s3_client = self.connector.get_client("s3")
            s3control_client = self.connector.get_client("s3control")

            # Get account ID for S3 Control API
            sts_client = self.connector.get_client("sts")
            account_id = sts_client.get_caller_identity()["Account"]

            # Check account-level public access block
            account_score = 0.0
            try:
                self.logger.info("checking_account_level_public_access_block")
                response = s3control_client.get_public_access_block(
                    AccountId=account_id
                )
                pab_config = response.get("PublicAccessBlockConfiguration", {})

                account_compliant = all([
                    pab_config.get("BlockPublicAcls", False),
                    pab_config.get("IgnorePublicAcls", False),
                    pab_config.get("BlockPublicPolicy", False),
                    pab_config.get("RestrictPublicBuckets", False),
                ])

                if account_compliant:
                    account_score = 30.0
                    self.logger.info("account_level_public_access_block_enabled")
                else:
                    # Create finding for account-level misconfiguration
                    finding = self.create_finding(
                        resource_id=f"account-{account_id}",
                        resource_type="s3_account",
                        severity=Severity.HIGH,
                        title="Account-level S3 public access block not fully enabled",
                        description=f"Account-level S3 public access block settings are not fully enabled. "
                                    f"Current settings: BlockPublicAcls={pab_config.get('BlockPublicAcls', False)}, "
                                    f"IgnorePublicAcls={pab_config.get('IgnorePublicAcls', False)}, "
                                    f"BlockPublicPolicy={pab_config.get('BlockPublicPolicy', False)}, "
                                    f"RestrictPublicBuckets={pab_config.get('RestrictPublicBuckets', False)}. "
                                    "This violates ISO 27001 A.8.11 requirement for secure configuration.",
                        remediation=(
                            "Enable all S3 public access block settings at account level:\n"
                            f"aws s3control put-public-access-block --account-id {account_id} \\\n"
                            "  --public-access-block-configuration \\\n"
                            "  'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to S3 → Block Public Access settings for this account\n"
                            "2. Click Edit\n"
                            "3. Enable all four settings\n"
                            "4. Click Save changes"
                        ),
                        evidence=self.create_evidence(
                            resource_id=f"account-{account_id}",
                            resource_type="s3_account",
                            data={"public_access_block_configuration": pab_config}
                        )
                    )
                    result.add_finding(finding)

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                if error_code == "NoSuchPublicAccessBlockConfiguration":
                    self.logger.warning("account_level_public_access_block_not_configured")
                    # Create finding for missing account-level configuration
                    finding = self.create_finding(
                        resource_id=f"account-{account_id}",
                        resource_type="s3_account",
                        severity=Severity.HIGH,
                        title="Account-level S3 public access block not configured",
                        description="Account-level S3 public access block is not configured. "
                                    "This leaves all buckets vulnerable to accidental public exposure.",
                        remediation=(
                            "Enable S3 public access block at account level:\n"
                            f"aws s3control put-public-access-block --account-id {account_id} \\\n"
                            "  --public-access-block-configuration \\\n"
                            "  'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'"
                        ),
                        evidence=self.create_evidence(
                            resource_id=f"account-{account_id}",
                            resource_type="s3_account",
                            data={"error": "NoSuchPublicAccessBlockConfiguration"}
                        )
                    )
                    result.add_finding(finding)
                else:
                    raise

            # List all buckets
            self.logger.info("listing_s3_buckets")
            buckets_response = s3_client.list_buckets()
            buckets = buckets_response.get("Buckets", [])

            if not buckets:
                # No buckets, only account-level score applies
                result.score = account_score / 0.3 if account_score > 0 else 0.0
                result.metadata["message"] = "No S3 buckets found, only account-level check performed"
                return result

            self.logger.info("s3_buckets_found", count=len(buckets))

            # Check each bucket for public access block
            compliant_buckets = 0
            total_buckets = len(buckets)

            for bucket in buckets:
                bucket_name = bucket["Name"]
                result.resources_scanned += 1

                # Check public access block for bucket
                bucket_compliant = self._check_bucket_public_access_block(s3_client, bucket_name, result)

                if bucket_compliant:
                    compliant_buckets += 1

            # Calculate total score (30% account + 70% buckets)
            bucket_score = (compliant_buckets / total_buckets) * 70.0 if total_buckets > 0 else 0.0
            result.score = account_score + bucket_score

            # Determine pass/fail (requires 100% compliance)
            result.passed = (result.score >= 99.9)  # Allow for floating point imprecision
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "account_level_compliant": account_score > 0,
                "total_buckets": total_buckets,
                "compliant_buckets": compliant_buckets,
                "non_compliant_buckets": total_buckets - compliant_buckets,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "s3_public_access_test_completed",
                total_buckets=total_buckets,
                compliant_buckets=compliant_buckets,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("s3_public_access_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("s3_public_access_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result

    def _check_bucket_public_access_block(self, s3_client: Any, bucket_name: str, result: TestResult) -> bool:
        """Check if bucket has public access block fully enabled.

        Args:
            s3_client: Boto3 S3 client
            bucket_name: Name of the bucket
            result: TestResult object to add findings to

        Returns:
            True if bucket is compliant, False otherwise
        """
        try:
            response = s3_client.get_public_access_block(Bucket=bucket_name)
            pab_config = response.get("PublicAccessBlockConfiguration", {})

            compliant = all([
                pab_config.get("BlockPublicAcls", False),
                pab_config.get("IgnorePublicAcls", False),
                pab_config.get("BlockPublicPolicy", False),
                pab_config.get("RestrictPublicBuckets", False),
            ])

            # Create evidence
            evidence = self.create_evidence(
                resource_id=bucket_name,
                resource_type="s3_bucket",
                data={
                    "bucket_name": bucket_name,
                    "public_access_block_configuration": pab_config,
                    "compliant": compliant,
                }
            )
            result.add_evidence(evidence)

            if compliant:
                self.logger.debug("bucket_public_access_block_enabled", bucket=bucket_name)
                return True
            else:
                # Create finding
                finding = self.create_finding(
                    resource_id=bucket_name,
                    resource_type="s3_bucket",
                    severity=Severity.HIGH,
                    title="S3 bucket public access block not fully enabled",
                    description=f"Bucket '{bucket_name}' does not have all public access block settings enabled. "
                                f"Current settings: BlockPublicAcls={pab_config.get('BlockPublicAcls', False)}, "
                                f"IgnorePublicAcls={pab_config.get('IgnorePublicAcls', False)}, "
                                f"BlockPublicPolicy={pab_config.get('BlockPublicPolicy', False)}, "
                                f"RestrictPublicBuckets={pab_config.get('RestrictPublicBuckets', False)}.",
                    remediation=(
                        f"Enable all public access block settings for bucket '{bucket_name}':\n"
                        f"aws s3api put-public-access-block --bucket {bucket_name} \\\n"
                        "  --public-access-block-configuration \\\n"
                        "  'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'"
                    ),
                    evidence=evidence
                )
                result.add_finding(finding)
                self.logger.warning("bucket_public_access_block_incomplete", bucket=bucket_name)
                return False

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")

            if error_code == "NoSuchPublicAccessBlockConfiguration":
                # No public access block configured for bucket
                finding = self.create_finding(
                    resource_id=bucket_name,
                    resource_type="s3_bucket",
                    severity=Severity.HIGH,
                    title="S3 bucket public access block not configured",
                    description=f"Bucket '{bucket_name}' does not have public access block configured.",
                    remediation=(
                        f"Enable public access block for bucket '{bucket_name}':\n"
                        f"aws s3api put-public-access-block --bucket {bucket_name} \\\n"
                        "  --public-access-block-configuration \\\n"
                        "  'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'"
                    ),
                    evidence=self.create_evidence(
                        resource_id=bucket_name,
                        resource_type="s3_bucket",
                        data={"error": "NoSuchPublicAccessBlockConfiguration"}
                    )
                )
                result.add_finding(finding)
                return False
            else:
                self.logger.error(
                    "bucket_public_access_check_error",
                    bucket=bucket_name,
                    error_code=error_code
                )
                return False


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_s3_public_access_block_test(connector: AWSConnector) -> TestResult:
    """Run S3 public access block compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_s3_public_access_block_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = S3PublicAccessBlockTest(connector)
    return test.execute()

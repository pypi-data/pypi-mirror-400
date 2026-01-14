"""
CloudTrail log encryption compliance test.

Checks that all CloudTrail trails have KMS encryption enabled for log files.

ISO 27001 Control: A.8.15 - Logging & A.8.24 - Use of cryptography
Requirement: Audit logs must be encrypted at rest

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.cloudtrail_encryption import CloudTrailEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = CloudTrailEncryptionTest(connector)
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


class CloudTrailEncryptionTest(ComplianceTest):
    """Test for CloudTrail log encryption compliance.

    Verifies that all CloudTrail trails use KMS encryption for log files
    to protect sensitive audit data at rest.

    Compliance Requirements:
        - All CloudTrail trails should have KmsKeyId configured
        - KMS encryption provides stronger protection than S3 default encryption
        - Trails without KMS encryption are flagged as medium severity

    Scoring:
        - 100% if all trails have KMS encryption
        - Proportional score based on compliant/total ratio
        - 0% if no trails have KMS encryption

    Example:
        >>> test = CloudTrailEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize CloudTrail encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="cloudtrail_encryption",
            test_name="CloudTrail Log Encryption Check",
            description="Verify all CloudTrail trails use KMS encryption for log files",
            control_id="A.8.15",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute CloudTrail encryption compliance test.

        Returns:
            TestResult with findings for trails without KMS encryption

        Example:
            >>> test = CloudTrailEncryptionTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            75.0
        """
        result = TestResult(
            test_id=self.test_id,
            test_name=self.test_name,
            status=TestStatus.PASSED,
            passed=True,
            score=100.0,
        )

        try:
            # Get CloudTrail client
            cloudtrail_client = self.connector.get_client("cloudtrail")

            # List all trails
            self.logger.info("listing_cloudtrail_trails")
            response = cloudtrail_client.describe_trails()
            trails = response.get("trailList", [])

            if not trails:
                self.logger.info("no_cloudtrail_trails_found")
                result.metadata["message"] = "No CloudTrail trails found in region"
                result.score = 0.0
                result.passed = False
                result.status = TestStatus.FAILED

                # Create finding for missing trails
                finding = self.create_finding(
                    resource_id="cloudtrail",
                    resource_type="cloudtrail",
                    severity=Severity.CRITICAL,
                    title="No CloudTrail trails configured",
                    description="No CloudTrail trails are configured in this region. "
                                "CloudTrail is required for audit logging and compliance.",
                    remediation=(
                        "Create a CloudTrail trail with KMS encryption:\n"
                        "1. Create a KMS key for CloudTrail:\n"
                        "   aws kms create-key --description 'CloudTrail encryption key'\n"
                        "2. Create the trail:\n"
                        "   aws cloudtrail create-trail --name my-trail \\\n"
                        "     --s3-bucket-name my-cloudtrail-bucket \\\n"
                        "     --kms-key-id <key-id>\n"
                        "3. Start logging:\n"
                        "   aws cloudtrail start-logging --name my-trail"
                    ),
                    evidence=self.create_evidence(
                        resource_id="cloudtrail",
                        resource_type="cloudtrail",
                        data={"trails_count": 0}
                    )
                )
                result.add_finding(finding)

                return result

            self.logger.info("cloudtrail_trails_found", count=len(trails))

            # Check each trail for KMS encryption
            encrypted_count = 0
            total_count = len(trails)

            for trail in trails:
                trail_name = trail.get("Name")
                trail_arn = trail.get("TrailARN")
                kms_key_id = trail.get("KmsKeyId")
                result.resources_scanned += 1

                # Get additional trail details
                is_multiregion = trail.get("IsMultiRegionTrail", False)
                is_organization = trail.get("IsOrganizationTrail", False)
                s3_bucket = trail.get("S3BucketName", "unknown")
                is_logging = trail.get("IsLogging", False)

                # Check if KMS encryption is enabled
                has_kms_encryption = kms_key_id is not None and kms_key_id != ""

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=trail_name,
                    resource_type="cloudtrail_trail",
                    data={
                        "trail_name": trail_name,
                        "trail_arn": trail_arn,
                        "kms_key_id": kms_key_id,
                        "has_kms_encryption": has_kms_encryption,
                        "is_multiregion_trail": is_multiregion,
                        "is_organization_trail": is_organization,
                        "s3_bucket_name": s3_bucket,
                        "is_logging": is_logging,
                        "home_region": trail.get("HomeRegion"),
                    }
                )
                result.add_evidence(evidence)

                if has_kms_encryption:
                    encrypted_count += 1
                    self.logger.debug(
                        "trail_kms_encrypted",
                        trail_name=trail_name,
                        kms_key_id=kms_key_id
                    )
                else:
                    # Create finding for trail without KMS encryption
                    finding = self.create_finding(
                        resource_id=trail_name,
                        resource_type="cloudtrail_trail",
                        severity=Severity.MEDIUM,
                        title="CloudTrail log encryption with KMS not enabled",
                        description=f"CloudTrail trail '{trail_name}' does not use KMS encryption for log files. "
                                    "While S3 bucket encryption may be enabled, KMS provides stronger key management "
                                    "and audit capabilities. ISO 27001 A.8.15 and A.8.24 recommend encryption with "
                                    "customer-controlled keys.",
                        remediation=(
                            f"Enable KMS encryption for trail '{trail_name}':\n"
                            "1. Create a KMS key (if not already created):\n"
                            "   aws kms create-key --description 'CloudTrail encryption key'\n"
                            "2. Update the trail to use KMS encryption:\n"
                            f"   aws cloudtrail update-trail --name {trail_name} \\\n"
                            "     --kms-key-id <key-arn>\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to CloudTrail → Trails\n"
                            f"2. Select trail '{trail_name}'\n"
                            "3. Click Edit\n"
                            "4. Under 'Log file SSE-KMS encryption', enable encryption\n"
                            "5. Select or create a KMS key\n"
                            "6. Click Save changes\n\n"
                            "Note: Ensure CloudTrail service has permission to use the KMS key."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "trail_not_kms_encrypted",
                        trail_name=trail_name
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (encrypted_count / total_count) * 100

            # Determine pass/fail
            result.passed = encrypted_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_trails": total_count,
                "trails_with_kms_encryption": encrypted_count,
                "trails_without_kms_encryption": total_count - encrypted_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "cloudtrail_encryption_test_completed",
                total=total_count,
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("cloudtrail_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("cloudtrail_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_cloudtrail_encryption_test(connector: AWSConnector) -> TestResult:
    """Run CloudTrail encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_cloudtrail_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = CloudTrailEncryptionTest(connector)
    return test.execute()

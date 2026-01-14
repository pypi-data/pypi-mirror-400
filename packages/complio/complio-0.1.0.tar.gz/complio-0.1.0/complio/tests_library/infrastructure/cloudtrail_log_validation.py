"""
CloudTrail log file validation compliance test.

Checks that all CloudTrail trails have log file validation enabled.

ISO 27001 Control: A.8.15 - Logging
Requirement: Log integrity must be ensured through validation mechanisms

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.cloudtrail_log_validation import CloudTrailLogValidationTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = CloudTrailLogValidationTest(connector)
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


class CloudTrailLogValidationTest(ComplianceTest):
    """Test for CloudTrail log file validation compliance.

    Verifies that all CloudTrail trails have log file validation enabled
    to ensure log integrity and detect tampering.

    Compliance Requirements:
        - All CloudTrail trails must have LogFileValidationEnabled=True
        - Log file validation provides cryptographic proof of log integrity
        - Trails without validation are non-compliant

    Scoring:
        - 100% if all trails have validation enabled
        - Proportional score based on compliant/total ratio
        - 0% if no trails have validation enabled

    Example:
        >>> test = CloudTrailLogValidationTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize CloudTrail log validation test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="cloudtrail_log_validation",
            test_name="CloudTrail Log File Validation Check",
            description="Verify all CloudTrail trails have log file validation enabled",
            control_id="A.8.15",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute CloudTrail log validation compliance test.

        Returns:
            TestResult with findings for trails without validation

        Example:
            >>> test = CloudTrailLogValidationTest(connector)
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
                        "Create a CloudTrail trail:\n"
                        "1. Go to AWS Console → CloudTrail → Create trail\n"
                        "2. Enable log file validation\n"
                        "3. Configure S3 bucket for log storage\n"
                        "Or use AWS CLI:\n"
                        "aws cloudtrail create-trail --name my-trail \\\n"
                        "  --s3-bucket-name my-cloudtrail-bucket \\\n"
                        "  --enable-log-file-validation"
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

            # Check each trail for log file validation
            compliant_count = 0
            total_count = len(trails)

            for trail in trails:
                trail_name = trail.get("Name")
                trail_arn = trail.get("TrailARN")
                log_validation_enabled = trail.get("LogFileValidationEnabled", False)
                result.resources_scanned += 1

                # Get additional trail details
                is_multiregion = trail.get("IsMultiRegionTrail", False)
                is_organization = trail.get("IsOrganizationTrail", False)
                s3_bucket = trail.get("S3BucketName", "unknown")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=trail_name,
                    resource_type="cloudtrail_trail",
                    data={
                        "trail_name": trail_name,
                        "trail_arn": trail_arn,
                        "log_file_validation_enabled": log_validation_enabled,
                        "is_multiregion_trail": is_multiregion,
                        "is_organization_trail": is_organization,
                        "s3_bucket_name": s3_bucket,
                        "home_region": trail.get("HomeRegion"),
                    }
                )
                result.add_evidence(evidence)

                if log_validation_enabled:
                    compliant_count += 1
                    self.logger.debug(
                        "trail_validation_enabled",
                        trail_name=trail_name,
                        is_multiregion=is_multiregion
                    )
                else:
                    # Create finding for trail without validation
                    finding = self.create_finding(
                        resource_id=trail_name,
                        resource_type="cloudtrail_trail",
                        severity=Severity.MEDIUM,
                        title="CloudTrail log file validation not enabled",
                        description=f"CloudTrail trail '{trail_name}' does not have log file validation enabled. "
                                    "Without validation, log files can be tampered with or deleted without detection. "
                                    "This violates ISO 27001 A.8.15 requirement for log integrity.",
                        remediation=(
                            f"Enable log file validation for trail '{trail_name}':\n"
                            f"aws cloudtrail update-trail --name {trail_name} \\\n"
                            "  --enable-log-file-validation\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to CloudTrail → Trails\n"
                            f"2. Select trail '{trail_name}'\n"
                            "3. Click Edit\n"
                            "4. Under Additional settings, enable 'Log file validation'\n"
                            "5. Click Save changes\n\n"
                            "Note: Validation only applies to logs created after enabling."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "trail_validation_disabled",
                        trail_name=trail_name
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (compliant_count / total_count) * 100

            # Determine pass/fail
            result.passed = compliant_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_trails": total_count,
                "trails_with_validation": compliant_count,
                "trails_without_validation": total_count - compliant_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "cloudtrail_log_validation_test_completed",
                total=total_count,
                compliant=compliant_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("cloudtrail_validation_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("cloudtrail_validation_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_cloudtrail_log_validation_test(connector: AWSConnector) -> TestResult:
    """Run CloudTrail log validation compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_cloudtrail_log_validation_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = CloudTrailLogValidationTest(connector)
    return test.execute()

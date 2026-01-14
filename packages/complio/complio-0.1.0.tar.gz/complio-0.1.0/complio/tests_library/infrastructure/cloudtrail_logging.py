"""
CloudTrail logging compliance test.

Checks that AWS CloudTrail is enabled and properly configured for audit logging.

ISO 27001 Control: A.12.4.1 - Event Logging
Requirement: Event logs recording user activities, exceptions, faults and information
security events shall be produced, kept and regularly reviewed.

CloudTrail requirements:
- At least one trail enabled
- Multi-region trail enabled
- Log file validation enabled
- S3 bucket logging enabled
- CloudWatch Logs integration (optional but recommended)

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.cloudtrail_logging import CloudTrailLoggingTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = CloudTrailLoggingTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

from typing import Any, Dict, List

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Evidence,
    Finding,
    Severity,
    TestResult,
    TestStatus,
)
from complio.utils.logger import get_logger


class CloudTrailLoggingTest(ComplianceTest):
    """Test for CloudTrail logging compliance.

    Verifies that AWS CloudTrail is properly configured for audit logging.

    Compliance Requirements (ISO 27001 A.12.4.1):
        - At least one trail must be enabled
        - Multi-region trail should be configured
        - Log file validation must be enabled
        - Logs must be delivered to S3
        - CloudWatch Logs integration recommended

    Scoring:
        - 100% if all requirements met
        - 0% if no trails configured
        - Deductions for missing features

    Example:
        >>> test = CloudTrailLoggingTest(connector)
        >>> result = test.run()
        >>> if not result.passed:
        ...     for finding in result.findings:
        ...         print(f"{finding.severity}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize CloudTrail logging test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="cloudtrail_logging",
            test_name="CloudTrail Audit Logging",
            description="Ensures CloudTrail is enabled with log file validation to maintain audit trails (checks trails in specified region)",
            control_id="A.12.4.1",
            connector=connector,
            scope="regional",
        )
        self.logger = get_logger(__name__)

    def execute(self) -> TestResult:
        """Execute the CloudTrail logging compliance test.

        Returns:
            TestResult with findings and evidence

        Raises:
            AWSConnectionError: If unable to connect to AWS
            AWSCredentialsError: If credentials are invalid
        """
        self.logger.info(
            "starting_cloudtrail_logging_test",
            region=self.connector.region,
        )

        findings: List[Finding] = []
        evidence_list: List[Evidence] = []

        try:
            # Get CloudTrail client
            cloudtrail_client = self.connector.get_client("cloudtrail")

            # Describe all trails
            response = cloudtrail_client.describe_trails()
            trails = response.get("trailList", [])

            # Get trail status for each trail
            trail_statuses = []
            for trail in trails:
                trail_name = trail.get("Name", "unknown")
                try:
                    status_response = cloudtrail_client.get_trail_status(Name=trail_name)
                    trail_statuses.append({
                        "trail": trail,
                        "status": status_response,
                    })
                except ClientError:
                    # If we can't get status, trail might not exist in this region
                    continue

            self.logger.info(
                "cloudtrail_trails_found",
                total_trails=len(trails),
                active_trails=len(trail_statuses),
                region=self.connector.region,
            )

            # Check if any trails exist
            if not trail_statuses:
                finding = Finding(
                    resource_id="aws-account",
                    resource_type="cloudtrail",
                    severity=Severity.CRITICAL,
                    title="No CloudTrail trails configured",
                    description=(
                        "AWS account has no CloudTrail trails configured. This means no audit "
                        "logs are being collected for AWS API calls. Without CloudTrail, you cannot "
                        "detect unauthorized access, track changes, or meet ISO 27001 A.12.4.1 requirements."
                    ),
                    remediation=(
                        "Enable CloudTrail:\n"
                        "1. Go to CloudTrail Console\n"
                        "2. Click 'Create trail'\n"
                        "3. Enable 'Apply trail to all regions'\n"
                        "4. Enable 'Log file validation'\n"
                        "5. Configure S3 bucket for log storage\n"
                        "6. Optionally configure CloudWatch Logs"
                    ),
                    iso27001_control="A.12.4.1",
                )
                findings.append(finding)

                evidence = Evidence(
                    resource_id="aws-account",
                    resource_type="cloudtrail",
                    region=self.connector.region,
                    data={"trails_configured": 0, "trails_active": 0},
                )
                evidence_list.append(evidence)

                return TestResult(
                    test_id=self.test_id,
                    test_name=self.test_name,
                    status=TestStatus.FAILED,
                    passed=False,
                    score=0.0,
                    findings=findings,
                    evidence=evidence_list,
                    metadata={
                        "region": self.connector.region,
                        "trails_configured": 0,
                        "iso27001_control": "A.12.4.1",
                    },
                )

            # Analyze each trail
            has_multi_region_trail = False
            has_log_file_validation = False
            has_cloudwatch_logs = False
            active_trails = 0

            for trail_data in trail_statuses:
                trail = trail_data["trail"]
                status = trail_data["status"]

                trail_name = trail.get("Name", "unknown")
                trail_arn = trail.get("TrailARN", "N/A")
                is_logging = status.get("IsLogging", False)
                is_multi_region = trail.get("IsMultiRegionTrail", False)
                log_validation = trail.get("LogFileValidationEnabled", False)
                cloudwatch_logs_arn = trail.get("CloudWatchLogsLogGroupArn")

                if is_logging:
                    active_trails += 1

                if is_multi_region:
                    has_multi_region_trail = True

                if log_validation:
                    has_log_file_validation = True

                if cloudwatch_logs_arn:
                    has_cloudwatch_logs = True

                # Create evidence for each trail
                evidence = Evidence(
                    resource_id=trail_arn,
                    resource_type="cloudtrail",
                    region=self.connector.region,
                    data={
                        "trail_name": trail_name,
                        "is_logging": is_logging,
                        "is_multi_region": is_multi_region,
                        "log_file_validation": log_validation,
                        "s3_bucket": trail.get("S3BucketName", "N/A"),
                        "has_cloudwatch_logs": cloudwatch_logs_arn is not None,
                    },
                )
                evidence_list.append(evidence)

                # Check for issues with this trail
                if not is_logging:
                    findings.append(
                        Finding(
                            resource_id=trail_arn,
                            resource_type="cloudtrail",
                            severity=Severity.HIGH,
                            title=f"CloudTrail '{trail_name}' is not logging",
                            description=(
                                f"Trail '{trail_name}' is configured but not currently logging. "
                                f"This means audit events are not being recorded."
                            ),
                            remediation=f"Enable logging for trail '{trail_name}' using CloudTrail console or AWS CLI",
                            iso27001_control="A.12.4.1",
                            metadata={"trail_name": trail_name},
                        )
                    )

            # Check for missing features across all trails
            score = 100.0
            score_deductions = 0

            if not has_multi_region_trail:
                score_deductions += 20
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="cloudtrail",
                        severity=Severity.HIGH,
                        title="No multi-region CloudTrail trail configured",
                        description=(
                            "None of the CloudTrail trails are configured for multi-region logging. "
                            "This means API calls in other regions are not being logged, creating audit gaps."
                        ),
                        remediation=(
                            "Configure at least one trail as multi-region:\n"
                            "1. Go to CloudTrail Console\n"
                            "2. Select a trail or create new one\n"
                            "3. Enable 'Apply trail to all regions'"
                        ),
                        iso27001_control="A.12.4.1",
                    )
                )

            if not has_log_file_validation:
                score_deductions += 15
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="cloudtrail",
                        severity=Severity.MEDIUM,
                        title="Log file validation not enabled",
                        description=(
                            "None of the CloudTrail trails have log file validation enabled. "
                            "Without this, you cannot verify that log files haven't been tampered with."
                        ),
                        remediation=(
                            "Enable log file validation:\n"
                            "1. Go to CloudTrail Console\n"
                            "2. Select a trail\n"
                            "3. Edit trail settings\n"
                            "4. Enable 'Enable log file validation'"
                        ),
                        iso27001_control="A.12.4.1",
                    )
                )

            if not has_cloudwatch_logs:
                score_deductions += 10
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="cloudtrail",
                        severity=Severity.LOW,
                        title="CloudWatch Logs integration not configured",
                        description=(
                            "CloudTrail is not integrated with CloudWatch Logs. "
                            "While not required, this integration enables real-time monitoring "
                            "and alerting on suspicious API activity."
                        ),
                        remediation=(
                            "Configure CloudWatch Logs (optional but recommended):\n"
                            "1. Go to CloudTrail Console\n"
                            "2. Select a trail\n"
                            "3. Edit trail settings\n"
                            "4. Configure CloudWatch Logs log group\n"
                            "5. Create IAM role for CloudTrail to write to CloudWatch"
                        ),
                        iso27001_control="A.12.4.1",
                    )
                )

            if active_trails == 0:
                score_deductions += 50  # Critical issue
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="cloudtrail",
                        severity=Severity.CRITICAL,
                        title="No active CloudTrail logging",
                        description=(
                            f"{len(trails)} trail(s) configured but none are actively logging. "
                            f"No audit logs are being collected."
                        ),
                        remediation="Start logging on at least one CloudTrail trail",
                        iso27001_control="A.12.4.1",
                    )
                )

            score = max(0.0, score - score_deductions)

            if score >= 90:
                status = TestStatus.PASSED
                passed = True
            elif score >= 70:
                status = TestStatus.WARNING
                passed = False
            else:
                status = TestStatus.FAILED
                passed = False

            self.logger.info(
                "cloudtrail_logging_test_complete",
                total_trails=len(trails),
                active_trails=active_trails,
                has_multi_region=has_multi_region_trail,
                score=score,
            )

            return TestResult(
                test_id=self.test_id,
                test_name=self.test_name,
                status=status,
                passed=passed,
                score=score,
                findings=findings,
                evidence=evidence_list,
                metadata={
                    "region": self.connector.region,
                    "total_trails": len(trails),
                    "active_trails": active_trails,
                    "has_multi_region_trail": has_multi_region_trail,
                    "has_log_file_validation": has_log_file_validation,
                    "has_cloudwatch_logs": has_cloudwatch_logs,
                    "iso27001_control": "A.12.4.1",
                },
            )

        except ClientError as e:
            self.logger.error(
                "cloudtrail_logging_test_failed",
                error=str(e),
                error_code=e.response.get("Error", {}).get("Code"),
            )

            return TestResult(
                test_id=self.test_id,
                test_name=self.test_name,
                status=TestStatus.ERROR,
                passed=False,
                score=0.0,
                findings=[
                    Finding(
                        resource_id="aws-account",
                        resource_type="cloudtrail",
                        severity=Severity.HIGH,
                        title="Failed to check CloudTrail configuration",
                        description=f"Error accessing CloudTrail: {str(e)}",
                        remediation="Check AWS credentials and permissions. Ensure IAM policy allows cloudtrail:DescribeTrails and cloudtrail:GetTrailStatus",
                        iso27001_control="A.12.4.1",
                    )
                ],
                evidence=[],
                metadata={"error": str(e)},
            )

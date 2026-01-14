"""
CloudWatch Logs retention compliance test.

Checks that all CloudWatch log groups have retention policies configured.

ISO 27001 Control: A.8.15 - Logging
Requirement: Log groups must have retention policies to manage log lifecycle

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.logging.cloudwatch_retention import CloudWatchRetentionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = CloudWatchRetentionTest(connector)
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


class CloudWatchRetentionTest(ComplianceTest):
    """Test for CloudWatch Logs retention compliance.

    Verifies that all CloudWatch log groups have retention policies configured
    to prevent indefinite log storage and manage costs.

    Compliance Requirements:
        - All log groups must have retention policy set (not "Never expire")
        - Retention period should align with compliance requirements
        - Typical retention: 30, 90, 180, 365 days or longer

    Scoring:
        - 100% if all log groups have retention configured
        - Proportional score based on compliant/total ratio
        - 100% if no log groups exist

    Example:
        >>> test = CloudWatchRetentionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize CloudWatch retention test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="cloudwatch_retention",
            test_name="CloudWatch Logs Retention Check",
            description="Verify all CloudWatch log groups have retention policies configured",
            control_id="A.8.15",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute CloudWatch Logs retention compliance test.

        Returns:
            TestResult with findings for log groups without retention

        Example:
            >>> test = CloudWatchRetentionTest(connector)
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
            # Get CloudWatch Logs client
            logs_client = self.connector.get_client("logs")

            # List all log groups
            self.logger.info("listing_log_groups")
            log_groups = []

            paginator = logs_client.get_paginator("describe_log_groups")
            for page in paginator.paginate():
                log_groups.extend(page.get("logGroups", []))

            if not log_groups:
                self.logger.info("no_log_groups_found")
                result.metadata["message"] = "No CloudWatch log groups found in region"
                return result

            self.logger.info("log_groups_found", count=len(log_groups))

            # Check retention for each log group
            retention_configured_count = 0

            for log_group in log_groups:
                log_group_name = log_group["logGroupName"]
                result.resources_scanned += 1

                # Check if retention is configured
                # retentionInDays is only present if retention is set
                retention_in_days = log_group.get("retentionInDays")
                has_retention = retention_in_days is not None

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=log_group_name,
                    resource_type="cloudwatch_log_group",
                    data={
                        "log_group_name": log_group_name,
                        "retention_in_days": retention_in_days,
                        "has_retention": has_retention,
                        "creation_time": log_group.get("creationTime"),
                        "stored_bytes": log_group.get("storedBytes", 0),
                    }
                )
                result.add_evidence(evidence)

                if has_retention:
                    retention_configured_count += 1
                    self.logger.debug(
                        "log_group_has_retention",
                        log_group=log_group_name,
                        retention_days=retention_in_days
                    )
                else:
                    # Create finding for log group without retention
                    finding = self.create_finding(
                        resource_id=log_group_name,
                        resource_type="cloudwatch_log_group",
                        severity=Severity.MEDIUM,
                        title="CloudWatch log group has no retention policy",
                        description=f"CloudWatch log group '{log_group_name}' does not have a retention "
                                    "policy configured (set to 'Never expire'). Without retention policies, "
                                    "logs are stored indefinitely, leading to unnecessary storage costs and "
                                    "making it difficult to manage log lifecycle according to compliance "
                                    "requirements. ISO 27001 A.8.15 requires proper logging practices "
                                    "including log retention management.",
                        remediation=(
                            f"Set retention policy for log group '{log_group_name}':\n\n"
                            "Using AWS CLI (example: 90 days retention):\n"
                            f"aws logs put-retention-policy \\\n"
                            f"  --log-group-name {log_group_name} \\\n"
                            "  --retention-in-days 90\n\n"
                            "Common retention periods:\n"
                            "- 1, 3, 5, 7, 14 days (development/testing)\n"
                            "- 30, 60, 90 days (operational logs)\n"
                            "- 120, 150, 180 days (compliance logs)\n"
                            "- 365, 400, 545, 731 days (audit logs)\n"
                            "- 1827, 2192, 2557, 2922, 3288, 3653 days (long-term compliance)\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to CloudWatch Logs console\n"
                            f"2. Select log group '{log_group_name}'\n"
                            "3. Click 'Actions' → 'Edit retention setting'\n"
                            "4. Select appropriate retention period\n"
                            "5. Click 'Save'\n\n"
                            "Note: Consider your compliance requirements (GDPR, HIPAA, PCI-DSS, etc.) "
                            "when choosing retention periods. Archive to S3 for longer retention if needed."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "log_group_no_retention",
                        log_group=log_group_name
                    )

            # Calculate compliance score
            result.score = (retention_configured_count / len(log_groups)) * 100

            # Determine pass/fail
            result.passed = retention_configured_count == len(log_groups)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_log_groups": len(log_groups),
                "retention_configured": retention_configured_count,
                "no_retention": len(log_groups) - retention_configured_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "cloudwatch_retention_test_completed",
                total_log_groups=len(log_groups),
                retention_configured=retention_configured_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("cloudwatch_retention_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("cloudwatch_retention_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_cloudwatch_retention_test(connector: AWSConnector) -> TestResult:
    """Run CloudWatch Logs retention compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_cloudwatch_retention_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = CloudWatchRetentionTest(connector)
    return test.execute()

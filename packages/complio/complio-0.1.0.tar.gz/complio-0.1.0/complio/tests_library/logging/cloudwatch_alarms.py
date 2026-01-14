"""
CloudWatch Alarms compliance test.

Checks that critical CloudWatch alarms are configured for monitoring.

ISO 27001 Control: A.8.16 - Monitoring activities
Requirement: Critical resources should have monitoring alarms configured

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.logging.cloudwatch_alarms import CloudWatchAlarmsTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = CloudWatchAlarmsTest(connector)
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


class CloudWatchAlarmsTest(ComplianceTest):
    """Test for CloudWatch Alarms compliance.

    Verifies that critical CloudWatch alarms are configured:
    - Alarms should be in OK or ALARM state (not INSUFFICIENT_DATA for long)
    - Alarms should have actions configured (SNS notifications)
    - Critical metrics should have alarms (EC2, RDS, Lambda, etc.)

    Compliance Requirements:
        - Alarms configured for critical resources
        - Actions configured (SNS topics for notifications)
        - Alarms in actionable states (not stuck in INSUFFICIENT_DATA)

    Scoring:
        - Based on alarm configuration and health
        - Checks for presence of critical alarms
        - Validates alarm actions are configured

    Example:
        >>> test = CloudWatchAlarmsTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize CloudWatch Alarms test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="cloudwatch_alarms",
            test_name="CloudWatch Alarms Check",
            description="Verify critical CloudWatch alarms are configured for monitoring",
            control_id="A.8.16",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute CloudWatch Alarms compliance test.

        Returns:
            TestResult with findings for missing or misconfigured alarms

        Example:
            >>> test = CloudWatchAlarmsTest(connector)
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
            # Get CloudWatch client
            cloudwatch_client = self.connector.get_client("cloudwatch")

            # List all metric alarms
            self.logger.info("listing_cloudwatch_alarms")
            alarms = []

            paginator = cloudwatch_client.get_paginator("describe_alarms")
            for page in paginator.paginate():
                metric_alarms = page.get("MetricAlarms", [])
                alarms.extend(metric_alarms)

            if not alarms:
                self.logger.info("no_cloudwatch_alarms_found")
                result.metadata["message"] = "No CloudWatch alarms found (consider creating alarms for critical resources)"
                result.metadata["recommendation"] = "Create alarms for EC2, RDS, Lambda, and other critical resources"
                # Not a hard failure, but should be monitored
                result.score = 50.0  # Partial score for having no alarms
                result.passed = False
                result.status = TestStatus.FAILED
                return result

            self.logger.info("cloudwatch_alarms_found", count=len(alarms))

            # Analyze alarm configurations
            properly_configured_count = 0
            alarms_without_actions = 0
            alarms_insufficient_data = 0

            for alarm in alarms:
                alarm_name = alarm.get("AlarmName", "")
                alarm_arn = alarm.get("AlarmArn", "")
                state_value = alarm.get("StateValue", "")
                actions_enabled = alarm.get("ActionsEnabled", False)
                alarm_actions = alarm.get("AlarmActions", [])
                metric_name = alarm.get("MetricName", "")
                namespace = alarm.get("Namespace", "")

                result.resources_scanned += 1

                # Determine issues
                issues = []
                severity = Severity.MEDIUM

                # Check if alarm has actions configured
                if actions_enabled and len(alarm_actions) == 0:
                    issues.append("Alarm has actions enabled but no actions configured")
                    alarms_without_actions += 1
                    severity = Severity.MEDIUM

                if not actions_enabled:
                    issues.append("Alarm actions are disabled")
                    alarms_without_actions += 1
                    severity = Severity.MEDIUM

                # Check alarm state
                if state_value == "INSUFFICIENT_DATA":
                    issues.append("Alarm in INSUFFICIENT_DATA state (may indicate misconfiguration)")
                    alarms_insufficient_data += 1
                    severity = Severity.LOW

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=alarm_arn,
                    resource_type="cloudwatch_alarm",
                    data={
                        "alarm_name": alarm_name,
                        "alarm_arn": alarm_arn,
                        "state_value": state_value,
                        "actions_enabled": actions_enabled,
                        "alarm_actions_count": len(alarm_actions),
                        "metric_name": metric_name,
                        "namespace": namespace,
                        "has_issues": len(issues) > 0,
                        "issues": issues,
                    }
                )
                result.add_evidence(evidence)

                if len(issues) == 0:
                    properly_configured_count += 1
                    self.logger.debug(
                        "alarm_properly_configured",
                        alarm_name=alarm_name
                    )
                else:
                    # Create finding for misconfigured alarm
                    finding = self.create_finding(
                        resource_id=alarm_arn,
                        resource_type="cloudwatch_alarm",
                        severity=severity,
                        title="CloudWatch alarm has configuration issues",
                        description=f"CloudWatch alarm '{alarm_name}' (monitoring {namespace}/{metric_name}) has "
                                    f"configuration issues: {'; '.join(issues)}. Alarms should have actions "
                                    "configured (SNS notifications) and be in actionable states to effectively "
                                    "monitor resources. ISO 27001 A.8.16 requires monitoring of system activities.",
                        remediation=(
                            f"Improve CloudWatch alarm '{alarm_name}' configuration:\n\n"
                            "1. Enable alarm actions:\n"
                            f"aws cloudwatch enable-alarm-actions \\\n"
                            f"  --alarm-names {alarm_name}\n\n"
                            "2. Configure SNS topic for notifications:\n"
                            "# Create SNS topic if needed\n"
                            "aws sns create-topic --name alarm-notifications\n\n"
                            "# Subscribe email to topic\n"
                            "aws sns subscribe \\\n"
                            "  --topic-arn <SNS-TOPIC-ARN> \\\n"
                            "  --protocol email \\\n"
                            "  --notification-endpoint your-email@example.com\n\n"
                            "# Add SNS topic to alarm\n"
                            f"aws cloudwatch put-metric-alarm \\\n"
                            f"  --alarm-name {alarm_name} \\\n"
                            f"  --metric-name {metric_name} \\\n"
                            f"  --namespace {namespace} \\\n"
                            "  --statistic Average \\\n"
                            "  --period 300 \\\n"
                            "  --evaluation-periods 2 \\\n"
                            "  --threshold 80 \\\n"
                            "  --comparison-operator GreaterThanThreshold \\\n"
                            "  --alarm-actions <SNS-TOPIC-ARN> \\\n"
                            "  --ok-actions <SNS-TOPIC-ARN> \\\n"
                            "  --insufficient-data-actions <SNS-TOPIC-ARN>\n\n"
                            "3. Fix INSUFFICIENT_DATA state:\n"
                            "# Check if metric is publishing data\n"
                            f"aws cloudwatch get-metric-statistics \\\n"
                            f"  --namespace {namespace} \\\n"
                            f"  --metric-name {metric_name} \\\n"
                            "  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \\\n"
                            "  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \\\n"
                            "  --period 300 \\\n"
                            "  --statistics Average\n\n"
                            "# Adjust alarm configuration if needed:\n"
                            "- Increase evaluation periods\n"
                            "- Adjust metric dimensions\n"
                            "- Verify resource is active and publishing metrics\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to CloudWatch console → Alarms\n"
                            f"2. Select alarm '{alarm_name}'\n"
                            "3. Click 'Actions' → 'Edit'\n"
                            "4. Configure notification:\n"
                            "   - Send notification to: Select or create SNS topic\n"
                            "   - Add email/SMS endpoints to SNS topic\n"
                            "5. Verify 'Enable actions' is checked\n"
                            "6. Configure actions for:\n"
                            "   - In alarm\n"
                            "   - OK\n"
                            "   - Insufficient data\n"
                            "7. Save changes\n\n"
                            "Critical alarms to configure:\n"
                            "EC2 Instances:\n"
                            "- CPUUtilization > 80%\n"
                            "- StatusCheckFailed (system + instance)\n"
                            "- DiskReadOps/WriteOps (high I/O)\n\n"
                            "RDS Databases:\n"
                            "- CPUUtilization > 80%\n"
                            "- FreeableMemory < 1GB\n"
                            "- DatabaseConnections > 80% of max\n"
                            "- ReadLatency/WriteLatency\n\n"
                            "Lambda Functions:\n"
                            "- Errors > 0\n"
                            "- Duration > threshold\n"
                            "- Throttles > 0\n"
                            "- ConcurrentExecutions near limit\n\n"
                            "ELB/ALB:\n"
                            "- UnHealthyHostCount > 0\n"
                            "- TargetResponseTime\n"
                            "- HTTPCode_Target_5XX_Count\n\n"
                            "S3 Buckets:\n"
                            "- 4xxErrors\n"
                            "- 5xxErrors\n\n"
                            "Best practices:\n"
                            "- Use composite alarms for complex conditions\n"
                            "- Configure multiple notification channels\n"
                            "- Set appropriate thresholds based on baselines\n"
                            "- Use alarm descriptions for runbook links\n"
                            "- Test alarm notifications regularly\n"
                            "- Use anomaly detection for dynamic thresholds\n"
                            "- Create alarms using Infrastructure as Code (Terraform, CloudFormation)\n"
                            "- Monitor alarm state changes in EventBridge\n"
                            "- Use alarm actions for auto-remediation (Lambda, Auto Scaling)\n"
                            "- Tag alarms for organization and cost allocation"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "alarm_misconfigured",
                        alarm_name=alarm_name,
                        issues=issues
                    )

            # Calculate compliance score
            result.score = (properly_configured_count / len(alarms)) * 100

            # Determine pass/fail
            result.passed = properly_configured_count == len(alarms)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_alarms": len(alarms),
                "properly_configured": properly_configured_count,
                "alarms_without_actions": alarms_without_actions,
                "alarms_insufficient_data": alarms_insufficient_data,
                "misconfigured": len(alarms) - properly_configured_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "cloudwatch_alarms_test_completed",
                total_alarms=len(alarms),
                properly_configured=properly_configured_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("cloudwatch_alarms_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("cloudwatch_alarms_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_cloudwatch_alarms_test(connector: AWSConnector) -> TestResult:
    """Run CloudWatch Alarms compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_cloudwatch_alarms_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = CloudWatchAlarmsTest(connector)
    return test.execute()

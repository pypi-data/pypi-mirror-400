"""
AWS EventBridge security monitoring rules compliance test.

Checks that EventBridge rules are configured for critical security events.

ISO 27001 Control: A.8.16 - Monitoring activities
Requirement: EventBridge rules should monitor critical security events

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.logging.eventbridge_rules import EventBridgeRulesTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = EventBridgeRulesTest(connector)
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


class EventBridgeRulesTest(ComplianceTest):
    """Test for EventBridge security monitoring rules compliance.

    Verifies that EventBridge rules are configured for critical security events:
    - Rules for GuardDuty findings
    - Rules for Security Hub findings
    - Rules for AWS Config compliance changes
    - Rules for CloudTrail security events
    - Rules should have targets configured (SNS, Lambda, etc.)
    - Rules should be enabled (not disabled)

    Compliance Requirements:
        - EventBridge rules for critical security services
        - Rules have targets for notifications/remediation
        - Rules are enabled and active
        - Coverage for major security event sources

    Scoring:
        - Based on presence of security monitoring rules
        - Checks for key event patterns
        - Validates targets are configured

    Example:
        >>> test = EventBridgeRulesTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    # Critical security event sources to monitor
    CRITICAL_EVENT_SOURCES = {
        "aws.guardduty": "GuardDuty threat detection findings",
        "aws.securityhub": "Security Hub aggregated findings",
        "aws.config": "AWS Config compliance changes",
        "aws.health": "AWS Health security events",
    }

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize EventBridge rules test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="eventbridge_rules",
            test_name="EventBridge Security Rules Check",
            description="Verify EventBridge rules are configured for critical security events",
            control_id="A.8.16",
            connector=connector,
            scope="regional",
        )

    def _check_rule_event_pattern(self, event_pattern: str, source: str) -> bool:
        """Check if event pattern matches a security event source.

        Args:
            event_pattern: JSON event pattern string
            source: Event source to check for

        Returns:
            True if pattern includes the source
        """
        if not event_pattern:
            return False

        try:
            import json
            pattern = json.loads(event_pattern)

            # Check if source is in the pattern
            pattern_sources = pattern.get("source", [])
            if isinstance(pattern_sources, str):
                pattern_sources = [pattern_sources]

            return source in pattern_sources

        except (json.JSONDecodeError, TypeError):
            return False

    def execute(self) -> TestResult:
        """Execute EventBridge security rules compliance test.

        Returns:
            TestResult with findings for missing or misconfigured rules

        Example:
            >>> test = EventBridgeRulesTest(connector)
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
            # Get EventBridge client
            events_client = self.connector.get_client("events")

            # List all EventBridge rules
            self.logger.info("listing_eventbridge_rules")
            rules = []

            paginator = events_client.get_paginator("list_rules")
            for page in paginator.paginate():
                rules.extend(page.get("Rules", []))

            self.logger.info("eventbridge_rules_found", count=len(rules))

            # Track which critical event sources have rules
            sources_covered = {}
            for source in self.CRITICAL_EVENT_SOURCES.keys():
                sources_covered[source] = {
                    "has_rule": False,
                    "rules": [],
                    "has_targets": False
                }

            # Check each rule
            for rule in rules:
                rule_name = rule.get("Name", "")
                rule_arn = rule.get("Arn", "")
                rule_state = rule.get("State", "DISABLED")
                event_pattern = rule.get("EventPattern", "")

                result.resources_scanned += 1

                # Check if rule is enabled
                if rule_state != "ENABLED":
                    continue

                # Check if rule monitors critical security events
                for source in self.CRITICAL_EVENT_SOURCES.keys():
                    if self._check_rule_event_pattern(event_pattern, source):
                        sources_covered[source]["has_rule"] = True
                        sources_covered[source]["rules"].append(rule_name)

                        # Check if rule has targets
                        try:
                            targets_response = events_client.list_targets_by_rule(Rule=rule_name)
                            targets = targets_response.get("Targets", [])

                            if len(targets) > 0:
                                sources_covered[source]["has_targets"] = True

                        except ClientError as e:
                            self.logger.warning("error_checking_targets", rule=rule_name, error=str(e))

            # Analyze coverage
            issues = []
            severity = Severity.MEDIUM
            score_points = 0

            # Calculate score based on coverage of critical sources
            points_per_source = 100 / len(self.CRITICAL_EVENT_SOURCES)

            for source, info in sources_covered.items():
                source_name = self.CRITICAL_EVENT_SOURCES[source]

                if info["has_rule"] and info["has_targets"]:
                    # Full coverage for this source
                    score_points += points_per_source
                    self.logger.debug(
                        "event_source_covered",
                        source=source,
                        rules=info["rules"]
                    )
                elif info["has_rule"]:
                    # Rule exists but no targets
                    score_points += points_per_source * 0.5
                    issues.append(f"{source_name} has rules but no targets configured")
                else:
                    # No rule for this source
                    issues.append(f"No EventBridge rule for {source_name}")
                    if source in ["aws.guardduty", "aws.securityhub"]:
                        severity = Severity.HIGH

            # If no rules at all, this is more serious
            if len(rules) == 0:
                issues.insert(0, "No EventBridge rules configured")
                severity = Severity.HIGH
                score_points = 0

            # Create evidence
            evidence = self.create_evidence(
                resource_id="eventbridge-security-rules",
                resource_type="eventbridge_rules",
                data={
                    "total_rules": len(rules),
                    "sources_coverage": sources_covered,
                    "has_issues": len(issues) > 0,
                    "issues": issues,
                    "security_score": score_points,
                }
            )
            result.add_evidence(evidence)

            if len(issues) > 0:
                # Create finding for EventBridge rules issues
                finding = self.create_finding(
                    resource_id="eventbridge-security-rules",
                    resource_type="eventbridge_rules",
                    severity=severity,
                    title="EventBridge security monitoring rules incomplete",
                    description=f"EventBridge security monitoring rules have coverage gaps: {'; '.join(issues)}. "
                                "EventBridge rules should be configured to monitor critical security events from "
                                "GuardDuty, Security Hub, Config, and other security services for timely "
                                "detection and response. ISO 27001 A.8.16 requires monitoring and alerting for "
                                "security events.",
                    remediation=(
                        "Configure EventBridge rules for security monitoring:\n\n"
                        "1. Create rule for GuardDuty findings:\n"
                        "aws events put-rule \\\n"
                        "  --name guardduty-high-severity \\\n"
                        "  --description 'Alert on high severity GuardDuty findings' \\\n"
                        "  --event-pattern '{\n"
                        '    "source": ["aws.guardduty"],\n'
                        '    "detail-type": ["GuardDuty Finding"],\n'
                        '    "detail": {\n'
                        '      "severity": [7, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9]\n'
                        '    }\n'
                        "  }' \\\n"
                        "  --state ENABLED\n\n"
                        "# Add SNS target\n"
                        "aws events put-targets \\\n"
                        "  --rule guardduty-high-severity \\\n"
                        "  --targets Id=1,Arn=arn:aws:sns:REGION:ACCOUNT:security-alerts\n\n"
                        "2. Create rule for Security Hub findings:\n"
                        "aws events put-rule \\\n"
                        "  --name securityhub-critical-findings \\\n"
                        "  --description 'Alert on critical Security Hub findings' \\\n"
                        "  --event-pattern '{\n"
                        '    "source": ["aws.securityhub"],\n'
                        '    "detail-type": ["Security Hub Findings - Imported"],\n'
                        '    "detail": {\n'
                        '      "findings": {\n'
                        '        "Severity": {\n'
                        '          "Label": ["CRITICAL", "HIGH"]\n'
                        '        }\n'
                        '      }\n'
                        '    }\n'
                        "  }' \\\n"
                        "  --state ENABLED\n\n"
                        "# Add SNS target\n"
                        "aws events put-targets \\\n"
                        "  --rule securityhub-critical-findings \\\n"
                        "  --targets Id=1,Arn=arn:aws:sns:REGION:ACCOUNT:security-alerts\n\n"
                        "3. Create rule for Config compliance changes:\n"
                        "aws events put-rule \\\n"
                        "  --name config-compliance-changes \\\n"
                        "  --description 'Alert on Config compliance changes' \\\n"
                        "  --event-pattern '{\n"
                        '    "source": ["aws.config"],\n'
                        '    "detail-type": ["Config Rules Compliance Change"],\n'
                        '    "detail": {\n'
                        '      "newEvaluationResult": {\n'
                        '        "complianceType": ["NON_COMPLIANT"]\n'
                        '      }\n'
                        '    }\n'
                        "  }' \\\n"
                        "  --state ENABLED\n\n"
                        "# Add SNS target\n"
                        "aws events put-targets \\\n"
                        "  --rule config-compliance-changes \\\n"
                        "  --targets Id=1,Arn=arn:aws:sns:REGION:ACCOUNT:compliance-alerts\n\n"
                        "4. Create rule for AWS Health events:\n"
                        "aws events put-rule \\\n"
                        "  --name health-security-events \\\n"
                        "  --description 'Alert on AWS Health security events' \\\n"
                        "  --event-pattern '{\n"
                        '    "source": ["aws.health"],\n'
                        '    "detail-type": ["AWS Health Event"],\n'
                        '    "detail": {\n'
                        '      "service": ["SECURITY"],\n'
                        '      "eventTypeCategory": ["issue", "accountNotification"]\n'
                        '    }\n'
                        "  }' \\\n"
                        "  --state ENABLED\n\n"
                        "# Add SNS target\n"
                        "aws events put-targets \\\n"
                        "  --rule health-security-events \\\n"
                        "  --targets Id=1,Arn=arn:aws:sns:REGION:ACCOUNT:security-alerts\n\n"
                        "Or use AWS Console:\n"
                        "1. Go to Amazon EventBridge console\n"
                        "2. Click 'Rules' → 'Create rule'\n"
                        "3. Configure rule:\n"
                        "   - Name: guardduty-high-severity\n"
                        "   - Event bus: default\n"
                        "   - Rule type: Rule with an event pattern\n"
                        "4. Build event pattern:\n"
                        "   - Event source: AWS events\n"
                        "   - Service: GuardDuty\n"
                        "   - Event type: GuardDuty Finding\n"
                        "   - Add condition: severity >= 7.0\n"
                        "5. Select targets:\n"
                        "   - SNS topic (for notifications)\n"
                        "   - Lambda function (for automated response)\n"
                        "   - Step Functions (for workflows)\n"
                        "6. Click 'Create'\n"
                        "7. Repeat for other security services\n\n"
                        "Recommended target types:\n"
                        "SNS Topics:\n"
                        "- Email notifications to security team\n"
                        "- SMS for critical alerts\n"
                        "- Integration with PagerDuty/Slack\n\n"
                        "Lambda Functions:\n"
                        "- Automated remediation\n"
                        "- Ticket creation in JIRA/ServiceNow\n"
                        "- Custom notification formatting\n\n"
                        "SQS Queues:\n"
                        "- Buffering for processing\n"
                        "- Integration with external systems\n\n"
                        "Step Functions:\n"
                        "- Complex remediation workflows\n"
                        "- Approval processes\n\n"
                        "Best practices:\n"
                        "- Use descriptive rule names\n"
                        "- Filter events by severity\n"
                        "- Configure multiple targets for redundancy\n"
                        "- Test rules with sample events\n"
                        "- Monitor rule invocation metrics\n"
                        "- Use dead-letter queues for failed invocations\n"
                        "- Document response procedures\n"
                        "- Regularly review and update rules\n"
                        "- Use tags for rule organization\n"
                        "- Implement rate limiting for high-volume events\n\n"
                        "Additional security event patterns:\n"
                        "Root account usage:\n"
                        '{"source": ["aws.signin"], "detail": {"userIdentity": {"type": ["Root"]}}}\n\n'
                        "Console sign-in failures:\n"
                        '{"source": ["aws.signin"], "detail": {"eventName": ["ConsoleLogin"], "errorCode": ["Failed"]}}\n\n'
                        "S3 bucket policy changes:\n"
                        '{"source": ["aws.s3"], "detail": {"eventName": ["PutBucketPolicy", "DeleteBucketPolicy"]}}\n\n'
                        "IAM policy changes:\n"
                        '{"source": ["aws.iam"], "detail": {"eventName": ["CreatePolicy", "DeletePolicy", "AttachUserPolicy"]}}\n\n'
                        "Security group changes:\n"
                        '{"source": ["aws.ec2"], "detail": {"eventName": ["AuthorizeSecurityGroupIngress", "RevokeSecurityGroupIngress"]}}'
                    ),
                    evidence=evidence
                )
                result.add_finding(finding)

                result.score = score_points
                result.passed = score_points >= 70  # Require 70% coverage for pass
                result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

                self.logger.warning(
                    "eventbridge_rules_incomplete",
                    issues=issues,
                    score=score_points
                )
            else:
                # All critical event sources have rules with targets
                result.score = 100.0
                result.passed = True
                result.status = TestStatus.PASSED

                self.logger.info(
                    "eventbridge_rules_complete",
                    total_rules=len(rules)
                )

            # Add metadata
            result.metadata = {
                "total_rules": len(rules),
                "critical_sources": len(self.CRITICAL_EVENT_SOURCES),
                "sources_covered": sum(1 for s in sources_covered.values() if s["has_rule"] and s["has_targets"]),
                "sources_partial": sum(1 for s in sources_covered.values() if s["has_rule"] and not s["has_targets"]),
                "sources_missing": sum(1 for s in sources_covered.values() if not s["has_rule"]),
                "security_score": score_points,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "eventbridge_rules_test_completed",
                total_rules=len(rules),
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("eventbridge_rules_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("eventbridge_rules_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_eventbridge_rules_test(connector: AWSConnector) -> TestResult:
    """Run EventBridge security rules compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_eventbridge_rules_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = EventBridgeRulesTest(connector)
    return test.execute()

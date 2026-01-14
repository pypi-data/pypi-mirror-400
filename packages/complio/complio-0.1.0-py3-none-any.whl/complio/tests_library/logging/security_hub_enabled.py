"""
AWS Security Hub enabled compliance test.

Checks that AWS Security Hub is enabled for centralized security monitoring.

ISO 27001 Control: A.8.16 - Monitoring activities
Requirement: Security Hub should be enabled for aggregated security findings

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.logging.security_hub_enabled import SecurityHubEnabledTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = SecurityHubEnabledTest(connector)
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


class SecurityHubEnabledTest(ComplianceTest):
    """Test for AWS Security Hub enabled compliance.

    Verifies that AWS Security Hub is properly enabled:
    - Security Hub should be enabled
    - Security standards should be enabled (CIS, AWS Foundational Security)
    - Product integrations should be enabled (GuardDuty, Config, etc.)
    - Findings should be aggregated and actionable

    Compliance Requirements:
        - Security Hub enabled in region
        - At least one security standard enabled
        - Product integrations enabled
        - Findings aggregation configured

    Scoring:
        - 100% if Security Hub fully enabled with standards
        - Partial score for basic enablement
        - 0% if Security Hub not enabled

    Example:
        >>> test = SecurityHubEnabledTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize Security Hub enabled test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="security_hub_enabled",
            test_name="AWS Security Hub Enabled Check",
            description="Verify AWS Security Hub is enabled for centralized security monitoring",
            control_id="A.8.16",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute Security Hub enabled compliance test.

        Returns:
            TestResult with findings if Security Hub is not properly enabled

        Example:
            >>> test = SecurityHubEnabledTest(connector)
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
            # Get Security Hub client
            securityhub_client = self.connector.get_client("securityhub")

            # Check if Security Hub is enabled
            self.logger.info("checking_security_hub_status")

            try:
                hub_response = securityhub_client.describe_hub()
                hub_arn = hub_response.get("HubArn", "")
                subscribed_at = hub_response.get("SubscribedAt", "")
                auto_enable_controls = hub_response.get("AutoEnableControls", False)

                security_hub_enabled = True
                result.resources_scanned += 1

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                if error_code == "InvalidAccessException":
                    security_hub_enabled = False
                    self.logger.warning("security_hub_not_enabled")
                else:
                    raise

            if not security_hub_enabled:
                # Create finding for Security Hub not enabled
                finding = self.create_finding(
                    resource_id="security-hub",
                    resource_type="security_hub",
                    severity=Severity.HIGH,
                    title="AWS Security Hub not enabled",
                    description="AWS Security Hub is not enabled in this region. Security Hub provides a "
                                "comprehensive view of security alerts and compliance status across AWS accounts. "
                                "It aggregates findings from GuardDuty, Inspector, Macie, IAM Access Analyzer, "
                                "AWS Firewall Manager, and third-party products. Without Security Hub, security "
                                "findings are dispersed and difficult to manage. ISO 27001 A.8.16 requires "
                                "centralized monitoring of security events.",
                    remediation=(
                        "Enable AWS Security Hub in this region:\n\n"
                        "1. Enable Security Hub:\n"
                        "aws securityhub enable-security-hub\n\n"
                        "2. Enable security standards:\n"
                        "# AWS Foundational Security Best Practices\n"
                        "aws securityhub batch-enable-standards \\\n"
                        "  --standards-subscription-requests \\\n"
                        "    StandardsArn=arn:aws:securityhub:REGION::standards/aws-foundational-security-best-practices/v/1.0.0\n\n"
                        "# CIS AWS Foundations Benchmark\n"
                        "aws securityhub batch-enable-standards \\\n"
                        "  --standards-subscription-requests \\\n"
                        "    StandardsArn=arn:aws:securityhub:REGION::standards/cis-aws-foundations-benchmark/v/1.2.0\n\n"
                        "# PCI-DSS (if applicable)\n"
                        "aws securityhub batch-enable-standards \\\n"
                        "  --standards-subscription-requests \\\n"
                        "    StandardsArn=arn:aws:securityhub:REGION::standards/pci-dss/v/3.2.1\n\n"
                        "3. Enable product integrations:\n"
                        "# GuardDuty\n"
                        "aws securityhub enable-import-findings-for-product \\\n"
                        "  --product-arn arn:aws:securityhub:REGION::product/aws/guardduty\n\n"
                        "# AWS Config\n"
                        "aws securityhub enable-import-findings-for-product \\\n"
                        "  --product-arn arn:aws:securityhub:REGION::product/aws/config\n\n"
                        "# IAM Access Analyzer\n"
                        "aws securityhub enable-import-findings-for-product \\\n"
                        "  --product-arn arn:aws:securityhub:REGION::product/aws/access-analyzer\n\n"
                        "4. Configure findings aggregation (for multi-region):\n"
                        "aws securityhub create-finding-aggregator \\\n"
                        "  --region-linking-mode ALL_REGIONS\n\n"
                        "Or use AWS Console:\n"
                        "1. Go to AWS Security Hub console\n"
                        "2. Click 'Enable Security Hub'\n"
                        "3. Select security standards to enable:\n"
                        "   - AWS Foundational Security Best Practices (recommended)\n"
                        "   - CIS AWS Foundations Benchmark\n"
                        "   - PCI-DSS (if applicable)\n"
                        "4. Enable product integrations:\n"
                        "   - Go to Integrations\n"
                        "   - Enable AWS services (GuardDuty, Config, IAM Access Analyzer)\n"
                        "   - Enable third-party products if needed\n"
                        "5. Configure settings:\n"
                        "   - Enable auto-enable for new controls\n"
                        "   - Set up finding aggregation for multi-region\n\n"
                        "Best practices:\n"
                        "- Enable Security Hub in all regions\n"
                        "- Use AWS Organizations for multi-account setup\n"
                        "- Enable delegated administrator account\n"
                        "- Configure automated remediation with EventBridge + Lambda\n"
                        "- Set up custom insights for your environment\n"
                        "- Integrate with SIEM tools (Splunk, etc.)\n"
                        "- Review findings daily/weekly\n"
                        "- Suppress accepted risks with proper documentation\n"
                        "- Use Security Hub automation rules\n"
                        "- Export findings to S3 for long-term analysis\n\n"
                        "Security standards comparison:\n"
                        "AWS Foundational Security Best Practices:\n"
                        "- 200+ automated checks\n"
                        "- AWS best practices\n"
                        "- Continuously updated by AWS\n"
                        "- Recommended for all accounts\n\n"
                        "CIS AWS Foundations Benchmark:\n"
                        "- Industry standard\n"
                        "- Required for compliance certifications\n"
                        "- Periodic updates\n"
                        "- Focus on foundational security\n\n"
                        "PCI-DSS:\n"
                        "- Required for payment card processing\n"
                        "- Specific compliance requirements\n"
                        "- More restrictive controls\n\n"
                        "Key integrations:\n"
                        "- GuardDuty: Threat detection\n"
                        "- Inspector: Vulnerability scanning\n"
                        "- Macie: Data security\n"
                        "- Config: Configuration compliance\n"
                        "- IAM Access Analyzer: Permissions analysis\n"
                        "- Firewall Manager: Network security\n"
                        "- Systems Manager: Patch compliance\n\n"
                        "Cost considerations:\n"
                        "- Free 30-day trial\n"
                        "- Pricing:\n"
                        "  • Security checks: $0.0010 per check\n"
                        "  • Finding ingestion: $0.00003 per finding\n"
                        "- Typical cost: $20-50 per account per month\n"
                        "- Consolidated billing with Organizations"
                    ),
                    evidence=None
                )
                result.add_finding(finding)
                result.score = 0.0
                result.passed = False
                result.status = TestStatus.FAILED
                result.metadata = {
                    "security_hub_enabled": False,
                    "message": "Security Hub not enabled in region"
                }
                return result

            # Security Hub is enabled, check configuration
            issues = []
            severity = Severity.MEDIUM
            score_points = 0  # Out of 100

            # Hub is enabled (40 points)
            score_points += 40

            # Check enabled standards (30 points)
            self.logger.info("checking_enabled_standards")
            standards_response = securityhub_client.get_enabled_standards()
            enabled_standards = standards_response.get("StandardsSubscriptions", [])

            active_standards = [
                s for s in enabled_standards
                if s.get("StandardsStatus") == "READY"
            ]

            if len(active_standards) > 0:
                score_points += 30
            else:
                issues.append("No security standards enabled")
                severity = Severity.HIGH

            # Check product integrations (20 points)
            self.logger.info("checking_product_integrations")
            try:
                integrations_response = securityhub_client.list_enabled_products_for_import()
                enabled_products = integrations_response.get("ProductSubscriptions", [])

                if len(enabled_products) > 0:
                    score_points += 20
                else:
                    issues.append("No product integrations enabled")
            except ClientError:
                issues.append("Could not check product integrations")

            # Check auto-enable controls (10 points - bonus)
            if auto_enable_controls:
                score_points += 10

            # Create evidence
            evidence = self.create_evidence(
                resource_id=hub_arn,
                resource_type="security_hub",
                data={
                    "hub_arn": hub_arn,
                    "subscribed_at": subscribed_at,
                    "auto_enable_controls": auto_enable_controls,
                    "enabled_standards_count": len(active_standards),
                    "enabled_products_count": len(enabled_products) if 'enabled_products' in locals() else 0,
                    "has_issues": len(issues) > 0,
                    "issues": issues,
                    "security_score": score_points,
                }
            )
            result.add_evidence(evidence)

            if len(issues) > 0:
                # Create finding for Security Hub configuration issues
                finding = self.create_finding(
                    resource_id=hub_arn,
                    resource_type="security_hub",
                    severity=severity,
                    title="AWS Security Hub has configuration issues",
                    description=f"AWS Security Hub is enabled but has configuration issues: {'; '.join(issues)}. "
                                "Security Hub should have security standards enabled and product integrations "
                                "configured to provide comprehensive security monitoring. ISO 27001 A.8.16 requires "
                                "effective monitoring and correlation of security events.",
                    remediation=(
                        "Improve Security Hub configuration:\n\n"
                        "1. Enable security standards:\n"
                        "aws securityhub batch-enable-standards \\\n"
                        "  --standards-subscription-requests \\\n"
                        "    StandardsArn=arn:aws:securityhub:REGION::standards/aws-foundational-security-best-practices/v/1.0.0 \\\n"
                        "    StandardsArn=arn:aws:securityhub:REGION::standards/cis-aws-foundations-benchmark/v/1.2.0\n\n"
                        "2. Enable product integrations:\n"
                        "aws securityhub enable-import-findings-for-product \\\n"
                        "  --product-arn arn:aws:securityhub:REGION::product/aws/guardduty\n\n"
                        "aws securityhub enable-import-findings-for-product \\\n"
                        "  --product-arn arn:aws:securityhub:REGION::product/aws/config\n\n"
                        "3. Enable auto-enable controls:\n"
                        "aws securityhub update-security-hub-configuration \\\n"
                        "  --auto-enable-controls\n\n"
                        "Or use AWS Console:\n"
                        "1. Go to Security Hub console\n"
                        "2. Click 'Security standards'\n"
                        "3. Enable recommended standards\n"
                        "4. Go to 'Integrations'\n"
                        "5. Enable AWS service integrations\n"
                        "6. Go to 'Settings'\n"
                        "7. Enable 'Auto-enable new controls'\n\n"
                        "Monitor and respond:\n"
                        "- Review critical/high findings daily\n"
                        "- Create EventBridge rules for automated responses\n"
                        "- Use custom insights for trending\n"
                        "- Suppress accepted risks with notes\n"
                        "- Track compliance scores over time"
                    ),
                    evidence=evidence
                )
                result.add_finding(finding)

                result.score = score_points
                result.passed = score_points >= 80  # Require 80% for pass
                result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

                self.logger.warning(
                    "security_hub_has_issues",
                    hub_arn=hub_arn,
                    issues=issues,
                    score=score_points
                )
            else:
                # Security Hub is properly configured
                result.score = 100.0
                result.passed = True
                result.status = TestStatus.PASSED

                self.logger.info(
                    "security_hub_properly_configured",
                    hub_arn=hub_arn
                )

            # Add metadata
            result.metadata = {
                "security_hub_enabled": True,
                "hub_arn": hub_arn,
                "enabled_standards": len(active_standards),
                "enabled_products": len(enabled_products) if 'enabled_products' in locals() else 0,
                "auto_enable_controls": auto_enable_controls,
                "security_score": score_points,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "security_hub_enabled_test_completed",
                hub_arn=hub_arn,
                enabled_standards=len(active_standards),
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("security_hub_enabled_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("security_hub_enabled_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_security_hub_enabled_test(connector: AWSConnector) -> TestResult:
    """Run AWS Security Hub enabled compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_security_hub_enabled_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = SecurityHubEnabledTest(connector)
    return test.execute()

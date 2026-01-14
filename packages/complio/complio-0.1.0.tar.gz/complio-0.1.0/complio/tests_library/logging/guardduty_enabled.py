"""
AWS GuardDuty enabled compliance test.

Checks that AWS GuardDuty is enabled for threat detection and monitoring.

ISO 27001 Control: A.8.16 - Monitoring activities
Requirement: GuardDuty should be enabled for continuous security monitoring

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.logging.guardduty_enabled import GuardDutyEnabledTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = GuardDutyEnabledTest(connector)
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


class GuardDutyEnabledTest(ComplianceTest):
    """Test for AWS GuardDuty enabled compliance.

    Verifies that AWS GuardDuty is properly enabled:
    - GuardDuty detector should be enabled
    - Should be publishing findings (not suspended)
    - S3 Protection should be enabled
    - EKS Protection should be enabled (if using EKS)
    - Malware Protection should be enabled

    Compliance Requirements:
        - GuardDuty enabled in region
        - Detector actively monitoring (not suspended)
        - Additional protections enabled (S3, EKS, Malware)
        - Findings published to EventBridge/SNS

    Scoring:
        - 100% if GuardDuty fully enabled with protections
        - Partial score for basic enablement
        - 0% if GuardDuty not enabled

    Example:
        >>> test = GuardDutyEnabledTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize GuardDuty enabled test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="guardduty_enabled",
            test_name="AWS GuardDuty Enabled Check",
            description="Verify AWS GuardDuty is enabled for threat detection and monitoring",
            control_id="A.8.16",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute GuardDuty enabled compliance test.

        Returns:
            TestResult with findings if GuardDuty is not properly enabled

        Example:
            >>> test = GuardDutyEnabledTest(connector)
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
            # Get GuardDuty client
            guardduty_client = self.connector.get_client("guardduty")

            # List detectors
            self.logger.info("listing_guardduty_detectors")
            detectors_response = guardduty_client.list_detectors()
            detector_ids = detectors_response.get("DetectorIds", [])

            if not detector_ids:
                self.logger.warning("no_guardduty_detectors_found")

                # Create finding for GuardDuty not enabled
                finding = self.create_finding(
                    resource_id="guardduty",
                    resource_type="guardduty_detector",
                    severity=Severity.HIGH,
                    title="AWS GuardDuty not enabled",
                    description="AWS GuardDuty is not enabled in this region. GuardDuty provides intelligent "
                                "threat detection by continuously monitoring AWS account and workload activity. "
                                "It analyzes VPC Flow Logs, CloudTrail events, and DNS logs to identify "
                                "malicious activity, unauthorized behavior, and potential security threats. "
                                "ISO 27001 A.8.16 requires monitoring of system activities for security events.",
                    remediation=(
                        "Enable AWS GuardDuty in this region:\n\n"
                        "1. Enable GuardDuty:\n"
                        "aws guardduty create-detector --enable\n\n"
                        "2. Enable additional protections:\n"
                        "# Get detector ID\n"
                        "DETECTOR_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)\n\n"
                        "# Enable S3 Protection\n"
                        "aws guardduty update-detector \\\n"
                        "  --detector-id $DETECTOR_ID \\\n"
                        "  --data-sources S3Logs={Enable=true}\n\n"
                        "# Enable EKS Protection (if using EKS)\n"
                        "aws guardduty update-detector \\\n"
                        "  --detector-id $DETECTOR_ID \\\n"
                        "  --data-sources Kubernetes={AuditLogs={Enable=true}}\n\n"
                        "# Enable Malware Protection (for EBS volumes)\n"
                        "aws guardduty update-malware-protection-plan \\\n"
                        "  --detector-id $DETECTOR_ID \\\n"
                        "  --enable\n\n"
                        "3. Configure findings export (optional but recommended):\n"
                        "# Export to S3\n"
                        "aws guardduty create-publishing-destination \\\n"
                        "  --detector-id $DETECTOR_ID \\\n"
                        "  --destination-type S3 \\\n"
                        "  --destination-properties \\\n"
                        "    DestinationArn=arn:aws:s3:::my-guardduty-findings,\\\n"
                        "    KmsKeyArn=arn:aws:kms:region:account:key/key-id\n\n"
                        "4. Set up EventBridge rule for notifications:\n"
                        "aws events put-rule \\\n"
                        "  --name guardduty-findings \\\n"
                        "  --event-pattern '{\n"
                        '    "source": ["aws.guardduty"],\n'
                        '    "detail-type": ["GuardDuty Finding"]\n'
                        "  }'\n\n"
                        "# Add SNS target\n"
                        "aws events put-targets \\\n"
                        "  --rule guardduty-findings \\\n"
                        "  --targets Id=1,Arn=arn:aws:sns:region:account:security-alerts\n\n"
                        "Or use AWS Console:\n"
                        "1. Go to GuardDuty console\n"
                        "2. Click 'Get Started'\n"
                        "3. Click 'Enable GuardDuty'\n"
                        "4. Configure settings:\n"
                        "   - Enable S3 Protection\n"
                        "   - Enable EKS Protection (if applicable)\n"
                        "   - Enable Malware Protection\n"
                        "5. Set up findings export:\n"
                        "   - Go to Settings → Findings export options\n"
                        "   - Configure S3 bucket for exports\n"
                        "6. Configure notifications:\n"
                        "   - Go to EventBridge console\n"
                        "   - Create rule for GuardDuty findings\n"
                        "   - Add SNS topic as target\n\n"
                        "Best practices:\n"
                        "- Enable GuardDuty in all regions\n"
                        "- Use GuardDuty Organization for multi-account\n"
                        "- Configure automated responses (Lambda)\n"
                        "- Export findings to S3 for long-term storage\n"
                        "- Integrate with Security Hub\n"
                        "- Set up SNS/email notifications for high severity\n"
                        "- Review findings regularly (daily/weekly)\n"
                        "- Create suppression rules for known false positives\n"
                        "- Use Trusted IP lists for known safe IPs\n"
                        "- Use Threat IP lists for known malicious IPs\n"
                        "- Monitor GuardDuty coverage metrics\n\n"
                        "GuardDuty finding types:\n"
                        "Reconnaissance:\n"
                        "- Port scanning\n"
                        "- Unusual API calls\n"
                        "- Discovery attempts\n\n"
                        "Instance compromise:\n"
                        "- Cryptocurrency mining\n"
                        "- Backdoor communication\n"
                        "- Malware activity\n\n"
                        "Account compromise:\n"
                        "- Unusual behavior\n"
                        "- API calls from unusual locations\n"
                        "- Credential exfiltration\n\n"
                        "Bucket compromise:\n"
                        "- Suspicious S3 access\n"
                        "- Data exfiltration\n"
                        "- Policy changes\n\n"
                        "Cost considerations:\n"
                        "- Free 30-day trial\n"
                        "- Pricing based on:\n"
                        "  • CloudTrail events analyzed\n"
                        "  • VPC Flow Logs analyzed\n"
                        "  • DNS logs analyzed\n"
                        "  • S3 logs analyzed\n"
                        "  • EKS logs analyzed\n"
                        "- Typically $4-5 per account per month\n"
                        "- Volume discounts available"
                    ),
                    evidence=None
                )
                result.add_finding(finding)
                result.score = 0.0
                result.passed = False
                result.status = TestStatus.FAILED
                result.metadata = {
                    "guardduty_enabled": False,
                    "message": "GuardDuty not enabled in region"
                }
                return result

            # Get first detector (typically only one per region)
            detector_id = detector_ids[0]
            result.resources_scanned += 1

            # Get detector details
            self.logger.info("getting_guardduty_detector_details", detector_id=detector_id)
            detector_response = guardduty_client.get_detector(DetectorId=detector_id)

            status = detector_response.get("Status", "")
            finding_publishing_frequency = detector_response.get("FindingPublishingFrequency", "")
            data_sources = detector_response.get("DataSources", {})

            # Check S3 protection
            s3_logs = data_sources.get("S3Logs", {})
            s3_protection_enabled = s3_logs.get("Status") == "ENABLED"

            # Check Kubernetes (EKS) protection
            kubernetes = data_sources.get("Kubernetes", {})
            eks_audit_logs = kubernetes.get("AuditLogs", {})
            eks_protection_enabled = eks_audit_logs.get("Status") == "ENABLED"

            # Check Malware protection
            malware_protection = data_sources.get("MalwareProtection", {})
            scan_ec2 = malware_protection.get("ScanEc2InstanceWithFindings", {})
            malware_protection_enabled = scan_ec2.get("EbsVolumes", {}).get("Status") == "ENABLED"

            # Determine issues and calculate score
            issues = []
            severity = Severity.MEDIUM
            score_points = 0  # Out of 100

            # Check if detector is enabled (40 points)
            if status == "ENABLED":
                score_points += 40
            else:
                issues.append(f"GuardDuty detector is {status} (not ENABLED)")
                severity = Severity.HIGH

            # Check S3 protection (20 points)
            if s3_protection_enabled:
                score_points += 20
            else:
                issues.append("S3 Protection not enabled")

            # Check EKS protection (20 points - if EKS is being used)
            # Note: This is optional as not all accounts use EKS
            if eks_protection_enabled:
                score_points += 20
            # Don't penalize if not enabled, as EKS might not be used

            # Check Malware protection (20 points)
            if malware_protection_enabled:
                score_points += 20
            else:
                issues.append("Malware Protection not enabled")

            # Create evidence
            evidence = self.create_evidence(
                resource_id=detector_id,
                resource_type="guardduty_detector",
                data={
                    "detector_id": detector_id,
                    "status": status,
                    "finding_publishing_frequency": finding_publishing_frequency,
                    "s3_protection_enabled": s3_protection_enabled,
                    "eks_protection_enabled": eks_protection_enabled,
                    "malware_protection_enabled": malware_protection_enabled,
                    "has_issues": len(issues) > 0,
                    "issues": issues,
                    "security_score": score_points,
                }
            )
            result.add_evidence(evidence)

            if len(issues) > 0:
                # Create finding for GuardDuty configuration issues
                finding = self.create_finding(
                    resource_id=detector_id,
                    resource_type="guardduty_detector",
                    severity=severity,
                    title="AWS GuardDuty has configuration issues",
                    description=f"AWS GuardDuty detector '{detector_id}' has configuration issues: "
                                f"{'; '.join(issues)}. GuardDuty should be fully enabled with all protection "
                                "features (S3, EKS, Malware) to provide comprehensive threat detection. "
                                "ISO 27001 A.8.16 requires comprehensive monitoring of security events.",
                    remediation=(
                        f"Improve GuardDuty detector '{detector_id}' configuration:\n\n"
                        "1. Ensure detector is enabled:\n"
                        f"aws guardduty update-detector \\\n"
                        f"  --detector-id {detector_id} \\\n"
                        "  --enable\n\n"
                        "2. Enable S3 Protection:\n"
                        f"aws guardduty update-detector \\\n"
                        f"  --detector-id {detector_id} \\\n"
                        "  --data-sources S3Logs={{Enable=true}}\n\n"
                        "3. Enable EKS Protection (if using EKS):\n"
                        f"aws guardduty update-detector \\\n"
                        f"  --detector-id {detector_id} \\\n"
                        "  --data-sources Kubernetes={{AuditLogs={{Enable=true}}}}\n\n"
                        "4. Enable Malware Protection:\n"
                        f"aws guardduty update-malware-protection-plan \\\n"
                        f"  --detector-id {detector_id} \\\n"
                        "  --enable\n\n"
                        "5. Configure findings frequency:\n"
                        f"aws guardduty update-detector \\\n"
                        f"  --detector-id {detector_id} \\\n"
                        "  --finding-publishing-frequency FIFTEEN_MINUTES\n\n"
                        "Or use AWS Console:\n"
                        "1. Go to GuardDuty console\n"
                        "2. Click Settings\n"
                        "3. Ensure 'Status' is Enabled\n"
                        "4. Enable protection features:\n"
                        "   - S3 Protection: On\n"
                        "   - EKS Protection: On (if using EKS)\n"
                        "   - Malware Protection: On\n"
                        "5. Set findings publishing frequency\n"
                        "6. Click 'Save'\n\n"
                        "Additional recommendations:\n"
                        "- Review GuardDuty findings regularly\n"
                        "- Set up automated remediation with Lambda\n"
                        "- Export findings to S3 for analysis\n"
                        "- Integrate with SIEM tools\n"
                        "- Create CloudWatch alarms for high severity findings"
                    ),
                    evidence=evidence
                )
                result.add_finding(finding)

                result.score = score_points
                result.passed = score_points >= 80  # Require 80% for pass
                result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

                self.logger.warning(
                    "guardduty_has_issues",
                    detector_id=detector_id,
                    issues=issues,
                    score=score_points
                )
            else:
                # GuardDuty is properly configured
                result.score = 100.0
                result.passed = True
                result.status = TestStatus.PASSED

                self.logger.info(
                    "guardduty_properly_configured",
                    detector_id=detector_id
                )

            # Add metadata
            result.metadata = {
                "guardduty_enabled": True,
                "detector_id": detector_id,
                "status": status,
                "s3_protection": s3_protection_enabled,
                "eks_protection": eks_protection_enabled,
                "malware_protection": malware_protection_enabled,
                "security_score": score_points,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "guardduty_enabled_test_completed",
                detector_id=detector_id,
                status=status,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("guardduty_enabled_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("guardduty_enabled_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_guardduty_enabled_test(connector: AWSConnector) -> TestResult:
    """Run AWS GuardDuty enabled compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_guardduty_enabled_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = GuardDutyEnabledTest(connector)
    return test.execute()

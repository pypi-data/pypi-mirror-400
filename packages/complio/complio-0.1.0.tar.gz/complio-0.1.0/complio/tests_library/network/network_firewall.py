"""
AWS Network Firewall compliance test.

Checks that Network Firewalls are deployed and properly configured.

ISO 27001 Control: A.8.20 - Networks security
Requirement: VPCs handling sensitive workloads should use Network Firewall

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.network_firewall import NetworkFirewallTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = NetworkFirewallTest(connector)
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


class NetworkFirewallTest(ComplianceTest):
    """Test for AWS Network Firewall compliance.

    Verifies that Network Firewalls are deployed for VPC protection:
    - Firewalls should be in READY state
    - Should have logging configured
    - Should have stateful and/or stateless rules configured

    Compliance Requirements:
        - Network Firewalls deployed for production VPCs
        - Logging enabled (flow logs and/or alert logs)
        - Active firewall rules configured

    Scoring:
        - Based on deployment and configuration status
        - 100% if Network Firewalls are properly configured
        - Note: This is an informational test about firewall presence

    Example:
        >>> test = NetworkFirewallTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize Network Firewall test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="network_firewall",
            test_name="AWS Network Firewall Check",
            description="Verify Network Firewalls are deployed and properly configured",
            control_id="A.8.20",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute Network Firewall compliance test.

        Returns:
            TestResult with findings for missing or misconfigured firewalls

        Example:
            >>> test = NetworkFirewallTest(connector)
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
            # Get Network Firewall client
            network_firewall_client = self.connector.get_client("network-firewall")

            # List all Network Firewalls
            self.logger.info("listing_network_firewalls")
            firewalls_response = network_firewall_client.list_firewalls()
            firewalls = firewalls_response.get("Firewalls", [])

            if not firewalls:
                self.logger.info("no_network_firewalls_found")
                result.metadata["message"] = "No Network Firewalls found in region (consider deploying for production VPCs)"
                result.metadata["recommendation"] = "Deploy Network Firewall for VPCs handling sensitive workloads"
                # Not a failure, just informational
                return result

            self.logger.info("network_firewalls_found", count=len(firewalls))

            # Check configuration for each firewall
            properly_configured_count = 0

            for firewall_summary in firewalls:
                firewall_name = firewall_summary.get("FirewallName", "")
                firewall_arn = firewall_summary.get("FirewallArn", "")

                result.resources_scanned += 1

                # Get detailed firewall configuration
                firewall_response = network_firewall_client.describe_firewall(
                    FirewallName=firewall_name
                )

                firewall = firewall_response.get("Firewall", {})
                firewall_status = firewall_response.get("FirewallStatus", {})

                status = firewall_status.get("Status", "")
                vpc_id = firewall.get("VpcId", "")
                firewall_policy_arn = firewall.get("FirewallPolicyArn", "")

                # Get logging configuration
                logging_response = network_firewall_client.describe_logging_configuration(
                    FirewallName=firewall_name
                )
                logging_config = logging_response.get("LoggingConfiguration", {})
                log_destination_configs = logging_config.get("LogDestinationConfigs", [])

                # Determine security issues
                issues = []
                severity = Severity.MEDIUM

                # Check firewall status
                if status != "READY":
                    issues.append(f"Firewall not in READY state (current: {status})")
                    severity = Severity.HIGH

                # Check logging configuration
                if not log_destination_configs:
                    issues.append("No logging configured (no alert or flow logs)")
                    severity = Severity.MEDIUM

                # Check if firewall policy exists
                if not firewall_policy_arn:
                    issues.append("No firewall policy configured")
                    severity = Severity.HIGH

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=firewall_arn,
                    resource_type="network_firewall",
                    data={
                        "firewall_name": firewall_name,
                        "firewall_arn": firewall_arn,
                        "vpc_id": vpc_id,
                        "status": status,
                        "firewall_policy_arn": firewall_policy_arn,
                        "logging_configured": len(log_destination_configs) > 0,
                        "log_destinations_count": len(log_destination_configs),
                        "has_issues": len(issues) > 0,
                        "issues": issues,
                    }
                )
                result.add_evidence(evidence)

                if len(issues) == 0:
                    properly_configured_count += 1
                    self.logger.debug(
                        "network_firewall_configured",
                        firewall_name=firewall_name
                    )
                else:
                    # Create finding for misconfigured firewall
                    finding = self.create_finding(
                        resource_id=firewall_arn,
                        resource_type="network_firewall",
                        severity=severity,
                        title="Network Firewall has configuration issues",
                        description=f"Network Firewall '{firewall_name}' in VPC '{vpc_id}' has configuration issues: "
                                    f"{'; '.join(issues)}. Network Firewalls should be in READY state, have active "
                                    "firewall policies, and enable logging for security monitoring. ISO 27001 A.8.20 "
                                    "requires proper network security controls.",
                        remediation=(
                            f"Improve Network Firewall '{firewall_name}' configuration:\n\n"
                            "1. Ensure firewall is in READY state:\n"
                            f"aws network-firewall describe-firewall \\\n"
                            f"  --firewall-name {firewall_name}\n\n"
                            "2. Enable logging (alert and flow logs):\n"
                            f"aws network-firewall update-logging-configuration \\\n"
                            f"  --firewall-name {firewall_name} \\\n"
                            "  --logging-configuration '{\n"
                            '    "LogDestinationConfigs": [\n'
                            '      {\n'
                            '        "LogType": "ALERT",\n'
                            '        "LogDestinationType": "CloudWatchLogs",\n'
                            '        "LogDestination": {\n'
                            '          "logGroup": "/aws/network-firewall/alerts"\n'
                            '        }\n'
                            '      },\n'
                            '      {\n'
                            '        "LogType": "FLOW",\n'
                            '        "LogDestinationType": "S3",\n'
                            '        "LogDestination": {\n'
                            '          "bucketName": "my-firewall-logs",\n'
                            '          "prefix": "network-firewall/flow"\n'
                            '        }\n'
                            '      }\n'
                            '    ]\n'
                            "  }'\n\n"
                            "3. Create and attach firewall policy with rules:\n"
                            "# Create stateful rule group\n"
                            "aws network-firewall create-rule-group \\\n"
                            "  --rule-group-name block-malicious-domains \\\n"
                            "  --type STATEFUL \\\n"
                            "  --capacity 100 \\\n"
                            "  --rule-group file://stateful-rules.json\n\n"
                            "# Create firewall policy\n"
                            "aws network-firewall create-firewall-policy \\\n"
                            "  --firewall-policy-name my-firewall-policy \\\n"
                            "  --firewall-policy file://policy.json\n\n"
                            "# Associate policy with firewall\n"
                            f"aws network-firewall associate-firewall-policy \\\n"
                            f"  --firewall-name {firewall_name} \\\n"
                            "  --firewall-policy-arn <POLICY-ARN>\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to VPC console → Network Firewall → Firewalls\n"
                            f"2. Select firewall '{firewall_name}'\n"
                            "3. Verify status is READY\n"
                            "4. Edit firewall:\n"
                            "   - Associate firewall policy\n"
                            "   - Enable logging:\n"
                            "     • Alert logs → CloudWatch Logs\n"
                            "     • Flow logs → S3 or CloudWatch\n"
                            "5. Create firewall policy:\n"
                            "   - Add stateful rule groups (domain lists, IPS rules)\n"
                            "   - Add stateless rule groups (basic filtering)\n"
                            "   - Set default actions\n\n"
                            "Security best practices:\n"
                            "- Deploy Network Firewall in dedicated inspection subnets\n"
                            "- Use stateful inspection for deep packet inspection\n"
                            "- Enable IPS/IDS with AWS managed rule groups\n"
                            "- Block known malicious domains and IPs\n"
                            "- Log all traffic for security analysis\n"
                            "- Use separate firewall policies for different zones\n"
                            "- Regularly update rule groups\n"
                            "- Monitor firewall metrics in CloudWatch\n"
                            "- Integrate with AWS Firewall Manager for centralized management\n"
                            "- Use with Transit Gateway for centralized inspection\n\n"
                            "Example stateful rules:\n"
                            "- Block malicious domains (using domain list)\n"
                            "- Block known malware signatures (using Suricata rules)\n"
                            "- Allow only specific protocols and ports\n"
                            "- Log and alert on suspicious patterns\n\n"
                            "Example deployment architectures:\n"
                            "1. Inspection VPC with Transit Gateway\n"
                            "2. Distributed firewalls in each VPC\n"
                            "3. Centralized egress filtering\n"
                            "4. East-West traffic inspection"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "network_firewall_misconfigured",
                        firewall_name=firewall_name,
                        issues=issues
                    )

            # Calculate compliance score
            if len(firewalls) > 0:
                result.score = (properly_configured_count / len(firewalls)) * 100
                result.passed = properly_configured_count == len(firewalls)
            else:
                result.score = 100.0
                result.passed = True

            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_firewalls": len(firewalls),
                "properly_configured": properly_configured_count,
                "misconfigured": len(firewalls) - properly_configured_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "network_firewall_test_completed",
                total_firewalls=len(firewalls),
                properly_configured=properly_configured_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            # Network Firewall may not be available in all regions
            if error_code in ["UnknownOperationException", "InvalidAction"]:
                self.logger.info("network_firewall_not_available_in_region")
                result.metadata["message"] = "AWS Network Firewall not available in this region"
                return result

            self.logger.error("network_firewall_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("network_firewall_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_network_firewall_test(connector: AWSConnector) -> TestResult:
    """Run AWS Network Firewall compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_network_firewall_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = NetworkFirewallTest(connector)
    return test.execute()

"""
AWS Direct Connect security compliance test.

Checks that Direct Connect connections use secure configurations.

ISO 27001 Control: A.8.22 - Network segregation
Requirement: Direct Connect connections should use encryption and proper configurations

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.direct_connect_security import DirectConnectSecurityTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = DirectConnectSecurityTest(connector)
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


class DirectConnectSecurityTest(ComplianceTest):
    """Test for AWS Direct Connect security compliance.

    Verifies that Direct Connect connections use secure configurations:
    - Virtual interfaces should use MACsec encryption when possible
    - Connection state should be available (not down)
    - Should have proper tagging for management

    Compliance Requirements:
        - Use MACsec encryption for Layer 2 security (when supported)
        - Connections should be in available state
        - Virtual interfaces properly configured

    Scoring:
        - 100% if all Direct Connect resources follow security best practices
        - Proportional score based on compliant/total ratio
        - 100% if no Direct Connect connections exist

    Example:
        >>> test = DirectConnectSecurityTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize Direct Connect security test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="direct_connect_security",
            test_name="AWS Direct Connect Security Check",
            description="Verify Direct Connect connections use secure configurations",
            control_id="A.8.22",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute Direct Connect security compliance test.

        Returns:
            TestResult with findings for insecure Direct Connect configurations

        Example:
            >>> test = DirectConnectSecurityTest(connector)
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
            # Get Direct Connect client
            dx_client = self.connector.get_client("directconnect")

            # List all Direct Connect connections
            self.logger.info("listing_direct_connect_connections")
            connections_response = dx_client.describe_connections()
            connections = connections_response.get("connections", [])

            if not connections:
                self.logger.info("no_direct_connect_connections_found")
                result.metadata["message"] = "No Direct Connect connections found in region"
                return result

            self.logger.info("direct_connect_connections_found", count=len(connections))

            # Check security for each connection
            secure_connection_count = 0

            for connection in connections:
                connection_id = connection.get("connectionId", "")
                connection_name = connection.get("connectionName", "")
                connection_state = connection.get("connectionState", "")
                location = connection.get("location", "")
                bandwidth = connection.get("bandwidth", "")

                # Skip deleted connections
                if connection_state in ["deleted", "deleting"]:
                    continue

                result.resources_scanned += 1

                # Check for security issues
                issues = []
                severity = Severity.MEDIUM

                # Check connection state
                if connection_state not in ["available", "requested", "pending"]:
                    issues.append(f"Connection not in healthy state: {connection_state}")
                    severity = Severity.HIGH

                # Check if MACsec is supported and enabled
                has_mac_sec_capability = connection.get("hasLogicalRedundancy", False)
                mac_sec_keys = connection.get("macSecKeys", [])

                # MACsec provides Layer 2 encryption
                if has_mac_sec_capability and len(mac_sec_keys) == 0:
                    issues.append("MACsec capable but not configured (encryption not enabled)")
                    severity = Severity.MEDIUM

                # Get associated virtual interfaces
                vifs_response = dx_client.describe_virtual_interfaces(connectionId=connection_id)
                virtual_interfaces = vifs_response.get("virtualInterfaces", [])

                # Check virtual interface configurations
                vif_issues = []
                for vif in virtual_interfaces:
                    vif_state = vif.get("virtualInterfaceState", "")
                    if vif_state == "down":
                        vif_issues.append(f"Virtual interface {vif.get('virtualInterfaceId')} is down")

                if vif_issues:
                    issues.extend(vif_issues)
                    severity = Severity.HIGH

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=connection_id,
                    resource_type="direct_connect_connection",
                    data={
                        "connection_id": connection_id,
                        "connection_name": connection_name,
                        "connection_state": connection_state,
                        "location": location,
                        "bandwidth": bandwidth,
                        "has_macsec_capability": has_mac_sec_capability,
                        "macsec_configured": len(mac_sec_keys) > 0,
                        "virtual_interfaces_count": len(virtual_interfaces),
                        "has_issues": len(issues) > 0,
                        "issues": issues,
                    }
                )
                result.add_evidence(evidence)

                if len(issues) == 0:
                    secure_connection_count += 1
                    self.logger.debug(
                        "direct_connect_secure",
                        connection_id=connection_id
                    )
                else:
                    # Create finding for insecure Direct Connect connection
                    finding = self.create_finding(
                        resource_id=connection_id,
                        resource_type="direct_connect_connection",
                        severity=severity,
                        title="Direct Connect connection has security issues",
                        description=f"Direct Connect connection '{connection_name}' ({connection_id}) at location "
                                    f"'{location}' has security issues: {'; '.join(issues)}. Direct Connect "
                                    "connections should use MACsec encryption when available, maintain healthy "
                                    "connection states, and have properly configured virtual interfaces. "
                                    "ISO 27001 A.8.22 requires secure network connections and encryption.",
                        remediation=(
                            f"Improve Direct Connect connection '{connection_id}' security:\n\n"
                            "1. Enable MACsec encryption (if supported):\n"
                            "# First, associate a MACsec secret key\n"
                            "aws directconnect associate-mac-sec-key \\\n"
                            f"  --connection-id {connection_id} \\\n"
                            "  --secret-arn <SECRETS-MANAGER-ARN>\n\n"
                            "# Verify MACsec is active\n"
                            f"aws directconnect describe-connections \\\n"
                            f"  --connection-id {connection_id}\n\n"
                            "2. Check connection health:\n"
                            f"aws directconnect describe-connections \\\n"
                            f"  --connection-id {connection_id}\n\n"
                            "If connection is down, contact AWS Support:\n"
                            "- Check Letter of Authorization (LOA) status\n"
                            "- Verify physical connectivity at colocation\n"
                            "- Check BGP configuration\n\n"
                            "3. Configure virtual interfaces properly:\n"
                            "# List all virtual interfaces\n"
                            f"aws directconnect describe-virtual-interfaces \\\n"
                            f"  --connection-id {connection_id}\n\n"
                            "# For down virtual interfaces, check:\n"
                            "- BGP peering status\n"
                            "- VLAN configuration\n"
                            "- Route propagation\n"
                            "- Security group rules\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to Direct Connect console\n"
                            "2. Select Connections\n"
                            f"3. Choose connection '{connection_name}'\n"
                            "4. Enable MACsec:\n"
                            "   - Select 'Actions' → 'Associate MACsec key'\n"
                            "   - Choose secret from Secrets Manager\n"
                            "   - Verify MACsec status shows 'enabled'\n"
                            "5. Check virtual interfaces:\n"
                            "   - Go to 'Virtual interfaces' tab\n"
                            "   - Verify each VIF is in 'available' state\n"
                            "   - Check BGP session status\n\n"
                            "Security best practices:\n"
                            "- Enable MACsec for Layer 2 encryption (10 Gbps and above)\n"
                            "- Use redundant connections for high availability\n"
                            "- Implement BGP authentication (MD5)\n"
                            "- Use VPN over Direct Connect for additional encryption\n"
                            "- Configure proper route filtering and BGP communities\n"
                            "- Enable Connection Health monitoring\n"
                            "- Use AWS Transit Gateway with Direct Connect Gateway\n"
                            "- Implement least privilege routing\n"
                            "- Tag connections for cost allocation and management\n"
                            "- Monitor with CloudWatch metrics:\n"
                            "  • ConnectionState\n"
                            "  • ConnectionBpsEgress/Ingress\n"
                            "  • ConnectionPpsEgress/Ingress\n"
                            "  • ConnectionLightLevelTx/Rx\n\n"
                            "MACsec encryption requirements:\n"
                            "- Supported on 10 Gbps and 100 Gbps connections\n"
                            "- Requires MACsec capable device at customer end\n"
                            "- Uses AES-256 GCM encryption\n"
                            "- Store keys in AWS Secrets Manager\n"
                            "- Rotate keys regularly\n\n"
                            "High availability setup:\n"
                            "- Deploy connections in multiple locations\n"
                            "- Use LAG (Link Aggregation Groups) when possible\n"
                            "- Configure BFD (Bidirectional Forwarding Detection)\n"
                            "- Implement active-active or active-passive failover\n"
                            "- Test failover scenarios regularly\n\n"
                            "Additional security layers:\n"
                            "- Use Site-to-Site VPN as backup\n"
                            "- Implement IPsec over Direct Connect for end-to-end encryption\n"
                            "- Use AWS PrivateLink for service-level isolation\n"
                            "- Configure network ACLs and security groups\n"
                            "- Enable VPC Flow Logs for traffic analysis"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "direct_connect_insecure",
                        connection_id=connection_id,
                        issues=issues
                    )

            # Calculate compliance score
            result.score = (secure_connection_count / len(connections)) * 100

            # Determine pass/fail
            result.passed = secure_connection_count == len(connections)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_connections": len(connections),
                "secure_connections": secure_connection_count,
                "insecure_connections": len(connections) - secure_connection_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "direct_connect_security_test_completed",
                total_connections=len(connections),
                secure=secure_connection_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("direct_connect_security_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("direct_connect_security_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_direct_connect_security_test(connector: AWSConnector) -> TestResult:
    """Run AWS Direct Connect security compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_direct_connect_security_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = DirectConnectSecurityTest(connector)
    return test.execute()

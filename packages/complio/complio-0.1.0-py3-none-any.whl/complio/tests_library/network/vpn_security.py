"""
VPN connection security compliance test.

Checks that all VPN connections use secure configurations.

ISO 27001 Control: A.8.22 - Network segregation
Requirement: VPN connections must use secure encryption and tunnel configurations

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.vpn_security import VPNSecurityTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = VPNSecurityTest(connector)
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


class VPNSecurityTest(ComplianceTest):
    """Test for VPN connection security compliance.

    Verifies that all VPN connections use secure tunnel configurations
    including proper encryption and integrity algorithms.

    Compliance Requirements:
        - All VPN tunnels must be UP (active)
        - Use strong encryption (AES-256 recommended)
        - Use strong integrity algorithms (SHA-256 or better)
        - Use IKEv2 protocol when possible

    Scoring:
        - 100% if all VPN connections have secure configurations
        - Proportional score based on compliant/total ratio
        - 100% if no VPN connections exist

    Example:
        >>> test = VPNSecurityTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize VPN security test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="vpn_security",
            test_name="VPN Connection Security Check",
            description="Verify all VPN connections use secure tunnel configurations",
            control_id="A.8.22",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute VPN connection security compliance test.

        Returns:
            TestResult with findings for insecure VPN configurations

        Example:
            >>> test = VPNSecurityTest(connector)
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
            # Get EC2 client
            ec2_client = self.connector.get_client("ec2")

            # List all VPN connections
            self.logger.info("listing_vpn_connections")
            vpn_response = ec2_client.describe_vpn_connections()
            vpn_connections = vpn_response.get("VpnConnections", [])

            if not vpn_connections:
                self.logger.info("no_vpn_connections_found")
                result.metadata["message"] = "No VPN connections found in region"
                return result

            self.logger.info("vpn_connections_found", count=len(vpn_connections))

            # Check security for each VPN connection
            secure_vpn_count = 0

            for vpn_connection in vpn_connections:
                vpn_id = vpn_connection["VpnConnectionId"]
                vpn_state = vpn_connection.get("State", "")
                result.resources_scanned += 1

                # Skip deleted/deleting VPN connections
                if vpn_state in ["deleted", "deleting"]:
                    continue

                # Check tunnel details
                vgw_telemetry = vpn_connection.get("VgwTelemetry", [])
                tunnel_options = vpn_connection.get("Options", {}).get("TunnelOptions", [])

                # Initialize security check variables
                all_tunnels_secure = True
                security_issues = []

                # Check each tunnel
                for idx, telemetry in enumerate(vgw_telemetry):
                    tunnel_status = telemetry.get("Status", "DOWN")

                    # Check if tunnel is up
                    if tunnel_status != "UP":
                        all_tunnels_secure = False
                        security_issues.append(f"Tunnel {idx + 1} is {tunnel_status} (not UP)")

                # Check tunnel options if available
                for idx, tunnel_option in enumerate(tunnel_options):
                    phase1_encryption = tunnel_option.get("Phase1EncryptionAlgorithms", [])
                    phase1_integrity = tunnel_option.get("Phase1IntegrityAlgorithms", [])
                    phase2_encryption = tunnel_option.get("Phase2EncryptionAlgorithms", [])
                    phase2_integrity = tunnel_option.get("Phase2IntegrityAlgorithms", [])
                    ike_versions = tunnel_option.get("IKEVersions", [])

                    # Check for weak encryption (prefer AES-256)
                    weak_encryption_found = False
                    for enc_alg in phase1_encryption + phase2_encryption:
                        if isinstance(enc_alg, dict):
                            value = enc_alg.get("Value", "")
                            if value and "AES128" in value:
                                weak_encryption_found = True

                    if weak_encryption_found:
                        security_issues.append(f"Tunnel {idx + 1} uses AES-128 (AES-256 recommended)")

                    # Check for weak integrity (prefer SHA-256 or better)
                    weak_integrity_found = False
                    for int_alg in phase1_integrity + phase2_integrity:
                        if isinstance(int_alg, dict):
                            value = int_alg.get("Value", "")
                            if value and "SHA1" in value:
                                weak_integrity_found = True

                    if weak_integrity_found:
                        security_issues.append(f"Tunnel {idx + 1} uses SHA-1 (SHA-256+ recommended)")

                    # Check IKE version (IKEv2 preferred)
                    if ike_versions:
                        has_ikev2 = any(
                            v.get("Value") == "ikev2" if isinstance(v, dict) else False
                            for v in ike_versions
                        )
                        if not has_ikev2:
                            security_issues.append(f"Tunnel {idx + 1} does not use IKEv2")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=vpn_id,
                    resource_type="vpn_connection",
                    data={
                        "vpn_connection_id": vpn_id,
                        "state": vpn_state,
                        "type": vpn_connection.get("Type"),
                        "category": vpn_connection.get("Category"),
                        "tunnel_count": len(vgw_telemetry),
                        "tunnel_status": [t.get("Status") for t in vgw_telemetry],
                        "security_issues": security_issues,
                    }
                )
                result.add_evidence(evidence)

                if all_tunnels_secure and not security_issues:
                    secure_vpn_count += 1
                    self.logger.debug(
                        "vpn_connection_secure",
                        vpn_id=vpn_id
                    )
                else:
                    # Determine severity based on issues
                    severity = Severity.HIGH if "DOWN" in str(security_issues) else Severity.MEDIUM

                    # Create finding for insecure VPN connection
                    finding = self.create_finding(
                        resource_id=vpn_id,
                        resource_type="vpn_connection",
                        severity=severity,
                        title="VPN connection has security issues",
                        description=f"VPN connection '{vpn_id}' has security configuration issues: "
                                    f"{', '.join(security_issues)}. "
                                    "VPN connections should use strong encryption (AES-256), strong "
                                    "integrity algorithms (SHA-256 or better), IKEv2 protocol, and "
                                    "all tunnels should be in UP status for high availability. "
                                    "ISO 27001 A.8.22 requires secure network segregation and "
                                    "encryption of data in transit.",
                        remediation=(
                            f"Improve VPN connection '{vpn_id}' security:\n\n"
                            "1. Use strong encryption and integrity algorithms:\n"
                            "   When creating/modifying VPN connection, specify tunnel options:\n"
                            "   - Phase1EncryptionAlgorithms: AES256, AES256-GCM-16\n"
                            "   - Phase1IntegrityAlgorithms: SHA2-256, SHA2-384, SHA2-512\n"
                            "   - Phase2EncryptionAlgorithms: AES256, AES256-GCM-16\n"
                            "   - Phase2IntegrityAlgorithms: SHA2-256, SHA2-384, SHA2-512\n"
                            "   - IKEVersions: ikev2\n\n"
                            "2. Ensure both tunnels are UP:\n"
                            "   - Check customer gateway configuration\n"
                            "   - Verify routing and firewall rules\n"
                            "   - Check VPN connection logs in CloudWatch\n\n"
                            "3. Create new VPN connection with secure settings:\n"
                            "   aws ec2 create-vpn-connection \\\n"
                            "     --type ipsec.1 \\\n"
                            "     --customer-gateway-id <cgw-id> \\\n"
                            "     --vpn-gateway-id <vgw-id> \\\n"
                            "     --options TunnelOptions='[{\n"
                            '       "Phase1EncryptionAlgorithms":[{"Value":"AES256"}],\n'
                            '       "Phase1IntegrityAlgorithms":[{"Value":"SHA2-256"}],\n'
                            '       "Phase2EncryptionAlgorithms":[{"Value":"AES256"}],\n'
                            '       "Phase2IntegrityAlgorithms":[{"Value":"SHA2-256"}],\n'
                            '       "IKEVersions":[{"Value":"ikev2"}]\n'
                            "     }]'\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to VPC console → Site-to-Site VPN Connections\n"
                            "2. Create new VPN connection or modify existing\n"
                            "3. Under 'Tunnel Options', configure:\n"
                            "   - Phase 1 Encryption: AES-256\n"
                            "   - Phase 1 Integrity: SHA2-256 or better\n"
                            "   - Phase 2 Encryption: AES-256\n"
                            "   - Phase 2 Integrity: SHA2-256 or better\n"
                            "   - IKE Version: IKEv2\n"
                            "4. Update customer gateway configuration accordingly\n\n"
                            "Security best practices:\n"
                            "- Enable VPN CloudWatch logs for monitoring\n"
                            "- Use DPD (Dead Peer Detection) timeout\n"
                            "- Configure tunnel inside CIDR appropriately\n"
                            "- Regularly rotate pre-shared keys\n"
                            "- Monitor tunnel status with CloudWatch alarms"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "vpn_connection_insecure",
                        vpn_id=vpn_id,
                        issues=security_issues
                    )

            # Calculate compliance score
            result.score = (secure_vpn_count / len(vpn_connections)) * 100

            # Determine pass/fail
            result.passed = secure_vpn_count == len(vpn_connections)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_vpn_connections": len(vpn_connections),
                "secure_vpn_connections": secure_vpn_count,
                "insecure_vpn_connections": len(vpn_connections) - secure_vpn_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "vpn_security_test_completed",
                total_vpn_connections=len(vpn_connections),
                secure=secure_vpn_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("vpn_security_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("vpn_security_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_vpn_security_test(connector: AWSConnector) -> TestResult:
    """Run VPN connection security compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_vpn_security_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = VPNSecurityTest(connector)
    return test.execute()

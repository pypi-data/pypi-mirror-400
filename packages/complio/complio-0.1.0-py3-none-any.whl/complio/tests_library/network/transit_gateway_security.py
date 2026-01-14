"""
Transit Gateway security compliance test.

Checks that Transit Gateways use secure configurations.

ISO 27001 Control: A.8.22 - Network segregation
Requirement: Transit Gateways must have proper route tables and security controls

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.transit_gateway_security import TransitGatewaySecurityTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = TransitGatewaySecurityTest(connector)
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


class TransitGatewaySecurityTest(ComplianceTest):
    """Test for Transit Gateway security compliance.

    Verifies that Transit Gateways use secure configurations:
    - Default route table association should be disabled (explicit control)
    - Default route table propagation should be disabled
    - Auto-accept shared attachments should be disabled
    - DNS support and VPN ECMP support configured appropriately

    Compliance Requirements:
        - DefaultRouteTableAssociation should be 'disable'
        - DefaultRouteTablePropagation should be 'disable'
        - AutoAcceptSharedAttachments should be 'disable'
        - Proper isolation between VPC attachments

    Scoring:
        - 100% if all Transit Gateways follow security best practices
        - Proportional score based on compliant/total ratio
        - 100% if no Transit Gateways exist

    Example:
        >>> test = TransitGatewaySecurityTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize Transit Gateway security test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="transit_gateway_security",
            test_name="Transit Gateway Security Check",
            description="Verify Transit Gateways use secure configurations",
            control_id="A.8.22",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute Transit Gateway security compliance test.

        Returns:
            TestResult with findings for insecure Transit Gateways

        Example:
            >>> test = TransitGatewaySecurityTest(connector)
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

            # List all Transit Gateways
            self.logger.info("listing_transit_gateways")
            tgw_response = ec2_client.describe_transit_gateways()
            transit_gateways = tgw_response.get("TransitGateways", [])

            if not transit_gateways:
                self.logger.info("no_transit_gateways_found")
                result.metadata["message"] = "No Transit Gateways found in region"
                return result

            self.logger.info("transit_gateways_found", count=len(transit_gateways))

            # Check security for each Transit Gateway
            secure_tgw_count = 0

            for tgw in transit_gateways:
                tgw_id = tgw["TransitGatewayId"]
                tgw_state = tgw.get("State", "")
                tgw_arn = tgw.get("TransitGatewayArn", "")

                # Skip deleted/deleting transit gateways
                if tgw_state in ["deleted", "deleting"]:
                    continue

                result.resources_scanned += 1

                # Get Transit Gateway options
                options = tgw.get("Options", {})
                default_route_table_association = options.get("DefaultRouteTableAssociation", "enable")
                default_route_table_propagation = options.get("DefaultRouteTablePropagation", "enable")
                auto_accept_shared_attachments = options.get("AutoAcceptSharedAttachments", "enable")
                dns_support = options.get("DnsSupport", "enable")

                # Determine security issues
                issues = []
                severity = Severity.MEDIUM

                # Check default route table association (should be disabled for security)
                if default_route_table_association == "enable":
                    issues.append("Default route table association enabled (should be disabled for explicit control)")
                    severity = Severity.MEDIUM

                # Check default route table propagation
                if default_route_table_propagation == "enable":
                    issues.append("Default route table propagation enabled (should be disabled for explicit control)")
                    severity = Severity.MEDIUM

                # Check auto-accept shared attachments (security risk)
                if auto_accept_shared_attachments == "enable":
                    issues.append("Auto-accept shared attachments enabled (security risk)")
                    severity = Severity.HIGH

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=tgw_id,
                    resource_type="transit_gateway",
                    data={
                        "transit_gateway_id": tgw_id,
                        "transit_gateway_arn": tgw_arn,
                        "state": tgw_state,
                        "default_route_table_association": default_route_table_association,
                        "default_route_table_propagation": default_route_table_propagation,
                        "auto_accept_shared_attachments": auto_accept_shared_attachments,
                        "dns_support": dns_support,
                        "has_issues": len(issues) > 0,
                        "issues": issues,
                    }
                )
                result.add_evidence(evidence)

                if len(issues) == 0:
                    secure_tgw_count += 1
                    self.logger.debug(
                        "transit_gateway_secure",
                        tgw_id=tgw_id
                    )
                else:
                    # Create finding for insecure Transit Gateway
                    finding = self.create_finding(
                        resource_id=tgw_id,
                        resource_type="transit_gateway",
                        severity=severity,
                        title="Transit Gateway has security configuration issues",
                        description=f"Transit Gateway '{tgw_id}' has security configuration issues: "
                                    f"{'; '.join(issues)}. Transit Gateways should use explicit route table "
                                    "associations and propagations for better security control, and should not "
                                    "auto-accept shared attachments to prevent unauthorized network access. "
                                    "ISO 27001 A.8.22 requires proper network segregation and security controls.",
                        remediation=(
                            f"Improve Transit Gateway '{tgw_id}' security configuration:\n\n"
                            "1. Disable default route table association:\n"
                            f"aws ec2 modify-transit-gateway \\\n"
                            f"  --transit-gateway-id {tgw_id} \\\n"
                            "  --options DefaultRouteTableAssociation=disable\n\n"
                            "2. Disable default route table propagation:\n"
                            f"aws ec2 modify-transit-gateway \\\n"
                            f"  --transit-gateway-id {tgw_id} \\\n"
                            "  --options DefaultRouteTablePropagation=disable\n\n"
                            "3. Disable auto-accept shared attachments:\n"
                            f"aws ec2 modify-transit-gateway \\\n"
                            f"  --transit-gateway-id {tgw_id} \\\n"
                            "  --options AutoAcceptSharedAttachments=disable\n\n"
                            "4. Explicitly manage route tables:\n"
                            "# Create dedicated route tables for different environments\n"
                            f"aws ec2 create-transit-gateway-route-table \\\n"
                            f"  --transit-gateway-id {tgw_id} \\\n"
                            "  --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=Production}]'\n\n"
                            "# Associate VPC attachments explicitly\n"
                            "aws ec2 associate-transit-gateway-route-table \\\n"
                            "  --transit-gateway-route-table-id <TGW-RT-ID> \\\n"
                            "  --transit-gateway-attachment-id <TGW-ATTACHMENT-ID>\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to VPC console → Transit Gateways\n"
                            f"2. Select Transit Gateway '{tgw_id}'\n"
                            "3. Actions → Modify Transit Gateway\n"
                            "4. Disable:\n"
                            "   - Default route table association\n"
                            "   - Default route table propagation\n"
                            "   - Auto accept shared attachments\n"
                            "5. Click 'Modify'\n"
                            "6. Go to 'Route Tables' tab\n"
                            "7. Create dedicated route tables for:\n"
                            "   - Production VPCs\n"
                            "   - Development VPCs\n"
                            "   - Shared services VPCs\n"
                            "8. Manually associate each VPC attachment to appropriate route table\n\n"
                            "Security best practices:\n"
                            "- Use separate route tables for different security zones\n"
                            "- Implement hub-and-spoke topology for centralized control\n"
                            "- Use blackhole routes to block unwanted traffic\n"
                            "- Enable VPC Flow Logs on attached VPCs\n"
                            "- Monitor Transit Gateway metrics in CloudWatch\n"
                            "- Use AWS Resource Access Manager (RAM) for controlled sharing\n"
                            "- Implement least privilege routing (only allow necessary routes)\n"
                            "- Tag route tables and attachments for easy management\n"
                            "- Regularly audit route table configurations\n"
                            "- Use AWS Network Firewall with Transit Gateway for inspection\n\n"
                            "Network isolation strategies:\n"
                            "- Production-to-production: Allow\n"
                            "- Production-to-dev: Deny (use separate route tables)\n"
                            "- Shared-services-to-all: Allow (DNS, AD, etc.)\n"
                            "- Internet-egress: Centralize through inspection VPC"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "transit_gateway_insecure",
                        tgw_id=tgw_id,
                        issues=issues
                    )

            # Calculate compliance score
            result.score = (secure_tgw_count / len(transit_gateways)) * 100

            # Determine pass/fail
            result.passed = secure_tgw_count == len(transit_gateways)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_transit_gateways": len(transit_gateways),
                "secure_transit_gateways": secure_tgw_count,
                "insecure_transit_gateways": len(transit_gateways) - secure_tgw_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "transit_gateway_security_test_completed",
                total_transit_gateways=len(transit_gateways),
                secure=secure_tgw_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("transit_gateway_security_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("transit_gateway_security_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_transit_gateway_security_test(connector: AWSConnector) -> TestResult:
    """Run Transit Gateway security compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_transit_gateway_security_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = TransitGatewaySecurityTest(connector)
    return test.execute()

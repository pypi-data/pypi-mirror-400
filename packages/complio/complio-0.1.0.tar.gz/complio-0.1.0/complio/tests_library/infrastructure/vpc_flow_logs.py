"""
VPC Flow Logs compliance test.

Checks that all VPCs have flow logs enabled for network traffic monitoring.

ISO 27001 Control: A.8.16 - Monitoring of network traffic
Requirement: Network traffic must be logged for security monitoring

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.vpc_flow_logs import VPCFlowLogsTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = VPCFlowLogsTest(connector)
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


class VPCFlowLogsTest(ComplianceTest):
    """Test for VPC Flow Logs compliance.

    Verifies that all VPCs have flow logs enabled to capture network
    traffic information for security monitoring and troubleshooting.

    Compliance Requirements:
        - Each VPC must have at least one flow log configured
        - Flow logs should capture accepted, rejected, or all traffic
        - VPCs without flow logs are non-compliant

    Scoring:
        - 100% if all VPCs have flow logs
        - Proportional score based on compliant/total ratio
        - 0% if no VPCs have flow logs

    Example:
        >>> test = VPCFlowLogsTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize VPC Flow Logs test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="vpc_flow_logs",
            test_name="VPC Flow Logs Check",
            description="Verify all VPCs have flow logs enabled for network traffic monitoring",
            control_id="A.8.16",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute VPC Flow Logs compliance test.

        Returns:
            TestResult with findings for VPCs without flow logs

        Example:
            >>> test = VPCFlowLogsTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            80.0
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

            # List all VPCs
            self.logger.info("listing_vpcs")
            vpcs_response = ec2_client.describe_vpcs()
            vpcs = vpcs_response.get("Vpcs", [])

            if not vpcs:
                self.logger.info("no_vpcs_found")
                result.metadata["message"] = "No VPCs found in region"
                return result

            self.logger.info("vpcs_found", count=len(vpcs))

            # Get all flow logs in the region
            self.logger.info("listing_flow_logs")
            flow_logs_response = ec2_client.describe_flow_logs()
            flow_logs = flow_logs_response.get("FlowLogs", [])

            # Create a map of VPC ID -> flow logs
            vpc_flow_logs_map: Dict[str, List[Dict[str, Any]]] = {}
            for flow_log in flow_logs:
                resource_id = flow_log.get("ResourceId")
                if resource_id and resource_id.startswith("vpc-"):
                    if resource_id not in vpc_flow_logs_map:
                        vpc_flow_logs_map[resource_id] = []
                    vpc_flow_logs_map[resource_id].append(flow_log)

            # Check each VPC for flow logs
            compliant_count = 0
            total_count = len(vpcs)

            for vpc in vpcs:
                vpc_id = vpc["VpcId"]
                is_default = vpc.get("IsDefault", False)
                cidr_block = vpc.get("CidrBlock", "unknown")
                result.resources_scanned += 1

                # Get VPC name from tags
                vpc_name = "unnamed"
                for tag in vpc.get("Tags", []):
                    if tag.get("Key") == "Name":
                        vpc_name = tag.get("Value", "unnamed")
                        break

                # Check if VPC has flow logs
                vpc_flow_logs = vpc_flow_logs_map.get(vpc_id, [])
                has_flow_logs = len(vpc_flow_logs) > 0

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=vpc_id,
                    resource_type="vpc",
                    data={
                        "vpc_id": vpc_id,
                        "vpc_name": vpc_name,
                        "is_default": is_default,
                        "cidr_block": cidr_block,
                        "has_flow_logs": has_flow_logs,
                        "flow_logs_count": len(vpc_flow_logs),
                        "flow_logs": [
                            {
                                "flow_log_id": fl.get("FlowLogId"),
                                "traffic_type": fl.get("TrafficType"),
                                "log_destination_type": fl.get("LogDestinationType"),
                                "log_destination": fl.get("LogDestination"),
                                "log_group_name": fl.get("LogGroupName"),
                            }
                            for fl in vpc_flow_logs
                        ] if vpc_flow_logs else [],
                    }
                )
                result.add_evidence(evidence)

                if has_flow_logs:
                    compliant_count += 1
                    self.logger.debug(
                        "vpc_has_flow_logs",
                        vpc_id=vpc_id,
                        vpc_name=vpc_name,
                        flow_logs_count=len(vpc_flow_logs)
                    )
                else:
                    # Create finding for VPC without flow logs
                    finding = self.create_finding(
                        resource_id=vpc_id,
                        resource_type="vpc",
                        severity=Severity.HIGH,
                        title="VPC Flow Logs not enabled",
                        description=f"VPC '{vpc_name}' ({vpc_id}, {cidr_block}) does not have flow logs enabled. "
                                    "Flow logs capture information about IP traffic going to and from network interfaces. "
                                    "Without flow logs, network security monitoring and troubleshooting are severely limited. "
                                    "This violates ISO 27001 A.8.16 requirement for network traffic monitoring.",
                        remediation=(
                            f"Enable VPC Flow Logs for VPC '{vpc_id}':\n"
                            "1. Create a CloudWatch log group (if using CloudWatch Logs):\n"
                            f"   aws logs create-log-group --log-group-name /aws/vpc/flowlogs/{vpc_id}\n"
                            "2. Create an IAM role for flow logs:\n"
                            "   (See AWS documentation for required trust policy and permissions)\n"
                            "3. Create the flow log:\n"
                            f"   aws ec2 create-flow-logs --resource-type VPC \\\n"
                            f"     --resource-ids {vpc_id} \\\n"
                            "     --traffic-type ALL \\\n"
                            "     --log-destination-type cloud-watch-logs \\\n"
                            f"     --log-group-name /aws/vpc/flowlogs/{vpc_id} \\\n"
                            "     --deliver-logs-permission-arn <iam-role-arn>\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to VPC → Your VPCs\n"
                            f"2. Select VPC '{vpc_id}'\n"
                            "3. Actions → Create flow log\n"
                            "4. Configure destination (CloudWatch Logs or S3)\n"
                            "5. Set traffic type to 'All'\n"
                            "6. Click Create flow log"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "vpc_without_flow_logs",
                        vpc_id=vpc_id,
                        vpc_name=vpc_name,
                        is_default=is_default
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (compliant_count / total_count) * 100

            # Determine pass/fail
            result.passed = compliant_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_vpcs": total_count,
                "vpcs_with_flow_logs": compliant_count,
                "vpcs_without_flow_logs": total_count - compliant_count,
                "total_flow_logs": len(flow_logs),
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "vpc_flow_logs_test_completed",
                total=total_count,
                compliant=compliant_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("vpc_flow_logs_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("vpc_flow_logs_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_vpc_flow_logs_test(connector: AWSConnector) -> TestResult:
    """Run VPC Flow Logs compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_vpc_flow_logs_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = VPCFlowLogsTest(connector)
    return test.execute()

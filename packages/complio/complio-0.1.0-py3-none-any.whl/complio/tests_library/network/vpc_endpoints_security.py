"""
VPC Endpoints security compliance test.

Checks that VPC Endpoints use secure configurations and policies.

ISO 27001 Control: A.8.22 - Network segregation
Requirement: VPC Endpoints should use restrictive policies and private DNS

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.vpc_endpoints_security import VPCEndpointsSecurityTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = VPCEndpointsSecurityTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

from typing import Any, Dict
import json

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Severity,
    TestResult,
    TestStatus,
)


class VPCEndpointsSecurityTest(ComplianceTest):
    """Test for VPC Endpoints security compliance.

    Verifies that VPC Endpoints use secure configurations:
    - Interface endpoints should have Private DNS enabled
    - Endpoint policies should not be overly permissive (not full access)
    - Gateway endpoints (S3, DynamoDB) should use restrictive policies

    Compliance Requirements:
        - Interface endpoints should enable Private DNS
        - Endpoint policies should follow least privilege
        - Avoid "*" in policy statements

    Scoring:
        - 100% if all VPC Endpoints follow security best practices
        - Proportional score based on compliant/total ratio
        - 100% if no VPC Endpoints exist

    Example:
        >>> test = VPCEndpointsSecurityTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize VPC Endpoints security test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="vpc_endpoints_security",
            test_name="VPC Endpoints Security Check",
            description="Verify VPC Endpoints use secure configurations and policies",
            control_id="A.8.22",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute VPC Endpoints security compliance test.

        Returns:
            TestResult with findings for insecure VPC Endpoints

        Example:
            >>> test = VPCEndpointsSecurityTest(connector)
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

            # List all VPC Endpoints
            self.logger.info("listing_vpc_endpoints")
            endpoints_response = ec2_client.describe_vpc_endpoints()
            vpc_endpoints = endpoints_response.get("VpcEndpoints", [])

            if not vpc_endpoints:
                self.logger.info("no_vpc_endpoints_found")
                result.metadata["message"] = "No VPC Endpoints found in region"
                return result

            self.logger.info("vpc_endpoints_found", count=len(vpc_endpoints))

            # Check security for each VPC Endpoint
            secure_endpoint_count = 0

            for endpoint in vpc_endpoints:
                endpoint_id = endpoint["VpcEndpointId"]
                endpoint_type = endpoint.get("VpcEndpointType", "")
                service_name = endpoint.get("ServiceName", "")
                vpc_id = endpoint.get("VpcId", "")
                state = endpoint.get("State", "")

                # Skip endpoints that are being deleted
                if state in ["deleted", "deleting", "failed"]:
                    continue

                result.resources_scanned += 1

                # Determine security issues
                issues = []
                severity = Severity.MEDIUM

                # Check for Interface endpoints
                if endpoint_type == "Interface":
                    private_dns_enabled = endpoint.get("PrivateDnsEnabled", False)
                    if not private_dns_enabled:
                        issues.append("Private DNS not enabled for interface endpoint")
                        severity = Severity.MEDIUM

                # Check endpoint policy
                policy_document = endpoint.get("PolicyDocument")
                if policy_document:
                    try:
                        policy = json.loads(policy_document)
                        # Check for overly permissive policies
                        if isinstance(policy, dict):
                            statements = policy.get("Statement", [])
                            for statement in statements:
                                if isinstance(statement, dict):
                                    effect = statement.get("Effect", "")
                                    action = statement.get("Action", "")
                                    resource = statement.get("Resource", "")
                                    principal = statement.get("Principal", "")

                                    # Check for full access
                                    if effect == "Allow" and action == "*" and (resource == "*" or resource == ["*"]):
                                        issues.append("Endpoint policy allows all actions on all resources (too permissive)")
                                        severity = Severity.HIGH

                                    # Check for any principal
                                    if effect == "Allow" and principal == "*":
                                        issues.append("Endpoint policy allows any principal (too permissive)")
                                        severity = Severity.HIGH

                    except json.JSONDecodeError:
                        issues.append("Endpoint policy is not valid JSON")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=endpoint_id,
                    resource_type="vpc_endpoint",
                    data={
                        "vpc_endpoint_id": endpoint_id,
                        "vpc_id": vpc_id,
                        "type": endpoint_type,
                        "service_name": service_name,
                        "state": state,
                        "private_dns_enabled": endpoint.get("PrivateDnsEnabled"),
                        "has_issues": len(issues) > 0,
                        "issues": issues,
                    }
                )
                result.add_evidence(evidence)

                if len(issues) == 0:
                    secure_endpoint_count += 1
                    self.logger.debug(
                        "vpc_endpoint_secure",
                        endpoint_id=endpoint_id
                    )
                else:
                    # Create finding for insecure VPC Endpoint
                    finding = self.create_finding(
                        resource_id=endpoint_id,
                        resource_type="vpc_endpoint",
                        severity=severity,
                        title="VPC Endpoint has security configuration issues",
                        description=f"VPC Endpoint '{endpoint_id}' (service: {service_name}) in VPC '{vpc_id}' has "
                                    f"security configuration issues: {'; '.join(issues)}. VPC Endpoints should enable "
                                    "Private DNS for interface endpoints and use least privilege policies to control "
                                    "access. ISO 27001 A.8.22 requires proper network segregation and access controls.",
                        remediation=(
                            f"Improve VPC Endpoint '{endpoint_id}' security:\n\n"
                            "1. Enable Private DNS (for interface endpoints):\n"
                            f"aws ec2 modify-vpc-endpoint \\\n"
                            f"  --vpc-endpoint-id {endpoint_id} \\\n"
                            "  --private-dns-enabled\n\n"
                            "2. Apply restrictive endpoint policy:\n"
                            "Create policy.json with least privilege access:\n"
                            "{\n"
                            '  "Statement": [\n'
                            '    {\n'
                            '      "Effect": "Allow",\n'
                            '      "Principal": {"AWS": "arn:aws:iam::ACCOUNT-ID:root"},\n'
                            '      "Action": [\n'
                            '        "s3:GetObject",\n'
                            '        "s3:PutObject"\n'
                            '      ],\n'
                            '      "Resource": "arn:aws:s3:::my-bucket/*"\n'
                            '    }\n'
                            '  ]\n'
                            '}\n\n'
                            f"aws ec2 modify-vpc-endpoint \\\n"
                            f"  --vpc-endpoint-id {endpoint_id} \\\n"
                            "  --policy-document file://policy.json\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to VPC console → Endpoints\n"
                            f"2. Select endpoint '{endpoint_id}'\n"
                            "3. Actions → Modify endpoint\n"
                            "4. For interface endpoints:\n"
                            "   - Enable 'Enable Private DNS Name'\n"
                            "5. Edit policy:\n"
                            "   - Click 'Custom' policy\n"
                            "   - Define specific actions and resources\n"
                            "   - Specify principal (avoid using '*')\n"
                            "6. Click 'Save'\n\n"
                            "Security best practices:\n"
                            "- Use interface endpoints for AWS services (more secure than internet)\n"
                            "- Enable Private DNS for seamless application integration\n"
                            "- Apply least privilege endpoint policies\n"
                            "- Use security groups to control access to interface endpoints\n"
                            "- Use VPC endpoint policies to restrict S3/DynamoDB access\n"
                            "- Monitor VPC endpoint usage with VPC Flow Logs\n"
                            "- Tag endpoints for easy management\n"
                            "- Regularly review and audit endpoint policies\n\n"
                            "Example restrictive policies:\n"
                            "S3 Gateway Endpoint (read-only for specific bucket):\n"
                            "{\n"
                            '  "Statement": [{\n'
                            '    "Effect": "Allow",\n'
                            '    "Principal": "*",\n'
                            '    "Action": "s3:GetObject",\n'
                            '    "Resource": "arn:aws:s3:::my-bucket/*"\n'
                            '  }]\n'
                            '}\n\n'
                            "DynamoDB Gateway Endpoint (specific table access):\n"
                            "{\n"
                            '  "Statement": [{\n'
                            '    "Effect": "Allow",\n'
                            '    "Principal": "*",\n'
                            '    "Action": ["dynamodb:GetItem", "dynamodb:PutItem"],\n'
                            '    "Resource": "arn:aws:dynamodb:region:account:table/MyTable"\n'
                            '  }]\n'
                            '}'
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "vpc_endpoint_insecure",
                        endpoint_id=endpoint_id,
                        issues=issues
                    )

            # Calculate compliance score
            result.score = (secure_endpoint_count / len(vpc_endpoints)) * 100

            # Determine pass/fail
            result.passed = secure_endpoint_count == len(vpc_endpoints)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_vpc_endpoints": len(vpc_endpoints),
                "secure_vpc_endpoints": secure_endpoint_count,
                "insecure_vpc_endpoints": len(vpc_endpoints) - secure_endpoint_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "vpc_endpoints_security_test_completed",
                total_vpc_endpoints=len(vpc_endpoints),
                secure=secure_endpoint_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("vpc_endpoints_security_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("vpc_endpoints_security_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_vpc_endpoints_security_test(connector: AWSConnector) -> TestResult:
    """Run VPC Endpoints security compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_vpc_endpoints_security_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = VPCEndpointsSecurityTest(connector)
    return test.execute()

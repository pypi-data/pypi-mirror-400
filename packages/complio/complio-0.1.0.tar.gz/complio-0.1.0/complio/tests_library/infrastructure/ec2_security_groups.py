"""
EC2 security group compliance test.

Checks that EC2 security groups don't have overly permissive ingress rules.

ISO 27001 Control: A.13.1.1 - Network Controls
Requirement: Networks must be controlled and protected

Dangerous configurations:
- 0.0.0.0/0 (all IPs) access on sensitive ports (22, 3389, 3306, 5432, etc.)
- Unrestricted access to databases
- Public SSH/RDP access

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.ec2_security_groups import EC2SecurityGroupTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = EC2SecurityGroupTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

from typing import Any, Dict, List

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Evidence,
    Finding,
    Severity,
    TestResult,
    TestStatus,
)
from complio.utils.logger import get_logger

# Sensitive ports that should never be open to 0.0.0.0/0
SENSITIVE_PORTS = {
    22: "SSH",
    3389: "RDP (Remote Desktop)",
    3306: "MySQL",
    5432: "PostgreSQL",
    1433: "SQL Server",
    27017: "MongoDB",
    6379: "Redis",
    5984: "CouchDB",
    9200: "Elasticsearch",
    11211: "Memcached",
}


class EC2SecurityGroupTest(ComplianceTest):
    """Test for EC2 security group compliance.

    Verifies that security groups don't have overly permissive ingress rules.

    Compliance Requirements:
        - No 0.0.0.0/0 access on sensitive ports (SSH, RDP, databases)
        - Security groups should follow principle of least privilege
        - Database ports should only be accessible from app servers

    Scoring:
        - 100% if no security groups have dangerous rules
        - Deduction for each dangerous rule found
        - 0% if critical ports (SSH/RDP) are publicly accessible

    Example:
        >>> test = EC2SecurityGroupTest(connector)
        >>> result = test.run()
        >>> if not result.passed:
        ...     for finding in result.findings:
        ...         print(f"{finding.severity}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize EC2 security group test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="ec2_security_groups",
            test_name="EC2 Security Group Network Controls",
            description="Ensures no security groups allow unrestricted access from 0.0.0.0/0 to critical ports (scans specified region only)",
            control_id="A.13.1.1",
            connector=connector,
            scope="regional",
        )
        self.logger = get_logger(__name__)

    def execute(self) -> TestResult:
        """Execute the EC2 security group compliance test.

        Returns:
            TestResult with findings and evidence

        Raises:
            AWSConnectionError: If unable to connect to AWS
            AWSCredentialsError: If credentials are invalid
        """
        self.logger.info(
            "starting_ec2_security_group_test",
            region=self.connector.region,
        )

        findings: List[Finding] = []
        evidence_list: List[Evidence] = []

        try:
            # Get EC2 client
            ec2_client = self.connector.get_client("ec2")

            # Describe all security groups
            response = ec2_client.describe_security_groups()
            security_groups = response.get("SecurityGroups", [])

            self.logger.info(
                "security_groups_found",
                count=len(security_groups),
                region=self.connector.region,
            )

            if not security_groups:
                # No security groups is unusual but not a failure
                return TestResult(
                    test_id=self.test_id,
                    test_name=self.test_name,
                    status=TestStatus.PASSED,
                    passed=True,
                    score=100.0,
                    findings=[],
                    evidence=[],
                    metadata={
                        "region": self.connector.region,
                        "total_security_groups": 0,
                        "dangerous_rules": 0,
                    },
                )

            # Check each security group for dangerous rules
            total_security_groups = len(security_groups)
            groups_with_issues = 0
            total_dangerous_rules = 0

            for sg in security_groups:
                sg_id = sg.get("GroupId", "unknown")
                sg_name = sg.get("GroupName", "unknown")
                ingress_rules = sg.get("IpPermissions", [])

                # Create evidence for this security group
                evidence = Evidence(
                    resource_id=sg_id,
                    resource_type="ec2_security_group",
                    region=self.connector.region,
                    data={
                        "group_name": sg_name,
                        "group_id": sg_id,
                        "ingress_rules_count": len(ingress_rules),
                        "vpc_id": sg.get("VpcId", "N/A"),
                    },
                )
                evidence_list.append(evidence)

                # Check each ingress rule
                dangerous_rules = []
                for rule in ingress_rules:
                    from_port = rule.get("FromPort", 0)
                    to_port = rule.get("ToPort", 65535)
                    ip_ranges = rule.get("IpRanges", [])

                    # Check if rule allows 0.0.0.0/0
                    for ip_range in ip_ranges:
                        cidr = ip_range.get("CidrIp", "")
                        if cidr == "0.0.0.0/0":
                            # Check if it's on a sensitive port
                            for port in range(from_port, to_port + 1):
                                if port in SENSITIVE_PORTS:
                                    dangerous_rules.append({
                                        "port": port,
                                        "service": SENSITIVE_PORTS[port],
                                        "cidr": cidr,
                                        "from_port": from_port,
                                        "to_port": to_port,
                                    })

                if dangerous_rules:
                    groups_with_issues += 1
                    total_dangerous_rules += len(dangerous_rules)

                    # Create finding for each dangerous rule
                    for rule in dangerous_rules:
                        severity = self._determine_severity(rule["port"])

                        finding = Finding(
                            resource_id=sg_id,
                            resource_type="ec2_security_group",
                            severity=severity,
                            title=f"Security group allows public access on {rule['service']} port",
                            description=(
                                f"Security group '{sg_name}' ({sg_id}) allows unrestricted "
                                f"access (0.0.0.0/0) on port {rule['port']} ({rule['service']}). "
                                f"This violates the principle of least privilege and exposes "
                                f"the service to potential attacks."
                            ),
                            remediation=(
                                f"Restrict access to port {rule['port']} to specific IP ranges:\n"
                                f"1. Identify which IPs need access to {rule['service']}\n"
                                f"2. Update security group rule to use specific CIDR blocks\n"
                                f"3. Remove 0.0.0.0/0 rule on port {rule['port']}\n"
                                f"4. Consider using VPN or bastion host for sensitive services"
                            ),
                            iso27001_control="A.13.1.1",
                            metadata={
                                "group_name": sg_name,
                                "port": rule["port"],
                                "service": rule["service"],
                                "cidr": rule["cidr"],
                                "port_range": f"{rule['from_port']}-{rule['to_port']}",
                            },
                        )
                        findings.append(finding)

            # Calculate score
            if total_dangerous_rules == 0:
                score = 100.0
                status = TestStatus.PASSED
                passed = True
            else:
                # Deduct points for each dangerous rule
                # Critical ports (SSH/RDP) cause immediate failure
                has_critical_exposure = any(
                    f.metadata.get("port") in [22, 3389]
                    for f in findings
                )

                if has_critical_exposure:
                    score = 0.0
                    status = TestStatus.FAILED
                    passed = False
                else:
                    # Deduct 10 points per dangerous rule, minimum 0
                    score = max(0.0, 100.0 - (total_dangerous_rules * 10))
                    status = TestStatus.FAILED if score < 70 else TestStatus.WARNING
                    passed = score >= 70

            self.logger.info(
                "ec2_security_group_test_complete",
                total_security_groups=total_security_groups,
                groups_with_issues=groups_with_issues,
                dangerous_rules=total_dangerous_rules,
                score=score,
            )

            return TestResult(
                test_id=self.test_id,
                test_name=self.test_name,
                status=status,
                passed=passed,
                score=score,
                findings=findings,
                evidence=evidence_list,
                metadata={
                    "region": self.connector.region,
                    "total_security_groups": total_security_groups,
                    "groups_with_issues": groups_with_issues,
                    "dangerous_rules": total_dangerous_rules,
                    "iso27001_control": "A.13.1.1",
                },
            )

        except ClientError as e:
            self.logger.error(
                "ec2_security_group_test_failed",
                error=str(e),
                error_code=e.response.get("Error", {}).get("Code"),
            )

            return TestResult(
                test_id=self.test_id,
                test_name=self.test_name,
                status=TestStatus.ERROR,
                passed=False,
                score=0.0,
                findings=[
                    Finding(
                        resource_id="N/A",
                        resource_type="ec2_security_group",
                        severity=Severity.HIGH,
                        title="Failed to check EC2 security groups",
                        description=f"Error accessing EC2: {str(e)}",
                        remediation="Check AWS credentials and permissions. Ensure IAM policy allows ec2:DescribeSecurityGroups",
                        iso27001_control="A.13.1.1",
                    )
                ],
                evidence=[],
                metadata={"error": str(e)},
            )

    def _determine_severity(self, port: int) -> Severity:
        """Determine severity level based on exposed port.

        Args:
            port: Port number being exposed

        Returns:
            Severity level (CRITICAL for SSH/RDP, HIGH for databases)
        """
        # SSH and RDP are critical - direct system access
        if port in [22, 3389]:
            return Severity.CRITICAL

        # Database ports are high severity - data exposure
        if port in [3306, 5432, 1433, 27017, 6379, 5984, 9200, 11211]:
            return Severity.HIGH

        # Other sensitive ports
        return Severity.MEDIUM

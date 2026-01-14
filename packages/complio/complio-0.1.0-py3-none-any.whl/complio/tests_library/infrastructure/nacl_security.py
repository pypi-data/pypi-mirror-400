"""
Network ACL security compliance test.

Checks that Network ACLs don't allow unrestricted access to sensitive ports.

ISO 27001 Control: A.8.20 - Network security
Requirement: Network access controls must restrict access to sensitive services

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.nacl_security import NACLSecurityTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = NACLSecurityTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

from typing import Any, Dict, List, Set

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Severity,
    TestResult,
    TestStatus,
)


# Sensitive ports that should not be open to 0.0.0.0/0
SENSITIVE_PORTS = {
    22: "SSH",
    3389: "RDP",
    1433: "MS SQL Server",
    3306: "MySQL",
    5432: "PostgreSQL",
    27017: "MongoDB",
    6379: "Redis",
    9200: "Elasticsearch",
    5984: "CouchDB",
}


class NACLSecurityTest(ComplianceTest):
    """Test for Network ACL security compliance.

    Verifies that Network ACLs don't allow unrestricted access (0.0.0.0/0)
    to sensitive ports commonly used by database and management services.

    Compliance Requirements:
        - NACLs should not allow 0.0.0.0/0 access to sensitive ports
        - Sensitive ports include: SSH (22), RDP (3389), databases (1433, 3306, 5432, 27017)
        - Unrestricted access to these ports is HIGH severity

    Scoring:
        - 100% if all NACLs are secure
        - Proportional score based on secure/total ratio
        - Each insecure rule reduces the score

    Example:
        >>> test = NACLSecurityTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize Network ACL security test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="nacl_security",
            test_name="Network ACL Security Check",
            description="Verify Network ACLs don't allow unrestricted access to sensitive ports",
            control_id="A.8.20",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute Network ACL security compliance test.

        Returns:
            TestResult with findings for insecure NACL rules

        Example:
            >>> test = NACLSecurityTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            90.0
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

            # List all Network ACLs
            self.logger.info("listing_network_acls")
            response = ec2_client.describe_network_acls()
            nacls = response.get("NetworkAcls", [])

            if not nacls:
                self.logger.info("no_nacls_found")
                result.metadata["message"] = "No Network ACLs found in region"
                return result

            self.logger.info("nacls_found", count=len(nacls))

            # Check each NACL for insecure rules
            secure_nacls = 0
            total_nacls = len(nacls)
            total_insecure_rules = 0

            for nacl in nacls:
                nacl_id = nacl["NetworkAclId"]
                vpc_id = nacl.get("VpcId", "unknown")
                is_default = nacl.get("IsDefault", False)
                result.resources_scanned += 1

                # Get NACL name from tags
                nacl_name = "unnamed"
                for tag in nacl.get("Tags", []):
                    if tag.get("Key") == "Name":
                        nacl_name = tag.get("Value", "unnamed")
                        break

                # Check inbound rules for insecure configurations
                insecure_rules = self._check_nacl_rules(nacl)

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=nacl_id,
                    resource_type="network_acl",
                    data={
                        "nacl_id": nacl_id,
                        "nacl_name": nacl_name,
                        "vpc_id": vpc_id,
                        "is_default": is_default,
                        "insecure_rules_count": len(insecure_rules),
                        "insecure_rules": insecure_rules,
                        "total_entries": len(nacl.get("Entries", [])),
                    }
                )
                result.add_evidence(evidence)

                if len(insecure_rules) == 0:
                    secure_nacls += 1
                    self.logger.debug(
                        "nacl_secure",
                        nacl_id=nacl_id,
                        nacl_name=nacl_name
                    )
                else:
                    total_insecure_rules += len(insecure_rules)

                    # Create finding for each insecure rule
                    for insecure_rule in insecure_rules:
                        rule_number = insecure_rule["rule_number"]
                        port_range = insecure_rule["port_range"]
                        protocol = insecure_rule["protocol"]
                        service_name = insecure_rule["service_name"]

                        finding = self.create_finding(
                            resource_id=nacl_id,
                            resource_type="network_acl",
                            severity=Severity.HIGH,
                            title=f"Network ACL allows unrestricted access to {service_name}",
                            description=f"Network ACL '{nacl_name}' ({nacl_id}) has rule #{rule_number} that allows "
                                        f"unrestricted access (0.0.0.0/0) to {service_name} on port {port_range}. "
                                        f"This exposes sensitive services to the entire internet. "
                                        "ISO 27001 A.8.20 requires proper network access controls.",
                            remediation=(
                                f"Restrict access to {service_name} in NACL '{nacl_id}':\n"
                                "1. Go to VPC → Network ACLs\n"
                                f"2. Select NACL '{nacl_id}'\n"
                                "3. Go to Inbound Rules tab\n"
                                f"4. Edit rule #{rule_number}\n"
                                "5. Change source from 0.0.0.0/0 to specific IP ranges\n"
                                "6. Save changes\n\n"
                                "Or use AWS CLI:\n"
                                f"# First, delete the insecure rule:\n"
                                f"aws ec2 delete-network-acl-entry --network-acl-id {nacl_id} \\\n"
                                f"  --rule-number {rule_number} --ingress\n\n"
                                f"# Then, add a secure rule with specific source:\n"
                                f"aws ec2 create-network-acl-entry --network-acl-id {nacl_id} \\\n"
                                f"  --rule-number {rule_number} --protocol {protocol} \\\n"
                                f"  --port-range From={port_range},To={port_range} \\\n"
                                "  --cidr-block <your-ip-range>/32 --rule-action allow --ingress"
                            ),
                            evidence=evidence
                        )
                        result.add_finding(finding)

                    self.logger.warning(
                        "nacl_insecure",
                        nacl_id=nacl_id,
                        nacl_name=nacl_name,
                        insecure_rules_count=len(insecure_rules)
                    )

            # Calculate compliance score
            # Score is based on the ratio of secure NACLs to total NACLs
            if total_nacls > 0:
                result.score = (secure_nacls / total_nacls) * 100

            # Determine pass/fail
            result.passed = secure_nacls == total_nacls
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_nacls": total_nacls,
                "secure_nacls": secure_nacls,
                "insecure_nacls": total_nacls - secure_nacls,
                "total_insecure_rules": total_insecure_rules,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "nacl_security_test_completed",
                total=total_nacls,
                secure=secure_nacls,
                total_insecure_rules=total_insecure_rules,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("nacl_security_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("nacl_security_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result

    def _check_nacl_rules(self, nacl: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check NACL rules for insecure configurations.

        Args:
            nacl: Network ACL dictionary from AWS API

        Returns:
            List of insecure rules with details
        """
        insecure_rules = []

        for entry in nacl.get("Entries", []):
            # Only check inbound ALLOW rules
            if entry.get("Egress", True):
                continue  # Skip egress rules

            if entry.get("RuleAction") != "allow":
                continue  # Skip deny rules

            # Check if rule allows 0.0.0.0/0 or ::/0
            cidr_block = entry.get("CidrBlock", "")
            ipv6_cidr_block = entry.get("Ipv6CidrBlock", "")

            if cidr_block != "0.0.0.0/0" and ipv6_cidr_block != "::/0":
                continue  # Not unrestricted, skip

            # Get port range
            port_range = entry.get("PortRange", {})
            from_port = port_range.get("From") if port_range else None
            to_port = port_range.get("To") if port_range else None

            # Get protocol
            protocol = entry.get("Protocol", "-1")

            # Check if rule allows sensitive ports
            if protocol == "-1":
                # All protocols - check if this is a problem
                # This is very permissive but not always wrong for NACLs
                # We'll flag it if it's rule 100 or lower (high priority)
                rule_number = entry.get("RuleNumber", 32767)
                if rule_number <= 100:
                    for port, service_name in SENSITIVE_PORTS.items():
                        insecure_rules.append({
                            "rule_number": rule_number,
                            "port_range": f"All (includes {port})",
                            "protocol": "All",
                            "service_name": f"All Services (includes {service_name})",
                            "cidr_block": cidr_block or ipv6_cidr_block,
                        })
                    break  # Only add once for "all protocols" rules
            elif from_port is not None and to_port is not None:
                # Check if any sensitive port is in the range
                for port, service_name in SENSITIVE_PORTS.items():
                    if from_port <= port <= to_port:
                        protocol_name = {
                            "6": "TCP",
                            "17": "UDP",
                            "-1": "All",
                        }.get(protocol, f"Protocol {protocol}")

                        port_display = f"{from_port}-{to_port}" if from_port != to_port else str(from_port)

                        insecure_rules.append({
                            "rule_number": entry.get("RuleNumber", 32767),
                            "port_range": port_display,
                            "protocol": protocol_name,
                            "service_name": service_name,
                            "cidr_block": cidr_block or ipv6_cidr_block,
                        })

        return insecure_rules


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_nacl_security_test(connector: AWSConnector) -> TestResult:
    """Run Network ACL security compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_nacl_security_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = NACLSecurityTest(connector)
    return test.execute()

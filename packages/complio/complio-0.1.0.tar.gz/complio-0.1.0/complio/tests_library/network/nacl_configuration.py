"""
Network ACL configuration compliance test.

Checks that Network ACLs follow security best practices for inbound/outbound rules.

ISO 27001 Control: A.8.20 - Networks security
Requirement: Network ACLs must have proper rule configuration and deny rules

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.nacl_configuration import NACLConfigurationTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = NACLConfigurationTest(connector)
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


class NACLConfigurationTest(ComplianceTest):
    """Test for Network ACL configuration compliance.

    Verifies that Network ACLs follow security best practices including:
    - Not using default allow-all rules only
    - Having explicit deny rules for security
    - Proper rule numbering (not all 100, 200, etc.)
    - No overly permissive rules (0.0.0.0/0 on all ports)

    Compliance Requirements:
        - NACLs should have custom rules beyond defaults
        - Should include explicit deny rules
        - Rule numbers should be properly spaced for maintainability
        - Should not allow all traffic from anywhere

    Scoring:
        - 100% if all NACLs follow best practices
        - Proportional score based on compliant/total ratio
        - 100% if only default NACLs exist (no custom NACLs)

    Example:
        >>> test = NACLConfigurationTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize Network ACL configuration test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="nacl_configuration",
            test_name="Network ACL Configuration Check",
            description="Verify Network ACLs follow security best practices",
            control_id="A.8.20",
            connector=connector,
            scope="regional",
        )

    def _check_nacl_rules(self, entries: List[Dict]) -> tuple:
        """Check NACL rules for security issues.

        Args:
            entries: List of NACL entries

        Returns:
            Tuple of (has_issues, issues_list)
        """
        issues = []

        # Check if only default rules exist (32767 is default rule number)
        non_default_rules = [e for e in entries if e.get("RuleNumber", 32767) != 32767]
        if len(non_default_rules) == 0:
            issues.append("Only default rules present (no custom rules)")

        # Check for overly permissive rules
        for entry in entries:
            rule_number = entry.get("RuleNumber")
            rule_action = entry.get("RuleAction")
            cidr_block = entry.get("CidrBlock", "")
            protocol = entry.get("Protocol", "-1")

            # Skip default deny-all rule
            if rule_number == 32767:
                continue

            # Check for allow-all rules (0.0.0.0/0 with protocol -1 or all ports)
            if rule_action == "allow" and cidr_block == "0.0.0.0/0":
                # Protocol -1 means all protocols
                if protocol == "-1":
                    issues.append(f"Rule {rule_number} allows all traffic from anywhere")
                else:
                    # Check if port range is too wide
                    port_range = entry.get("PortRange", {})
                    if port_range:
                        from_port = port_range.get("From", 0)
                        to_port = port_range.get("To", 0)
                        if from_port == 0 and to_port == 65535:
                            issues.append(f"Rule {rule_number} allows all ports from anywhere")

        # Check if there are any explicit deny rules (security best practice)
        deny_rules = [e for e in entries if e.get("RuleAction") == "deny" and e.get("RuleNumber") != 32767]
        if len(deny_rules) == 0 and len(non_default_rules) > 0:
            issues.append("No explicit deny rules (only relying on default deny)")

        # Check rule numbering (should have spacing for future rules)
        rule_numbers = sorted([e.get("RuleNumber") for e in non_default_rules])
        if len(rule_numbers) > 1:
            consecutive_rules = 0
            for i in range(len(rule_numbers) - 1):
                if rule_numbers[i+1] - rule_numbers[i] == 1:
                    consecutive_rules += 1

            if consecutive_rules > 0:
                issues.append("Consecutive rule numbers detected (should use spacing like 100, 200, 300)")

        return len(issues) > 0, issues

    def execute(self) -> TestResult:
        """Execute Network ACL configuration compliance test.

        Returns:
            TestResult with findings for misconfigured NACLs

        Example:
            >>> test = NACLConfigurationTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            85.0
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
            nacls_response = ec2_client.describe_network_acls()
            nacls = nacls_response.get("NetworkAcls", [])

            if not nacls:
                self.logger.info("no_network_acls_found")
                result.metadata["message"] = "No Network ACLs found in region"
                return result

            self.logger.info("network_acls_found", count=len(nacls))

            # Check configuration for each NACL
            properly_configured_count = 0
            default_nacls_count = 0

            for nacl in nacls:
                nacl_id = nacl["NetworkAclId"]
                is_default = nacl.get("IsDefault", False)
                vpc_id = nacl.get("VpcId")
                entries = nacl.get("Entries", [])

                result.resources_scanned += 1

                # Skip default NACLs (they are expected to have default rules)
                if is_default:
                    default_nacls_count += 1
                    self.logger.debug("skipping_default_nacl", nacl_id=nacl_id)
                    continue

                # Check rules for security issues
                has_issues, issues_list = self._check_nacl_rules(entries)

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=nacl_id,
                    resource_type="network_acl",
                    data={
                        "nacl_id": nacl_id,
                        "vpc_id": vpc_id,
                        "is_default": is_default,
                        "entry_count": len(entries),
                        "has_issues": has_issues,
                        "issues": issues_list,
                    }
                )
                result.add_evidence(evidence)

                if not has_issues:
                    properly_configured_count += 1
                    self.logger.debug(
                        "nacl_properly_configured",
                        nacl_id=nacl_id
                    )
                else:
                    # Determine severity based on issues
                    severity = Severity.HIGH if any("all traffic" in issue or "all ports" in issue for issue in issues_list) else Severity.MEDIUM

                    # Create finding for misconfigured NACL
                    finding = self.create_finding(
                        resource_id=nacl_id,
                        resource_type="network_acl",
                        severity=severity,
                        title="Network ACL has configuration issues",
                        description=f"Network ACL '{nacl_id}' in VPC '{vpc_id}' has security configuration "
                                    f"issues: {'; '.join(issues_list)}. Network ACLs should follow security "
                                    "best practices including proper rule numbering, explicit deny rules, and "
                                    "avoiding overly permissive allow rules. ISO 27001 A.8.20 requires proper "
                                    "network security controls.",
                        remediation=(
                            f"Improve Network ACL '{nacl_id}' configuration:\n\n"
                            "Best practices:\n"
                            "1. Use rule number spacing (100, 200, 300) for future flexibility\n"
                            "2. Add explicit deny rules for known bad traffic patterns\n"
                            "3. Avoid allowing all traffic from 0.0.0.0/0 on all ports\n"
                            "4. Use specific port ranges instead of all ports\n"
                            "5. Document each rule's purpose using tags\n\n"
                            "Example of good NACL configuration:\n"
                            "Inbound Rules:\n"
                            "- Rule 100: Allow HTTP (80) from 0.0.0.0/0\n"
                            "- Rule 110: Allow HTTPS (443) from 0.0.0.0/0\n"
                            "- Rule 120: Allow SSH (22) from 10.0.0.0/8 only\n"
                            "- Rule 900: Deny all from known bad IP ranges\n"
                            "- Rule 32767: Deny all (default)\n\n"
                            "Outbound Rules:\n"
                            "- Rule 100: Allow HTTP (80) to 0.0.0.0/0\n"
                            "- Rule 110: Allow HTTPS (443) to 0.0.0.0/0\n"
                            "- Rule 120: Allow ephemeral ports (1024-65535)\n"
                            "- Rule 32767: Deny all (default)\n\n"
                            "To modify NACL rules using AWS CLI:\n"
                            f"# Create a new allow rule\n"
                            f"aws ec2 create-network-acl-entry \\\n"
                            f"  --network-acl-id {nacl_id} \\\n"
                            "  --rule-number 100 \\\n"
                            "  --protocol tcp \\\n"
                            "  --port-range From=443,To=443 \\\n"
                            "  --cidr-block 0.0.0.0/0 \\\n"
                            "  --rule-action allow \\\n"
                            "  --ingress\n\n"
                            "# Create a deny rule for bad traffic\n"
                            f"aws ec2 create-network-acl-entry \\\n"
                            f"  --network-acl-id {nacl_id} \\\n"
                            "  --rule-number 900 \\\n"
                            "  --protocol -1 \\\n"
                            "  --cidr-block <BAD-IP-RANGE> \\\n"
                            "  --rule-action deny \\\n"
                            "  --ingress\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to VPC console → Network ACLs\n"
                            f"2. Select NACL '{nacl_id}'\n"
                            "3. Edit inbound/outbound rules\n"
                            "4. Add specific allow rules with proper spacing\n"
                            "5. Add explicit deny rules for known threats\n"
                            "6. Remove overly permissive rules\n\n"
                            "Security considerations:\n"
                            "- NACLs are stateless (need both inbound and outbound rules)\n"
                            "- Lower rule numbers are evaluated first\n"
                            "- Use Security Groups for instance-level filtering\n"
                            "- Use NACLs for subnet-level defense in depth\n"
                            "- Regularly review and audit NACL rules\n"
                            "- Use VPC Flow Logs to monitor traffic patterns"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "nacl_configuration_issues",
                        nacl_id=nacl_id,
                        issues=issues_list
                    )

            # Calculate score based on custom NACLs only
            custom_nacls_count = len(nacls) - default_nacls_count

            if custom_nacls_count == 0:
                # No custom NACLs, only defaults - this is acceptable
                result.metadata["message"] = f"Only default NACLs found ({default_nacls_count} default NACLs)"
                result.score = 100.0
                result.passed = True
            else:
                # Calculate compliance score
                result.score = (properly_configured_count / custom_nacls_count) * 100
                result.passed = properly_configured_count == custom_nacls_count

            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_nacls": len(nacls),
                "default_nacls": default_nacls_count,
                "custom_nacls": custom_nacls_count,
                "properly_configured": properly_configured_count,
                "misconfigured": custom_nacls_count - properly_configured_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "nacl_configuration_test_completed",
                total_nacls=len(nacls),
                custom_nacls=custom_nacls_count,
                properly_configured=properly_configured_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("nacl_configuration_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("nacl_configuration_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_nacl_configuration_test(connector: AWSConnector) -> TestResult:
    """Run Network ACL configuration compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_nacl_configuration_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = NACLConfigurationTest(connector)
    return test.execute()

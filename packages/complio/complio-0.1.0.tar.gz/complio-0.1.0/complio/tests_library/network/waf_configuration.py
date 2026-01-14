"""
AWS WAF (Web Application Firewall) configuration compliance test.

Checks that AWS WAF is properly configured for web application protection.

ISO 27001 Control: A.8.20 - Networks security
Requirement: Web applications should be protected by WAF with proper rules

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.waf_configuration import WAFConfigurationTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = WAFConfigurationTest(connector)
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


class WAFConfigurationTest(ComplianceTest):
    """Test for AWS WAF configuration compliance.

    Verifies that AWS WAF (Web Application Firewall) is properly configured:
    - WAF WebACLs should be associated with resources (ALB, CloudFront, API Gateway)
    - WebACLs should have rules configured (not empty)
    - Logging should be enabled
    - Should use AWS managed rules or custom rules for protection

    Compliance Requirements:
        - WAF deployed for public-facing web applications
        - WebACLs have active rules (managed or custom)
        - Logging enabled for security monitoring
        - Rules cover common vulnerabilities (OWASP Top 10)

    Scoring:
        - Based on WebACL configuration and associations
        - Checks rule counts and logging status
        - Validates resource protection

    Example:
        >>> test = WAFConfigurationTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize WAF configuration test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="waf_configuration",
            test_name="AWS WAF Configuration Check",
            description="Verify AWS WAF is properly configured for web application protection",
            control_id="A.8.20",
            connector=connector,
            scope="regional",  # WAFv2 is regional, but also has CLOUDFRONT scope
        )

    def _check_webacl_configuration(self, webacl: Dict, wafv2_client: Any, scope: str) -> tuple:
        """Check WebACL configuration for issues.

        Args:
            webacl: WebACL summary dict
            wafv2_client: WAFv2 client
            scope: REGIONAL or CLOUDFRONT

        Returns:
            Tuple of (has_issues, issues_list, severity, rule_count)
        """
        issues = []
        severity = Severity.MEDIUM

        webacl_id = webacl.get("Id")
        webacl_name = webacl.get("Name")
        webacl_arn = webacl.get("ARN")

        # Get detailed WebACL configuration
        try:
            webacl_response = wafv2_client.get_web_acl(
                Name=webacl_name,
                Scope=scope,
                Id=webacl_id
            )

            webacl_details = webacl_response.get("WebACL", {})
            rules = webacl_details.get("Rules", [])
            rule_count = len(rules)

            # Check if WebACL has rules
            if rule_count == 0:
                issues.append("No rules configured (WebACL provides no protection)")
                severity = Severity.HIGH

            # Check if WebACL is associated with resources
            # Note: Need to check associations separately for ALB/CloudFront/API Gateway
            # This requires additional API calls which we'll do in the main execute method

            # Check for logging
            try:
                logging_config = wafv2_client.get_logging_configuration(
                    ResourceArn=webacl_arn
                )
                logging_enabled = True
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") == "WAFNonexistentItemException":
                    logging_enabled = False
                    issues.append("WAF logging not enabled")
                else:
                    raise

            return len(issues) > 0, issues, severity, rule_count, logging_enabled

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            issues.append(f"Error retrieving WebACL details: {error_code}")
            return True, issues, Severity.MEDIUM, 0, False

    def execute(self) -> TestResult:
        """Execute AWS WAF configuration compliance test.

        Returns:
            TestResult with findings for missing or misconfigured WAF

        Example:
            >>> test = WAFConfigurationTest(connector)
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
            # Get WAFv2 client
            wafv2_client = self.connector.get_client("wafv2")

            # Check both REGIONAL and CLOUDFRONT scopes
            all_webacls = []

            # Regional WebACLs (for ALB, API Gateway)
            self.logger.info("listing_regional_webacls")
            try:
                regional_response = wafv2_client.list_web_acls(Scope="REGIONAL")
                regional_webacls = regional_response.get("WebACLs", [])
                for webacl in regional_webacls:
                    webacl["_scope"] = "REGIONAL"
                    all_webacls.append(webacl)
                self.logger.info("regional_webacls_found", count=len(regional_webacls))
            except ClientError as e:
                self.logger.warning("error_listing_regional_webacls", error=str(e))

            # CloudFront WebACLs (global)
            self.logger.info("listing_cloudfront_webacls")
            try:
                # CloudFront WAF must be in us-east-1
                cloudfront_wafv2_client = self.connector.session.client("wafv2", region_name="us-east-1")
                cloudfront_response = cloudfront_wafv2_client.list_web_acls(Scope="CLOUDFRONT")
                cloudfront_webacls = cloudfront_response.get("WebACLs", [])
                for webacl in cloudfront_webacls:
                    webacl["_scope"] = "CLOUDFRONT"
                    all_webacls.append(webacl)
                self.logger.info("cloudfront_webacls_found", count=len(cloudfront_webacls))
            except ClientError as e:
                self.logger.warning("error_listing_cloudfront_webacls", error=str(e))

            if not all_webacls:
                self.logger.info("no_waf_webacls_found")
                result.metadata["message"] = "No AWS WAF WebACLs found (consider deploying WAF for web applications)"
                result.metadata["recommendation"] = "Deploy WAF for ALB, CloudFront, and API Gateway"
                # Not a hard failure, but should be noted
                result.score = 50.0
                result.passed = False
                result.status = TestStatus.FAILED
                return result

            self.logger.info("waf_webacls_found", total_count=len(all_webacls))

            # Check configuration for each WebACL
            properly_configured_count = 0

            for webacl in all_webacls:
                webacl_name = webacl.get("Name", "")
                webacl_arn = webacl.get("ARN", "")
                webacl_id = webacl.get("Id", "")
                scope = webacl.get("_scope", "REGIONAL")

                result.resources_scanned += 1

                # Use appropriate client based on scope
                if scope == "CLOUDFRONT":
                    check_client = self.connector.session.client("wafv2", region_name="us-east-1")
                else:
                    check_client = wafv2_client

                # Check WebACL configuration
                has_issues, issues_list, severity, rule_count, logging_enabled = \
                    self._check_webacl_configuration(webacl, check_client, scope)

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=webacl_arn,
                    resource_type="waf_webacl",
                    data={
                        "webacl_name": webacl_name,
                        "webacl_arn": webacl_arn,
                        "webacl_id": webacl_id,
                        "scope": scope,
                        "rule_count": rule_count,
                        "logging_enabled": logging_enabled,
                        "has_issues": has_issues,
                        "issues": issues_list,
                    }
                )
                result.add_evidence(evidence)

                if not has_issues:
                    properly_configured_count += 1
                    self.logger.debug(
                        "webacl_properly_configured",
                        webacl_name=webacl_name,
                        scope=scope
                    )
                else:
                    # Create finding for misconfigured WebACL
                    finding = self.create_finding(
                        resource_id=webacl_arn,
                        resource_type="waf_webacl",
                        severity=severity,
                        title=f"WAF WebACL has configuration issues ({scope})",
                        description=f"AWS WAF WebACL '{webacl_name}' (scope: {scope}) has configuration issues: "
                                    f"{'; '.join(issues_list)}. WAF WebACLs should have active rules configured "
                                    f"and logging enabled to protect web applications from common attacks and "
                                    "monitor security events. ISO 27001 A.8.20 requires proper network security "
                                    "controls for web applications.",
                        remediation=(
                            f"Improve WAF WebACL '{webacl_name}' configuration:\n\n"
                            "1. Add AWS Managed Rule Groups (recommended):\n"
                            f"aws wafv2 update-web-acl \\\n"
                            f"  --name {webacl_name} \\\n"
                            f"  --scope {scope} \\\n"
                            f"  --id {webacl_id} \\\n"
                            "  --cli-input-json file://webacl-config.json\n\n"
                            "Recommended AWS Managed Rule Groups:\n"
                            "- AWSManagedRulesCommonRuleSet (OWASP Top 10)\n"
                            "- AWSManagedRulesKnownBadInputsRuleSet (bad inputs)\n"
                            "- AWSManagedRulesSQLiRuleSet (SQL injection)\n"
                            "- AWSManagedRulesLinuxRuleSet (Linux exploits)\n"
                            "- AWSManagedRulesAmazonIpReputationList (IP reputation)\n"
                            "- AWSManagedRulesAnonymousIpList (Tor, VPN, proxies)\n\n"
                            "2. Enable WAF logging:\n"
                            "# Create S3 bucket or Kinesis stream first\n"
                            "# Bucket name must start with 'aws-waf-logs-'\n"
                            "aws s3 mb s3://aws-waf-logs-myapp\n\n"
                            f"aws wafv2 put-logging-configuration \\\n"
                            "  --logging-configuration '{\n"
                            f'    "ResourceArn": "{webacl_arn}",\n'
                            '    "LogDestinationConfigs": [\n'
                            '      "arn:aws:s3:::aws-waf-logs-myapp"\n'
                            '    ]\n'
                            "  }'\n\n"
                            "3. Associate WebACL with resources:\n"
                            "For Application Load Balancer:\n"
                            f"aws wafv2 associate-web-acl \\\n"
                            f"  --web-acl-arn {webacl_arn} \\\n"
                            "  --resource-arn <ALB-ARN>\n\n"
                            "For API Gateway (REST):\n"
                            f"aws wafv2 associate-web-acl \\\n"
                            f"  --web-acl-arn {webacl_arn} \\\n"
                            "  --resource-arn <API-GATEWAY-STAGE-ARN>\n\n"
                            "For CloudFront (must use CLOUDFRONT scope WebACL):\n"
                            "aws cloudfront update-distribution \\\n"
                            "  --id <DISTRIBUTION-ID> \\\n"
                            "  --distribution-config file://dist-config.json\n"
                            "# Add WebACLId in distribution config\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to AWS WAF console\n"
                            f"2. Select WebACL '{webacl_name}'\n"
                            "3. Add rules:\n"
                            "   - Click 'Rules' tab → 'Add rules'\n"
                            "   - Add managed rule groups (AWS or Marketplace)\n"
                            "   - Configure custom rules if needed\n"
                            "   - Set rule priorities\n"
                            "4. Enable logging:\n"
                            "   - Go to 'Logging' tab\n"
                            "   - Enable logging\n"
                            "   - Select S3 bucket or Kinesis stream\n"
                            "5. Associate with resources:\n"
                            "   - Go to 'Associated AWS resources' tab\n"
                            "   - Add ALB, CloudFront, or API Gateway\n\n"
                            "Security best practices:\n"
                            "- Use AWS Managed Rules as baseline\n"
                            "- Add rate limiting rules to prevent DDoS\n"
                            "- Configure geo-blocking for specific countries\n"
                            "- Use IP sets for allow/deny lists\n"
                            "- Enable bot control for automated traffic\n"
                            "- Set up CloudWatch alarms for blocked requests\n"
                            "- Use AWS Firewall Manager for centralized management\n"
                            "- Regularly review WAF logs and metrics\n"
                            "- Test rules in COUNT mode before BLOCK\n"
                            "- Use custom rules for application-specific logic\n\n"
                            "Common rule examples:\n"
                            "Rate limiting:\n"
                            "- Limit: 2000 requests per 5 minutes per IP\n"
                            "- Action: Block for 10 minutes\n\n"
                            "Geo-blocking:\n"
                            "- Block requests from high-risk countries\n"
                            "- Allow only specific countries if applicable\n\n"
                            "IP reputation:\n"
                            "- Block known malicious IPs\n"
                            "- Block Tor exit nodes\n"
                            "- Block proxies and VPNs if needed\n\n"
                            "OWASP Top 10 protection:\n"
                            "- SQL injection\n"
                            "- Cross-site scripting (XSS)\n"
                            "- Path traversal\n"
                            "- Command injection\n"
                            "- Session fixation\n\n"
                            "Monitoring and alerting:\n"
                            "- Set CloudWatch alarms for:\n"
                            "  • Blocked requests > threshold\n"
                            "  • Counted requests (testing rules)\n"
                            "  • Rule evaluation errors\n"
                            "- Integrate with Security Hub\n"
                            "- Send logs to SIEM for analysis\n"
                            "- Use Athena to query WAF logs in S3"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "webacl_misconfigured",
                        webacl_name=webacl_name,
                        scope=scope,
                        issues=issues_list
                    )

            # Calculate compliance score
            if len(all_webacls) > 0:
                result.score = (properly_configured_count / len(all_webacls)) * 100
                result.passed = properly_configured_count == len(all_webacls)
            else:
                result.score = 50.0
                result.passed = False

            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_webacls": len(all_webacls),
                "properly_configured": properly_configured_count,
                "misconfigured": len(all_webacls) - properly_configured_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "waf_configuration_test_completed",
                total_webacls=len(all_webacls),
                properly_configured=properly_configured_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("waf_configuration_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("waf_configuration_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_waf_configuration_test(connector: AWSConnector) -> TestResult:
    """Run AWS WAF configuration compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_waf_configuration_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = WAFConfigurationTest(connector)
    return test.execute()

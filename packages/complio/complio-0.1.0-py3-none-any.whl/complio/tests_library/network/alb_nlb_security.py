"""
Application Load Balancer and Network Load Balancer security compliance test.

Checks that ALBs and NLBs use secure configurations including HTTPS listeners.

ISO 27001 Control: A.8.22 - Network segregation
Requirement: Load balancers must use secure protocols and configurations

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.alb_nlb_security import ALBNLBSecurityTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = ALBNLBSecurityTest(connector)
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


class ALBNLBSecurityTest(ComplianceTest):
    """Test for ALB/NLB security compliance.

    Verifies that Application and Network Load Balancers use secure configurations:
    - ALBs should use HTTPS listeners
    - HTTPS listeners should use modern TLS versions (TLS 1.2+)
    - Should have access logging enabled
    - Should have deletion protection enabled (recommended)

    Compliance Requirements:
        - ALBs should have at least one HTTPS listener
        - HTTPS listeners must use TLS 1.2 or higher
        - Access logging should be enabled for audit trail
        - Deletion protection recommended for production

    Scoring:
        - 100% if all load balancers meet security requirements
        - Proportional score based on compliant/total ratio
        - 100% if no load balancers exist

    Example:
        >>> test = ALBNLBSecurityTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize ALB/NLB security test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="alb_nlb_security",
            test_name="ALB/NLB Security Check",
            description="Verify Application and Network Load Balancers use secure configurations",
            control_id="A.8.22",
            connector=connector,
            scope="regional",
        )

    def _check_alb_security(self, lb_arn: str, lb_name: str, listeners: List[Dict], attributes: Dict) -> tuple:
        """Check ALB security configuration.

        Args:
            lb_arn: Load balancer ARN
            lb_name: Load balancer name
            listeners: List of listener configurations
            attributes: Load balancer attributes

        Returns:
            Tuple of (has_issues, issues_list, severity)
        """
        issues = []
        severity = Severity.MEDIUM

        # Check if there's at least one HTTPS listener
        https_listeners = [l for l in listeners if l.get("Protocol") == "HTTPS"]
        http_listeners = [l for l in listeners if l.get("Protocol") == "HTTP"]

        if len(https_listeners) == 0 and len(http_listeners) > 0:
            issues.append("No HTTPS listeners configured (only HTTP)")
            severity = Severity.HIGH

        # Check HTTPS listener SSL policies
        for listener in https_listeners:
            ssl_policy = listener.get("SslPolicy", "")
            # Check for outdated SSL policies
            if ssl_policy and any(weak in ssl_policy for weak in ["ELBSecurityPolicy-2016", "ELBSecurityPolicy-TLS"]):
                if "TLS-1-2" not in ssl_policy:
                    issues.append(f"HTTPS listener uses outdated SSL policy: {ssl_policy}")
                    severity = Severity.HIGH

        # Check if access logging is enabled
        access_logs_enabled = False
        for attr in attributes:
            if attr.get("Key") == "access_logs.s3.enabled":
                access_logs_enabled = attr.get("Value") == "true"
                break

        if not access_logs_enabled:
            issues.append("Access logging not enabled")
            if severity == Severity.MEDIUM:
                severity = Severity.MEDIUM

        # Check deletion protection (best practice, not critical)
        deletion_protection = False
        for attr in attributes:
            if attr.get("Key") == "deletion_protection.enabled":
                deletion_protection = attr.get("Value") == "true"
                break

        if not deletion_protection:
            issues.append("Deletion protection not enabled (recommended for production)")

        return len(issues) > 0, issues, severity

    def _check_nlb_security(self, lb_arn: str, lb_name: str, listeners: List[Dict], attributes: Dict) -> tuple:
        """Check NLB security configuration.

        Args:
            lb_arn: Load balancer ARN
            lb_name: Load balancer name
            listeners: List of listener configurations
            attributes: Load balancer attributes

        Returns:
            Tuple of (has_issues, issues_list, severity)
        """
        issues = []
        severity = Severity.MEDIUM

        # NLBs can use TLS listeners for secure traffic
        tls_listeners = [l for l in listeners if l.get("Protocol") == "TLS"]
        tcp_listeners = [l for l in listeners if l.get("Protocol") == "TCP"]

        # Check if TLS is used where appropriate
        if len(tls_listeners) == 0 and len(tcp_listeners) > 0:
            # Check if any TCP listener is on standard HTTPS port (443)
            https_tcp_listeners = [l for l in tcp_listeners if l.get("Port") == 443]
            if https_tcp_listeners:
                issues.append("TCP listener on port 443 without TLS (should use TLS protocol)")
                severity = Severity.HIGH

        # Check TLS listener SSL policies
        for listener in tls_listeners:
            ssl_policy = listener.get("SslPolicy", "")
            if ssl_policy and "TLS-1-2" not in ssl_policy:
                issues.append(f"TLS listener uses outdated SSL policy: {ssl_policy}")
                severity = Severity.HIGH

        # Check if access logging is enabled (NLB supports this via S3)
        access_logs_enabled = False
        for attr in attributes:
            if attr.get("Key") == "access_logs.s3.enabled":
                access_logs_enabled = attr.get("Value") == "true"
                break

        if not access_logs_enabled:
            issues.append("Access logging not enabled")

        # Check deletion protection
        deletion_protection = False
        for attr in attributes:
            if attr.get("Key") == "deletion_protection.enabled":
                deletion_protection = attr.get("Value") == "true"
                break

        if not deletion_protection:
            issues.append("Deletion protection not enabled (recommended for production)")

        return len(issues) > 0, issues, severity

    def execute(self) -> TestResult:
        """Execute ALB/NLB security compliance test.

        Returns:
            TestResult with findings for insecure load balancers

        Example:
            >>> test = ALBNLBSecurityTest(connector)
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
            # Get ELBv2 client
            elbv2_client = self.connector.get_client("elbv2")

            # List all load balancers (ALB and NLB)
            self.logger.info("listing_load_balancers")
            lbs_response = elbv2_client.describe_load_balancers()
            load_balancers = lbs_response.get("LoadBalancers", [])

            if not load_balancers:
                self.logger.info("no_load_balancers_found")
                result.metadata["message"] = "No load balancers found in region"
                return result

            self.logger.info("load_balancers_found", count=len(load_balancers))

            # Check security for each load balancer
            secure_lb_count = 0

            for lb in load_balancers:
                lb_arn = lb["LoadBalancerArn"]
                lb_name = lb["LoadBalancerName"]
                lb_type = lb.get("Type", "application")  # application or network
                lb_scheme = lb.get("Scheme", "internet-facing")

                result.resources_scanned += 1

                # Get listeners for this load balancer
                listeners_response = elbv2_client.describe_listeners(LoadBalancerArn=lb_arn)
                listeners = listeners_response.get("Listeners", [])

                # Get load balancer attributes
                attributes_response = elbv2_client.describe_load_balancer_attributes(LoadBalancerArn=lb_arn)
                attributes = attributes_response.get("Attributes", [])

                # Check security based on type
                if lb_type == "application":
                    has_issues, issues_list, severity = self._check_alb_security(
                        lb_arn, lb_name, listeners, attributes
                    )
                elif lb_type == "network":
                    has_issues, issues_list, severity = self._check_nlb_security(
                        lb_arn, lb_name, listeners, attributes
                    )
                else:
                    # Gateway load balancers - skip for now
                    continue

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=lb_arn,
                    resource_type="load_balancer",
                    data={
                        "load_balancer_arn": lb_arn,
                        "load_balancer_name": lb_name,
                        "type": lb_type,
                        "scheme": lb_scheme,
                        "listener_count": len(listeners),
                        "has_issues": has_issues,
                        "issues": issues_list,
                    }
                )
                result.add_evidence(evidence)

                if not has_issues:
                    secure_lb_count += 1
                    self.logger.debug(
                        "load_balancer_secure",
                        lb_name=lb_name,
                        lb_type=lb_type
                    )
                else:
                    # Create finding for insecure load balancer
                    finding = self.create_finding(
                        resource_id=lb_arn,
                        resource_type="load_balancer",
                        severity=severity,
                        title=f"{lb_type.upper()} has security configuration issues",
                        description=f"{lb_type.upper()} '{lb_name}' has security configuration issues: "
                                    f"{'; '.join(issues_list)}. Load balancers should use secure protocols "
                                    "(HTTPS/TLS), modern SSL/TLS policies (TLS 1.2+), enable access logging "
                                    "for audit trails, and enable deletion protection for production workloads. "
                                    "ISO 27001 A.8.22 requires secure network segregation and encryption.",
                        remediation=(
                            f"Improve {lb_type.upper()} '{lb_name}' security:\n\n"
                            "1. Add HTTPS/TLS listener:\n"
                            f"aws elbv2 create-listener \\\n"
                            f"  --load-balancer-arn {lb_arn} \\\n"
                            "  --protocol {'HTTPS' if lb_type == 'application' else 'TLS'} \\\n"
                            "  --port 443 \\\n"
                            "  --certificates CertificateArn=<ACM-CERT-ARN> \\\n"
                            "  --default-actions Type=forward,TargetGroupArn=<TG-ARN> \\\n"
                            "  --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06\n\n"
                            "2. Enable access logging:\n"
                            f"aws elbv2 modify-load-balancer-attributes \\\n"
                            f"  --load-balancer-arn {lb_arn} \\\n"
                            "  --attributes \\\n"
                            "    Key=access_logs.s3.enabled,Value=true \\\n"
                            "    Key=access_logs.s3.bucket,Value=<S3-BUCKET-NAME> \\\n"
                            "    Key=access_logs.s3.prefix,Value=<PREFIX>\n\n"
                            "3. Enable deletion protection:\n"
                            f"aws elbv2 modify-load-balancer-attributes \\\n"
                            f"  --load-balancer-arn {lb_arn} \\\n"
                            "  --attributes Key=deletion_protection.enabled,Value=true\n\n"
                            "4. Update SSL policy to modern version:\n"
                            f"aws elbv2 modify-listener \\\n"
                            "  --listener-arn <LISTENER-ARN> \\\n"
                            "  --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to EC2 console → Load Balancers\n"
                            f"2. Select '{lb_name}'\n"
                            "3. Add HTTPS/TLS listener:\n"
                            "   - Click 'Add listener'\n"
                            "   - Select protocol: {'HTTPS' if lb_type == 'application' else 'TLS'}\n"
                            "   - Port: 443\n"
                            "   - Default SSL certificate: Select from ACM\n"
                            "   - Security policy: ELBSecurityPolicy-TLS13-1-2-2021-06\n"
                            "4. Enable access logs:\n"
                            "   - Go to 'Attributes' tab\n"
                            "   - Edit 'Access logs'\n"
                            "   - Enable and specify S3 bucket\n"
                            "5. Enable deletion protection:\n"
                            "   - Edit 'Deletion protection'\n"
                            "   - Enable\n\n"
                            "Recommended SSL/TLS policies (in order of preference):\n"
                            "- ELBSecurityPolicy-TLS13-1-2-2021-06 (TLS 1.3 + 1.2)\n"
                            "- ELBSecurityPolicy-TLS13-1-2-Res-2021-06 (Restricted)\n"
                            "- ELBSecurityPolicy-TLS-1-2-2017-01 (TLS 1.2 minimum)\n\n"
                            "Security best practices:\n"
                            "- Use AWS Certificate Manager (ACM) for SSL/TLS certificates\n"
                            "- Enable automatic certificate renewal\n"
                            "- Configure HTTP to HTTPS redirect for ALBs\n"
                            "- Use security groups to restrict access\n"
                            "- Enable WAF for ALBs handling web traffic\n"
                            "- Monitor access logs for suspicious activity\n"
                            "- Use CloudWatch alarms for unhealthy targets"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "load_balancer_security_issues",
                        lb_name=lb_name,
                        lb_type=lb_type,
                        issues=issues_list
                    )

            # Calculate compliance score
            result.score = (secure_lb_count / len(load_balancers)) * 100

            # Determine pass/fail
            result.passed = secure_lb_count == len(load_balancers)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_load_balancers": len(load_balancers),
                "secure_load_balancers": secure_lb_count,
                "insecure_load_balancers": len(load_balancers) - secure_lb_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "alb_nlb_security_test_completed",
                total_load_balancers=len(load_balancers),
                secure=secure_lb_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("alb_nlb_security_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("alb_nlb_security_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_alb_nlb_security_test(connector: AWSConnector) -> TestResult:
    """Run ALB/NLB security compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_alb_nlb_security_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = ALBNLBSecurityTest(connector)
    return test.execute()

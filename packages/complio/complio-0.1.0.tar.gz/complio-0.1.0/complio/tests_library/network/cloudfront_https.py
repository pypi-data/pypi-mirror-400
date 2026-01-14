"""
CloudFront HTTPS enforcement compliance test.

Checks that CloudFront distributions enforce HTTPS for secure content delivery.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: CloudFront distributions must use HTTPS to encrypt data in transit

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.cloudfront_https import CloudFrontHTTPSTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = CloudFrontHTTPSTest(connector)
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


class CloudFrontHTTPSTest(ComplianceTest):
    """Test for CloudFront HTTPS enforcement compliance.

    Verifies that CloudFront distributions use HTTPS for secure content delivery:
    - Viewer protocol policy should redirect HTTP to HTTPS or HTTPS-only
    - Origin protocol policy should use HTTPS when possible
    - Minimum TLS version should be TLS 1.2 or higher
    - Should use modern security policy

    Compliance Requirements:
        - ViewerProtocolPolicy must be 'redirect-to-https' or 'https-only'
        - MinimumProtocolVersion should be TLSv1.2_2021 or higher
        - Origin should use HTTPS when communicating with backend
        - SSL/TLS certificate should be valid

    Scoring:
        - 100% if all distributions enforce HTTPS properly
        - Proportional score based on compliant/total ratio
        - 100% if no distributions exist

    Example:
        >>> test = CloudFrontHTTPSTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize CloudFront HTTPS test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="cloudfront_https",
            test_name="CloudFront HTTPS Enforcement Check",
            description="Verify CloudFront distributions enforce HTTPS for secure content delivery",
            control_id="A.8.24",
            connector=connector,
            scope="global",  # CloudFront is a global service
        )

    def execute(self) -> TestResult:
        """Execute CloudFront HTTPS compliance test.

        Returns:
            TestResult with findings for insecure distributions

        Example:
            >>> test = CloudFrontHTTPSTest(connector)
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
            # Get CloudFront client (global service, no region needed)
            cloudfront_client = self.connector.get_client("cloudfront")

            # List all distributions
            self.logger.info("listing_cloudfront_distributions")
            distributions = []

            paginator = cloudfront_client.get_paginator("list_distributions")
            for page in paginator.paginate():
                dist_list = page.get("DistributionList", {})
                items = dist_list.get("Items", [])
                distributions.extend(items)

            if not distributions:
                self.logger.info("no_cloudfront_distributions_found")
                result.metadata["message"] = "No CloudFront distributions found"
                return result

            self.logger.info("cloudfront_distributions_found", count=len(distributions))

            # Check HTTPS configuration for each distribution
            https_enforced_count = 0

            for dist_summary in distributions:
                dist_id = dist_summary["Id"]
                dist_domain = dist_summary.get("DomainName", "")
                dist_status = dist_summary.get("Status", "")

                result.resources_scanned += 1

                # Get full distribution configuration
                dist_response = cloudfront_client.get_distribution(Id=dist_id)
                dist_config = dist_response.get("Distribution", {}).get("DistributionConfig", {})

                # Check viewer protocol policy in default cache behavior
                default_cache_behavior = dist_config.get("DefaultCacheBehavior", {})
                viewer_protocol_policy = default_cache_behavior.get("ViewerProtocolPolicy", "allow-all")

                # Check minimum protocol version
                viewer_certificate = dist_config.get("ViewerCertificate", {})
                min_protocol_version = viewer_certificate.get("MinimumProtocolVersion", "SSLv3")

                # Check origin protocol policy
                origins = dist_config.get("Origins", {}).get("Items", [])
                insecure_origins = []
                for origin in origins:
                    custom_origin_config = origin.get("CustomOriginConfig", {})
                    if custom_origin_config:
                        origin_protocol_policy = custom_origin_config.get("OriginProtocolPolicy", "http-only")
                        if origin_protocol_policy == "http-only":
                            insecure_origins.append(origin.get("Id", "unknown"))

                # Determine if configuration is secure
                issues = []
                severity = Severity.MEDIUM

                # Check viewer protocol policy
                if viewer_protocol_policy not in ["redirect-to-https", "https-only"]:
                    issues.append(f"Viewer protocol allows HTTP (policy: {viewer_protocol_policy})")
                    severity = Severity.HIGH

                # Check minimum TLS version
                if min_protocol_version not in ["TLSv1.2_2021", "TLSv1.2_2019", "TLSv1.2_2018", "TLSv1.1_2016"]:
                    if "TLSv1.2" not in min_protocol_version and "TLSv1.3" not in min_protocol_version:
                        issues.append(f"Outdated minimum TLS version: {min_protocol_version}")
                        severity = Severity.HIGH

                # Check origin protocol
                if insecure_origins:
                    issues.append(f"Origins using HTTP-only: {', '.join(insecure_origins)}")
                    severity = Severity.MEDIUM

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=dist_id,
                    resource_type="cloudfront_distribution",
                    data={
                        "distribution_id": dist_id,
                        "domain_name": dist_domain,
                        "status": dist_status,
                        "viewer_protocol_policy": viewer_protocol_policy,
                        "minimum_protocol_version": min_protocol_version,
                        "insecure_origins": insecure_origins,
                        "has_issues": len(issues) > 0,
                        "issues": issues,
                    }
                )
                result.add_evidence(evidence)

                if len(issues) == 0:
                    https_enforced_count += 1
                    self.logger.debug(
                        "cloudfront_https_enforced",
                        distribution_id=dist_id
                    )
                else:
                    # Create finding for insecure distribution
                    finding = self.create_finding(
                        resource_id=dist_id,
                        resource_type="cloudfront_distribution",
                        severity=severity,
                        title="CloudFront distribution not properly enforcing HTTPS",
                        description=f"CloudFront distribution '{dist_id}' (domain: {dist_domain}) has HTTPS "
                                    f"enforcement issues: {'; '.join(issues)}. CloudFront distributions should "
                                    "enforce HTTPS to encrypt data in transit, use modern TLS versions (1.2+), "
                                    "and communicate with origins securely. ISO 27001 A.8.24 requires "
                                    "cryptographic controls for data in transit.",
                        remediation=(
                            f"Improve CloudFront distribution '{dist_id}' HTTPS configuration:\n\n"
                            "1. Enforce HTTPS for viewers:\n"
                            f"aws cloudfront get-distribution-config --id {dist_id} > dist-config.json\n"
                            "# Edit dist-config.json:\n"
                            "# Set DefaultCacheBehavior.ViewerProtocolPolicy to 'redirect-to-https' or 'https-only'\n"
                            f"aws cloudfront update-distribution \\\n"
                            f"  --id {dist_id} \\\n"
                            "  --distribution-config file://dist-config.json \\\n"
                            "  --if-match <ETag-from-get-distribution-config>\n\n"
                            "2. Update minimum TLS version:\n"
                            "# In dist-config.json:\n"
                            "# Set ViewerCertificate.MinimumProtocolVersion to 'TLSv1.2_2021'\n\n"
                            "3. Use HTTPS for origin communication:\n"
                            "# In dist-config.json:\n"
                            "# For each CustomOriginConfig:\n"
                            "# Set OriginProtocolPolicy to 'https-only' or 'match-viewer'\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to CloudFront console\n"
                            f"2. Select distribution '{dist_id}'\n"
                            "3. Go to 'Behaviors' tab\n"
                            "4. Edit default behavior:\n"
                            "   - Viewer Protocol Policy: 'Redirect HTTP to HTTPS'\n"
                            "5. Go to 'General' tab → Edit:\n"
                            "   - Custom SSL Certificate (if using custom domain)\n"
                            "   - Security Policy: TLSv1.2_2021 (recommended)\n"
                            "6. Go to 'Origins' tab\n"
                            "7. Edit each origin:\n"
                            "   - Protocol: HTTPS only\n"
                            "   - Minimum Origin SSL Protocol: TLSv1.2\n\n"
                            "Recommended configurations:\n"
                            "Viewer Protocol Policy:\n"
                            "- redirect-to-https (recommended for public sites)\n"
                            "- https-only (for APIs or sensitive content)\n\n"
                            "Security Policy (Minimum TLS Version):\n"
                            "- TLSv1.2_2021 (recommended, supports TLS 1.2 and 1.3)\n"
                            "- TLSv1.2_2019\n"
                            "- TLSv1.2_2018\n\n"
                            "Origin Protocol Policy:\n"
                            "- https-only (most secure)\n"
                            "- match-viewer (flexible, but ensure viewers use HTTPS)\n\n"
                            "Additional security best practices:\n"
                            "- Use AWS Certificate Manager (ACM) for SSL/TLS certificates\n"
                            "- Enable automatic certificate renewal\n"
                            "- Configure custom SSL certificate for custom domains\n"
                            "- Enable AWS WAF for web application protection\n"
                            "- Enable access logging for audit trail\n"
                            "- Use Origin Access Identity (OAI) for S3 origins\n"
                            "- Enable field-level encryption for sensitive data\n"
                            "- Configure security headers (HSTS, CSP, etc.)\n"
                            "- Monitor CloudFront metrics in CloudWatch\n"
                            "- Use signed URLs/cookies for private content"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "cloudfront_https_not_enforced",
                        distribution_id=dist_id,
                        issues=issues
                    )

            # Calculate compliance score
            result.score = (https_enforced_count / len(distributions)) * 100

            # Determine pass/fail
            result.passed = https_enforced_count == len(distributions)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_distributions": len(distributions),
                "https_enforced": https_enforced_count,
                "insecure_distributions": len(distributions) - https_enforced_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "cloudfront_https_test_completed",
                total_distributions=len(distributions),
                https_enforced=https_enforced_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("cloudfront_https_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("cloudfront_https_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_cloudfront_https_test(connector: AWSConnector) -> TestResult:
    """Run CloudFront HTTPS enforcement compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_cloudfront_https_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = CloudFrontHTTPSTest(connector)
    return test.execute()

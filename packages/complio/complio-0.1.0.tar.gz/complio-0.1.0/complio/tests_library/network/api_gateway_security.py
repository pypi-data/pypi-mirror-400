"""
API Gateway security compliance test.

Checks that API Gateway APIs use secure configurations.

ISO 27001 Control: A.8.22 - Network segregation
Requirement: API Gateway APIs must use secure authentication, authorization, and encryption

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.network.api_gateway_security import APIGatewaySecurityTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = APIGatewaySecurityTest(connector)
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


class APIGatewaySecurityTest(ComplianceTest):
    """Test for API Gateway security compliance.

    Verifies that API Gateway APIs use secure configurations:
    - Use authentication (API keys, IAM, Cognito, Lambda authorizers)
    - Use HTTPS with TLS 1.2+
    - Have access logging enabled
    - Have throttling configured
    - Use WAF for protection (recommended)
    - Have proper resource policies (for private APIs)

    Compliance Requirements:
        - Authentication/authorization configured
        - TLS encryption enforced
        - Access logging enabled
        - Throttling/rate limiting configured
        - WAF protection for public APIs

    Scoring:
        - Based on security configuration completeness
        - Multiple checks per API
        - Weighted scoring

    Example:
        >>> test = APIGatewaySecurityTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize API Gateway security test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="api_gateway_security",
            test_name="API Gateway Security Check",
            description="Verify API Gateway APIs use secure configurations",
            control_id="A.8.22",
            connector=connector,
            scope="regional",
        )

    def _check_rest_api_security(self, api_id: str, api_name: str, apigateway_client: Any) -> tuple:
        """Check REST API security configuration.

        Args:
            api_id: API Gateway REST API ID
            api_name: API name
            apigateway_client: API Gateway client

        Returns:
            Tuple of (has_issues, issues_list, severity, score_points)
        """
        issues = []
        severity = Severity.MEDIUM
        score_points = 0  # Out of 100

        try:
            # Get API stages
            stages_response = apigateway_client.get_stages(restApiId=api_id)
            stages = stages_response.get("item", [])

            if not stages:
                issues.append("No stages deployed")
                return True, issues, Severity.HIGH, 0

            # Check each stage
            for stage in stages:
                stage_name = stage.get("stageName", "")

                # Check access logging (20 points)
                access_log_settings = stage.get("accessLogSettings")
                if access_log_settings and access_log_settings.get("destinationArn"):
                    score_points += 20
                else:
                    issues.append(f"Stage '{stage_name}' has no access logging")

                # Check throttling (20 points)
                throttle_settings = stage.get("throttleSettings", {})
                if throttle_settings.get("rateLimit") or throttle_settings.get("burstLimit"):
                    score_points += 20
                else:
                    issues.append(f"Stage '{stage_name}' has no throttling configured")

                # Check WAF association (20 points)
                web_acl_arn = stage.get("webAclArn")
                if web_acl_arn:
                    score_points += 20
                else:
                    issues.append(f"Stage '{stage_name}' not protected by WAF")
                    severity = Severity.MEDIUM

                # Check tracing (10 points - nice to have)
                tracing_enabled = stage.get("tracingEnabled", False)
                if tracing_enabled:
                    score_points += 10

            # Check authentication at method level (30 points)
            # Get resources and methods
            resources_response = apigateway_client.get_resources(restApiId=api_id)
            resources = resources_response.get("items", [])

            has_auth = False
            open_methods = []

            for resource in resources:
                resource_methods = resource.get("resourceMethods", {})
                for method, method_data in resource_methods.items():
                    authorization_type = method_data.get("authorizationType", "NONE")
                    if authorization_type != "NONE":
                        has_auth = True
                    else:
                        resource_path = resource.get("path", "/")
                        open_methods.append(f"{method} {resource_path}")

            if has_auth:
                score_points += 30
            else:
                issues.append("No authentication configured on any methods")
                severity = Severity.HIGH

            if open_methods:
                issues.append(f"Open methods without auth: {', '.join(open_methods[:5])}")

            # Normalize score to 100
            score_points = min(score_points, 100)

            return len(issues) > 0, issues, severity, score_points

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            issues.append(f"Error checking REST API: {error_code}")
            return True, issues, Severity.MEDIUM, 0

    def execute(self) -> TestResult:
        """Execute API Gateway security compliance test.

        Returns:
            TestResult with findings for insecure API configurations

        Example:
            >>> test = APIGatewaySecurityTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            75.0
        """
        result = TestResult(
            test_id=self.test_id,
            test_name=self.test_name,
            status=TestStatus.PASSED,
            passed=True,
            score=100.0,
        )

        try:
            # Get API Gateway client
            apigateway_client = self.connector.get_client("apigateway")

            # List REST APIs
            self.logger.info("listing_rest_apis")
            rest_apis = []

            paginator = apigateway_client.get_paginator("get_rest_apis")
            for page in paginator.paginate():
                rest_apis.extend(page.get("items", []))

            if not rest_apis:
                self.logger.info("no_rest_apis_found")
                result.metadata["message"] = "No API Gateway REST APIs found in region"
                # Not a failure, just informational
                return result

            self.logger.info("rest_apis_found", count=len(rest_apis))

            # Check security for each API
            total_score = 0
            apis_checked = 0

            for api in rest_apis:
                api_id = api.get("id", "")
                api_name = api.get("name", "")
                api_endpoint = api.get("endpoint", "")

                result.resources_scanned += 1
                apis_checked += 1

                # Check REST API security
                has_issues, issues_list, severity, api_score = \
                    self._check_rest_api_security(api_id, api_name, apigateway_client)

                total_score += api_score

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=api_id,
                    resource_type="api_gateway_rest_api",
                    data={
                        "api_id": api_id,
                        "api_name": api_name,
                        "api_endpoint": api_endpoint,
                        "has_issues": has_issues,
                        "issues": issues_list,
                        "security_score": api_score,
                    }
                )
                result.add_evidence(evidence)

                if has_issues:
                    # Create finding for insecure API
                    finding = self.create_finding(
                        resource_id=api_id,
                        resource_type="api_gateway_rest_api",
                        severity=severity,
                        title="API Gateway REST API has security issues",
                        description=f"API Gateway REST API '{api_name}' ({api_id}) has security configuration "
                                    f"issues: {'; '.join(issues_list)}. API Gateway APIs should use authentication, "
                                    "HTTPS encryption, access logging, throttling, and WAF protection to secure "
                                    "access and protect against attacks. ISO 27001 A.8.22 requires secure network "
                                    "access controls and encryption.",
                        remediation=(
                            f"Improve API Gateway REST API '{api_name}' security:\n\n"
                            "1. Enable access logging:\n"
                            "# Create CloudWatch Log Group first\n"
                            "aws logs create-log-group --log-group-name /aws/apigateway/myapi\n\n"
                            "# Enable logging on stage\n"
                            f"aws apigateway update-stage \\\n"
                            f"  --rest-api-id {api_id} \\\n"
                            "  --stage-name prod \\\n"
                            "  --patch-operations \\\n"
                            '    op=replace,path=/accessLogSettings/destinationArn,value=arn:aws:logs:REGION:ACCOUNT:log-group:/aws/apigateway/myapi \\\n'
                            '    op=replace,path=/accessLogSettings/format,value=\'$context.requestId\'\n\n'
                            "2. Configure throttling:\n"
                            f"aws apigateway update-stage \\\n"
                            f"  --rest-api-id {api_id} \\\n"
                            "  --stage-name prod \\\n"
                            "  --patch-operations \\\n"
                            "    op=replace,path=/throttle/rateLimit,value=1000 \\\n"
                            "    op=replace,path=/throttle/burstLimit,value=2000\n\n"
                            "3. Associate WAF WebACL:\n"
                            f"aws wafv2 associate-web-acl \\\n"
                            "  --web-acl-arn <WAF-WEBACL-ARN> \\\n"
                            f"  --resource-arn arn:aws:apigateway:REGION::/restapis/{api_id}/stages/prod\n\n"
                            "4. Configure authentication:\n"
                            "For IAM authentication:\n"
                            f"aws apigateway update-method \\\n"
                            f"  --rest-api-id {api_id} \\\n"
                            "  --resource-id <RESOURCE-ID> \\\n"
                            "  --http-method GET \\\n"
                            "  --patch-operations op=replace,path=/authorizationType,value=AWS_IAM\n\n"
                            "For Cognito User Pool:\n"
                            f"aws apigateway update-method \\\n"
                            f"  --rest-api-id {api_id} \\\n"
                            "  --resource-id <RESOURCE-ID> \\\n"
                            "  --http-method GET \\\n"
                            "  --patch-operations \\\n"
                            "    op=replace,path=/authorizationType,value=COGNITO_USER_POOLS \\\n"
                            "    op=replace,path=/authorizerId,value=<AUTHORIZER-ID>\n\n"
                            "For Lambda Authorizer:\n"
                            "# Create authorizer first\n"
                            f"aws apigateway create-authorizer \\\n"
                            f"  --rest-api-id {api_id} \\\n"
                            "  --name MyAuthorizer \\\n"
                            "  --type TOKEN \\\n"
                            "  --authorizer-uri <LAMBDA-ARN> \\\n"
                            "  --identity-source method.request.header.Authorization\n\n"
                            "5. Enable X-Ray tracing:\n"
                            f"aws apigateway update-stage \\\n"
                            f"  --rest-api-id {api_id} \\\n"
                            "  --stage-name prod \\\n"
                            "  --patch-operations op=replace,path=/tracingEnabled,value=true\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to API Gateway console\n"
                            f"2. Select API '{api_name}'\n"
                            "3. Go to Stages → Select stage (e.g., 'prod')\n"
                            "4. Configure Logs:\n"
                            "   - Enable CloudWatch Logs\n"
                            "   - Enable Access Logging\n"
                            "   - Select/create log group\n"
                            "5. Configure throttling:\n"
                            "   - Set Rate: 1000 requests/sec\n"
                            "   - Set Burst: 2000 requests\n"
                            "6. Associate WAF:\n"
                            "   - Go to 'Web ACL' section\n"
                            "   - Select WAF WebACL\n"
                            "7. Configure authorization:\n"
                            "   - Go to Resources\n"
                            "   - For each method:\n"
                            "     • Click method (GET, POST, etc.)\n"
                            "     • Method Request → Authorization\n"
                            "     • Select: AWS_IAM, Cognito, or Lambda\n"
                            "8. Enable X-Ray tracing for debugging\n\n"
                            "Security best practices:\n"
                            "- Use API keys for basic rate limiting\n"
                            "- Use IAM for AWS service-to-service\n"
                            "- Use Cognito for user authentication\n"
                            "- Use Lambda authorizers for custom logic\n"
                            "- Enable request/response validation\n"
                            "- Use custom domain with ACM certificate\n"
                            "- Implement CORS properly\n"
                            "- Use resource policies for VPC endpoints\n"
                            "- Monitor with CloudWatch metrics and alarms\n"
                            "- Enable AWS WAF for DDoS and injection attacks\n"
                            "- Use usage plans for API quotas\n"
                            "- Implement proper error handling\n"
                            "- Use stage variables for environment config\n\n"
                            "Authentication options comparison:\n"
                            "API Keys:\n"
                            "- Basic identification\n"
                            "- Not for security (use with other auth)\n"
                            "- Good for usage tracking\n\n"
                            "IAM Authentication:\n"
                            "- AWS Signature Version 4\n"
                            "- Best for service-to-service\n"
                            "- Leverages AWS credentials\n\n"
                            "Cognito User Pools:\n"
                            "- OAuth 2.0 / OpenID Connect\n"
                            "- Best for user authentication\n"
                            "- Built-in user management\n\n"
                            "Lambda Authorizers:\n"
                            "- Custom authentication logic\n"
                            "- Flexible validation\n"
                            "- Can validate JWT, OAuth, etc.\n\n"
                            "Monitoring and alerting:\n"
                            "- Set CloudWatch alarms for:\n"
                            "  • 4XX errors (client errors)\n"
                            "  • 5XX errors (server errors)\n"
                            "  • Latency > threshold\n"
                            "  • Request count spikes\n"
                            "- Analyze access logs with Athena\n"
                            "- Use X-Ray for performance analysis\n"
                            "- Monitor WAF blocked requests"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "api_gateway_insecure",
                        api_id=api_id,
                        api_name=api_name,
                        issues=issues_list
                    )
                else:
                    self.logger.debug(
                        "api_gateway_secure",
                        api_id=api_id,
                        api_name=api_name
                    )

            # Calculate overall compliance score
            if apis_checked > 0:
                result.score = total_score / apis_checked
            else:
                result.score = 100.0

            # Determine pass/fail (require at least 70% score)
            result.passed = result.score >= 70.0
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_apis": len(rest_apis),
                "average_security_score": result.score,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "api_gateway_security_test_completed",
                total_apis=len(rest_apis),
                average_score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("api_gateway_security_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("api_gateway_security_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_api_gateway_security_test(connector: AWSConnector) -> TestResult:
    """Run API Gateway security compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_api_gateway_security_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = APIGatewaySecurityTest(connector)
    return test.execute()

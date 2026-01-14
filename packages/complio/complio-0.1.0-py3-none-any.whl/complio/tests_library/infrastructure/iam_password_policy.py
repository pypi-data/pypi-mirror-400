"""
IAM password policy compliance test.

Checks that AWS account has a strong IAM password policy configured.

ISO 27001 Control: A.9.4.3 - Password Management System
Requirement: Password management systems must be interactive and ensure quality passwords

Password policy requirements:
- Minimum password length >= 14 characters
- Require uppercase letters
- Require lowercase letters
- Require numbers
- Require symbols
- Password expiration <= 90 days
- Password reuse prevention (>= 5 passwords)

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.iam_password_policy import IAMPasswordPolicyTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = IAMPasswordPolicyTest(connector)
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


class IAMPasswordPolicyTest(ComplianceTest):
    """Test for IAM password policy compliance.

    Verifies that AWS account has a strong password policy configured.

    Compliance Requirements (ISO 27001 A.9.4.3):
        - Minimum password length >= 14 characters
        - Require at least one uppercase letter
        - Require at least one lowercase letter
        - Require at least one number
        - Require at least one symbol
        - Password expiration <= 90 days
        - Prevent password reuse (>= 5 previous passwords)
        - Require password change on first login

    Scoring:
        - 100% if all requirements are met
        - Deductions for each missing requirement
        - Critical failure if minimum length < 8

    Example:
        >>> test = IAMPasswordPolicyTest(connector)
        >>> result = test.run()
        >>> if not result.passed:
        ...     for finding in result.findings:
        ...         print(f"{finding.title}: {finding.description}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize IAM password policy test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="iam_password_policy",
            test_name="IAM Password Policy Compliance",
            description="Verifies that a strong password policy is configured requiring minimum length, complexity, expiration, and reuse prevention (account-wide)",
            control_id="A.9.4.3",
            connector=connector,
            scope="global",
        )
        self.logger = get_logger(__name__)

    def execute(self) -> TestResult:
        """Execute the IAM password policy compliance test.

        Returns:
            TestResult with findings and evidence

        Raises:
            AWSConnectionError: If unable to connect to AWS
            AWSCredentialsError: If credentials are invalid
        """
        self.logger.info(
            "starting_iam_password_policy_test",
            region=self.connector.region,
        )

        findings: List[Finding] = []
        evidence_list: List[Evidence] = []

        try:
            # Get IAM client (IAM is global, but we use connector's region)
            iam_client = self.connector.get_client("iam")

            # Get account password policy
            try:
                response = iam_client.get_account_password_policy()
                policy = response.get("PasswordPolicy", {})
                policy_exists = True
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") == "NoSuchEntity":
                    # No password policy configured
                    policy = {}
                    policy_exists = False
                else:
                    raise

            # Create evidence
            evidence = Evidence(
                resource_id="aws-account",
                resource_type="iam_password_policy",
                region=self.connector.region,
                data={
                    "policy_exists": policy_exists,
                    "minimum_password_length": policy.get("MinimumPasswordLength", 0),
                    "require_uppercase": policy.get("RequireUppercaseCharacters", False),
                    "require_lowercase": policy.get("RequireLowercaseCharacters", False),
                    "require_numbers": policy.get("RequireNumbers", False),
                    "require_symbols": policy.get("RequireSymbols", False),
                    "max_password_age": policy.get("MaxPasswordAge", None),
                    "password_reuse_prevention": policy.get("PasswordReusePrevention", 0),
                    "hard_expiry": policy.get("HardExpiry", False),
                },
            )
            evidence_list.append(evidence)

            # If no policy exists, this is a critical failure
            if not policy_exists:
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.CRITICAL,
                        title="No IAM password policy configured",
                        description=(
                            "The AWS account does not have an IAM password policy configured. "
                            "This allows users to set weak passwords, violating ISO 27001 A.9.4.3. "
                            "Users could set passwords like '12345' or 'password', creating "
                            "a severe security risk."
                        ),
                        remediation=(
                            "Configure an IAM password policy:\n"
                            "1. Go to IAM Console → Account Settings\n"
                            "2. Click 'Set password policy'\n"
                            "3. Enable all recommended settings:\n"
                            "   - Minimum length: 14 characters\n"
                            "   - Require uppercase, lowercase, numbers, symbols\n"
                            "   - Password expiration: 90 days\n"
                            "   - Prevent reuse of last 5 passwords\n"
                            "   - Require administrator reset on first login"
                        ),
                        iso27001_control="A.9.4.3",
                    )
                )

                return TestResult(
                    test_id=self.test_id,
                    test_name=self.test_name,
                    status=TestStatus.FAILED,
                    passed=False,
                    score=0.0,
                    findings=findings,
                    evidence=evidence_list,
                    metadata={
                        "region": self.connector.region,
                        "policy_exists": False,
                        "iso27001_control": "A.9.4.3",
                    },
                )

            # Check each requirement
            score_deductions = 0
            requirements_met = 0
            total_requirements = 8

            # 1. Minimum password length (>= 14)
            min_length = policy.get("MinimumPasswordLength", 0)
            if min_length < 8:
                score_deductions += 50  # Critical - very weak passwords
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.CRITICAL,
                        title="Password minimum length too short",
                        description=(
                            f"Minimum password length is {min_length} characters, which is "
                            f"critically insufficient. NIST recommends minimum 8 characters, "
                            f"ISO 27001 best practice recommends 14+ characters."
                        ),
                        remediation=f"Increase MinimumPasswordLength to at least 14 (current: {min_length})",
                        iso27001_control="A.9.4.3",
                        metadata={"current_value": min_length, "required_value": 14},
                    )
                )
            elif min_length < 14:
                score_deductions += 15
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.MEDIUM,
                        title="Password minimum length below best practice",
                        description=(
                            f"Minimum password length is {min_length} characters. "
                            f"While above critical threshold, ISO 27001 best practice recommends 14+ characters."
                        ),
                        remediation=f"Increase MinimumPasswordLength to 14 (current: {min_length})",
                        iso27001_control="A.9.4.3",
                        metadata={"current_value": min_length, "required_value": 14},
                    )
                )
            else:
                requirements_met += 1

            # 2. Require uppercase
            if not policy.get("RequireUppercaseCharacters", False):
                score_deductions += 10
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.MEDIUM,
                        title="Password policy doesn't require uppercase letters",
                        description="Passwords can be created without uppercase letters, reducing password complexity.",
                        remediation="Enable RequireUppercaseCharacters in password policy",
                        iso27001_control="A.9.4.3",
                    )
                )
            else:
                requirements_met += 1

            # 3. Require lowercase
            if not policy.get("RequireLowercaseCharacters", False):
                score_deductions += 10
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.MEDIUM,
                        title="Password policy doesn't require lowercase letters",
                        description="Passwords can be created without lowercase letters, reducing password complexity.",
                        remediation="Enable RequireLowercaseCharacters in password policy",
                        iso27001_control="A.9.4.3",
                    )
                )
            else:
                requirements_met += 1

            # 4. Require numbers
            if not policy.get("RequireNumbers", False):
                score_deductions += 10
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.MEDIUM,
                        title="Password policy doesn't require numbers",
                        description="Passwords can be created without numbers, reducing password complexity.",
                        remediation="Enable RequireNumbers in password policy",
                        iso27001_control="A.9.4.3",
                    )
                )
            else:
                requirements_met += 1

            # 5. Require symbols
            if not policy.get("RequireSymbols", False):
                score_deductions += 10
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.MEDIUM,
                        title="Password policy doesn't require symbols",
                        description="Passwords can be created without special characters, reducing password complexity.",
                        remediation="Enable RequireSymbols in password policy",
                        iso27001_control="A.9.4.3",
                    )
                )
            else:
                requirements_met += 1

            # 6. Password expiration (<=90 days)
            max_age = policy.get("MaxPasswordAge")
            if max_age is None or max_age == 0:
                score_deductions += 15
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.HIGH,
                        title="Passwords never expire",
                        description=(
                            "Password policy does not enforce password expiration. "
                            "Passwords should be rotated regularly to limit exposure from compromised credentials."
                        ),
                        remediation="Set MaxPasswordAge to 90 days or less",
                        iso27001_control="A.9.4.3",
                    )
                )
            elif max_age > 90:
                score_deductions += 10
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.MEDIUM,
                        title="Password expiration too long",
                        description=(
                            f"Passwords expire after {max_age} days. "
                            f"ISO 27001 best practice recommends password rotation every 90 days or less."
                        ),
                        remediation=f"Reduce MaxPasswordAge to 90 or less (current: {max_age})",
                        iso27001_control="A.9.4.3",
                        metadata={"current_value": max_age, "required_value": 90},
                    )
                )
            else:
                requirements_met += 1

            # 7. Password reuse prevention (>=5)
            reuse_prevention = policy.get("PasswordReusePrevention", 0)
            if reuse_prevention == 0:
                score_deductions += 15
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.HIGH,
                        title="Password reuse not prevented",
                        description=(
                            "Users can reuse old passwords immediately. This allows users to "
                            "rotate back to previously compromised passwords."
                        ),
                        remediation="Set PasswordReusePrevention to 5 or more",
                        iso27001_control="A.9.4.3",
                    )
                )
            elif reuse_prevention < 5:
                score_deductions += 10
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.MEDIUM,
                        title="Password reuse prevention too low",
                        description=(
                            f"Password policy prevents reuse of last {reuse_prevention} passwords. "
                            f"Best practice recommends preventing reuse of at least 5 previous passwords."
                        ),
                        remediation=f"Increase PasswordReusePrevention to 5 or more (current: {reuse_prevention})",
                        iso27001_control="A.9.4.3",
                        metadata={"current_value": reuse_prevention, "required_value": 5},
                    )
                )
            else:
                requirements_met += 1

            # 8. Expire passwords (HardExpiry)
            if not policy.get("HardExpiry", False):
                score_deductions += 5
                findings.append(
                    Finding(
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.LOW,
                        title="Hard expiry not enabled",
                        description=(
                            "Password hard expiry is not enabled. Users can continue using expired passwords "
                            "if they don't log into the console."
                        ),
                        remediation="Enable HardExpiry in password policy",
                        iso27001_control="A.9.4.3",
                    )
                )
            else:
                requirements_met += 1

            # Calculate final score
            score = max(0.0, 100.0 - score_deductions)

            if score >= 90:
                status = TestStatus.PASSED
                passed = True
            elif score >= 70:
                status = TestStatus.WARNING
                passed = False
            else:
                status = TestStatus.FAILED
                passed = False

            self.logger.info(
                "iam_password_policy_test_complete",
                requirements_met=requirements_met,
                total_requirements=total_requirements,
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
                    "policy_exists": policy_exists,
                    "requirements_met": requirements_met,
                    "total_requirements": total_requirements,
                    "iso27001_control": "A.9.4.3",
                },
            )

        except ClientError as e:
            self.logger.error(
                "iam_password_policy_test_failed",
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
                        resource_id="aws-account",
                        resource_type="iam_password_policy",
                        severity=Severity.HIGH,
                        title="Failed to check IAM password policy",
                        description=f"Error accessing IAM: {str(e)}",
                        remediation="Check AWS credentials and permissions. Ensure IAM policy allows iam:GetAccountPasswordPolicy",
                        iso27001_control="A.9.4.3",
                    )
                ],
                evidence=[],
                metadata={"error": str(e)},
            )

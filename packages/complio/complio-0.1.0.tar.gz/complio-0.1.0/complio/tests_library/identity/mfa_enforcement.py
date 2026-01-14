"""
MFA enforcement compliance test.

Checks that all IAM users have MFA (Multi-Factor Authentication) enabled.

ISO 27001 Control: A.8.5 - Access control
Requirement: Multi-factor authentication for user access

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.identity.mfa_enforcement import MFAEnforcementTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = MFAEnforcementTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

import csv
import io
import time
from typing import Any, Dict

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Severity,
    TestResult,
    TestStatus,
)


class MFAEnforcementTest(ComplianceTest):
    """Test for MFA enforcement compliance.

    Verifies that all IAM users have MFA enabled by parsing the
    IAM credential report.

    Compliance Requirements:
        - All IAM users must have MFA enabled
        - Users without MFA are vulnerable to credential compromise
        - Password-based access requires MFA protection

    Scoring:
        - 100% if all users have MFA enabled
        - Proportional score based on MFA-enabled/total ratio
        - 0% if no users have MFA enabled

    Example:
        >>> test = MFAEnforcementTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize MFA enforcement test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="mfa_enforcement",
            test_name="IAM MFA Enforcement Check",
            description="Verify all IAM users have MFA (Multi-Factor Authentication) enabled",
            control_id="A.8.5",
            connector=connector,
            scope="global",
        )

    def execute(self) -> TestResult:
        """Execute MFA enforcement compliance test.

        Returns:
            TestResult with findings for users without MFA

        Example:
            >>> test = MFAEnforcementTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            92.5
        """
        result = TestResult(
            test_id=self.test_id,
            test_name=self.test_name,
            status=TestStatus.PASSED,
            passed=True,
            score=100.0,
        )

        try:
            # Get IAM client
            iam_client = self.connector.get_client("iam")

            # Generate credential report (may need to wait)
            self.logger.info("generating_credential_report")
            report_ready = self._generate_credential_report(iam_client)

            if not report_ready:
                self.logger.error("credential_report_generation_failed")
                result.status = TestStatus.ERROR
                result.passed = False
                result.score = 0.0
                result.error_message = "Failed to generate IAM credential report after retries"
                return result

            # Get credential report
            self.logger.info("retrieving_credential_report")
            report_response = iam_client.get_credential_report()
            report_content = report_response["Content"]

            # Parse CSV report
            report_csv = report_content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(report_csv))

            users_with_mfa = 0
            total_users = 0
            root_user_checked = False

            for row in csv_reader:
                user_name = row.get("user", "")

                # Skip root account (checked in separate test)
                if user_name == "<root_account>":
                    root_user_checked = True
                    continue

                # Check if user has console access (password enabled)
                password_enabled = row.get("password_enabled", "false") == "true"

                # If no console password, MFA is not required
                if not password_enabled:
                    self.logger.debug("user_no_console_access", user=user_name)
                    continue

                total_users += 1
                result.resources_scanned += 1

                # Check MFA status
                mfa_active = row.get("mfa_active", "false") == "true"

                # Get user creation date and last login
                user_creation_time = row.get("user_creation_time", "")
                password_last_used = row.get("password_last_used", "no_information")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=user_name,
                    resource_type="iam_user",
                    data={
                        "user_name": user_name,
                        "mfa_active": mfa_active,
                        "password_enabled": password_enabled,
                        "user_creation_time": user_creation_time,
                        "password_last_used": password_last_used,
                        "access_key_1_active": row.get("access_key_1_active", "false") == "true",
                        "access_key_2_active": row.get("access_key_2_active", "false") == "true",
                    }
                )
                result.add_evidence(evidence)

                if mfa_active:
                    users_with_mfa += 1
                    self.logger.debug(
                        "user_has_mfa",
                        user=user_name
                    )
                else:
                    # Create finding for user without MFA
                    finding = self.create_finding(
                        resource_id=user_name,
                        resource_type="iam_user",
                        severity=Severity.HIGH,
                        title="IAM user does not have MFA enabled",
                        description=f"IAM user '{user_name}' has console access (password enabled) but does not have "
                                    "Multi-Factor Authentication (MFA) enabled. This leaves the account vulnerable to "
                                    "credential compromise through phishing, password leaks, or brute force attacks. "
                                    f"User was created on {user_creation_time} and last used password on {password_last_used}. "
                                    "ISO 27001 A.8.5 requires multi-factor authentication for privileged access.",
                        remediation=(
                            f"Enable MFA for IAM user '{user_name}':\n\n"
                            "User must enable MFA themselves:\n"
                            "1. Sign in to AWS Console as the user\n"
                            "2. Go to IAM → Users → Your username → Security credentials\n"
                            "3. Under 'Multi-factor authentication (MFA)', click 'Assign MFA device'\n"
                            "4. Choose virtual MFA device (Google Authenticator, Authy, etc.)\n"
                            "5. Scan QR code with authenticator app\n"
                            "6. Enter two consecutive MFA codes to verify\n\n"
                            "Administrator can enforce MFA:\n"
                            "1. Create IAM policy requiring MFA for API calls\n"
                            "2. Attach policy to users or groups\n"
                            "3. Set up console login with MFA requirement\n\n"
                            f"Or use AWS CLI to check MFA devices:\n"
                            f"aws iam list-mfa-devices --user-name {user_name}\n\n"
                            "Best practice: Enforce MFA for all users with console access."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "user_without_mfa",
                        user=user_name,
                        password_last_used=password_last_used
                    )

            if total_users == 0:
                self.logger.info("no_users_with_console_access")
                result.metadata["message"] = "No IAM users with console access found"
                return result

            # Calculate compliance score
            result.score = (users_with_mfa / total_users) * 100

            # Determine pass/fail
            result.passed = users_with_mfa == total_users
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_users_with_console_access": total_users,
                "users_with_mfa": users_with_mfa,
                "users_without_mfa": total_users - users_with_mfa,
                "compliance_percentage": result.score,
                "root_user_checked": root_user_checked,
            }

            self.logger.info(
                "mfa_enforcement_test_completed",
                total_users=total_users,
                with_mfa=users_with_mfa,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("mfa_enforcement_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("mfa_enforcement_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result

    def _generate_credential_report(self, iam_client: Any, max_retries: int = 3, retry_delay: int = 5) -> bool:
        """Generate IAM credential report with retry logic.

        Args:
            iam_client: Boto3 IAM client
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds

        Returns:
            True if report is ready, False otherwise
        """
        for attempt in range(max_retries):
            try:
                response = iam_client.generate_credential_report()
                state = response.get("State")

                if state == "COMPLETE":
                    self.logger.info("credential_report_ready")
                    return True
                elif state == "INPROGRESS":
                    self.logger.info(
                        "credential_report_generating",
                        attempt=attempt + 1,
                        max_retries=max_retries
                    )
                    time.sleep(retry_delay)
                else:
                    self.logger.warning("credential_report_unexpected_state", state=state)
                    time.sleep(retry_delay)

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                if error_code == "LimitExceededException":
                    self.logger.warning("credential_report_rate_limited", attempt=attempt + 1)
                    time.sleep(retry_delay)
                else:
                    raise

        # Final check
        try:
            response = iam_client.generate_credential_report()
            return response.get("State") == "COMPLETE"
        except Exception:
            return False


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_mfa_enforcement_test(connector: AWSConnector) -> TestResult:
    """Run MFA enforcement compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_mfa_enforcement_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = MFAEnforcementTest(connector)
    return test.execute()

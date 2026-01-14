"""
Root account protection compliance test.

Checks multiple security controls for the AWS root account.

ISO 27001 Control: A.8.2 - Privileged access rights
Requirement: Root account must be properly secured

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.identity.root_account_protection import RootAccountProtectionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = RootAccountProtectionTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

import csv
import io
import time
from datetime import datetime, timezone
from typing import Any, Dict

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Severity,
    TestResult,
    TestStatus,
)


class RootAccountProtectionTest(ComplianceTest):
    """Test for root account protection compliance.

    Performs multiple checks on the AWS root account:
    1. Root account has MFA enabled (CRITICAL)
    2. Root account has no access keys (HIGH)
    3. Root account not used recently (MEDIUM if used in last 90 days)

    Compliance Requirements:
        - Root MFA must be enabled
        - Root access keys must not exist
        - Root account should not be used for day-to-day operations

    Scoring:
        - MFA enabled: 50 points
        - No access keys: 30 points
        - Not used recently: 20 points
        - Total: 100 points

    Example:
        >>> test = RootAccountProtectionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize root account protection test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="root_account_protection",
            test_name="Root Account Protection Check",
            description="Verify root account has MFA, no access keys, and is not used regularly",
            control_id="A.8.2",
            connector=connector,
            scope="global",
        )

    def execute(self) -> TestResult:
        """Execute root account protection compliance test.

        Returns:
            TestResult with findings for root account security issues

        Example:
            >>> test = RootAccountProtectionTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            70.0
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

            # Initialize score components
            mfa_score = 0  # 50 points
            access_keys_score = 0  # 30 points
            usage_score = 0  # 20 points

            # Check 1: Root account MFA status
            self.logger.info("checking_root_mfa_status")
            root_mfa_enabled = self._check_root_mfa(iam_client, result)

            if root_mfa_enabled:
                mfa_score = 50
                self.logger.info("root_mfa_enabled")
            else:
                self.logger.error("root_mfa_disabled")
                # Finding already created in _check_root_mfa

            # Check 2: Root access keys
            self.logger.info("checking_root_access_keys")
            has_access_keys, access_key_details = self._check_root_access_keys(iam_client, result)

            if not has_access_keys:
                access_keys_score = 30
                self.logger.info("root_no_access_keys")
            else:
                self.logger.warning("root_has_access_keys", details=access_key_details)
                # Finding already created in _check_root_access_keys

            # Check 3: Root account usage
            self.logger.info("checking_root_usage")
            recently_used, last_used = self._check_root_usage(iam_client, result)

            if not recently_used:
                usage_score = 20
                self.logger.info("root_not_recently_used", last_used=last_used)
            else:
                self.logger.warning("root_recently_used", last_used=last_used)
                # Finding already created in _check_root_usage

            # Calculate total score
            result.score = mfa_score + access_keys_score + usage_score
            result.resources_scanned = 1  # Root account

            # Determine pass/fail (require all checks to pass)
            result.passed = result.score == 100
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "root_mfa_enabled": root_mfa_enabled,
                "root_has_access_keys": has_access_keys,
                "root_recently_used": recently_used,
                "root_last_used": last_used,
                "mfa_score": mfa_score,
                "access_keys_score": access_keys_score,
                "usage_score": usage_score,
                "total_score": result.score,
            }

            self.logger.info(
                "root_account_protection_test_completed",
                score=result.score,
                passed=result.passed,
                mfa=root_mfa_enabled,
                access_keys=has_access_keys,
                recently_used=recently_used
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("root_account_protection_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("root_account_protection_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result

    def _check_root_mfa(self, iam_client: Any, result: TestResult) -> bool:
        """Check if root account has MFA enabled.

        Args:
            iam_client: Boto3 IAM client
            result: TestResult to add findings to

        Returns:
            True if MFA is enabled, False otherwise
        """
        try:
            summary = iam_client.get_account_summary()
            account_mfa_enabled = summary.get("SummaryMap", {}).get("AccountMFAEnabled", 0)

            mfa_enabled = account_mfa_enabled == 1

            if not mfa_enabled:
                finding = self.create_finding(
                    resource_id="root_account",
                    resource_type="aws_account",
                    severity=Severity.CRITICAL,
                    title="Root account MFA not enabled",
                    description="The AWS root account does not have Multi-Factor Authentication (MFA) enabled. "
                                "The root account has unrestricted access to all resources and services. "
                                "Without MFA, the account is vulnerable to credential compromise. "
                                "If root credentials are stolen, attackers gain complete control of the AWS account. "
                                "ISO 27001 A.8.2 requires strong protection for privileged accounts.",
                    remediation=(
                        "Enable MFA for the root account immediately:\n\n"
                        "1. Sign in to AWS Console as root user\n"
                        "2. Click on account name → Security credentials\n"
                        "3. Under 'Multi-factor authentication (MFA)', click 'Assign MFA device'\n"
                        "4. Choose virtual MFA device (recommended) or hardware MFA device\n"
                        "5. For virtual MFA:\n"
                        "   - Install an authenticator app (Google Authenticator, Authy, etc.)\n"
                        "   - Scan the QR code\n"
                        "   - Enter two consecutive MFA codes\n"
                        "6. Securely store MFA recovery codes\n\n"
                        "Best practices:\n"
                        "- Use hardware MFA device for maximum security\n"
                        "- Store recovery codes in secure offline location\n"
                        "- Never share MFA device or recovery codes\n"
                        "- Avoid using root account for day-to-day operations"
                    ),
                    evidence=self.create_evidence(
                        resource_id="root_account",
                        resource_type="aws_account",
                        data={"mfa_enabled": mfa_enabled, "check": "root_mfa"}
                    )
                )
                result.add_finding(finding)

            return mfa_enabled

        except Exception as e:
            self.logger.error("root_mfa_check_error", error=str(e))
            return False

    def _check_root_access_keys(self, iam_client: Any, result: TestResult) -> tuple:
        """Check if root account has access keys.

        Args:
            iam_client: Boto3 IAM client
            result: TestResult to add findings to

        Returns:
            Tuple of (has_keys: bool, key_details: dict)
        """
        try:
            # Generate credential report to check root access keys
            self._generate_credential_report(iam_client)

            report_response = iam_client.get_credential_report()
            report_content = report_response["Content"]
            report_csv = report_content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(report_csv))

            for row in csv_reader:
                if row.get("user") == "<root_account>":
                    key1_active = row.get("access_key_1_active", "false") == "true"
                    key2_active = row.get("access_key_2_active", "false") == "true"

                    has_keys = key1_active or key2_active

                    if has_keys:
                        active_keys = []
                        if key1_active:
                            active_keys.append("access_key_1")
                        if key2_active:
                            active_keys.append("access_key_2")

                        finding = self.create_finding(
                            resource_id="root_account",
                            resource_type="aws_account",
                            severity=Severity.HIGH,
                            title="Root account has active access keys",
                            description=f"The AWS root account has {len(active_keys)} active access key(s): "
                                        f"{', '.join(active_keys)}. Root account access keys provide "
                                        "unrestricted access to all AWS resources and should never exist. "
                                        "If these keys are leaked or compromised, attackers gain full control. "
                                        "ISO 27001 A.8.2 requires minimizing use of highly privileged credentials.",
                            remediation=(
                                "Delete root account access keys immediately:\n\n"
                                "1. Sign in to AWS Console as root user\n"
                                "2. Click on account name → Security credentials\n"
                                "3. Under 'Access keys', locate the active keys\n"
                                "4. Click 'Delete' for each access key\n"
                                "5. Confirm deletion\n\n"
                                "If you need programmatic access:\n"
                                "1. Create IAM users with specific permissions\n"
                                "2. Use IAM roles for EC2 instances and Lambda functions\n"
                                "3. Enable AWS Organizations for multi-account management\n"
                                "4. Never use root access keys for any purpose\n\n"
                                "CRITICAL: If root keys were exposed:\n"
                                "1. Delete keys immediately\n"
                                "2. Check CloudTrail for unauthorized activity\n"
                                "3. Review all resources for changes\n"
                                "4. Contact AWS Support if compromise is suspected"
                            ),
                            evidence=self.create_evidence(
                                resource_id="root_account",
                                resource_type="aws_account",
                                data={
                                    "access_key_1_active": key1_active,
                                    "access_key_2_active": key2_active,
                                    "check": "root_access_keys"
                                }
                            )
                        )
                        result.add_finding(finding)

                    return has_keys, {"key1": key1_active, "key2": key2_active}

            return False, {}

        except Exception as e:
            self.logger.error("root_access_keys_check_error", error=str(e))
            return False, {}

    def _check_root_usage(self, iam_client: Any, result: TestResult) -> tuple:
        """Check when root account was last used.

        Args:
            iam_client: Boto3 IAM client
            result: TestResult to add findings to

        Returns:
            Tuple of (recently_used: bool, last_used: str)
        """
        try:
            # Get credential report for root usage info
            self._generate_credential_report(iam_client)

            report_response = iam_client.get_credential_report()
            report_content = report_response["Content"]
            report_csv = report_content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(report_csv))

            for row in csv_reader:
                if row.get("user") == "<root_account>":
                    password_last_used = row.get("password_last_used", "no_information")

                    if password_last_used == "no_information" or password_last_used == "N/A":
                        # Root has never been used (good)
                        return False, "never"

                    # Parse last used date
                    try:
                        last_used_date = datetime.fromisoformat(password_last_used.replace("Z", "+00:00"))
                        now = datetime.now(timezone.utc)
                        days_since_use = (now - last_used_date).days

                        recently_used = days_since_use < 90

                        if recently_used:
                            finding = self.create_finding(
                                resource_id="root_account",
                                resource_type="aws_account",
                                severity=Severity.MEDIUM,
                                title=f"Root account used recently ({days_since_use} days ago)",
                                description=f"The AWS root account was last used {days_since_use} days ago "
                                            f"(on {password_last_used}). Root account should only be used for "
                                            "account and service management tasks that cannot be performed by IAM users. "
                                            "Regular use of root account increases risk of credential compromise. "
                                            "ISO 27001 A.8.2 requires limiting use of privileged accounts.",
                                remediation=(
                                    "Minimize root account usage:\n\n"
                                    "1. Create IAM users with appropriate permissions for day-to-day tasks\n"
                                    "2. Use IAM roles for service-to-service access\n"
                                    "3. Enable AWS Organizations for centralized management\n"
                                    "4. Use IAM users for administrative tasks\n\n"
                                    "Root account should only be used for:\n"
                                    "- Changing account settings\n"
                                    "- Closing the account\n"
                                    "- Restoring IAM user permissions\n"
                                    "- Managing AWS support plan\n"
                                    "- Tasks specifically requiring root access\n\n"
                                    "Best practices:\n"
                                    "- Lock away root credentials securely\n"
                                    "- Enable MFA on root account\n"
                                    "- Monitor root account usage via CloudTrail\n"
                                    "- Set up SNS alerts for root account activity"
                                ),
                                evidence=self.create_evidence(
                                    resource_id="root_account",
                                    resource_type="aws_account",
                                    data={
                                        "password_last_used": password_last_used,
                                        "days_since_use": days_since_use,
                                        "check": "root_usage"
                                    }
                                )
                            )
                            result.add_finding(finding)

                        return recently_used, password_last_used

                    except Exception as e:
                        self.logger.error("parse_last_used_date_error", error=str(e))
                        return False, password_last_used

            return False, "unknown"

        except Exception as e:
            self.logger.error("root_usage_check_error", error=str(e))
            return False, "error"

    def _generate_credential_report(self, iam_client: Any, max_retries: int = 3) -> bool:
        """Generate IAM credential report with retry logic.

        Args:
            iam_client: Boto3 IAM client
            max_retries: Maximum number of retries

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                response = iam_client.generate_credential_report()
                state = response.get("State")

                if state == "COMPLETE":
                    return True
                elif state == "INPROGRESS":
                    time.sleep(5)
                else:
                    time.sleep(5)

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                if error_code == "LimitExceededException":
                    time.sleep(5)
                else:
                    raise

        return False


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_root_account_protection_test(connector: AWSConnector) -> TestResult:
    """Run root account protection compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_root_account_protection_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = RootAccountProtectionTest(connector)
    return test.execute()

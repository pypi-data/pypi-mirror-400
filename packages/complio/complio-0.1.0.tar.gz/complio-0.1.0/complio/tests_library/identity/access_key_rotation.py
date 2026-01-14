"""
IAM access key rotation compliance test.

Checks that all IAM access keys are rotated regularly (< 90 days).

ISO 27001 Control: A.8.5 - Access control
Requirement: Access credentials must be rotated regularly

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.identity.access_key_rotation import AccessKeyRotationTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = AccessKeyRotationTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

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


class AccessKeyRotationTest(ComplianceTest):
    """Test for IAM access key rotation compliance.

    Verifies that all IAM access keys are rotated regularly.
    Keys older than 90 days are flagged.

    Compliance Requirements:
        - Access keys should be < 90 days old (COMPLIANT)
        - Access keys 90-180 days old (MEDIUM severity)
        - Access keys > 180 days old (HIGH severity)

    Scoring:
        - 100% if all keys are < 90 days old
        - Proportional score based on compliant/total ratio
        - 0% if no keys are compliant

    Example:
        >>> test = AccessKeyRotationTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize access key rotation test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="access_key_rotation",
            test_name="IAM Access Key Rotation Check",
            description="Verify all IAM access keys are rotated regularly (< 90 days)",
            control_id="A.8.5",
            connector=connector,
            scope="global",
        )

    def execute(self) -> TestResult:
        """Execute access key rotation compliance test.

        Returns:
            TestResult with findings for old access keys

        Example:
            >>> test = AccessKeyRotationTest(connector)
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
            # Get IAM client
            iam_client = self.connector.get_client("iam")

            # List all users
            self.logger.info("listing_iam_users")
            users = []

            paginator = iam_client.get_paginator("list_users")
            for page in paginator.paginate():
                users.extend(page.get("Users", []))

            if not users:
                self.logger.info("no_iam_users_found")
                result.metadata["message"] = "No IAM users found in account"
                return result

            self.logger.info("iam_users_found", count=len(users))

            # Check access keys for each user
            total_keys = 0
            compliant_keys = 0
            now = datetime.now(timezone.utc)

            for user in users:
                user_name = user["UserName"]

                # List access keys for user
                try:
                    keys_response = iam_client.list_access_keys(UserName=user_name)
                    access_keys = keys_response.get("AccessKeyMetadata", [])

                    for access_key in access_keys:
                        access_key_id = access_key["AccessKeyId"]
                        create_date = access_key["CreateDate"]
                        status = access_key["Status"]

                        # Skip inactive keys
                        if status != "Active":
                            self.logger.debug("skipping_inactive_key", access_key_id=access_key_id, user=user_name)
                            continue

                        total_keys += 1
                        result.resources_scanned += 1

                        # Calculate age
                        age_delta = now - create_date
                        age_days = age_delta.days

                        # Determine severity based on age
                        if age_days <= 90:
                            compliant = True
                            severity = None
                        elif age_days <= 180:
                            compliant = False
                            severity = Severity.MEDIUM
                        else:
                            compliant = False
                            severity = Severity.HIGH

                        # Create evidence
                        evidence = self.create_evidence(
                            resource_id=access_key_id,
                            resource_type="iam_access_key",
                            data={
                                "access_key_id": access_key_id,
                                "user_name": user_name,
                                "create_date": create_date.isoformat(),
                                "age_days": age_days,
                                "status": status,
                                "compliant": compliant,
                            }
                        )
                        result.add_evidence(evidence)

                        if compliant:
                            compliant_keys += 1
                            self.logger.debug(
                                "access_key_compliant",
                                access_key_id=access_key_id,
                                user=user_name,
                                age_days=age_days
                            )
                        else:
                            # Create finding for old access key
                            finding = self.create_finding(
                                resource_id=access_key_id,
                                resource_type="iam_access_key",
                                severity=severity,
                                title=f"IAM access key not rotated ({age_days} days old)",
                                description=f"Access key '{access_key_id}' for user '{user_name}' is {age_days} days old. "
                                            f"Keys should be rotated every 90 days. This key has not been rotated in "
                                            f"{age_days // 30} months. Old credentials increase the risk of unauthorized access. "
                                            "ISO 27001 A.8.5 requires regular rotation of access credentials.",
                                remediation=(
                                    f"Rotate access key for user '{user_name}':\n\n"
                                    "1. Create a new access key:\n"
                                    f"   aws iam create-access-key --user-name {user_name}\n\n"
                                    "2. Update all applications/services using the old key\n"
                                    "   with the new access key ID and secret access key\n\n"
                                    "3. Test that applications work with the new key\n\n"
                                    "4. Deactivate the old key (don't delete yet):\n"
                                    f"   aws iam update-access-key --user-name {user_name} \\\n"
                                    f"     --access-key-id {access_key_id} --status Inactive\n\n"
                                    "5. Monitor for a few days to ensure no errors\n\n"
                                    "6. Delete the old key:\n"
                                    f"   aws iam delete-access-key --user-name {user_name} \\\n"
                                    f"     --access-key-id {access_key_id}\n\n"
                                    "Or use AWS Console:\n"
                                    "1. Go to IAM → Users\n"
                                    f"2. Select user '{user_name}'\n"
                                    "3. Go to 'Security credentials' tab\n"
                                    "4. Click 'Create access key'\n"
                                    "5. Update applications with new key\n"
                                    f"6. Deactivate and delete old key '{access_key_id}'\n\n"
                                    "Best practice: Rotate keys every 90 days."
                                ),
                                evidence=evidence
                            )
                            result.add_finding(finding)

                            self.logger.warning(
                                "access_key_rotation_overdue",
                                access_key_id=access_key_id,
                                user=user_name,
                                age_days=age_days,
                                severity=severity.value
                            )

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code")
                    self.logger.warning(
                        "user_access_keys_list_error",
                        user=user_name,
                        error_code=error_code
                    )
                    continue

            if total_keys == 0:
                self.logger.info("no_active_access_keys_found")
                result.metadata["message"] = "No active IAM access keys found in account"
                return result

            # Calculate compliance score
            result.score = (compliant_keys / total_keys) * 100

            # Determine pass/fail
            result.passed = compliant_keys == total_keys
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_users": len(users),
                "total_active_keys": total_keys,
                "compliant_keys": compliant_keys,
                "non_compliant_keys": total_keys - compliant_keys,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "access_key_rotation_test_completed",
                total_keys=total_keys,
                compliant=compliant_keys,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("access_key_rotation_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("access_key_rotation_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_access_key_rotation_test(connector: AWSConnector) -> TestResult:
    """Run IAM access key rotation compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_access_key_rotation_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = AccessKeyRotationTest(connector)
    return test.execute()

"""
CloudWatch Logs encryption compliance test.

Checks that all CloudWatch log groups use encryption at rest with KMS.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: Log groups must be encrypted with KMS keys

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.logging.cloudwatch_logs_encryption import CloudWatchLogsEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = CloudWatchLogsEncryptionTest(connector)
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


class CloudWatchLogsEncryptionTest(ComplianceTest):
    """Test for CloudWatch Logs encryption compliance.

    Verifies that all CloudWatch log groups use server-side encryption
    with AWS KMS keys to protect log data at rest.

    Compliance Requirements:
        - All log groups must have kmsKeyId configured
        - Encryption protects sensitive log data
        - Customer-managed KMS keys recommended for audit trail

    Scoring:
        - 100% if all log groups are encrypted
        - Proportional score based on compliant/total ratio
        - 100% if no log groups exist

    Example:
        >>> test = CloudWatchLogsEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize CloudWatch Logs encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="cloudwatch_logs_encryption",
            test_name="CloudWatch Logs Encryption Check",
            description="Verify all CloudWatch log groups use encryption at rest with KMS",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute CloudWatch Logs encryption compliance test.

        Returns:
            TestResult with findings for unencrypted log groups

        Example:
            >>> test = CloudWatchLogsEncryptionTest(connector)
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
            # Get CloudWatch Logs client
            logs_client = self.connector.get_client("logs")

            # List all log groups
            self.logger.info("listing_log_groups")
            log_groups = []

            paginator = logs_client.get_paginator("describe_log_groups")
            for page in paginator.paginate():
                log_groups.extend(page.get("logGroups", []))

            if not log_groups:
                self.logger.info("no_log_groups_found")
                result.metadata["message"] = "No CloudWatch log groups found in region"
                return result

            self.logger.info("log_groups_found", count=len(log_groups))

            # Check encryption for each log group
            encrypted_count = 0

            for log_group in log_groups:
                log_group_name = log_group["logGroupName"]
                result.resources_scanned += 1

                # Check if KMS key is configured
                kms_key_id = log_group.get("kmsKeyId")
                is_encrypted = kms_key_id is not None and kms_key_id != ""

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=log_group_name,
                    resource_type="cloudwatch_log_group",
                    data={
                        "log_group_name": log_group_name,
                        "kms_key_id": kms_key_id,
                        "is_encrypted": is_encrypted,
                        "creation_time": log_group.get("creationTime"),
                        "stored_bytes": log_group.get("storedBytes", 0),
                        "retention_in_days": log_group.get("retentionInDays"),
                    }
                )
                result.add_evidence(evidence)

                if is_encrypted:
                    encrypted_count += 1
                    self.logger.debug(
                        "log_group_encrypted",
                        log_group=log_group_name,
                        kms_key_id=kms_key_id
                    )
                else:
                    # Create finding for unencrypted log group
                    finding = self.create_finding(
                        resource_id=log_group_name,
                        resource_type="cloudwatch_log_group",
                        severity=Severity.HIGH,
                        title="CloudWatch log group encryption not enabled",
                        description=f"CloudWatch log group '{log_group_name}' does not have encryption enabled. "
                                    "Without encryption, log data is stored unencrypted at rest, potentially "
                                    "exposing sensitive information such as application logs, system events, "
                                    "security events, and operational data. CloudWatch Logs encryption with "
                                    "AWS KMS provides an additional layer of security for sensitive log data. "
                                    "ISO 27001 A.8.24 requires cryptographic controls for protecting "
                                    "sensitive information.",
                        remediation=(
                            f"Enable encryption for CloudWatch log group:\n\n"
                            "Note: You cannot add encryption to existing log groups. "
                            "You must create a new encrypted log group and migrate.\n\n"
                            "Step 1: Create new encrypted log group:\n"
                            f"aws logs create-log-group \\\n"
                            f"  --log-group-name {log_group_name}-encrypted \\\n"
                            "  --kms-key-id arn:aws:kms:REGION:ACCOUNT:key/KEY-ID\n\n"
                            "Step 2: Update applications to use new log group\n\n"
                            "Step 3: Copy retention settings if needed:\n"
                            f"aws logs put-retention-policy \\\n"
                            f"  --log-group-name {log_group_name}-encrypted \\\n"
                            "  --retention-in-days <RETENTION-DAYS>\n\n"
                            "Step 4: Verify logs are flowing to new group\n\n"
                            "Step 5: Delete old unencrypted log group:\n"
                            f"aws logs delete-log-group \\\n"
                            f"  --log-group-name {log_group_name}\n\n"
                            "Or use AWS Console:\n"
                            "1. Go to CloudWatch Logs console\n"
                            "2. Click 'Create log group'\n"
                            "3. Enter new log group name\n"
                            "4. Under 'KMS key', select a customer-managed key\n"
                            "5. Click 'Create'\n"
                            "6. Update applications to use new log group\n"
                            "7. Delete old log group after migration\n\n"
                            "KMS Key Policy Requirements:\n"
                            "Ensure the KMS key policy allows CloudWatch Logs:\n"
                            "{\n"
                            '  "Sid": "Allow CloudWatch Logs",\n'
                            '  "Effect": "Allow",\n'
                            '  "Principal": {\n'
                            '    "Service": "logs.REGION.amazonaws.com"\n'
                            '  },\n'
                            '  "Action": [\n'
                            '    "kms:Encrypt",\n'
                            '    "kms:Decrypt",\n'
                            '    "kms:ReEncrypt*",\n'
                            '    "kms:GenerateDataKey*",\n'
                            '    "kms:CreateGrant",\n'
                            '    "kms:DescribeKey"\n'
                            '  ],\n'
                            '  "Resource": "*",\n'
                            '  "Condition": {\n'
                            '    "ArnLike": {\n'
                            f'      "kms:EncryptionContext:aws:logs:arn": "arn:aws:logs:REGION:ACCOUNT:log-group:{log_group_name}*"\n'
                            '    }\n'
                            '  }\n'
                            '}'
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "log_group_not_encrypted",
                        log_group=log_group_name
                    )

            # Calculate compliance score
            result.score = (encrypted_count / len(log_groups)) * 100

            # Determine pass/fail
            result.passed = encrypted_count == len(log_groups)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_log_groups": len(log_groups),
                "encrypted_log_groups": encrypted_count,
                "unencrypted_log_groups": len(log_groups) - encrypted_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "cloudwatch_logs_encryption_test_completed",
                total_log_groups=len(log_groups),
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("cloudwatch_logs_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("cloudwatch_logs_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_cloudwatch_logs_encryption_test(connector: AWSConnector) -> TestResult:
    """Run CloudWatch Logs encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_cloudwatch_logs_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = CloudWatchLogsEncryptionTest(connector)
    return test.execute()

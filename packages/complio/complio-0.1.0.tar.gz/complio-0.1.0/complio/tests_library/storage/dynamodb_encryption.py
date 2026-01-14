"""
DynamoDB table encryption compliance test.

Checks that all DynamoDB tables have server-side encryption enabled.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: All data at rest must be encrypted

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.storage.dynamodb_encryption import DynamoDBEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = DynamoDBEncryptionTest(connector)
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


class DynamoDBEncryptionTest(ComplianceTest):
    """Test for DynamoDB table encryption compliance.

    Verifies that all DynamoDB tables have server-side encryption enabled.

    Compliance Requirements:
        - All DynamoDB tables must have SSEDescription.Status=ENABLED
        - Tables can use AWS managed or customer managed KMS keys
        - Tables without SSE are non-compliant

    Scoring:
        - 100% if all tables are encrypted
        - Proportional score based on encrypted/total ratio
        - 0% if no tables are encrypted

    Example:
        >>> test = DynamoDBEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize DynamoDB encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="dynamodb_encryption",
            test_name="DynamoDB Table Encryption Check",
            description="Verify all DynamoDB tables have server-side encryption enabled",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute DynamoDB encryption compliance test.

        Returns:
            TestResult with findings for non-encrypted tables

        Example:
            >>> test = DynamoDBEncryptionTest(connector)
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
            # Get DynamoDB client
            dynamodb_client = self.connector.get_client("dynamodb")

            # List all tables
            self.logger.info("listing_dynamodb_tables")
            table_names = []

            # Handle pagination for list_tables
            paginator = dynamodb_client.get_paginator("list_tables")
            for page in paginator.paginate():
                table_names.extend(page.get("TableNames", []))

            if not table_names:
                self.logger.info("no_dynamodb_tables_found")
                result.metadata["message"] = "No DynamoDB tables found in region"
                return result

            self.logger.info("dynamodb_tables_found", count=len(table_names))

            # Check each table for encryption
            encrypted_count = 0
            total_count = len(table_names)

            for table_name in table_names:
                result.resources_scanned += 1

                # Describe table to get encryption details
                try:
                    table_response = dynamodb_client.describe_table(TableName=table_name)
                    table = table_response.get("Table", {})

                    # Check SSEDescription
                    sse_description = table.get("SSEDescription", {})
                    sse_status = sse_description.get("Status", "DISABLED")
                    sse_type = sse_description.get("SSEType", "None")
                    kms_key_arn = sse_description.get("KMSMasterKeyArn")

                    # Encryption is enabled if Status=ENABLED or ENABLING
                    encrypted = sse_status in ["ENABLED", "ENABLING"]

                    # Get table details
                    table_status = table.get("TableStatus", "unknown")
                    item_count = table.get("ItemCount", 0)
                    table_size_bytes = table.get("TableSizeBytes", 0)
                    billing_mode = table.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED")

                    # Create evidence
                    evidence = self.create_evidence(
                        resource_id=table_name,
                        resource_type="dynamodb_table",
                        data={
                            "table_name": table_name,
                            "encrypted": encrypted,
                            "sse_status": sse_status,
                            "sse_type": sse_type,
                            "kms_key_arn": kms_key_arn,
                            "table_status": table_status,
                            "item_count": item_count,
                            "table_size_bytes": table_size_bytes,
                            "billing_mode": billing_mode,
                        }
                    )
                    result.add_evidence(evidence)

                    if encrypted:
                        encrypted_count += 1
                        self.logger.debug(
                            "dynamodb_table_encrypted",
                            table_name=table_name,
                            sse_type=sse_type,
                            sse_status=sse_status
                        )
                    else:
                        # Create finding for non-encrypted table
                        size_mb = table_size_bytes / (1024 * 1024) if table_size_bytes > 0 else 0
                        finding = self.create_finding(
                            resource_id=table_name,
                            resource_type="dynamodb_table",
                            severity=Severity.HIGH,
                            title="DynamoDB table encryption not enabled",
                            description=f"DynamoDB table '{table_name}' with {item_count} items ({size_mb:.2f}MB) "
                                        f"does not have server-side encryption enabled (SSE Status: {sse_status}). "
                                        "Table data is stored unencrypted. "
                                        "This violates ISO 27001 A.8.24 requirement for data-at-rest encryption.",
                            remediation=(
                                f"Enable server-side encryption for table '{table_name}':\n\n"
                                "Using AWS managed key (easier):\n"
                                f"aws dynamodb update-table --table-name {table_name} \\\n"
                                "  --sse-specification Enabled=true\n\n"
                                "Or using customer managed KMS key (more control):\n"
                                f"aws dynamodb update-table --table-name {table_name} \\\n"
                                "  --sse-specification Enabled=true,SSEType=KMS,KMSMasterKeyId=<your-kms-key-id>\n\n"
                                "Or use AWS Console:\n"
                                "1. Go to DynamoDB → Tables\n"
                                f"2. Select table '{table_name}'\n"
                                "3. Go to 'Additional settings' tab\n"
                                "4. Under 'Encryption at rest', click 'Manage encryption'\n"
                                "5. Select 'AWS owned key' or 'AWS managed key' or 'Customer managed key'\n"
                                "6. Click 'Save changes'\n\n"
                                "Note: Encryption can be enabled on existing tables without downtime."
                            ),
                            evidence=evidence
                        )
                        result.add_finding(finding)

                        self.logger.warning(
                            "dynamodb_table_not_encrypted",
                            table_name=table_name,
                            sse_status=sse_status
                        )

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code")
                    self.logger.error(
                        "dynamodb_table_describe_error",
                        table_name=table_name,
                        error_code=error_code
                    )
                    # Skip this table and continue
                    continue

            # Calculate compliance score
            if total_count > 0:
                result.score = (encrypted_count / total_count) * 100

            # Determine pass/fail
            result.passed = encrypted_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_tables": total_count,
                "encrypted_tables": encrypted_count,
                "non_encrypted_tables": total_count - encrypted_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "dynamodb_encryption_test_completed",
                total=total_count,
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("dynamodb_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("dynamodb_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_dynamodb_encryption_test(connector: AWSConnector) -> TestResult:
    """Run DynamoDB encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_dynamodb_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = DynamoDBEncryptionTest(connector)
    return test.execute()

"""
AWS Backup encryption compliance test.

Checks that all AWS Backup recovery points use encryption.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: Backup data must be encrypted at rest

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.storage.backup_encryption import BackupEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = BackupEncryptionTest(connector)
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


class BackupEncryptionTest(ComplianceTest):
    """Test for AWS Backup encryption compliance.

    Verifies that all AWS Backup recovery points use encryption to protect
    backup data at rest.

    Compliance Requirements:
        - All backup recovery points must be encrypted
        - Encryption protects backup data from unauthorized access
        - Applies to all supported AWS resources (EC2, RDS, EBS, EFS, DynamoDB, etc.)

    Scoring:
        - 100% if all recovery points are encrypted
        - Proportional score based on compliant/total ratio
        - 100% if no recovery points exist (no backups configured)

    Example:
        >>> test = BackupEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize AWS Backup encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="backup_encryption",
            test_name="AWS Backup Encryption Check",
            description="Verify all AWS Backup recovery points are encrypted",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute AWS Backup encryption compliance test.

        Returns:
            TestResult with findings for unencrypted recovery points

        Example:
            >>> test = BackupEncryptionTest(connector)
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
            # Get Backup client
            backup_client = self.connector.get_client("backup")

            # List all backup vaults
            self.logger.info("listing_backup_vaults")
            vaults_response = backup_client.list_backup_vaults()
            vaults = vaults_response.get("BackupVaultList", [])

            if not vaults:
                self.logger.info("no_backup_vaults_found")
                result.metadata["message"] = "No AWS Backup vaults found in region"
                return result

            self.logger.info("backup_vaults_found", count=len(vaults))

            # Track recovery points across all vaults
            total_recovery_points = 0
            encrypted_recovery_points = 0

            # Check recovery points in each vault
            for vault in vaults:
                vault_name = vault["BackupVaultName"]

                try:
                    # List recovery points in vault
                    paginator = backup_client.get_paginator("list_recovery_points_by_backup_vault")

                    for page in paginator.paginate(BackupVaultName=vault_name):
                        recovery_points = page.get("RecoveryPoints", [])

                        for recovery_point in recovery_points:
                            recovery_point_arn = recovery_point.get("RecoveryPointArn")
                            resource_arn = recovery_point.get("ResourceArn")
                            resource_type = recovery_point.get("ResourceType")
                            is_encrypted = recovery_point.get("IsEncrypted", False)
                            creation_date = recovery_point.get("CreationDate")
                            status = recovery_point.get("Status")

                            # Only check completed recovery points
                            if status != "COMPLETED":
                                continue

                            total_recovery_points += 1
                            result.resources_scanned += 1

                            # Create evidence
                            evidence = self.create_evidence(
                                resource_id=recovery_point_arn,
                                resource_type="backup_recovery_point",
                                data={
                                    "recovery_point_arn": recovery_point_arn,
                                    "resource_arn": resource_arn,
                                    "resource_type": resource_type,
                                    "is_encrypted": is_encrypted,
                                    "backup_vault_name": vault_name,
                                    "creation_date": creation_date.isoformat() if creation_date else None,
                                    "status": status,
                                }
                            )
                            result.add_evidence(evidence)

                            if is_encrypted:
                                encrypted_recovery_points += 1
                                self.logger.debug(
                                    "recovery_point_encrypted",
                                    recovery_point_arn=recovery_point_arn,
                                    resource_type=resource_type
                                )
                            else:
                                # Create finding for unencrypted recovery point
                                finding = self.create_finding(
                                    resource_id=recovery_point_arn,
                                    resource_type="backup_recovery_point",
                                    severity=Severity.HIGH,
                                    title="AWS Backup recovery point not encrypted",
                                    description=f"Backup recovery point for resource '{resource_arn}' "
                                                f"(type: {resource_type}) in vault '{vault_name}' is not encrypted. "
                                                "Unencrypted backups expose sensitive data to unauthorized access. "
                                                "All backup data must be encrypted at rest to comply with "
                                                "ISO 27001 A.8.24 cryptographic controls.",
                                    remediation=(
                                        "AWS Backup automatically encrypts recovery points based on the source resource encryption:\n\n"
                                        "1. Enable encryption on source resources BEFORE backing them up:\n"
                                        "   - EBS volumes: Enable encryption\n"
                                        "   - RDS instances: Enable storage encryption\n"
                        "   - EFS file systems: Enable encryption at rest\n"
                                        "   - DynamoDB tables: Enable encryption\n"
                                        "   - S3 buckets: Enable default encryption\n\n"
                                        "2. Delete existing unencrypted recovery points:\n"
                                        f"   aws backup delete-recovery-point \\\n"
                                        f"     --backup-vault-name {vault_name} \\\n"
                                        f"     --recovery-point-arn {recovery_point_arn}\n\n"
                                        "3. Create new backup after encrypting source resource:\n"
                                        "   aws backup start-backup-job \\\n"
                                        f"     --backup-vault-name {vault_name} \\\n"
                                        f"     --resource-arn {resource_arn} \\\n"
                                        "     --iam-role-arn <backup-role-arn>\n\n"
                                        "Note: You cannot encrypt existing recovery points in-place. "
                                        "You must encrypt the source resource and create new backups."
                                    ),
                                    evidence=evidence
                                )
                                result.add_finding(finding)

                                self.logger.warning(
                                    "recovery_point_not_encrypted",
                                    recovery_point_arn=recovery_point_arn,
                                    resource_type=resource_type,
                                    vault=vault_name
                                )

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code")
                    if error_code in ["ResourceNotFoundException", "AccessDeniedException"]:
                        self.logger.warning(
                            "backup_vault_access_error",
                            vault=vault_name,
                            error_code=error_code
                        )
                        continue
                    else:
                        raise

            # Handle case where no recovery points exist
            if total_recovery_points == 0:
                self.logger.info("no_recovery_points_found")
                result.metadata["message"] = "No completed recovery points found in any backup vault"
                return result

            # Calculate compliance score
            result.score = (encrypted_recovery_points / total_recovery_points) * 100

            # Determine pass/fail
            result.passed = encrypted_recovery_points == total_recovery_points
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_vaults": len(vaults),
                "total_recovery_points": total_recovery_points,
                "encrypted_recovery_points": encrypted_recovery_points,
                "unencrypted_recovery_points": total_recovery_points - encrypted_recovery_points,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "backup_encryption_test_completed",
                total_recovery_points=total_recovery_points,
                encrypted=encrypted_recovery_points,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("backup_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("backup_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_backup_encryption_test(connector: AWSConnector) -> TestResult:
    """Run AWS Backup encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_backup_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = BackupEncryptionTest(connector)
    return test.execute()

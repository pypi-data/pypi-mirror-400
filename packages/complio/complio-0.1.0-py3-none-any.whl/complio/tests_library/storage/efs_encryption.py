"""
EFS (Elastic File System) encryption compliance test.

Checks that all EFS file systems have encryption enabled.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: All data at rest must be encrypted

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.storage.efs_encryption import EFSEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = EFSEncryptionTest(connector)
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


class EFSEncryptionTest(ComplianceTest):
    """Test for EFS file system encryption compliance.

    Verifies that all EFS file systems have encryption enabled.

    Compliance Requirements:
        - All EFS file systems must have Encrypted=True
        - Unencrypted file systems expose shared data
        - File systems without encryption are non-compliant

    Scoring:
        - 100% if all file systems are encrypted
        - Proportional score based on encrypted/total ratio
        - 0% if no file systems are encrypted

    Example:
        >>> test = EFSEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize EFS encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="efs_encryption",
            test_name="EFS File System Encryption Check",
            description="Verify all EFS file systems have encryption enabled",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute EFS encryption compliance test.

        Returns:
            TestResult with findings for non-encrypted file systems

        Example:
            >>> test = EFSEncryptionTest(connector)
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
            # Get EFS client
            efs_client = self.connector.get_client("efs")

            # List all file systems
            self.logger.info("listing_efs_file_systems")
            response = efs_client.describe_file_systems()
            file_systems = response.get("FileSystems", [])

            if not file_systems:
                self.logger.info("no_efs_file_systems_found")
                result.metadata["message"] = "No EFS file systems found in region"
                return result

            self.logger.info("efs_file_systems_found", count=len(file_systems))

            # Check each file system for encryption
            encrypted_count = 0
            total_count = len(file_systems)

            for fs in file_systems:
                fs_id = fs["FileSystemId"]
                encrypted = fs.get("Encrypted", False)
                result.resources_scanned += 1

                # Get file system details
                name = fs.get("Name", "unnamed")
                life_cycle_state = fs.get("LifeCycleState", "unknown")
                size_in_bytes = fs.get("SizeInBytes", {}).get("Value", 0)
                number_of_mount_targets = fs.get("NumberOfMountTargets", 0)
                performance_mode = fs.get("PerformanceMode", "unknown")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=fs_id,
                    resource_type="efs_file_system",
                    data={
                        "file_system_id": fs_id,
                        "name": name,
                        "encrypted": encrypted,
                        "life_cycle_state": life_cycle_state,
                        "size_bytes": size_in_bytes,
                        "number_of_mount_targets": number_of_mount_targets,
                        "performance_mode": performance_mode,
                        "kms_key_id": fs.get("KmsKeyId"),
                        "creation_token": fs.get("CreationToken"),
                    }
                )
                result.add_evidence(evidence)

                if encrypted:
                    encrypted_count += 1
                    self.logger.debug(
                        "efs_file_system_encrypted",
                        fs_id=fs_id,
                        name=name,
                        kms_key_id=fs.get("KmsKeyId")
                    )
                else:
                    # Create finding for non-encrypted file system
                    size_mb = size_in_bytes / (1024 * 1024) if size_in_bytes > 0 else 0
                    finding = self.create_finding(
                        resource_id=fs_id,
                        resource_type="efs_file_system",
                        severity=Severity.HIGH,
                        title="EFS file system encryption not enabled",
                        description=f"EFS file system '{name}' ({fs_id}) with {number_of_mount_targets} mount targets "
                                    f"and {size_mb:.2f}MB of data does not have encryption enabled. "
                                    "Shared file system data is stored unencrypted. "
                                    "This violates ISO 27001 A.8.24 requirement for data-at-rest encryption.",
                        remediation=(
                            "EFS file systems cannot be encrypted after creation. To remediate:\n"
                            "1. Create a new EFS file system with encryption enabled:\n"
                            "   aws efs create-file-system --encrypted \\\n"
                            "     --kms-key-id <your-kms-key-id> \\\n"
                            f"     --performance-mode {performance_mode} \\\n"
                            "     --tags Key=Name,Value=encrypted-replacement\n"
                            "2. Create mount targets in the same subnets:\n"
                            "   aws efs create-mount-target --file-system-id <new-fs-id> \\\n"
                            "     --subnet-id <subnet-id> --security-groups <sg-id>\n"
                            "3. Use AWS DataSync or rsync to migrate data:\n"
                            "   # Mount both file systems, then:\n"
                            "   rsync -av /mnt/old-efs/ /mnt/new-efs/\n"
                            "4. Update application mount points\n"
                            f"5. Delete the old unencrypted file system '{fs_id}'\n\n"
                            "Note: This will cause temporary downtime during data migration.\n"
                            "For future file systems, enable encryption at creation time."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "efs_file_system_not_encrypted",
                        fs_id=fs_id,
                        name=name,
                        size_mb=size_mb
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (encrypted_count / total_count) * 100

            # Determine pass/fail
            result.passed = encrypted_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_file_systems": total_count,
                "encrypted_file_systems": encrypted_count,
                "non_encrypted_file_systems": total_count - encrypted_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "efs_encryption_test_completed",
                total=total_count,
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("efs_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("efs_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_efs_encryption_test(connector: AWSConnector) -> TestResult:
    """Run EFS encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_efs_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = EFSEncryptionTest(connector)
    return test.execute()

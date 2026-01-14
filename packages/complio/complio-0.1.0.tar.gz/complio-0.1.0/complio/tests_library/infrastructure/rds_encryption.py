"""
RDS instance encryption compliance test.

Checks that all RDS database instances have storage encryption enabled.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: All data at rest must be encrypted

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.rds_encryption import RDSEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = RDSEncryptionTest(connector)
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


class RDSEncryptionTest(ComplianceTest):
    """Test for RDS instance encryption compliance.

    Verifies that all RDS database instances have storage encryption enabled.

    Compliance Requirements:
        - All RDS instances must have StorageEncrypted=True
        - Both primary and read replicas must be encrypted
        - Instances without encryption are non-compliant

    Scoring:
        - 100% if all instances are encrypted
        - Proportional score based on encrypted/total ratio
        - 0% if no instances are encrypted

    Example:
        >>> test = RDSEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize RDS encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="rds_encryption",
            test_name="RDS Instance Encryption Check",
            description="Verify all RDS database instances have storage encryption enabled",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute RDS encryption compliance test.

        Returns:
            TestResult with findings for non-encrypted instances

        Example:
            >>> test = RDSEncryptionTest(connector)
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
            # Get RDS client
            rds_client = self.connector.get_client("rds")

            # List all DB instances
            self.logger.info("listing_rds_instances")
            response = rds_client.describe_db_instances()
            instances = response.get("DBInstances", [])

            if not instances:
                self.logger.info("no_rds_instances_found")
                result.metadata["message"] = "No RDS instances found in region"
                return result

            self.logger.info("rds_instances_found", count=len(instances))

            # Check each instance for encryption
            encrypted_count = 0
            total_count = len(instances)

            for instance in instances:
                instance_id = instance["DBInstanceIdentifier"]
                encrypted = instance.get("StorageEncrypted", False)
                result.resources_scanned += 1

                # Get instance details
                engine = instance.get("Engine", "unknown")
                engine_version = instance.get("EngineVersion", "unknown")
                instance_class = instance.get("DBInstanceClass", "unknown")
                storage_size = instance.get("AllocatedStorage", 0)
                instance_status = instance.get("DBInstanceStatus", "unknown")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=instance_id,
                    resource_type="rds_instance",
                    data={
                        "instance_id": instance_id,
                        "encrypted": encrypted,
                        "engine": engine,
                        "engine_version": engine_version,
                        "instance_class": instance_class,
                        "storage_size_gb": storage_size,
                        "status": instance_status,
                        "kms_key_id": instance.get("KmsKeyId"),
                        "availability_zone": instance.get("AvailabilityZone"),
                    }
                )
                result.add_evidence(evidence)

                if encrypted:
                    encrypted_count += 1
                    self.logger.debug(
                        "rds_instance_encrypted",
                        instance_id=instance_id,
                        engine=engine,
                        kms_key_id=instance.get("KmsKeyId")
                    )
                else:
                    # Create finding for non-encrypted instance
                    finding = self.create_finding(
                        resource_id=instance_id,
                        resource_type="rds_instance",
                        severity=Severity.HIGH,
                        title="RDS instance storage encryption not enabled",
                        description=f"RDS instance '{instance_id}' ({engine} {engine_version}, {storage_size}GB) "
                                    "does not have storage encryption enabled. "
                                    "This violates ISO 27001 A.8.24 requirement for data-at-rest encryption.",
                        remediation=(
                            "RDS instances cannot be encrypted after creation. To remediate:\n"
                            "1. Create a snapshot of the unencrypted instance:\n"
                            f"   aws rds create-db-snapshot --db-instance-identifier {instance_id} "
                            f"--db-snapshot-identifier {instance_id}-snapshot\n"
                            "2. Copy the snapshot with encryption enabled:\n"
                            f"   aws rds copy-db-snapshot --source-db-snapshot-identifier {instance_id}-snapshot "
                            f"--target-db-snapshot-identifier {instance_id}-encrypted-snapshot --kms-key-id <key-id>\n"
                            "3. Restore a new instance from the encrypted snapshot:\n"
                            f"   aws rds restore-db-instance-from-db-snapshot "
                            f"--db-instance-identifier {instance_id}-encrypted "
                            f"--db-snapshot-identifier {instance_id}-encrypted-snapshot\n"
                            "4. Update application connection strings\n"
                            "5. Delete the old unencrypted instance\n\n"
                            "Note: This will cause downtime during the migration."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "rds_instance_not_encrypted",
                        instance_id=instance_id,
                        engine=engine
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (encrypted_count / total_count) * 100

            # Determine pass/fail
            result.passed = encrypted_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_instances": total_count,
                "encrypted_instances": encrypted_count,
                "non_encrypted_instances": total_count - encrypted_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "rds_encryption_test_completed",
                total=total_count,
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("rds_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("rds_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_rds_encryption_test(connector: AWSConnector) -> TestResult:
    """Run RDS encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_rds_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = RDSEncryptionTest(connector)
    return test.execute()

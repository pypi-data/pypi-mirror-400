"""
EBS volume encryption compliance test.

Checks that all EBS volumes have encryption enabled.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: All data at rest must be encrypted

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.infrastructure.ebs_encryption import EBSEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = EBSEncryptionTest(connector)
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


class EBSEncryptionTest(ComplianceTest):
    """Test for EBS volume encryption compliance.

    Verifies that all EBS volumes have encryption enabled.

    Compliance Requirements:
        - All EBS volumes must be encrypted
        - Both root and non-root volumes must be encrypted
        - Volumes without encryption are non-compliant

    Scoring:
        - 100% if all volumes are encrypted
        - Proportional score based on encrypted/total ratio
        - 0% if no volumes are encrypted

    Example:
        >>> test = EBSEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize EBS encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="ebs_encryption",
            test_name="EBS Volume Encryption Check",
            description="Verify all EBS volumes have encryption enabled",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute EBS encryption compliance test.

        Returns:
            TestResult with findings for non-encrypted volumes

        Example:
            >>> test = EBSEncryptionTest(connector)
            >>> result = test.execute()
            >>> print(result.score)
            92.3
        """
        result = TestResult(
            test_id=self.test_id,
            test_name=self.test_name,
            status=TestStatus.PASSED,
            passed=True,
            score=100.0,
        )

        try:
            # Get EC2 client
            ec2_client = self.connector.get_client("ec2")

            # List all volumes
            self.logger.info("listing_ebs_volumes")
            response = ec2_client.describe_volumes()
            volumes = response.get("Volumes", [])

            if not volumes:
                self.logger.info("no_ebs_volumes_found")
                result.metadata["message"] = "No EBS volumes found in region"
                return result

            self.logger.info("ebs_volumes_found", count=len(volumes))

            # Check each volume for encryption
            encrypted_count = 0
            total_count = len(volumes)

            for volume in volumes:
                volume_id = volume["VolumeId"]
                encrypted = volume.get("Encrypted", False)
                result.resources_scanned += 1

                # Get volume details
                volume_size = volume.get("Size", 0)
                volume_type = volume.get("VolumeType", "unknown")
                state = volume.get("State", "unknown")
                availability_zone = volume.get("AvailabilityZone", "unknown")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=volume_id,
                    resource_type="ebs_volume",
                    data={
                        "volume_id": volume_id,
                        "encrypted": encrypted,
                        "size_gb": volume_size,
                        "volume_type": volume_type,
                        "state": state,
                        "availability_zone": availability_zone,
                        "kms_key_id": volume.get("KmsKeyId"),
                    }
                )
                result.add_evidence(evidence)

                if encrypted:
                    encrypted_count += 1
                    self.logger.debug(
                        "volume_encrypted",
                        volume_id=volume_id,
                        kms_key_id=volume.get("KmsKeyId")
                    )
                else:
                    # Create finding for non-encrypted volume
                    finding = self.create_finding(
                        resource_id=volume_id,
                        resource_type="ebs_volume",
                        severity=Severity.HIGH,
                        title="EBS volume encryption not enabled",
                        description=f"Volume '{volume_id}' ({volume_size}GB, {volume_type}) does not have encryption enabled. "
                                    "This violates ISO 27001 A.8.24 requirement for data-at-rest encryption.",
                        remediation=(
                            "EBS volumes cannot be encrypted after creation. To remediate:\n"
                            "1. Create a snapshot of the unencrypted volume\n"
                            "2. Copy the snapshot with encryption enabled:\n"
                            f"   aws ec2 copy-snapshot --source-region {self.connector.region} "
                            f"--source-snapshot-id <snap-id> --encrypted\n"
                            "3. Create a new volume from the encrypted snapshot\n"
                            "4. Attach the new volume to the instance\n"
                            "5. Update /etc/fstab if needed\n"
                            "6. Delete the old unencrypted volume\n\n"
                            "For future volumes, enable encryption by default:\n"
                            "aws ec2 enable-ebs-encryption-by-default --region " + self.connector.region
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "volume_not_encrypted",
                        volume_id=volume_id,
                        size_gb=volume_size
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (encrypted_count / total_count) * 100

            # Determine pass/fail
            result.passed = encrypted_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_volumes": total_count,
                "encrypted_volumes": encrypted_count,
                "non_encrypted_volumes": total_count - encrypted_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "ebs_encryption_test_completed",
                total=total_count,
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("ebs_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("ebs_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_ebs_encryption_test(connector: AWSConnector) -> TestResult:
    """Run EBS encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_ebs_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = EBSEncryptionTest(connector)
    return test.execute()

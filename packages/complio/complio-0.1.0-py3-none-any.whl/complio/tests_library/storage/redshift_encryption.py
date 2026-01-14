"""
Redshift cluster encryption compliance test.

Checks that all Redshift clusters have encryption enabled.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: All data at rest must be encrypted

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.storage.redshift_encryption import RedshiftEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = RedshiftEncryptionTest(connector)
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


class RedshiftEncryptionTest(ComplianceTest):
    """Test for Redshift cluster encryption compliance.

    Verifies that all Redshift clusters have encryption enabled.

    Compliance Requirements:
        - All Redshift clusters must have Encrypted=True
        - Unencrypted clusters expose sensitive data warehouse data
        - Clusters without encryption are non-compliant

    Scoring:
        - 100% if all clusters are encrypted
        - Proportional score based on encrypted/total ratio
        - 0% if no clusters are encrypted

    Example:
        >>> test = RedshiftEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize Redshift encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="redshift_encryption",
            test_name="Redshift Cluster Encryption Check",
            description="Verify all Redshift clusters have encryption enabled",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute Redshift encryption compliance test.

        Returns:
            TestResult with findings for non-encrypted clusters

        Example:
            >>> test = RedshiftEncryptionTest(connector)
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
            # Get Redshift client
            redshift_client = self.connector.get_client("redshift")

            # List all clusters
            self.logger.info("listing_redshift_clusters")
            response = redshift_client.describe_clusters()
            clusters = response.get("Clusters", [])

            if not clusters:
                self.logger.info("no_redshift_clusters_found")
                result.metadata["message"] = "No Redshift clusters found in region"
                return result

            self.logger.info("redshift_clusters_found", count=len(clusters))

            # Check each cluster for encryption
            encrypted_count = 0
            total_count = len(clusters)

            for cluster in clusters:
                cluster_id = cluster["ClusterIdentifier"]
                encrypted = cluster.get("Encrypted", False)
                result.resources_scanned += 1

                # Get cluster details
                node_type = cluster.get("NodeType", "unknown")
                number_of_nodes = cluster.get("NumberOfNodes", 0)
                cluster_status = cluster.get("ClusterStatus", "unknown")
                db_name = cluster.get("DBName", "unknown")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=cluster_id,
                    resource_type="redshift_cluster",
                    data={
                        "cluster_id": cluster_id,
                        "encrypted": encrypted,
                        "node_type": node_type,
                        "number_of_nodes": number_of_nodes,
                        "cluster_status": cluster_status,
                        "db_name": db_name,
                        "kms_key_id": cluster.get("KmsKeyId"),
                        "availability_zone": cluster.get("AvailabilityZone"),
                    }
                )
                result.add_evidence(evidence)

                if encrypted:
                    encrypted_count += 1
                    self.logger.debug(
                        "redshift_cluster_encrypted",
                        cluster_id=cluster_id,
                        kms_key_id=cluster.get("KmsKeyId")
                    )
                else:
                    # Create finding for non-encrypted cluster
                    finding = self.create_finding(
                        resource_id=cluster_id,
                        resource_type="redshift_cluster",
                        severity=Severity.HIGH,
                        title="Redshift cluster encryption not enabled",
                        description=f"Redshift cluster '{cluster_id}' ({node_type}, {number_of_nodes} nodes) "
                                    "does not have encryption enabled. Data warehouse data is stored unencrypted. "
                                    "This violates ISO 27001 A.8.24 requirement for data-at-rest encryption.",
                        remediation=(
                            "Redshift clusters cannot be encrypted after creation. To remediate:\n"
                            "1. Create a snapshot of the unencrypted cluster:\n"
                            f"   aws redshift create-cluster-snapshot --cluster-identifier {cluster_id} "
                            f"--snapshot-identifier {cluster_id}-snapshot\n"
                            "2. Copy the snapshot with encryption enabled:\n"
                            f"   aws redshift copy-cluster-snapshot "
                            f"--source-snapshot-identifier {cluster_id}-snapshot "
                            f"--target-snapshot-identifier {cluster_id}-encrypted-snapshot "
                            "--kms-key-id <your-kms-key-id>\n"
                            "3. Restore a new cluster from the encrypted snapshot:\n"
                            f"   aws redshift restore-from-cluster-snapshot "
                            f"--cluster-identifier {cluster_id}-encrypted "
                            f"--snapshot-identifier {cluster_id}-encrypted-snapshot\n"
                            "4. Update application connection strings\n"
                            "5. Delete the old unencrypted cluster\n\n"
                            "Note: This will cause downtime during the migration.\n"
                            "For future clusters, enable encryption at creation time."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "redshift_cluster_not_encrypted",
                        cluster_id=cluster_id,
                        number_of_nodes=number_of_nodes
                    )

            # Calculate compliance score
            if total_count > 0:
                result.score = (encrypted_count / total_count) * 100

            # Determine pass/fail
            result.passed = encrypted_count == total_count
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_clusters": total_count,
                "encrypted_clusters": encrypted_count,
                "non_encrypted_clusters": total_count - encrypted_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "redshift_encryption_test_completed",
                total=total_count,
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("redshift_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("redshift_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_redshift_encryption_test(connector: AWSConnector) -> TestResult:
    """Run Redshift encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_redshift_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = RedshiftEncryptionTest(connector)
    return test.execute()

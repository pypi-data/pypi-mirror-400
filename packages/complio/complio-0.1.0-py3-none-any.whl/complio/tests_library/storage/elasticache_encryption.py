"""
ElastiCache encryption compliance test.

Checks that all ElastiCache clusters have both at-rest and in-transit encryption enabled.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: All data at rest and in transit must be encrypted

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.storage.elasticache_encryption import ElastiCacheEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = ElastiCacheEncryptionTest(connector)
    >>> result = test.run()
    >>> print(f"Passed: {result.passed}, Score: {result.score}")
"""

from typing import Any, Dict, List

from botocore.exceptions import ClientError

from complio.connectors.aws.client import AWSConnector
from complio.tests_library.base import (
    ComplianceTest,
    Severity,
    TestResult,
    TestStatus,
)


class ElastiCacheEncryptionTest(ComplianceTest):
    """Test for ElastiCache encryption compliance.

    Verifies that all ElastiCache clusters have both at-rest and in-transit
    encryption enabled.

    Compliance Requirements:
        - All cache clusters must have AtRestEncryptionEnabled=True
        - All cache clusters must have TransitEncryptionEnabled=True
        - Both encryption types are required for full compliance

    Scoring:
        - 100% if all clusters have both encryption types
        - Proportional score based on compliant/total ratio
        - 0% if no clusters are compliant

    Example:
        >>> test = ElastiCacheEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize ElastiCache encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="elasticache_encryption",
            test_name="ElastiCache Encryption Check",
            description="Verify all ElastiCache clusters have at-rest and in-transit encryption",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute ElastiCache encryption compliance test.

        Returns:
            TestResult with findings for clusters without full encryption

        Example:
            >>> test = ElastiCacheEncryptionTest(connector)
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
            # Get ElastiCache client
            elasticache_client = self.connector.get_client("elasticache")

            # List all replication groups (for Redis)
            self.logger.info("listing_elasticache_replication_groups")
            replication_groups = []

            try:
                response = elasticache_client.describe_replication_groups()
                replication_groups = response.get("ReplicationGroups", [])
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                self.logger.warning("replication_groups_list_error", error_code=error_code)

            # List all cache clusters (standalone nodes)
            self.logger.info("listing_elasticache_cache_clusters")
            cache_clusters = []

            try:
                response = elasticache_client.describe_cache_clusters()
                cache_clusters = response.get("CacheClusters", [])
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                self.logger.warning("cache_clusters_list_error", error_code=error_code)

            total_resources = len(replication_groups) + len(cache_clusters)

            if total_resources == 0:
                self.logger.info("no_elasticache_resources_found")
                result.metadata["message"] = "No ElastiCache resources found in region"
                return result

            self.logger.info(
                "elasticache_resources_found",
                replication_groups=len(replication_groups),
                cache_clusters=len(cache_clusters)
            )

            compliant_count = 0

            # Check replication groups
            for rep_group in replication_groups:
                rep_group_id = rep_group["ReplicationGroupId"]
                result.resources_scanned += 1

                at_rest_enabled = rep_group.get("AtRestEncryptionEnabled", False)
                transit_enabled = rep_group.get("TransitEncryptionEnabled", False)
                fully_encrypted = at_rest_enabled and transit_enabled

                # Get replication group details
                status = rep_group.get("Status", "unknown")
                engine = rep_group.get("CacheNodeType", "unknown")
                num_node_groups = len(rep_group.get("NodeGroups", []))

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=rep_group_id,
                    resource_type="elasticache_replication_group",
                    data={
                        "replication_group_id": rep_group_id,
                        "at_rest_encryption_enabled": at_rest_enabled,
                        "transit_encryption_enabled": transit_enabled,
                        "fully_encrypted": fully_encrypted,
                        "status": status,
                        "engine": engine,
                        "num_node_groups": num_node_groups,
                        "kms_key_id": rep_group.get("KmsKeyId"),
                    }
                )
                result.add_evidence(evidence)

                if fully_encrypted:
                    compliant_count += 1
                    self.logger.debug(
                        "elasticache_replication_group_encrypted",
                        rep_group_id=rep_group_id
                    )
                else:
                    # Create finding for incomplete encryption
                    missing_encryption = []
                    if not at_rest_enabled:
                        missing_encryption.append("at-rest encryption")
                    if not transit_enabled:
                        missing_encryption.append("in-transit encryption")

                    finding = self.create_finding(
                        resource_id=rep_group_id,
                        resource_type="elasticache_replication_group",
                        severity=Severity.HIGH,
                        title=f"ElastiCache replication group missing {', '.join(missing_encryption)}",
                        description=f"Redis replication group '{rep_group_id}' with {num_node_groups} node group(s) "
                                    f"is missing {', '.join(missing_encryption)}. "
                                    f"At-rest encryption: {'enabled' if at_rest_enabled else 'disabled'}. "
                                    f"In-transit encryption: {'enabled' if transit_enabled else 'disabled'}. "
                                    "This violates ISO 27001 A.8.24 requirement for comprehensive data encryption.",
                        remediation=(
                            f"Encryption cannot be enabled on existing replication groups. To remediate:\n"
                            "1. Create a backup of the replication group:\n"
                            f"   aws elasticache create-snapshot --replication-group-id {rep_group_id} "
                            f"--snapshot-name {rep_group_id}-backup\n"
                            "2. Create a new replication group with encryption enabled:\n"
                            f"   aws elasticache create-replication-group \\\n"
                            f"     --replication-group-id {rep_group_id}-encrypted \\\n"
                            "     --replication-group-description 'Encrypted replacement' \\\n"
                            f"     --cache-node-type {engine} \\\n"
                            "     --at-rest-encryption-enabled \\\n"
                            "     --transit-encryption-enabled \\\n"
                            "     --auth-token <strong-password>\n"
                            "3. Migrate data using Redis replication or application-level migration\n"
                            "4. Update application connection strings (enable TLS)\n"
                            f"5. Delete old replication group '{rep_group_id}'\n\n"
                            "Note: This requires downtime and application updates for TLS support."
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "elasticache_replication_group_not_fully_encrypted",
                        rep_group_id=rep_group_id,
                        at_rest=at_rest_enabled,
                        transit=transit_enabled
                    )

            # Check standalone cache clusters
            for cluster in cache_clusters:
                cluster_id = cluster["CacheClusterId"]

                # Skip clusters that are part of replication groups (already checked)
                if cluster.get("ReplicationGroupId"):
                    continue

                result.resources_scanned += 1

                # For standalone clusters, check if encryption is possible
                at_rest_enabled = cluster.get("AtRestEncryptionEnabled", False)
                transit_enabled = cluster.get("TransitEncryptionEnabled", False)
                fully_encrypted = at_rest_enabled and transit_enabled

                # Get cluster details
                engine = cluster.get("Engine", "unknown")
                engine_version = cluster.get("EngineVersion", "unknown")
                cache_node_type = cluster.get("CacheNodeType", "unknown")

                # Create evidence
                evidence = self.create_evidence(
                    resource_id=cluster_id,
                    resource_type="elasticache_cluster",
                    data={
                        "cluster_id": cluster_id,
                        "at_rest_encryption_enabled": at_rest_enabled,
                        "transit_encryption_enabled": transit_enabled,
                        "fully_encrypted": fully_encrypted,
                        "engine": engine,
                        "engine_version": engine_version,
                        "cache_node_type": cache_node_type,
                    }
                )
                result.add_evidence(evidence)

                if fully_encrypted:
                    compliant_count += 1
                    self.logger.debug(
                        "elasticache_cluster_encrypted",
                        cluster_id=cluster_id
                    )
                else:
                    # Create finding for incomplete encryption
                    missing_encryption = []
                    if not at_rest_enabled:
                        missing_encryption.append("at-rest encryption")
                    if not transit_enabled:
                        missing_encryption.append("in-transit encryption")

                    finding = self.create_finding(
                        resource_id=cluster_id,
                        resource_type="elasticache_cluster",
                        severity=Severity.HIGH,
                        title=f"ElastiCache cluster missing {', '.join(missing_encryption)}",
                        description=f"{engine} cluster '{cluster_id}' (version {engine_version}) "
                                    f"is missing {', '.join(missing_encryption)}. "
                                    "This violates ISO 27001 A.8.24 requirement for comprehensive data encryption.",
                        remediation=(
                            f"Encryption cannot be enabled on existing clusters. To remediate:\n"
                            "1. Create a backup:\n"
                            f"   aws elasticache create-snapshot --cache-cluster-id {cluster_id} "
                            f"--snapshot-name {cluster_id}-backup\n"
                            "2. Create a new cluster with encryption:\n"
                            f"   aws elasticache create-cache-cluster \\\n"
                            f"     --cache-cluster-id {cluster_id}-encrypted \\\n"
                            f"     --engine {engine} \\\n"
                            f"     --cache-node-type {cache_node_type} \\\n"
                            "     --at-rest-encryption-enabled \\\n"
                            "     --transit-encryption-enabled\n"
                            "3. Migrate data and update application\n"
                            f"4. Delete old cluster '{cluster_id}'"
                        ),
                        evidence=evidence
                    )
                    result.add_finding(finding)

                    self.logger.warning(
                        "elasticache_cluster_not_fully_encrypted",
                        cluster_id=cluster_id,
                        at_rest=at_rest_enabled,
                        transit=transit_enabled
                    )

            # Calculate compliance score
            if total_resources > 0:
                result.score = (compliant_count / total_resources) * 100

            # Determine pass/fail
            result.passed = compliant_count == total_resources
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_resources": total_resources,
                "replication_groups": len(replication_groups),
                "standalone_clusters": len([c for c in cache_clusters if not c.get("ReplicationGroupId")]),
                "fully_encrypted": compliant_count,
                "not_fully_encrypted": total_resources - compliant_count,
                "compliance_percentage": result.score,
                "region": self.connector.region,
            }

            self.logger.info(
                "elasticache_encryption_test_completed",
                total=total_resources,
                compliant=compliant_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("elasticache_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("elasticache_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_elasticache_encryption_test(connector: AWSConnector) -> TestResult:
    """Run ElastiCache encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_elasticache_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = ElastiCacheEncryptionTest(connector)
    return test.execute()

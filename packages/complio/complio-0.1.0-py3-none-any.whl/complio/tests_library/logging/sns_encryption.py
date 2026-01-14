"""
SNS topic encryption compliance test.

Checks that all SNS topics use encryption at rest.

ISO 27001 Control: A.8.24 - Use of cryptography
Requirement: SNS topics must be encrypted with KMS keys

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.logging.sns_encryption import SNSEncryptionTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = SNSEncryptionTest(connector)
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


class SNSEncryptionTest(ComplianceTest):
    """Test for SNS topic encryption compliance.

    Verifies that all SNS topics use server-side encryption with KMS keys
    to protect message data at rest.

    Compliance Requirements:
        - All SNS topics must have KmsMasterKeyId configured
        - Encryption protects sensitive notification data
        - Customer-managed KMS keys recommended for better control

    Scoring:
        - 100% if all topics are encrypted
        - Proportional score based on compliant/total ratio
        - 100% if no topics exist

    Example:
        >>> test = SNSEncryptionTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize SNS encryption test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="sns_encryption",
            test_name="SNS Topic Encryption Check",
            description="Verify all SNS topics use encryption at rest with KMS",
            control_id="A.8.24",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute SNS topic encryption compliance test.

        Returns:
            TestResult with findings for unencrypted topics

        Example:
            >>> test = SNSEncryptionTest(connector)
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
            # Get SNS client
            sns_client = self.connector.get_client("sns")

            # List all SNS topics
            self.logger.info("listing_sns_topics")
            topics = []

            paginator = sns_client.get_paginator("list_topics")
            for page in paginator.paginate():
                topics.extend(page.get("Topics", []))

            if not topics:
                self.logger.info("no_sns_topics_found")
                result.metadata["message"] = "No SNS topics found in region"
                return result

            self.logger.info("sns_topics_found", count=len(topics))

            # Check encryption for each topic
            encrypted_count = 0

            for topic in topics:
                topic_arn = topic["TopicArn"]
                result.resources_scanned += 1

                try:
                    # Get topic attributes to check encryption
                    attributes_response = sns_client.get_topic_attributes(TopicArn=topic_arn)
                    attributes = attributes_response.get("Attributes", {})

                    # Check if KMS master key is configured
                    kms_master_key_id = attributes.get("KmsMasterKeyId")
                    is_encrypted = kms_master_key_id is not None and kms_master_key_id != ""

                    # Create evidence
                    evidence = self.create_evidence(
                        resource_id=topic_arn,
                        resource_type="sns_topic",
                        data={
                            "topic_arn": topic_arn,
                            "kms_master_key_id": kms_master_key_id,
                            "is_encrypted": is_encrypted,
                            "display_name": attributes.get("DisplayName"),
                            "subscriptions_confirmed": attributes.get("SubscriptionsConfirmed", "0"),
                        }
                    )
                    result.add_evidence(evidence)

                    if is_encrypted:
                        encrypted_count += 1
                        self.logger.debug(
                            "sns_topic_encrypted",
                            topic_arn=topic_arn,
                            kms_key_id=kms_master_key_id
                        )
                    else:
                        # Create finding for unencrypted topic
                        finding = self.create_finding(
                            resource_id=topic_arn,
                            resource_type="sns_topic",
                            severity=Severity.HIGH,
                            title="SNS topic encryption not enabled",
                            description=f"SNS topic '{topic_arn}' does not have encryption enabled. "
                                        "Without encryption, messages published to this topic are stored "
                                        "unencrypted at rest, potentially exposing sensitive notification "
                                        "data. SNS encryption with AWS KMS protects message data and metadata "
                                        "at rest. ISO 27001 A.8.24 requires cryptographic controls for "
                                        "protecting sensitive information.",
                            remediation=(
                                f"Enable encryption for SNS topic:\n\n"
                                "Using AWS CLI:\n"
                                f"aws sns set-topic-attributes \\\n"
                                f"  --topic-arn {topic_arn} \\\n"
                                "  --attribute-name KmsMasterKeyId \\\n"
                                "  --attribute-value alias/aws/sns\n\n"
                                "Or use a customer-managed KMS key (recommended):\n"
                                f"aws sns set-topic-attributes \\\n"
                                f"  --topic-arn {topic_arn} \\\n"
                                "  --attribute-name KmsMasterKeyId \\\n"
                                "  --attribute-value arn:aws:kms:REGION:ACCOUNT:key/KEY-ID\n\n"
                                "Or use AWS Console:\n"
                                "1. Go to AWS SNS console\n"
                                "2. Select the topic\n"
                                "3. Click 'Edit'\n"
                                "4. Expand 'Encryption'\n"
                                "5. Select 'Enable encryption'\n"
                                "6. Choose a KMS key (AWS managed or customer managed)\n"
                                "7. Click 'Save changes'\n\n"
                                "Important notes:\n"
                                "- Update KMS key policy to allow SNS to use it\n"
                                "- Publishers need kms:GenerateDataKey permission\n"
                                "- Subscribers need kms:Decrypt permission\n"
                                "- Consider using customer-managed keys for better audit trail"
                            ),
                            evidence=evidence
                        )
                        result.add_finding(finding)

                        self.logger.warning(
                            "sns_topic_not_encrypted",
                            topic_arn=topic_arn
                        )

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code")
                    if error_code in ["NotFound", "AuthorizationError"]:
                        self.logger.warning(
                            "sns_topic_access_error",
                            topic_arn=topic_arn,
                            error_code=error_code
                        )
                        continue
                    else:
                        raise

            # Calculate compliance score
            result.score = (encrypted_count / len(topics)) * 100

            # Determine pass/fail
            result.passed = encrypted_count == len(topics)
            result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED

            # Add metadata
            result.metadata = {
                "total_topics": len(topics),
                "encrypted_topics": encrypted_count,
                "unencrypted_topics": len(topics) - encrypted_count,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "sns_encryption_test_completed",
                total_topics=len(topics),
                encrypted=encrypted_count,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("sns_encryption_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("sns_encryption_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_sns_encryption_test(connector: AWSConnector) -> TestResult:
    """Run SNS topic encryption compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_sns_encryption_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = SNSEncryptionTest(connector)
    return test.execute()

"""
AWS Config enabled compliance test.

Checks that AWS Config is enabled for configuration tracking and compliance.

ISO 27001 Control: A.8.16 - Monitoring activities
Requirement: AWS Config should be enabled for resource configuration tracking

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.tests_library.logging.config_enabled import ConfigEnabledTest
    >>>
    >>> connector = AWSConnector("production", "us-east-1")
    >>> connector.connect()
    >>>
    >>> test = ConfigEnabledTest(connector)
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


class ConfigEnabledTest(ComplianceTest):
    """Test for AWS Config enabled compliance.

    Verifies that AWS Config is properly enabled and configured:
    - Configuration recorder should be created
    - Configuration recorder should be recording (not stopped)
    - Delivery channel should be configured (S3 bucket)
    - Should be recording all resource types (global and regional)

    Compliance Requirements:
        - AWS Config enabled in region
        - Recording all supported resource types
        - Delivery channel configured with S3 bucket
        - Configuration recorder in RECORDING state

    Scoring:
        - 100% if AWS Config is properly enabled and recording
        - 0% if AWS Config is not enabled or not recording
        - Partial score for partial configuration

    Example:
        >>> test = ConfigEnabledTest(connector)
        >>> result = test.execute()
        >>> for finding in result.findings:
        ...     print(f"{finding.resource_id}: {finding.title}")
    """

    def __init__(self, connector: AWSConnector) -> None:
        """Initialize AWS Config enabled test.

        Args:
            connector: AWS connector instance
        """
        super().__init__(
            test_id="config_enabled",
            test_name="AWS Config Enabled Check",
            description="Verify AWS Config is enabled for configuration tracking and compliance",
            control_id="A.8.16",
            connector=connector,
            scope="regional",
        )

    def execute(self) -> TestResult:
        """Execute AWS Config enabled compliance test.

        Returns:
            TestResult with findings if Config is not properly enabled

        Example:
            >>> test = ConfigEnabledTest(connector)
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
            # Get Config client
            config_client = self.connector.get_client("config")

            # Check configuration recorders
            self.logger.info("checking_config_recorders")
            recorders_response = config_client.describe_configuration_recorders()
            recorders = recorders_response.get("ConfigurationRecorders", [])

            if not recorders:
                self.logger.warning("no_config_recorders_found")

                # Create finding for missing Config
                finding = self.create_finding(
                    resource_id="aws-config",
                    resource_type="config_service",
                    severity=Severity.HIGH,
                    title="AWS Config not enabled",
                    description="AWS Config is not enabled in this region. AWS Config provides configuration "
                                "history, change tracking, and compliance monitoring for AWS resources. "
                                "Without Config, you cannot track configuration changes, assess compliance "
                                "against rules, or perform resource inventory. ISO 27001 A.8.16 requires "
                                "monitoring of system activities and configuration changes.",
                    remediation=(
                        "Enable AWS Config in this region:\n\n"
                        "1. Create S3 bucket for Config data:\n"
                        "aws s3 mb s3://my-config-bucket-<account-id>-<region>\n\n"
                        "# Enable versioning on the bucket\n"
                        "aws s3api put-bucket-versioning \\\n"
                        "  --bucket my-config-bucket-<account-id>-<region> \\\n"
                        "  --versioning-configuration Status=Enabled\n\n"
                        "2. Create IAM role for Config:\n"
                        "aws iam create-role \\\n"
                        "  --role-name AWSConfigRole \\\n"
                        "  --assume-role-policy-document file://config-trust-policy.json\n\n"
                        "# Attach AWS managed policy\n"
                        "aws iam attach-role-policy \\\n"
                        "  --role-name AWSConfigRole \\\n"
                        "  --policy-arn arn:aws:iam::aws:policy/service-role/ConfigRole\n\n"
                        "3. Create configuration recorder:\n"
                        "aws configservice put-configuration-recorder \\\n"
                        "  --configuration-recorder name=default,roleARN=arn:aws:iam::<account-id>:role/AWSConfigRole \\\n"
                        "  --recording-group allSupported=true,includeGlobalResourceTypes=true\n\n"
                        "4. Create delivery channel:\n"
                        "aws configservice put-delivery-channel \\\n"
                        "  --delivery-channel name=default,s3BucketName=my-config-bucket-<account-id>-<region>\n\n"
                        "5. Start configuration recorder:\n"
                        "aws configservice start-configuration-recorder \\\n"
                        "  --configuration-recorder-name default\n\n"
                        "Or use AWS Console:\n"
                        "1. Go to AWS Config console\n"
                        "2. Click 'Get started' (if first time)\n"
                        "3. Configure settings:\n"
                        "   - Resource types to record: All resources\n"
                        "   - Include global resources: Yes (in one region)\n"
                        "   - S3 bucket: Create new or use existing\n"
                        "   - SNS topic: Optional (for notifications)\n"
                        "   - IAM role: Create new or use existing\n"
                        "4. Click 'Confirm'\n\n"
                        "Best practices:\n"
                        "- Enable Config in all regions\n"
                        "- Record all supported resource types\n"
                        "- Include global resources in one region (usually us-east-1)\n"
                        "- Enable S3 bucket encryption\n"
                        "- Set up SNS notifications for changes\n"
                        "- Configure Config Rules for compliance checks\n"
                        "- Use Config Aggregator for multi-account view\n"
                        "- Set up lifecycle policies for S3 bucket\n"
                        "- Enable CloudTrail for Config API activity\n"
                        "- Use AWS Organizations for centralized Config\n\n"
                        "Config Rules to consider:\n"
                        "- required-tags (ensure proper tagging)\n"
                        "- encrypted-volumes (EBS encryption)\n"
                        "- rds-storage-encrypted (RDS encryption)\n"
                        "- s3-bucket-public-read-prohibited\n"
                        "- s3-bucket-public-write-prohibited\n"
                        "- cloudtrail-enabled\n"
                        "- iam-password-policy\n"
                        "- root-account-mfa-enabled\n"
                        "- vpc-flow-logs-enabled"
                    ),
                    evidence=None
                )
                result.add_finding(finding)
                result.score = 0.0
                result.passed = False
                result.status = TestStatus.FAILED
                result.metadata = {
                    "config_enabled": False,
                    "message": "AWS Config not enabled in region"
                }
                return result

            # Check first recorder (typically there's only one)
            recorder = recorders[0]
            recorder_name = recorder.get("name", "")
            role_arn = recorder.get("roleARN", "")
            recording_group = recorder.get("recordingGroup", {})

            all_supported = recording_group.get("allSupported", False)
            include_global = recording_group.get("includeGlobalResourceTypes", False)

            result.resources_scanned += 1

            # Check recorder status
            status_response = config_client.describe_configuration_recorder_status(
                ConfigurationRecorderNames=[recorder_name]
            )
            recorder_statuses = status_response.get("ConfigurationRecordersStatus", [])

            is_recording = False
            last_status = None
            if recorder_statuses:
                recorder_status = recorder_statuses[0]
                is_recording = recorder_status.get("recording", False)
                last_status = recorder_status.get("lastStatus", "")

            # Check delivery channel
            channels_response = config_client.describe_delivery_channels()
            channels = channels_response.get("DeliveryChannels", [])
            has_delivery_channel = len(channels) > 0

            # Determine issues
            issues = []
            severity = Severity.HIGH

            if not is_recording:
                issues.append("Configuration recorder not recording (stopped)")
                severity = Severity.HIGH

            if not all_supported:
                issues.append("Not recording all supported resource types")
                severity = Severity.MEDIUM

            if not has_delivery_channel:
                issues.append("No delivery channel configured (no S3 bucket)")
                severity = Severity.HIGH

            if last_status and last_status != "SUCCESS":
                issues.append(f"Last recording status: {last_status}")
                severity = Severity.MEDIUM

            # Create evidence
            evidence = self.create_evidence(
                resource_id=recorder_name,
                resource_type="config_recorder",
                data={
                    "recorder_name": recorder_name,
                    "role_arn": role_arn,
                    "is_recording": is_recording,
                    "all_supported": all_supported,
                    "include_global": include_global,
                    "has_delivery_channel": has_delivery_channel,
                    "last_status": last_status,
                    "has_issues": len(issues) > 0,
                    "issues": issues,
                }
            )
            result.add_evidence(evidence)

            if len(issues) > 0:
                # Create finding for Config issues
                finding = self.create_finding(
                    resource_id=recorder_name,
                    resource_type="config_recorder",
                    severity=severity,
                    title="AWS Config has configuration issues",
                    description=f"AWS Config recorder '{recorder_name}' has configuration issues: "
                                f"{'; '.join(issues)}. AWS Config should be actively recording all "
                                "supported resource types and delivering data to S3. ISO 27001 A.8.16 "
                                "requires proper monitoring and configuration tracking.",
                    remediation=(
                        f"Fix AWS Config recorder '{recorder_name}' issues:\n\n"
                        "1. Start configuration recorder if stopped:\n"
                        f"aws configservice start-configuration-recorder \\\n"
                        f"  --configuration-recorder-name {recorder_name}\n\n"
                        "2. Update to record all resource types:\n"
                        f"aws configservice put-configuration-recorder \\\n"
                        f"  --configuration-recorder name={recorder_name},roleARN={role_arn} \\\n"
                        "  --recording-group allSupported=true,includeGlobalResourceTypes=true\n\n"
                        "3. Configure delivery channel if missing:\n"
                        "aws configservice put-delivery-channel \\\n"
                        "  --delivery-channel name=default,s3BucketName=my-config-bucket\n\n"
                        "4. Verify recorder is working:\n"
                        f"aws configservice describe-configuration-recorder-status \\\n"
                        f"  --configuration-recorder-names {recorder_name}\n\n"
                        "Or use AWS Console:\n"
                        "1. Go to AWS Config console\n"
                        "2. Click 'Settings'\n"
                        "3. Verify configuration:\n"
                        "   - Recording is ON\n"
                        "   - All resources selected\n"
                        "   - Include global resources (if primary region)\n"
                        "   - S3 bucket configured\n"
                        "4. Click 'Save' if changes made\n\n"
                        "Troubleshooting:\n"
                        "- Check IAM role has correct permissions\n"
                        "- Verify S3 bucket exists and Config has access\n"
                        "- Check S3 bucket policy allows Config writes\n"
                        "- Verify region is correct\n"
                        "- Check service limits not exceeded\n"
                        "- Review CloudTrail for Config API errors"
                    ),
                    evidence=evidence
                )
                result.add_finding(finding)

                # Calculate partial score
                score_components = []
                if is_recording:
                    score_components.append(40)  # 40% for recording
                if has_delivery_channel:
                    score_components.append(40)  # 40% for delivery channel
                if all_supported:
                    score_components.append(20)  # 20% for recording all resources

                result.score = sum(score_components)
                result.passed = False
                result.status = TestStatus.FAILED

                self.logger.warning(
                    "config_has_issues",
                    recorder_name=recorder_name,
                    issues=issues
                )
            else:
                # Config is properly configured
                result.score = 100.0
                result.passed = True
                result.status = TestStatus.PASSED

                self.logger.info(
                    "config_properly_configured",
                    recorder_name=recorder_name
                )

            # Add metadata
            result.metadata = {
                "config_enabled": True,
                "recorder_name": recorder_name,
                "is_recording": is_recording,
                "all_supported": all_supported,
                "include_global": include_global,
                "has_delivery_channel": has_delivery_channel,
                "compliance_percentage": result.score,
            }

            self.logger.info(
                "config_enabled_test_completed",
                recorder_name=recorder_name,
                is_recording=is_recording,
                score=result.score,
                passed=result.passed
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            self.logger.error("config_enabled_test_error", error_code=error_code, error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = f"AWS API Error: {error_code} - {str(e)}"

        except Exception as e:
            self.logger.error("config_enabled_test_error", error=str(e))
            result.status = TestStatus.ERROR
            result.passed = False
            result.score = 0.0
            result.error_message = str(e)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def run_config_enabled_test(connector: AWSConnector) -> TestResult:
    """Run AWS Config enabled compliance test.

    Convenience function for running the test.

    Args:
        connector: AWS connector

    Returns:
        TestResult

    Example:
        >>> from complio.connectors.aws.client import AWSConnector
        >>> connector = AWSConnector("production", "us-east-1")
        >>> connector.connect()
        >>> result = run_config_enabled_test(connector)
        >>> print(f"Score: {result.score}%")
    """
    test = ConfigEnabledTest(connector)
    return test.execute()

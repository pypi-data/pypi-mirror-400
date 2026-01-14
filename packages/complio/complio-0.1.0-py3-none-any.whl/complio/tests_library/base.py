"""
Base classes for compliance tests.

This module defines the abstract base class for all compliance tests,
along with models for test results, evidence, and findings.

Example:
    >>> from complio.tests_library.base import ComplianceTest, TestResult
    >>> class MyTest(ComplianceTest):
    ...     def execute(self) -> TestResult:
    ...         # Implementation
    ...         pass
"""

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from complio.connectors.aws.client import AWSConnector
from complio.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# ENUMS
# ============================================================================


class TestStatus(str, Enum):
    """Test execution status."""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class Severity(str, Enum):
    """Finding severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# ============================================================================
# EVIDENCE MODELS
# ============================================================================


class Evidence(BaseModel):
    """Evidence collected during compliance test.

    Attributes:
        resource_id: Unique identifier for the AWS resource
        resource_type: Type of resource (e.g., 's3_bucket', 'ec2_instance')
        region: AWS region
        data: Raw data collected from AWS
        timestamp: When evidence was collected
        signature: SHA-256 hash of evidence for integrity

    Example:
        >>> evidence = Evidence(
        ...     resource_id="my-bucket",
        ...     resource_type="s3_bucket",
        ...     region="us-east-1",
        ...     data={"encryption": {"status": "enabled"}}
        ... )
    """

    resource_id: str = Field(..., description="Unique resource identifier")
    resource_type: str = Field(..., description="Type of AWS resource")
    region: str = Field(..., description="AWS region")
    data: Dict[str, Any] = Field(default_factory=dict, description="Raw evidence data")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Evidence collection timestamp"
    )
    signature: Optional[str] = Field(None, description="SHA-256 signature for integrity")

    def model_post_init(self, __context: Any) -> None:
        """Calculate signature after initialization."""
        if not self.signature:
            self.signature = self.calculate_signature()

    def calculate_signature(self) -> str:
        """Calculate SHA-256 signature of evidence.

        Creates a tamper-proof signature of the evidence data.

        Returns:
            Hexadecimal SHA-256 hash string

        Example:
            >>> evidence = Evidence(resource_id="test", resource_type="s3", region="us-east-1", data={})
            >>> sig = evidence.calculate_signature()
            >>> len(sig)
            64
        """
        # Create canonical representation
        canonical_data = {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "region": self.region,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }

        # Sort keys for deterministic hashing
        canonical_json = json.dumps(canonical_data, sort_keys=True)

        # Calculate SHA-256
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def verify_signature(self) -> bool:
        """Verify evidence signature.

        Returns:
            True if signature is valid, False otherwise

        Example:
            >>> evidence = Evidence(resource_id="test", resource_type="s3", region="us-east-1", data={})
            >>> evidence.verify_signature()
            True
        """
        expected_signature = self.calculate_signature()
        return self.signature == expected_signature


class Finding(BaseModel):
    """Compliance finding from a test.

    Attributes:
        resource_id: Resource with the finding
        resource_type: Type of resource
        severity: Finding severity level
        title: Short finding title
        description: Detailed description
        remediation: How to fix the finding
        evidence: Associated evidence

    Example:
        >>> finding = Finding(
        ...     resource_id="my-bucket",
        ...     resource_type="s3_bucket",
        ...     severity=Severity.HIGH,
        ...     title="S3 bucket not encrypted",
        ...     description="Bucket does not have default encryption enabled",
        ...     remediation="Enable default encryption in bucket settings"
        ... )
    """

    resource_id: str = Field(..., description="Resource identifier")
    resource_type: str = Field(..., description="Resource type")
    severity: Severity = Field(..., description="Finding severity")
    title: str = Field(..., description="Short finding title")
    description: str = Field(..., description="Detailed description")
    remediation: str = Field(..., description="Remediation steps")
    evidence: Optional[Evidence] = Field(None, description="Supporting evidence")

    model_config = ConfigDict(use_enum_values=True)


# ============================================================================
# TEST RESULT MODELS
# ============================================================================


class TestResult(BaseModel):
    """Result of a compliance test execution.

    Attributes:
        test_id: Unique test identifier
        test_name: Human-readable test name
        status: Test execution status
        passed: Whether test passed
        score: Compliance score (0-100)
        findings: List of findings
        evidence: List of evidence collected
        resources_scanned: Number of resources scanned
        start_time: Test start timestamp
        end_time: Test end timestamp
        duration_seconds: Test duration
        error_message: Error message if test failed
        metadata: Additional test metadata

    Example:
        >>> result = TestResult(
        ...     test_id="s3_encryption",
        ...     test_name="S3 Bucket Encryption Check",
        ...     status=TestStatus.PASSED,
        ...     passed=True,
        ...     score=100.0,
        ...     resources_scanned=5
        ... )
    """

    test_id: str = Field(..., description="Unique test identifier")
    test_name: str = Field(..., description="Human-readable test name")
    status: TestStatus = Field(..., description="Test status")
    passed: bool = Field(..., description="Whether test passed")
    score: float = Field(..., ge=0.0, le=100.0, description="Compliance score (0-100)")
    findings: List[Finding] = Field(default_factory=list, description="Test findings")
    evidence: List[Evidence] = Field(default_factory=list, description="Collected evidence")
    resources_scanned: int = Field(default=0, ge=0, description="Resources scanned")
    start_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Test start time"
    )
    end_time: Optional[datetime] = Field(None, description="Test end time")
    duration_seconds: Optional[float] = Field(None, description="Test duration")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(use_enum_values=True)

    def complete(self) -> None:
        """Mark test as complete and calculate duration.

        Example:
            >>> result = TestResult(test_id="test", test_name="Test", status=TestStatus.PASSED, passed=True, score=100)
            >>> result.complete()
            >>> assert result.duration_seconds is not None
        """
        self.end_time = datetime.now(timezone.utc)
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = delta.total_seconds()

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the test result.

        Args:
            finding: Finding to add

        Example:
            >>> result = TestResult(test_id="test", test_name="Test", status=TestStatus.FAILED, passed=False, score=50)
            >>> finding = Finding(
            ...     resource_id="bucket1",
            ...     resource_type="s3_bucket",
            ...     severity=Severity.HIGH,
            ...     title="Not encrypted",
            ...     description="Bucket not encrypted",
            ...     remediation="Enable encryption"
            ... )
            >>> result.add_finding(finding)
            >>> len(result.findings)
            1
        """
        self.findings.append(finding)

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the test result.

        Args:
            evidence: Evidence to add

        Example:
            >>> result = TestResult(test_id="test", test_name="Test", status=TestStatus.PASSED, passed=True, score=100)
            >>> evidence = Evidence(resource_id="bucket1", resource_type="s3_bucket", region="us-east-1", data={})
            >>> result.add_evidence(evidence)
            >>> len(result.evidence)
            1
        """
        self.evidence.append(evidence)


# ============================================================================
# BASE COMPLIANCE TEST
# ============================================================================


class ComplianceTest(ABC):
    """Abstract base class for compliance tests.

    All compliance tests must inherit from this class and implement
    the execute() method.

    Attributes:
        test_id: Unique test identifier
        test_name: Human-readable test name
        description: Test description
        control_id: ISO 27001 control ID (e.g., 'A.9.1.2')
        scope: Test scope ('global' or 'regional')
        connector: AWS connector
        region: AWS region

    Example:
        >>> class MyComplianceTest(ComplianceTest):
        ...     def execute(self) -> TestResult:
        ...         result = TestResult(
        ...             test_id=self.test_id,
        ...             test_name=self.test_name,
        ...             status=TestStatus.PASSED,
        ...             passed=True,
        ...             score=100.0
        ...         )
        ...         return result
    """

    def __init__(
        self,
        test_id: str,
        test_name: str,
        description: str,
        control_id: str,
        connector: AWSConnector,
        region: Optional[str] = None,
        scope: str = "regional",
    ) -> None:
        """Initialize compliance test.

        Args:
            test_id: Unique test identifier
            test_name: Human-readable test name
            description: Test description
            control_id: ISO 27001 control ID
            connector: AWS connector
            region: AWS region (uses connector region if not specified)
            scope: Test scope - 'global' (account-wide) or 'regional' (region-specific)
        """
        self.test_id = test_id
        self.test_name = test_name
        self.description = description
        self.control_id = control_id
        self.scope = scope
        self.connector = connector
        self.region = region or connector.region

        self.logger = get_logger(f"{__name__}.{self.test_id}")

    @abstractmethod
    def execute(self) -> TestResult:
        """Execute the compliance test.

        Returns:
            TestResult with findings and evidence

        Raises:
            Exception: If test execution fails

        Example:
            >>> test = MyComplianceTest(...)
            >>> result = test.execute()
            >>> print(result.passed)
            True
        """
        pass

    def run(self) -> TestResult:
        """Run the test with error handling.

        Wrapper around execute() that handles errors and logging.

        Returns:
            TestResult

        Example:
            >>> test = MyComplianceTest(...)
            >>> result = test.run()
        """
        self.logger.info(
            "test_started",
            test_id=self.test_id,
            test_name=self.test_name,
            region=self.region
        )

        try:
            result = self.execute()
            result.complete()

            # Add scope to metadata
            result.metadata["scope"] = self.scope
            result.metadata["iso27001_control"] = self.control_id

            self.logger.info(
                "test_completed",
                test_id=self.test_id,
                status=result.status,
                passed=result.passed,
                score=result.score,
                findings_count=len(result.findings),
                duration=result.duration_seconds
            )

            return result

        except Exception as e:
            self.logger.error(
                "test_failed",
                test_id=self.test_id,
                error=str(e)
            )

            # Create error result
            result = TestResult(
                test_id=self.test_id,
                test_name=self.test_name,
                status=TestStatus.ERROR,
                passed=False,
                score=0.0,
                error_message=str(e)
            )
            result.complete()

            return result

    def create_evidence(
        self,
        resource_id: str,
        resource_type: str,
        data: Dict[str, Any],
    ) -> Evidence:
        """Create evidence for a resource.

        Args:
            resource_id: Resource identifier
            resource_type: Resource type
            data: Evidence data

        Returns:
            Evidence object with signature

        Example:
            >>> test = MyComplianceTest(...)
            >>> evidence = test.create_evidence(
            ...     resource_id="my-bucket",
            ...     resource_type="s3_bucket",
            ...     data={"encryption": "enabled"}
            ... )
        """
        return Evidence(
            resource_id=resource_id,
            resource_type=resource_type,
            region=self.region,
            data=data
        )

    def create_finding(
        self,
        resource_id: str,
        resource_type: str,
        severity: Severity,
        title: str,
        description: str,
        remediation: str,
        evidence: Optional[Evidence] = None,
    ) -> Finding:
        """Create a compliance finding.

        Args:
            resource_id: Resource identifier
            resource_type: Resource type
            severity: Finding severity
            title: Finding title
            description: Finding description
            remediation: Remediation steps
            evidence: Supporting evidence

        Returns:
            Finding object

        Example:
            >>> test = MyComplianceTest(...)
            >>> finding = test.create_finding(
            ...     resource_id="my-bucket",
            ...     resource_type="s3_bucket",
            ...     severity=Severity.HIGH,
            ...     title="Bucket not encrypted",
            ...     description="Default encryption not enabled",
            ...     remediation="Enable default encryption"
            ... )
        """
        return Finding(
            resource_id=resource_id,
            resource_type=resource_type,
            severity=severity,
            title=title,
            description=description,
            remediation=remediation,
            evidence=evidence
        )

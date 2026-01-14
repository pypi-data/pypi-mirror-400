"""
Test runner for executing compliance tests.

This module provides the TestRunner class that orchestrates the execution
of compliance tests, handles parallelization, and collects results.

Example:
    >>> from complio.connectors.aws.client import AWSConnector
    >>> from complio.core.runner import TestRunner
    >>>
    >>> connector = AWSConnector("production", "us-east-1", password="...")
    >>> connector.connect()
    >>>
    >>> runner = TestRunner(connector)
    >>> results = runner.run_all()
    >>> print(f"Score: {results.overall_score}%")
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from complio.connectors.aws.client import AWSConnector
from complio.core.registry import TestRegistry
from complio.licensing.validator import LicenseValidator
from complio.tests_library.base import ComplianceTest, TestResult, TestStatus
from complio.utils.logger import get_logger


@dataclass
class ScanResults:
    """Results from a compliance scan.

    Attributes:
        test_results: List of individual test results
        total_tests: Total number of tests executed
        passed_tests: Number of tests that passed
        failed_tests: Number of tests that failed
        error_tests: Number of tests that errored
        overall_score: Average score across all tests
        execution_time: Total execution time in seconds
        region: AWS region scanned
        timestamp: Unix timestamp of scan start
    """

    test_results: List[TestResult]
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    overall_score: float = 0.0
    execution_time: float = 0.0
    region: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Calculate statistics from test results."""
        self.total_tests = len(self.test_results)

        if self.total_tests == 0:
            return

        # Count test statuses
        for result in self.test_results:
            if result.status == TestStatus.PASSED:
                self.passed_tests += 1
            elif result.status == TestStatus.ERROR:
                self.error_tests += 1
            elif result.status == TestStatus.WARNING:
                # WARNING counts as passed (score >= 70) but with findings
                self.passed_tests += 1
            else:
                self.failed_tests += 1

        # Calculate overall score (average of all test scores)
        total_score = sum(r.score for r in self.test_results)
        self.overall_score = round(total_score / self.total_tests, 2)


class TestRunner:
    """Execute compliance tests and collect results.

    This class orchestrates the execution of compliance tests,
    with support for parallel execution and progress reporting.

    Attributes:
        connector: AWS connector for accessing cloud resources
        registry: Test registry for discovering tests
        max_workers: Maximum number of parallel test executions

    Example:
        >>> connector = AWSConnector("prod", "us-east-1", password="...")
        >>> connector.connect()
        >>>
        >>> runner = TestRunner(connector, max_workers=4)
        >>> results = runner.run_all()
        >>>
        >>> print(f"Passed: {results.passed_tests}/{results.total_tests}")
        >>> print(f"Score: {results.overall_score}%")
    """

    def __init__(
        self,
        connector: AWSConnector,
        max_workers: int = 4,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> None:
        """Initialize test runner.

        Args:
            connector: AWS connector instance
            max_workers: Maximum parallel workers (default: 4)
            progress_callback: Optional callback for progress updates
                              Signature: (test_name, current, total) -> None

        Example:
            >>> def progress(test_name, current, total):
            ...     print(f"[{current}/{total}] Running {test_name}")
            >>>
            >>> runner = TestRunner(connector, progress_callback=progress)
        """
        self.connector = connector
        self.registry = TestRegistry()
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.logger = get_logger(__name__)

        # Initialize license validator and log tier
        self.validator = LicenseValidator()
        self.tier = self.validator.get_current_tier()
        self.logger.info(
            "test_runner_initialized",
            license_tier=self.tier,
            max_workers=max_workers,
            parallel=max_workers > 1
        )

    def run_all(self, parallel: bool = False) -> ScanResults:
        """Run all registered compliance tests.

        Args:
            parallel: Whether to run tests in parallel (default: False)

        Returns:
            ScanResults with all test results and statistics

        Example:
            >>> results = runner.run_all(parallel=True)
            >>> for result in results.test_results:
            ...     print(f"{result.test_name}: {result.score}%")
        """
        test_ids = self.registry.get_test_ids()
        return self.run_tests(test_ids, parallel=parallel)

    def run_tests(
        self,
        test_ids: List[str],
        parallel: bool = False,
    ) -> ScanResults:
        """Run specific compliance tests.

        Args:
            test_ids: List of test IDs to execute
            parallel: Whether to run tests in parallel

        Returns:
            ScanResults with test results and statistics

        Raises:
            KeyError: If any test_id is not found in registry

        Example:
            >>> results = runner.run_tests(["s3_encryption", "ec2_security_groups"])
            >>> print(f"Overall score: {results.overall_score}%")
        """
        self.logger.info(
            "starting_compliance_scan",
            test_count=len(test_ids),
            parallel=parallel,
            region=self.connector.region,
        )

        start_time = time.time()
        test_results: List[TestResult] = []

        if parallel:
            test_results = self._run_parallel(test_ids)
        else:
            test_results = self._run_sequential(test_ids)

        execution_time = time.time() - start_time

        results = ScanResults(
            test_results=test_results,
            execution_time=execution_time,
            region=self.connector.region,
        )

        self.logger.info(
            "compliance_scan_complete",
            total_tests=results.total_tests,
            passed=results.passed_tests,
            failed=results.failed_tests,
            errors=results.error_tests,
            score=results.overall_score,
            duration=execution_time,
        )

        return results

    def run_single_test(self, test_id: str) -> TestResult:
        """Run a single compliance test.

        Args:
            test_id: Test identifier

        Returns:
            TestResult for the executed test

        Raises:
            KeyError: If test_id not found

        Example:
            >>> result = runner.run_single_test("s3_encryption")
            >>> print(f"S3 Encryption: {result.score}% - {'PASS' if result.passed else 'FAIL'}")
        """
        test_class = self.registry.get_test(test_id)
        test_instance = test_class(self.connector)

        self.logger.info("running_test", test_id=test_id, test_name=test_instance.test_name)

        try:
            result = test_instance.run()
            self.logger.info(
                "test_complete",
                test_id=test_id,
                passed=result.passed,
                score=result.score,
                findings_count=len(result.findings),
            )
            return result
        except Exception as e:
            self.logger.error(
                "test_execution_failed",
                test_id=test_id,
                error=str(e),
            )
            # Return error result
            from complio.tests_library.base import Finding, Severity

            return TestResult(
                test_id=test_id,
                test_name=test_instance.test_name,
                status=TestStatus.ERROR,
                passed=False,
                score=0.0,
                findings=[
                    Finding(
                        resource_id="N/A",
                        resource_type="test_execution",
                        severity=Severity.CRITICAL,
                        title=f"Test execution failed: {test_id}",
                        description=f"Error during test execution: {str(e)}",
                        remediation="Check test logs for details",
                    )
                ],
                evidence=[],
                metadata={"error": str(e), "test_id": test_id},
            )

    def _run_sequential(self, test_ids: List[str]) -> List[TestResult]:
        """Run tests sequentially.

        Args:
            test_ids: List of test IDs to execute

        Returns:
            List of test results
        """
        results: List[TestResult] = []
        total = len(test_ids)

        for index, test_id in enumerate(test_ids, start=1):
            if self.progress_callback:
                test_class = self.registry.get_test(test_id)
                test_instance = test_class(self.connector)
                test_name = test_instance.test_name
                scope = getattr(test_instance, 'scope', 'regional')
                self.progress_callback(test_name, index, total, scope)

            result = self.run_single_test(test_id)
            results.append(result)

        return results

    def _run_parallel(self, test_ids: List[str]) -> List[TestResult]:
        """Run tests in parallel using thread pool.

        Args:
            test_ids: List of test IDs to execute

        Returns:
            List of test results (order may differ from input)
        """
        results: List[TestResult] = []
        total = len(test_ids)
        completed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tests
            future_to_test_id = {
                executor.submit(self.run_single_test, test_id): test_id
                for test_id in test_ids
            }

            # Collect results as they complete
            for future in as_completed(future_to_test_id):
                test_id = future_to_test_id[future]
                completed += 1

                try:
                    result = future.result()
                    results.append(result)

                    if self.progress_callback:
                        self.progress_callback(result.test_name, completed, total)

                except Exception as e:
                    self.logger.error(
                        "parallel_test_failed",
                        test_id=test_id,
                        error=str(e),
                    )

        return results

    def get_available_tests(self) -> Dict[str, str]:
        """Get dictionary of available tests.

        Returns:
            Dictionary of test_id -> test_name mappings

        Example:
            >>> tests = runner.get_available_tests()
            >>> for test_id, test_name in tests.items():
            ...     print(f"{test_id}: {test_name}")
        """
        test_dict = {}
        for test_id in self.registry.get_test_ids():
            test_class = self.registry.get_test(test_id)
            # Create temporary instance to get test name
            temp_instance = test_class(self.connector)
            test_dict[test_id] = temp_instance.test_name

        return test_dict

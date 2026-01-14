"""
Report generation for compliance scan results.

This module provides formatters for generating compliance reports
in various formats (JSON, Markdown, HTML, PDF).

Example:
    >>> from complio.reporters.generator import ReportGenerator
    >>> generator = ReportGenerator()
    >>> json_report = generator.generate_json(scan_results)
    >>> markdown_report = generator.generate_markdown(scan_results)
"""

import json
import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from complio.core.runner import ScanResults
from complio.tests_library.base import Severity, TestStatus


def generate_scan_id() -> str:
    """Generate a unique scan identifier.

    Returns:
        Unique scan ID in format: scan_YYYYMMDD_HHMMSS_abc123

    Example:
        >>> scan_id = generate_scan_id()
        >>> print(scan_id)
        'scan_20240115_162335_abc123'
    """
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"scan_{timestamp}_{random_suffix}"


def get_complio_version() -> str:
    """Get Complio version.

    Returns:
        Version string

    Example:
        >>> version = get_complio_version()
        >>> print(version)
        '0.1.0'
    """
    try:
        from complio.config.settings import get_settings
        settings = get_settings()
        return settings.VERSION
    except Exception:
        return "unknown"


def sanitize_resource_name(name: str) -> str:
    """Sanitize resource names to handle special characters safely.

    Ensures resource names with Unicode characters, emojis, or other
    special characters are safely displayable in reports without causing
    encoding errors.

    Args:
        name: Resource name to sanitize

    Returns:
        Sanitized resource name that can be safely displayed

    Example:
        >>> sanitize_resource_name("bucket-émojis-🎉")
        'bucket-émojis-🎉'
        >>> sanitize_resource_name("test-\udcff-invalid")
        'test-�-invalid'
    """
    if not isinstance(name, str):
        return str(name)

    try:
        # Try to encode/decode to catch issues early
        name.encode('utf-8').decode('utf-8')
        return name
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Replace problematic characters with replacement character
        return name.encode('utf-8', errors='replace').decode('utf-8')


class ReportGenerator:
    """Generate compliance reports in various formats.

    This class provides methods to format ScanResults into
    different output formats suitable for humans and machines.

    Example:
        >>> generator = ReportGenerator()
        >>> json_str = generator.generate_json(results)
        >>> markdown_str = generator.generate_markdown(results)
        >>> generator.save_report(results, Path("report.md"), "markdown")
    """

    def generate_json(self, results: ScanResults) -> str:
        """Generate JSON format report.

        Args:
            results: Scan results to format

        Returns:
            JSON formatted string

        Example:
            >>> json_report = generator.generate_json(scan_results)
            >>> with open("report.json", "w") as f:
            ...     f.write(json_report)
        """
        # Categorize tests by scope
        global_tests = []
        regional_tests = []
        for test_result in results.test_results:
            scope = test_result.metadata.get("scope", "regional")
            if scope == "global":
                global_tests.append(test_result.test_name)
            else:
                regional_tests.append(test_result.test_name)

        # Generate unique scan ID
        scan_id = generate_scan_id()

        report_data = {
            "scan_metadata": {
                "scan_id": scan_id,
                "timestamp": datetime.fromtimestamp(results.timestamp).isoformat(),
                "complio_version": get_complio_version(),
                "region": results.region,
                "execution_time_seconds": round(results.execution_time, 2),
                "scope_note": "S3 and IAM are global services. Results apply to entire account. EC2 and CloudTrail are regional.",
            },
            "scan_scope": {
                "global_services": global_tests,
                "regional_services": regional_tests,
                "scanned_region": results.region,
            },
            "summary": {
                "total_tests": results.total_tests,
                "passed_tests": results.passed_tests,
                "failed_tests": results.failed_tests,
                "error_tests": results.error_tests,
                "overall_score": results.overall_score,
                "compliance_status": "COMPLIANT" if results.overall_score >= 90 else "NON_COMPLIANT",
            },
            "test_results": [],
        }

        # Add each test result
        for test_result in results.test_results:
            scope = test_result.metadata.get("scope", "regional")
            scope_description = "Scans all regions across the account" if scope == "global" else f"Only scans {results.region}"

            test_data = {
                "test_id": test_result.test_id,
                "test_name": test_result.test_name,
                "scope": scope,
                "scope_description": scope_description,
                "status": test_result.status,  # Already a string due to use_enum_values=True
                "passed": test_result.passed,
                "score": test_result.score,
                "findings_count": len(test_result.findings),
                "evidence_count": len(test_result.evidence),
                "findings": [],
                "evidence": [],
                "metadata": test_result.metadata,
            }

            # Add findings
            for finding in test_result.findings:
                test_data["findings"].append({
                    "resource_id": sanitize_resource_name(finding.resource_id),
                    "resource_type": sanitize_resource_name(finding.resource_type),
                    "severity": finding.severity,  # Already a string due to use_enum_values=True
                    "title": finding.title,
                    "description": finding.description,
                    "remediation": finding.remediation,
                    # Note: iso27001_control is in test_result.metadata, not in individual findings
                })

            # Add evidence
            for evidence in test_result.evidence:
                test_data["evidence"].append({
                    "resource_id": sanitize_resource_name(evidence.resource_id),
                    "resource_type": sanitize_resource_name(evidence.resource_type),
                    "region": evidence.region,
                    "timestamp": evidence.timestamp.isoformat() if evidence.timestamp else None,
                    "data": evidence.data,
                    "signature": evidence.signature,
                })

            report_data["test_results"].append(test_data)

        return json.dumps(report_data, indent=2)

    def generate_markdown(self, results: ScanResults) -> str:
        """Generate Markdown format report.

        Args:
            results: Scan results to format

        Returns:
            Markdown formatted string

        Example:
            >>> md_report = generator.generate_markdown(scan_results)
            >>> with open("report.md", "w") as f:
            ...     f.write(md_report)
        """
        lines: List[str] = []

        # Header
        lines.append("# Compliance Scan Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.fromtimestamp(results.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Region:** {results.region}")
        lines.append(f"**Execution Time:** {results.execution_time:.2f} seconds")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")

        compliance_status = "✅ **COMPLIANT**" if results.overall_score >= 90 else "❌ **NON-COMPLIANT**"
        lines.append(f"**Overall Status:** {compliance_status}")
        lines.append(f"**Overall Score:** {results.overall_score}%")
        lines.append("")

        lines.append("### Test Statistics")
        lines.append("")
        lines.append(f"- **Total Tests:** {results.total_tests}")
        lines.append(f"- **Passed:** ✅ {results.passed_tests}")
        lines.append(f"- **Failed:** ❌ {results.failed_tests}")
        lines.append(f"- **Errors:** ⚠️ {results.error_tests}")
        lines.append("")

        # Scan Scope Section
        lines.append("## Scan Scope")
        lines.append("")

        # Categorize tests by scope
        global_tests = []
        regional_tests = []
        for test_result in results.test_results:
            scope = test_result.metadata.get("scope", "regional")
            if scope == "global":
                global_tests.append(test_result.test_name)
            else:
                regional_tests.append(test_result.test_name)

        if global_tests:
            lines.append("**Global Services (Account-wide):**")
            lines.append("")
            lines.append("These services are evaluated once and apply to your entire AWS account:")
            lines.append("")
            for test_name in global_tests:
                lines.append(f"- ✅ {test_name}")
            lines.append("")

        if regional_tests:
            lines.append(f"**Regional Services ({results.region} only):**")
            lines.append("")
            lines.append("These services are specific to the scanned region:")
            lines.append("")
            for test_name in regional_tests:
                lines.append(f"- ✅ {test_name}")
            lines.append("")

        if regional_tests:
            lines.append("💡 **Tip:** Run scans in each region where you have infrastructure to check regional services.")
            lines.append("")

        # Test Results
        lines.append("## Test Results")
        lines.append("")

        for test_result in results.test_results:
            # Test header
            # Use string keys since test_result.status is a string (due to use_enum_values=True)
            status_emoji = {
                "passed": "✅",
                "warning": "⚠️",
                "failed": "❌",
                "error": "🚫",
            }.get(test_result.status, "❓")

            lines.append(f"### {status_emoji} {test_result.test_name}")
            lines.append("")
            lines.append(f"**Test ID:** `{test_result.test_id}`")
            lines.append(f"**Status:** {test_result.status}")  # Already a string
            lines.append(f"**Score:** {test_result.score}%")
            lines.append(f"**ISO 27001 Control:** {test_result.metadata.get('iso27001_control', 'N/A')}")
            lines.append("")

            # Findings
            if test_result.findings:
                lines.append(f"**Findings:** {len(test_result.findings)}")
                lines.append("")

                for finding in test_result.findings:
                    # Use string keys since finding.severity is a string (due to use_enum_values=True)
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🔵",
                        "info": "ℹ️",
                    }.get(finding.severity, "❓")

                    lines.append(f"#### {severity_emoji} {finding.severity}: {finding.title}")  # severity is already a string
                    lines.append("")
                    safe_resource_id = sanitize_resource_name(finding.resource_id)
                    safe_resource_type = sanitize_resource_name(finding.resource_type)
                    lines.append(f"**Resource:** `{safe_resource_id}` ({safe_resource_type})")
                    lines.append("")
                    lines.append(f"**Description:**")
                    lines.append(f"{finding.description}")
                    lines.append("")
                    lines.append(f"**Remediation:**")
                    lines.append(f"{finding.remediation}")
                    lines.append("")
            else:
                lines.append("**Findings:** None - All checks passed ✅")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Summary Statistics
        lines.append("## Summary Statistics")
        lines.append("")

        # Count findings by severity
        # Use string keys since finding.severity is a string (due to use_enum_values=True)
        severity_counts: Dict[str, int] = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for test_result in results.test_results:
            for finding in test_result.findings:
                severity_counts[finding.severity] += 1

        lines.append("### Findings by Severity")
        lines.append("")
        lines.append(f"- 🔴 **CRITICAL:** {severity_counts['critical']}")
        lines.append(f"- 🟠 **HIGH:** {severity_counts['high']}")
        lines.append(f"- 🟡 **MEDIUM:** {severity_counts['medium']}")
        lines.append(f"- 🔵 **LOW:** {severity_counts['low']}")
        lines.append(f"- ℹ️ **INFO:** {severity_counts['info']}")
        lines.append("")

        # Recommendations
        if severity_counts["critical"] > 0 or severity_counts["high"] > 0:
            lines.append("## 🚨 Immediate Actions Required")
            lines.append("")
            lines.append("This scan identified CRITICAL or HIGH severity findings that require immediate attention:")
            lines.append("")

            for test_result in results.test_results:
                for finding in test_result.findings:
                    # finding.severity is a string, so compare with strings
                    if finding.severity in ["critical", "high"]:
                        lines.append(f"- **{finding.title}** ({finding.severity})")  # severity is already a string

            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by Complio - Compliance-as-Code Platform*")
        lines.append("")

        return "\n".join(lines)

    def save_report(
        self,
        results: ScanResults,
        output_path: Path,
        format: str = "json",
    ) -> None:
        """Save report to file.

        Args:
            results: Scan results to save
            output_path: Path to output file
            format: Report format ("json" or "markdown")

        Raises:
            ValueError: If format is not supported

        Example:
            >>> generator.save_report(results, Path("report.json"), "json")
            >>> generator.save_report(results, Path("report.md"), "markdown")
        """
        if format == "json":
            content = self.generate_json(results)
        elif format == "markdown":
            content = self.generate_markdown(results)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'markdown'")

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write report
        output_path.write_text(content, encoding="utf-8")

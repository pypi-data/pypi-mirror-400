"""
Scan history tracking for Complio.

This module manages local storage of scan results to allow users to:
- View recent scans
- Compare scan results over time
- Track compliance improvements

Example:
    >>> from complio.utils.history import save_scan_to_history, get_scan_history
    >>> save_scan_to_history(scan_id, results)
    >>> history = get_scan_history(limit=10)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from complio.core.runner import ScanResults


# History directory location
SCAN_HISTORY_DIR = Path.home() / ".complio" / "history"


def ensure_history_dir() -> Path:
    """Ensure scan history directory exists with proper permissions.

    Returns:
        Path to history directory

    Example:
        >>> history_dir = ensure_history_dir()
        >>> print(history_dir)
        PosixPath('/home/user/.complio/history')
    """
    SCAN_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    # Set directory permissions to 700 (owner only)
    SCAN_HISTORY_DIR.chmod(0o700)
    return SCAN_HISTORY_DIR


def save_scan_to_history(scan_id: str, results: ScanResults, region: str) -> Path:
    """Save scan results to local history.

    Args:
        scan_id: Unique scan identifier
        results: Scan results to save
        region: AWS region that was scanned

    Returns:
        Path to saved history file

    Example:
        >>> save_scan_to_history("scan_20260107_162335_abc123", results, "eu-west-3")
        PosixPath('/home/user/.complio/history/scan_20260107_162335_abc123.json')
    """
    history_dir = ensure_history_dir()
    filepath = history_dir / f"{scan_id}.json"

    # Prepare history data
    history_data = {
        "scan_id": scan_id,
        "timestamp": datetime.fromtimestamp(results.timestamp).isoformat(),
        "region": region,
        "summary": {
            "total_tests": results.total_tests,
            "passed_tests": results.passed_tests,
            "failed_tests": results.failed_tests,
            "error_tests": results.error_tests,
            "overall_score": results.overall_score,
            "compliance_status": "COMPLIANT" if results.overall_score >= 90 else "NON_COMPLIANT",
            "execution_time_seconds": round(results.execution_time, 2),
        },
        "test_results": [
            {
                "test_id": tr.test_id,
                "test_name": tr.test_name,
                "status": tr.status,
                "passed": tr.passed,
                "score": tr.score,
                "findings_count": len(tr.findings),
            }
            for tr in results.test_results
        ],
    }

    # Save to file
    with open(filepath, 'w') as f:
        json.dump(history_data, f, indent=2)

    # Set file permissions to 600 (owner read/write only)
    filepath.chmod(0o600)

    return filepath


def get_scan_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Get list of recent scans from history.

    Args:
        limit: Maximum number of scans to return (default: 10)

    Returns:
        List of scan history entries, most recent first

    Example:
        >>> history = get_scan_history(limit=5)
        >>> for scan in history:
        ...     print(f"{scan['timestamp']}: {scan['summary']['overall_score']}%")
    """
    if not SCAN_HISTORY_DIR.exists():
        return []

    # Get all scan files
    scan_files = sorted(
        SCAN_HISTORY_DIR.glob("scan_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True  # Most recent first
    )

    history = []
    for scan_file in scan_files[:limit]:
        try:
            with open(scan_file, 'r') as f:
                data = json.load(f)
                history.append(data)
        except (json.JSONDecodeError, KeyError):
            # Skip corrupted files
            continue

    return history


def get_scan_by_id(scan_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific scan by its ID.

    Args:
        scan_id: Scan identifier to retrieve

    Returns:
        Scan data dictionary, or None if not found

    Example:
        >>> scan = get_scan_by_id("scan_20260107_162335_abc123")
        >>> if scan:
        ...     print(scan['summary']['overall_score'])
    """
    filepath = SCAN_HISTORY_DIR / f"{scan_id}.json"

    if not filepath.exists():
        return None

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def compare_scans(scan_id_1: str, scan_id_2: str) -> Dict[str, Any]:
    """Compare two scans and return the differences.

    Args:
        scan_id_1: First scan ID
        scan_id_2: Second scan ID

    Returns:
        Dictionary containing comparison data

    Example:
        >>> diff = compare_scans("scan_20260107_...", "scan_20260106_...")
        >>> print(f"Score change: {diff['score_change']}%")
    """
    scan1 = get_scan_by_id(scan_id_1)
    scan2 = get_scan_by_id(scan_id_2)

    if not scan1 or not scan2:
        raise ValueError(f"One or both scans not found in history")

    # Calculate differences
    score1 = scan1['summary']['overall_score']
    score2 = scan2['summary']['overall_score']
    score_change = score1 - score2

    passed1 = scan1['summary']['passed_tests']
    passed2 = scan2['summary']['passed_tests']

    failed1 = scan1['summary']['failed_tests']
    failed2 = scan2['summary']['failed_tests']

    return {
        "scan1": {
            "scan_id": scan1['scan_id'],
            "timestamp": scan1['timestamp'],
            "score": score1,
            "passed": passed1,
            "failed": failed1,
        },
        "scan2": {
            "scan_id": scan2['scan_id'],
            "timestamp": scan2['timestamp'],
            "score": score2,
            "passed": passed2,
            "failed": failed2,
        },
        "differences": {
            "score_change": score_change,
            "score_change_direction": "improved" if score_change > 0 else "declined" if score_change < 0 else "unchanged",
            "passed_change": passed1 - passed2,
            "failed_change": failed1 - failed2,
        }
    }


def clear_old_history(keep_days: int = 30) -> int:
    """Clear scan history older than specified days.

    Args:
        keep_days: Number of days to keep (default: 30)

    Returns:
        Number of files deleted

    Example:
        >>> deleted = clear_old_history(keep_days=30)
        >>> print(f"Deleted {deleted} old scans")
    """
    if not SCAN_HISTORY_DIR.exists():
        return 0

    from datetime import timedelta
    cutoff_time = datetime.now().timestamp() - (keep_days * 86400)

    deleted_count = 0
    for scan_file in SCAN_HISTORY_DIR.glob("scan_*.json"):
        if scan_file.stat().st_mtime < cutoff_time:
            scan_file.unlink()
            deleted_count += 1

    return deleted_count

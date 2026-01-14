"""
Licensing module for Complio.

This module provides license validation, feature gating, and upgrade messaging.
"""

from complio.licensing.exceptions import (
    FeatureNotAvailableError,
    InvalidLicenseError,
    LicenseAPIError,
    LicenseError,
    LicenseExpiredError,
)
from complio.licensing.models import LicenseCache, LicenseInfo
from complio.licensing.validator import (
    DEV_MODE,
    TIER_FEATURES,
    TEST_LICENSE_KEYS,
    LicenseValidator,
)

__all__ = [
    # Validator
    "LicenseValidator",
    "TIER_FEATURES",
    "DEV_MODE",
    "TEST_LICENSE_KEYS",
    # Models
    "LicenseInfo",
    "LicenseCache",
    # Exceptions
    "LicenseError",
    "InvalidLicenseError",
    "LicenseExpiredError",
    "FeatureNotAvailableError",
    "LicenseAPIError",
]

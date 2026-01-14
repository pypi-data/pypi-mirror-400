"""
License validation and feature gating for Complio.

This module implements the core licensing logic with DEV MODE support
for testing without a backend API.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import structlog

from complio.config.settings import get_settings
from complio.licensing.exceptions import (
    FeatureNotAvailableError,
    InvalidLicenseError,
    LicenseAPIError,
    LicenseExpiredError,
)
from complio.licensing.models import LicenseCache, LicenseInfo

# ============================================================================
# DEV MODE CONFIGURATION - CRITICAL FOR TESTING
# ============================================================================

# DEV_MODE: Bypass all licensing checks and grant Early Access tier
DEV_MODE = os.getenv("COMPLIO_DEV_MODE", "false").lower() == "true"

# Test license keys that always work (no backend required)
TEST_LICENSE_KEYS = [
    "TEST-TEST-TEST-TEST",
    "DEV0-DEV0-DEV0-DEV0",
    "DEMO-DEMO-DEMO-DEMO",
]

# License API URL (configurable for testing)
# Default to Vercel backend production URL
LICENSE_API_URL = os.getenv(
    "COMPLIO_LICENSE_API_URL",
    "https://complio-backend.vercel.app/api/validate-license"
)

# Validate HTTPS enforcement (except localhost for development)
if LICENSE_API_URL and not ("localhost" in LICENSE_API_URL or "127.0.0.1" in LICENSE_API_URL):
    if not LICENSE_API_URL.startswith("https://"):
        raise ValueError(
            f"SECURITY ERROR: License API URL must use HTTPS for security. "
            f"Received: {LICENSE_API_URL}. "
            f"HTTPS is required to protect your license key during transmission."
        )

# ============================================================================
# TIER FEATURES MAPPING
# ============================================================================

TIER_FEATURES: dict[str, list[str]] = {
    "free": [],  # No features - must upgrade
    "early_access": [
        "scanning",
        "basic_tests",
        "advanced_tests",
        "markdown_reports",
        "json_reports",
        "pdf_reports",
        "email_notifications",
        "multi_profile",
        "multi_region",
        "parallel_execution",
    ],
    "pro": [
        # Same as early_access for now
        "scanning",
        "basic_tests",
        "advanced_tests",
        "markdown_reports",
        "json_reports",
        "pdf_reports",
        "email_notifications",
        "multi_profile",
        "multi_region",
        "parallel_execution",
    ],
    "enterprise": [
        # All pro features plus enterprise-only
        "scanning",
        "basic_tests",
        "advanced_tests",
        "markdown_reports",
        "json_reports",
        "pdf_reports",
        "email_notifications",
        "multi_profile",
        "multi_region",
        "parallel_execution",
        "multi_cloud",
        "soc2_framework",
        "api_access",
        "sso",
        "multi_user",
        "audit_logs",
        "custom_tests",
    ],
}

logger = structlog.get_logger(__name__)


class LicenseValidator:
    """
    License validator with DEV MODE support.

    This class handles license validation, caching, and feature gating.
    It includes three bypass mechanisms for development:
    1. COMPLIO_DEV_MODE=true environment variable
    2. Hardcoded test license keys
    3. Offline mode fallback for localhost APIs
    """

    def __init__(self) -> None:
        """Initialize the license validator."""
        self.settings = get_settings()
        self.cache_path = self._get_cache_path()
        self.cache: LicenseCache | None = None

        # Load existing cache if available
        self._load_cache()

        # Log warning if DEV_MODE is active
        if DEV_MODE:
            logger.warning(
                "dev_mode_active",
                message="DEV_MODE enabled - all licensing bypassed",
                tier="early_access",
                bypass_method="COMPLIO_DEV_MODE environment variable"
            )

    def _get_cache_path(self) -> Path:
        """Get the path to the license cache file."""
        complio_dir = Path.home() / ".complio"
        complio_dir.mkdir(mode=0o700, exist_ok=True)
        return complio_dir / "license.json"

    def activate(self, license_key: str) -> LicenseInfo:
        """
        Activate a license key.

        Args:
            license_key: The license key to activate (format: COMPL-XXXX-XXXX-XXXX-XXXX)

        Returns:
            LicenseInfo object with license details

        Raises:
            InvalidLicenseError: If the key format is invalid or key is rejected
            LicenseExpiredError: If the license has expired
            LicenseAPIError: If the API is unreachable
        """
        # Validate key format
        if not self._validate_key_format(license_key):
            raise InvalidLicenseError(
                "Invalid license key format. Expected: COMPL-XXXX-XXXX-XXXX-XXXX"
            )

        logger.info("activating_license", key_masked=self._mask_key(license_key))

        # Validate with API (handles test keys internally)
        license_info = self._validate_online(license_key)

        # Check if expired
        if license_info.is_expired():
            raise LicenseExpiredError(
                expired_at=license_info.expires.isoformat() if license_info.expires else "unknown"
            )

        # Save to cache
        self._save_cache(license_key, license_info)

        logger.info(
            "license_activated",
            tier=license_info.tier,
            early_access=license_info.early_access,
            founder=license_info.is_founder()
        )

        return license_info

    def get_current_tier(self) -> str:
        """
        Get the current license tier.

        Returns:
            Tier name: "free", "early_access", "pro", or "enterprise"
        """
        # FIRST: Check DEV_MODE
        if DEV_MODE:
            logger.debug("dev_mode_tier_override", tier="early_access")
            return "early_access"

        # Check cache
        if self.cache is None:
            logger.debug("no_license_cache", tier="free")
            return "free"

        # Refresh if stale (7 days)
        if self.cache.is_stale(max_age_days=7):
            logger.info("license_cache_stale", refreshing=True)
            try:
                # Try to refresh from API
                license_info = self._validate_online(self.cache.license_key)
                self._save_cache(self.cache.license_key, license_info)
            except LicenseAPIError:
                # API unreachable - use stale cache with grace period
                logger.warning(
                    "license_refresh_failed",
                    using_stale_cache=True,
                    message="Using cached license (offline mode)"
                )

        # Check if license is expired
        if self.cache.license_info.is_expired():
            logger.warning("license_expired", tier="free")
            return "free"

        return self.cache.license_info.tier

    def has_feature(self, feature: str) -> bool:
        """
        Check if a feature is available in the current license tier.

        Args:
            feature: Feature name (e.g., "scanning", "pdf_reports")

        Returns:
            True if feature is available, False otherwise
        """
        # FIRST: Check DEV_MODE - grant all features
        if DEV_MODE:
            logger.debug("dev_mode_feature_granted", feature=feature)
            return True

        tier = self.get_current_tier()
        available_features = TIER_FEATURES.get(tier, [])

        has_access = feature in available_features

        logger.debug(
            "feature_check",
            feature=feature,
            tier=tier,
            has_access=has_access
        )

        return has_access

    def require_feature(
        self,
        feature: str,
        required_tier: str = "early_access"
    ) -> None:
        """
        Require a feature to be available, raising an exception if not.

        Args:
            feature: Feature name to check
            required_tier: Tier required for this feature

        Raises:
            FeatureNotAvailableError: If feature is not available in current tier
        """
        if not self.has_feature(feature):
            current_tier = self.get_current_tier()
            raise FeatureNotAvailableError(
                feature=feature,
                current_tier=current_tier,
                required_tier=required_tier
            )

    def get_license_info(self) -> LicenseInfo | None:
        """
        Get the current license information.

        Returns:
            LicenseInfo object if license is active, None otherwise
        """
        # FIRST: Check DEV_MODE - return fake license
        if DEV_MODE:
            logger.debug("dev_mode_license_info_override")
            return LicenseInfo(
                valid=True,
                tier="early_access",
                early_access=True,
                expires=None,  # Lifetime
                features=TIER_FEATURES["early_access"],
                email="dev@localhost",
                company="Development Mode",
                locked_price=0.0,
                founder_badge=True,
                activated_at=datetime.now(),
                metadata={
                    "dev_mode": True,
                    "bypass_method": "COMPLIO_DEV_MODE environment variable"
                }
            )

        # Return cached license info
        if self.cache is not None:
            return self.cache.license_info

        return None

    def _validate_online(self, license_key: str) -> LicenseInfo:
        """
        Validate license key with API (or use test keys).

        This method handles:
        1. Test license keys (hardcoded)
        2. Real API validation
        3. Offline fallback for localhost APIs

        Args:
            license_key: License key to validate

        Returns:
            LicenseInfo object

        Raises:
            InvalidLicenseError: If key is rejected
            LicenseAPIError: If API is unreachable (except localhost fallback)
        """
        # FIRST: Check if this is a test license key
        if license_key in TEST_LICENSE_KEYS:
            logger.info(
                "test_license_key_accepted",
                key=license_key,
                bypass_method="hardcoded test key"
            )
            return LicenseInfo(
                valid=True,
                tier="early_access",
                early_access=True,
                expires=None,  # Lifetime
                features=TIER_FEATURES["early_access"],
                email="test@dev.local",
                company="Test License",
                locked_price=0.0,
                founder_badge=True,
                activated_at=datetime.now(),
                metadata={
                    "test_license": True,
                    "bypass_method": "hardcoded test key"
                }
            )

        # THEN: Try API validation
        try:
            logger.info("validating_license_online", api_url=LICENSE_API_URL)

            response = requests.post(
                LICENSE_API_URL,
                json={"license_key": license_key},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"Complio/{self.settings.VERSION}"
                },
                timeout=10,
                verify=True  # Explicitly verify SSL certificates for security
            )

            if response.status_code == 200:
                data = response.json()

                # Check if license is valid (backend returns {"valid": true/false})
                if not data.get("valid", False):
                    error_msg = data.get("error", "License validation failed")
                    logger.warning("license_validation_rejected", error=error_msg)
                    raise InvalidLicenseError(f"License key rejected: {error_msg}")

                # License is valid - extract data
                tier_raw = data.get("tier", "free")
                # Convert backend tier format (EARLY_ACCESS) to internal format (early_access)
                tier = tier_raw.lower() if tier_raw else "free"

                logger.info("license_validation_success", tier=tier, status=data.get("status"))

                # Build LicenseInfo from backend response
                return LicenseInfo(
                    valid=True,
                    tier=tier,
                    early_access=(tier == "early_access"),
                    expires=None,  # Currently no expiration for subscriptions
                    features=TIER_FEATURES.get(tier, []),
                    email=data.get("email"),
                    company=None,  # Not provided by backend yet
                    locked_price=99.0 if tier == "early_access" else None,
                    founder_badge=(tier == "early_access"),  # All early access are founders
                    activated_at=datetime.now(),  # Use current time (could be tracked in backend)
                    metadata={
                        "status": data.get("status"),
                        "validated_via": "production_api"
                    }
                )

            else:
                logger.error(
                    "license_validation_error",
                    status=response.status_code,
                    response=response.text[:200]
                )
                raise LicenseAPIError(
                    f"License API returned status {response.status_code}",
                    status_code=response.status_code
                )

        except requests.exceptions.RequestException as e:
            # Check if this is localhost API (offline dev mode)
            if "localhost" in LICENSE_API_URL or "127.0.0.1" in LICENSE_API_URL:
                logger.warning(
                    "offline_dev_mode_granted",
                    api_url=LICENSE_API_URL,
                    reason="localhost API unreachable",
                    bypass_method="offline fallback"
                )
                # Grant offline dev access
                return LicenseInfo(
                    valid=True,
                    tier="early_access",
                    early_access=True,
                    expires=None,
                    features=TIER_FEATURES["early_access"],
                    email="offline@dev.local",
                    company="Offline Development",
                    locked_price=0.0,
                    founder_badge=True,
                    activated_at=datetime.now(),
                    metadata={
                        "offline_mode": True,
                        "bypass_method": "offline fallback for localhost API"
                    }
                )

            # Production API unreachable - raise error
            logger.error("license_api_unreachable", error=str(e), api_url=LICENSE_API_URL)
            raise LicenseAPIError(
                f"Could not reach license API: {str(e)}. "
                f"Check your internet connection or try again later."
            )

    def _validate_key_format(self, license_key: str) -> bool:
        """
        Validate license key format.

        Accepts both formats:
        - Production: COMPL-XXXX-XXXX-XXXX-XXXX (generated by backend)
        - Legacy/Dev: XXXX-XXXX-XXXX-XXXX (test keys, backward compatibility)

        Where X can be alphanumeric (uppercase A-Z, 0-9, or hex A-F, 0-9 for production)

        Args:
            license_key: Key to validate

        Returns:
            True if format is valid
        """
        # Production format with COMPL prefix (backend-generated licenses use hex: A-F, 0-9)
        production_pattern = r"^COMPL-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$"

        # Legacy format without prefix (test keys, backward compatibility - allows all alphanumeric)
        legacy_pattern = r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$"

        # Accept either format (case-insensitive)
        key_upper = license_key.upper()
        return bool(re.match(production_pattern, key_upper) or re.match(legacy_pattern, key_upper))

    def _mask_key(self, license_key: str) -> str:
        """Mask license key for logging (show only last segment)."""
        parts = license_key.split("-")
        if len(parts) >= 2:
            return "-".join(["****"] * (len(parts) - 1) + [parts[-1]])
        return "****"

    def _load_cache(self) -> None:
        """Load license cache from disk."""
        if not self.cache_path.exists():
            logger.debug("no_license_cache_file")
            self.cache = None
            return

        try:
            with open(self.cache_path, "r") as f:
                data = json.load(f)

            self.cache = LicenseCache(**data)
            logger.info(
                "license_cache_loaded",
                tier=self.cache.license_info.tier,
                cached_at=datetime.fromtimestamp(self.cache.cached_at).isoformat()
            )

        except Exception as e:
            logger.error("license_cache_load_failed", error=str(e))
            self.cache = None

    def _save_cache(self, license_key: str, license_info: LicenseInfo) -> None:
        """
        Save license cache to disk.

        Args:
            license_key: The license key
            license_info: Validated license information
        """
        self.cache = LicenseCache(
            license_key=license_key,
            license_info=license_info,
            cached_at=datetime.now().timestamp()
        )

        try:
            # Write to file with secure permissions
            with open(self.cache_path, "w") as f:
                json.dump(self.cache.model_dump(mode="json"), f, indent=2, default=str)

            # Set file permissions to owner-only (0600)
            os.chmod(self.cache_path, 0o600)

            logger.info(
                "license_cache_saved",
                path=str(self.cache_path),
                tier=license_info.tier
            )

        except Exception as e:
            logger.error("license_cache_save_failed", error=str(e))


__all__ = [
    "LicenseValidator",
    "TIER_FEATURES",
    "DEV_MODE",
    "TEST_LICENSE_KEYS",
]

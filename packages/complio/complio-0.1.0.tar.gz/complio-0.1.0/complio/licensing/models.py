"""
Licensing data models for Complio.

This module defines Pydantic models for license information and caching.
"""

import time
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LicenseInfo(BaseModel):
    """
    License information returned from validation.

    This model represents a validated license with all associated metadata.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        frozen=False,
    )

    valid: bool = Field(
        description="Whether the license key is valid and active"
    )
    tier: str = Field(
        description="License tier: free, early_access, pro, enterprise"
    )
    early_access: bool = Field(
        default=False,
        description="Whether this is an Early Access (founder) license"
    )
    expires: datetime | None = Field(
        default=None,
        description="Expiration date (None = lifetime license)"
    )
    features: list[str] = Field(
        default_factory=list,
        description="List of enabled features for this license"
    )
    email: str | None = Field(
        default=None,
        description="License holder email address"
    )
    company: str | None = Field(
        default=None,
        description="License holder company name"
    )
    locked_price: float | None = Field(
        default=None,
        description="Locked monthly price in EUR (for early access)"
    )
    founder_badge: bool = Field(
        default=False,
        description="Whether to display founder badge (first 50 customers)"
    )
    activated_at: datetime | None = Field(
        default=None,
        description="When the license was first activated"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (API version, etc.)"
    )

    def is_expired(self) -> bool:
        """Check if the license has expired."""
        if self.expires is None:
            return False  # Lifetime license
        return datetime.now() > self.expires

    def is_founder(self) -> bool:
        """Check if this is a founder license."""
        return self.early_access and self.founder_badge

    def get_savings(self) -> float:
        """Calculate annual savings for early access licenses."""
        if not self.early_access or self.locked_price is None:
            return 0.0

        regular_price = 299.0  # Regular price per month
        annual_savings = (regular_price - self.locked_price) * 12
        return annual_savings


class LicenseCache(BaseModel):
    """
    Cached license information stored locally.

    This model represents the local cache of license validation results,
    reducing API calls and enabling offline usage.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        frozen=False,
    )

    license_key: str = Field(
        description="The license key (last 4 chars visible for security)"
    )
    license_info: LicenseInfo = Field(
        description="Cached license validation result"
    )
    cached_at: float = Field(
        default_factory=time.time,
        description="Unix timestamp when cache was created"
    )
    cache_version: int = Field(
        default=1,
        description="Cache format version for future compatibility"
    )

    def is_stale(self, max_age_days: int = 7) -> bool:
        """
        Check if the cache is stale and needs refresh.

        Args:
            max_age_days: Maximum age in days before cache is considered stale

        Returns:
            True if cache is older than max_age_days
        """
        age_seconds = time.time() - self.cached_at
        age_days = age_seconds / 86400  # 86400 seconds in a day
        return age_days > max_age_days

    def get_masked_key(self) -> str:
        """
        Get a masked version of the license key for display.

        Returns:
            License key with only last 4 characters visible
            Example: "TEST-TEST-TEST-TEST" -> "****-****-****-TEST"
        """
        if len(self.license_key) < 4:
            return "****"

        # Split by hyphens and mask all but last segment
        parts = self.license_key.split("-")
        if len(parts) >= 2:
            masked_parts = ["****"] * (len(parts) - 1) + [parts[-1]]
            return "-".join(masked_parts)
        else:
            # No hyphens - just mask all but last 4 chars
            return "****" + self.license_key[-4:]


__all__ = [
    "LicenseInfo",
    "LicenseCache",
]

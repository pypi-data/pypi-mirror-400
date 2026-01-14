"""
Licensing exceptions for Complio.

This module defines custom exceptions for licensing-related errors,
providing clear user-facing messages for license validation failures.
"""


class LicenseError(Exception):
    """Base exception for all licensing-related errors."""

    pass


class InvalidLicenseError(LicenseError):
    """Raised when a license key is invalid or unrecognized."""

    def __init__(self, message: str = "Invalid license key") -> None:
        self.message = message
        super().__init__(self.message)


class LicenseExpiredError(LicenseError):
    """Raised when a license has expired."""

    def __init__(self, expired_at: str) -> None:
        self.expired_at = expired_at
        self.message = f"License expired on {expired_at}"
        super().__init__(self.message)


class FeatureNotAvailableError(LicenseError):
    """
    Raised when a feature is not available in the current license tier.

    This exception provides upgrade messaging to encourage users to
    purchase the Early Access tier.
    """

    def __init__(
        self,
        feature: str,
        current_tier: str = "free",
        required_tier: str = "early_access",
    ) -> None:
        self.feature = feature
        self.current_tier = current_tier
        self.required_tier = required_tier

        # Special messaging for scanning feature (most common)
        if feature == "scanning":
            self.message = self._generate_scanning_blocked_message()
        else:
            self.message = (
                f"Feature '{feature}' requires {required_tier.upper()} tier.\n"
                f"Current tier: {current_tier.upper()}\n\n"
                f"🚀 Upgrade to Early Access for €99/month (limited to 50 founders)\n"
                f"   Regular price will be €299/month - lock in founder pricing forever!\n\n"
                f"   Run: complio activate --license-key YOUR-KEY"
            )

        super().__init__(self.message)

    def _generate_scanning_blocked_message(self) -> str:
        """Generate user-friendly upgrade message for scanning feature."""
        return """
╔════════════════════════════════════════════════════════════════════╗
║                    🔒 COMPLIANCE SCANNING LOCKED                   ║
╚════════════════════════════════════════════════════════════════════╝

The compliance scanning feature requires an Early Access license.

🎯 EARLY ACCESS OFFER - LIMITED TO 50 FOUNDERS

   Price: €99/month (normally €299/month)
   Savings: €2,400/year locked in FOREVER
   Status: Lifetime price guarantee 🔒

✨ WHAT YOU GET TODAY:
   ✅ All 4 ISO 27001 compliance tests (S3, EC2, IAM, CloudTrail)
   ✅ Parallel test execution (4x faster)
   ✅ JSON & Markdown reports
   ✅ Cryptographically signed evidence
   ✅ Rich CLI with progress bars
   ✅ Multi-profile & multi-region support

🚀 COMING IN NEXT 6 WEEKS:
   ✅ 10+ additional compliance tests
   ✅ PDF report generation with charts
   ✅ Email notifications & scheduling
   ✅ SOC 2 compliance framework
   ✅ Historical trend analysis
   ✅ CI/CD integration

🏆 FOUNDER BENEFITS:
   • Price locked at €99/month forever
   • Founder badge on profile
   • Priority feature requests
   • Direct Slack channel access
   • Lifetime updates included

📧 GET YOUR LICENSE KEY:
   Visit: https://compl.io/early-access
   Email: founders@compl.io

💡 Already have a key?
   Run: complio activate --license-key YOUR-KEY

────────────────────────────────────────────────────────────────────
"""


class LicenseAPIError(LicenseError):
    """
    Raised when the license validation API is unreachable or returns an error.

    This can indicate network issues, API downtime, or configuration problems.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code

        if status_code:
            full_message = f"License API error (HTTP {status_code}): {message}"
        else:
            full_message = f"License API error: {message}"

        super().__init__(full_message)


__all__ = [
    "LicenseError",
    "InvalidLicenseError",
    "LicenseExpiredError",
    "FeatureNotAvailableError",
    "LicenseAPIError",
]

# Changelog

All notable changes to Complio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-29

### 🎉 Initial Alpha Release

First public release of Complio - Compliance-as-Code Platform for AWS infrastructure.

### Added

#### Core Features
- **Secure Credential Management**
  - AES-256 encrypted credential storage at `~/.complio/credentials.enc`
  - PBKDF2 key derivation with 480,000 iterations (OWASP recommended)
  - Secure file permissions (chmod 600) automatically applied
  - Zero credential logging - credentials filtered from all logs

- **Interactive CLI**
  - Rich terminal output with colors and formatting
  - ASCII art banner and branding
  - Commands: `configure`, `list-profiles`, `remove-profile`, `scan`, `activate`, `license`, `deactivate`
  - Progress bars for long-running operations

- **AWS Connector**
  - boto3 integration for AWS API calls
  - Connection pooling and credential validation
  - Multi-region support
  - Multi-profile support for managing multiple AWS accounts

#### Compliance Testing Framework

- **ISO 27001 Annex A Compliance Tests (4 total)**:
  1. **S3 Bucket Encryption** (A.8.2.3) - Validates encryption configuration
  2. **EC2 Security Groups** (A.13.1.1) - Detects overly permissive network rules
  3. **IAM Password Policy** (A.9.4.3) - Validates password requirements
  4. **CloudTrail Logging** (A.12.4.1) - Verifies audit logging configuration

- **Test Execution Engine**
  - Parallel test execution with ThreadPoolExecutor
  - Sequential execution mode for debugging
  - Progress callbacks for real-time UI updates
  - Comprehensive error handling

- **Evidence Collection**
  - SHA-256 cryptographic signatures for tamper detection
  - Timestamped evidence with AWS account ID
  - Structured evidence format (JSON-serializable)

#### Reporting

- **Report Formats**:
  - JSON reports - Machine-readable with full metadata
  - Markdown reports - Human-readable with emoji indicators

- **Report Features**:
  - Executive summary with compliance score
  - Detailed findings by severity (CRITICAL, HIGH, MEDIUM, LOW)
  - Remediation steps for each finding
  - Evidence chain with signatures
  - Export to file or display in terminal

#### Licensing System

- **Early Access Licensing**
  - License activation with cryptographic key validation
  - Offline caching with 7-day grace period
  - Feature gating per tier (free, early_access, pro, enterprise)
  - Founder badge for first 50 customers

- **DEV MODE for Development**:
  - Environment variable bypass: `COMPLIO_DEV_MODE=true`
  - Test license keys: `TEST-TEST-TEST-TEST`, `DEV0-DEV0-DEV0-DEV0`, `DEMO-DEMO-DEMO-DEMO`
  - Offline fallback for localhost API URLs

- **License Commands**:
  - `complio activate` - Activate license key with celebration messaging
  - `complio license` - Display current license status with upgrade pitch
  - `complio deactivate` - Remove local license cache

### Security

- **Security Audit Completed**
  - 131 unit and security tests passing
  - All P0 (Critical) vulnerabilities fixed
  - All P1 (High) vulnerabilities fixed
  - Comprehensive input validation
  - SQL injection prevention (parameterized queries)
  - XSS prevention (proper output encoding)
  - CSRF protection (stateless API design)
  - Authentication/authorization checks

- **Security Best Practices**
  - Credential encryption at rest (AES-256)
  - Secure random number generation
  - Rate limiting considerations
  - Dependency vulnerability scanning
  - Type safety with mypy strict mode

### Developer Experience

- **Code Quality**
  - Black formatting (line length 100)
  - Ruff linting (pycodestyle, pyflakes, isort)
  - mypy strict type checking
  - 100% type annotation coverage

- **Testing**
  - pytest with 131 tests passing
  - Unit tests for all modules
  - Integration tests for AWS operations (using moto)
  - Security audit tests
  - Coverage reporting (HTML, XML, terminal)

- **Documentation**
  - Comprehensive README with Quick Start
  - QUICKSTART.md for 5-minute setup
  - TESTING_GUIDE.md for comprehensive testing docs
  - Inline code documentation with docstrings
  - Type hints for all functions

### Technical Details

- **Dependencies**:
  - Python 3.11+ (required)
  - click 8.1.7+ (CLI framework)
  - rich 13.7.0+ (terminal output)
  - boto3 1.34.0+ (AWS SDK)
  - pydantic 2.5.3+ (data validation)
  - cryptography 42.0.0+ (encryption)
  - structlog 24.1.0+ (structured logging)
  - requests 2.31.0+ (HTTP client for licensing API)

- **Package Distribution**:
  - Available on PyPI as `complio`
  - Installable via `pip install complio`
  - Poetry-managed dependencies
  - Entry point: `complio` CLI command

### Known Limitations

- **AWS Only**: Currently supports AWS infrastructure only (Azure and GCP planned)
- **Limited Test Coverage**: 4 compliance tests (40+ planned)
- **No PDF Reports**: PDF generation coming in Week 6
- **No Scheduled Scans**: Cron/scheduled scanning coming in Week 7
- **No Historical Trends**: Trend analysis coming in Week 9
- **No CI/CD Integration**: GitHub Actions/GitLab CI plugins coming in Week 10

### Upgrade Notes

This is the initial release, no upgrade path required.

### Breaking Changes

None (initial release).

### Deprecations

None (initial release).

### Contributors

- Complio Team <team@compl.io>

### Links

- **Homepage**: https://compl.io
- **Repository**: https://github.com/complio/complio
- **Documentation**: https://docs.compl.io
- **Issue Tracker**: https://github.com/complio/complio/issues
- **Early Access**: https://compl.io/early-access

---

## [Unreleased]

### Planned for v0.2.0 (Week 5)

- Expand to 10+ compliance tests
- Add VPC security group tests
- Add RDS encryption tests
- Add Lambda configuration tests
- Add KMS key rotation tests
- Add Secrets Manager tests

### Planned for v0.3.0 (Week 6)

- PDF report generation with charts
- Executive summary reports
- Compliance trend charts
- Custom branding support

### Planned for v0.4.0 (Week 7-10)

- Email notifications and scheduling
- SOC 2 compliance framework
- Historical trend analysis
- CI/CD integration (GitHub Actions, GitLab CI, Jenkins)
- Multi-cloud support (Azure, GCP)

---

[0.1.0]: https://github.com/complio/complio/releases/tag/v0.1.0
[Unreleased]: https://github.com/complio/complio/compare/v0.1.0...HEAD

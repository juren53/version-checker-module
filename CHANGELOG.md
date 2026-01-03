# Changelog

All notable changes to the GitHub Version Checker Module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Note**: All timestamps use Central Time USA (CST/CDT) per project conventions.

## [Unreleased]

## [v0.0.1] - 2026-01-01

### Added
- Initial release of GitHub Version Checker Module
- `GitHubVersionChecker` class with sync and async version checking
- `VersionCheckResult` data class for structured results
- Semantic version comparison with prerelease support (alpha, beta, rc)
- Support for multiple GitHub URL formats (owner/repo, full URLs)
- Robust error handling for network and API issues
- Background thread support for non-blocking UI operations
- Minimal dependencies (urllib only)
- Comprehensive test suite with version comparison tests
- Complete module documentation with usage examples
- README.md with API reference and integration examples

### Features
- Synchronous version checking via `get_latest_version()`
- Asynchronous version checking via `check_for_updates(callback)`
- Version comparison supporting semantic versioning rules
- Prerelease detection (alpha < beta < rc < release)
- Configurable timeout for network requests
- Flexible repository URL parsing

### Documentation
- Inline code documentation with docstrings
- README.md with installation and usage guide
- API reference documentation
- Integration examples for PyQt applications
- Version comparison rules and examples

---

**Initial Release**: Wed 01 Jan 2026 12:00:00 PM CST
**Repository**: https://github.com/juren53/version-checker-module
**Tag**: v0.0.1

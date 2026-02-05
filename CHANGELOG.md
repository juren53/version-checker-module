# Changelog

All notable changes to the GitHub Version Checker Module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Note**: All timestamps use Central Time USA (CST/CDT) per project conventions.

## [Unreleased]

## [v1.0.1] - 2026-02-04 2157 CST

### Fixed
- **Release Downloader**: `working_dir` used `os.getcwd()` which could resolve to the user's home directory instead of the installation directory, causing the backup to copy the entire home directory. Changed to `os.path.dirname(os.path.abspath(__file__))`.
- **Release Downloader**: Backup now gracefully handles ephemeral files (e.g., Chrome singleton lock files) that disappear mid-copy, instead of aborting with a `shutil.Error`.

---

## [v1.0.0] - 2026-01-30 1509 CST

### Major Release - Complete Version Checking and Update System

Extracted from MDviewer project as a standalone, reusable module. This is the first complete release with full update functionality for both git and non-git installations.

### Added
- **Git Updater Module** (`git_updater.py`)
  - Safe git repository updates using `git reset --hard`
  - Version detection from remote repository
  - 30-second timeout protection on all git operations
  - Repository status checking and validation
  - Comprehensive error handling for git operations

- **Release Downloader Module** (`release_downloader.py`)
  - Archive-based updates for non-git installations
  - Platform-specific archive handling (ZIP for Windows, tar.gz for Unix)
  - Automatic backup system with timestamped backups
  - Rollback capability on update failure
  - Keeps last 3 backups automatically
  - Archive integrity validation

- **Centralized Version Management** (`version.py`)
  - Semantic versioning support
  - Version utility functions (`get_version_string()`, `get_semver()`, `get_version_tuple()`)
  - Date and time tracking in CST/CDT

- **Comprehensive Documentation**
  - `AGENTS.md` - Warp AI guidance with architecture and conventions
  - `CONTENTS.md` - Complete file inventory and module structure
  - `INTEGRATION_GUIDE.md` - Quick-start guide with integration patterns
  - `PLAN_version-checker-implementation.md` - Original implementation plan
  - `PLAN_Non-Git-Update-Support.md` - Archive update design document
  - Enhanced `README.md` with complete API reference

- **Test Scripts**
  - `test_release_downloader.py` - Non-destructive release downloader tests
  - `test_update_dialog.py` - PyQt6 GUI dialog tests
  - Built-in test functions in all core modules

- **Project Conventions**
  - Central Time USA (CST/CDT) timezone requirement
  - Version numbering scheme (v0.0.X, v0.0.Xa/b/c)
  - Complete project rules documentation

### Enhanced
- **GitHub Version Checker** improvements:
  - Better URL normalization
  - Enhanced error messages
  - Improved version comparison algorithm

### Architecture
- **Three-strategy update system**:
  1. GitHub API version checking (works for all installation types)
  2. Git-based updates (for git repository installations)
  3. Archive-based updates (for downloaded release installations)

- **Result object pattern** across all modules for consistent error handling
- **No external dependencies** - uses only Python standard library
- **Cross-platform support** - Windows, macOS, and Linux
- **Thread-safe** asynchronous operations

### Features
- Dual update strategies based on installation type detection
- Automatic backup before updates with rollback capability
- Platform-specific archive format detection
- Timeout protection on all network and subprocess operations
- Semantic version comparison with prerelease support
- Complete integration examples for CLI and GUI applications

### Project Provenance
- Extracted from **MDviewer** project
- Based on original implementation from **HPM (HST-Metadata Photos)**
- Additional refinement from **SysMon** project

---

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

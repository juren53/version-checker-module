# GitHub Version Checker Module

A standalone module for checking GitHub repository releases and comparing versions.
Designed to be reusable across different PyQt5/PyQt6/PySide applications.

## Features

- **Async version checking** with callbacks for non-blocking UI operations
- **Semantic version comparison** with prerelease support (alpha, beta, rc)
- **Robust error handling** for network and API issues
- **Configurable repositories** - works with any GitHub repository
- **Minimal dependencies** - uses only Python's built-in `urllib` library
- **Flexible URL formats** - accepts various GitHub URL formats

## Installation

Simply copy `github_version_checker.py` into your project directory.

```bash
# Or clone the repository
git clone https://github.com/juren53/version-checker-module.git
```

## Requirements

- Python 3.6+
- No external dependencies (uses built-in `urllib` and `json`)

## Usage

### Basic Synchronous Check

```python
from github_version_checker import GitHubVersionChecker

# Initialize checker
checker = GitHubVersionChecker(
    repo_url="juren53/system-monitor",  # or full URL: https://github.com/juren53/system-monitor
    current_version="0.2.18",
    timeout=10
)

# Perform synchronous check
result = checker.get_latest_version()

if result.error_message:
    print(f"Error: {result.error_message}")
else:
    print(f"Current version: {result.current_version}")
    print(f"Latest version: {result.latest_version}")
    print(f"Has update: {result.has_update}")
    print(f"Download URL: {result.download_url}")
```

### Asynchronous Check with Callback

```python
from github_version_checker import GitHubVersionChecker

def handle_version_check(result):
    if result.error_message:
        print(f"Check failed: {result.error_message}")
    elif result.has_update:
        print(f"New version available: {result.latest_version}")
        print(f"Download: {result.download_url}")
    else:
        print("You're up to date!")

# Initialize and start async check
checker = GitHubVersionChecker("owner/repo", "1.0.0")
checker.check_for_updates(handle_version_check)
```

### Version Comparison

```python
from github_version_checker import GitHubVersionChecker

checker = GitHubVersionChecker("owner/repo", "1.0.0")

# Returns: -1 (less than), 0 (equal), or 1 (greater than)
result = checker.compare_versions("0.2.18", "0.2.19")  # Returns -1
result = checker.compare_versions("1.0.0", "1.0.0")    # Returns 0
result = checker.compare_versions("1.1.0", "1.0.0")    # Returns 1

# Handles prerelease versions
result = checker.compare_versions("1.0.0a", "1.0.0")   # Returns -1 (alpha < release)
result = checker.compare_versions("1.0.0b", "1.0.0a")  # Returns 1 (beta > alpha)
```

## API Reference

### `GitHubVersionChecker`

#### Constructor
```python
GitHubVersionChecker(repo_url: str, current_version: str, timeout: int = 10)
```

**Parameters:**
- `repo_url`: GitHub repository URL (formats: `owner/repo` or `https://github.com/owner/repo`)
- `current_version`: Current application version (e.g., `"0.2.18d"`)
- `timeout`: Network request timeout in seconds (default: 10)

#### Methods

##### `get_latest_version() -> VersionCheckResult`
Performs a synchronous (blocking) version check.

**Returns:** `VersionCheckResult` object containing:
- `has_update` (bool): True if a newer version is available
- `current_version` (str): The current version string
- `latest_version` (str): The latest version from GitHub
- `download_url` (str): URL to the release page
- `release_notes` (str): Release notes/body from GitHub
- `published_date` (str): Publication date of the release
- `error_message` (str): Error message if check failed
- `is_newer` (bool): True if latest > current

##### `check_for_updates(callback: Callable[[VersionCheckResult], None]) -> None`
Performs an asynchronous (non-blocking) version check in a background thread.

**Parameters:**
- `callback`: Function that receives a `VersionCheckResult` when complete

##### `compare_versions(version1: str, version2: str) -> int`
Compares two semantic version strings.

**Returns:**
- `-1` if version1 < version2
- `0` if version1 == version2
- `1` if version1 > version2

**Supports:**
- Standard semantic versioning (major.minor.patch)
- Prerelease suffixes (a=alpha, b=beta, rc=release candidate)
- Version strings with 'v' prefix (e.g., "v1.0.0")

## Version Comparison Rules

The module understands semantic versioning with prerelease support:

1. **Numeric comparison**: `0.2.18` < `0.2.19`
2. **Prerelease < Release**: `1.0.0a` < `1.0.0`
3. **Prerelease ranking**: alpha < beta < rc < release

Examples:
- `0.2.18d` = `0.2.18d` ✓
- `0.2.18` < `0.2.19` ✓
- `0.2.18a` < `0.2.18` ✓ (alpha is prerelease)
- `0.2.18b` > `0.2.18a` ✓ (beta > alpha)

## Error Handling

The module handles various error conditions gracefully:

- Network timeouts and connectivity issues
- Invalid JSON responses
- GitHub API rate limiting
- Invalid repository URLs
- Missing releases

All errors are captured in the `VersionCheckResult.error_message` field.

## Testing

Run the included test suite:

```bash
python github_version_checker.py
```

This will test:
- Synchronous version checking
- Version comparison logic
- Asynchronous callback functionality

## Integration Example

```python
# In your PyQt application
from PyQt5.QtCore import QTimer
from github_version_checker import GitHubVersionChecker

class MyApplication:
    def __init__(self):
        self.version_checker = GitHubVersionChecker(
            "myusername/myapp",
            "1.0.0"
        )

        # Check for updates on startup
        self.version_checker.check_for_updates(self.on_version_checked)

    def on_version_checked(self, result):
        if result.has_update:
            # Show update notification in UI
            self.show_update_notification(
                f"Version {result.latest_version} available!",
                result.download_url
            )
```

## License

MIT License - See repository for details

## Author

SysMon Project

## Version

v0.0.1 - Initial release (2026-01-01)

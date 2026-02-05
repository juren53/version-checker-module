# Version Checker Module

A comprehensive, reusable version checking and updating system for Python applications using GitHub releases.

## Overview

This module provides a complete solution for checking, downloading, and installing application updates from GitHub repositories. It supports both git-based installations and standalone release archives (ZIP/tarball).

## Features

- **GitHub Version Checking**: Check for latest releases via GitHub API
- **Semantic Version Comparison**: Intelligent version comparison (e.g., 0.3.0 vs 0.3.1)
- **Dual Update Strategies**:
  - Git-based updates using `git reset --hard`
  - Direct download updates from release archives
- **Cross-platform Support**: Works on Windows, macOS, and Linux
- **Safety Features**:
  - Automatic backup before updates
  - Rollback capability on failure
  - 30-second timeout protection
  - Comprehensive error handling
- **No External Dependencies**: Uses only Python standard library (urllib, subprocess, etc.)

## Components

### Core Modules

#### 1. `github_version_checker.py`
Standalone module for checking GitHub repository releases and comparing versions.

**Key Features**:
- Asynchronous version checking with callbacks
- Semantic version comparison
- Robust error handling
- Minimal dependencies (urllib only)

**Usage**:
```python
from github_version_checker import GitHubVersionChecker

checker = GitHubVersionChecker(
    repo_url="owner/repo",
    current_version="0.3.0",
    timeout=10
)

# Synchronous check
result = checker.get_latest_version()
if result.has_update:
    print(f"Update available: {result.latest_version}")

# Asynchronous check
def callback(result):
    if result.has_update:
        print(f"Update available: {result.latest_version}")

checker.check_for_updates(callback)
```

#### 2. `git_updater.py`
Handles safe git repository updates using force update strategy.

**Key Features**:
- Force update using `git reset --hard` to avoid conflicts
- 30-second timeout on git operations
- Comprehensive error handling
- Version comparison and validation
- Safe repository detection

**Usage**:
```python
from git_updater import GitUpdater

updater = GitUpdater(
    repo_url="https://github.com/owner/repo.git",
    version_file_path="version.py",
    branch="main",
    timeout=30
)

# Check for updates
has_update, current, latest = updater.get_update_info()

# Perform update
if has_update:
    result = updater.force_update()
    if result.success:
        print(f"Updated from {result.current_version} to {result.new_version}")
```

#### 3. `release_downloader.py`
Downloads and installs release archives from GitHub for non-git installations.

**Key Features**:
- Downloads release archives (ZIP/tarball) from GitHub
- Creates backups before update
- Validates archive integrity
- Provides rollback on failure
- Cross-platform support (Windows/Linux)
- 30-second timeout on operations

**Usage**:
```python
from release_downloader import ReleaseDownloader

downloader = ReleaseDownloader(
    repo_url="owner/repo",
    version_file_path="version.py",
    timeout=30
)

# Perform complete update
result = downloader.perform_update("0.3.1")
if result.success:
    print(f"Updated to {result.new_version}")
    print(f"Backup at: {result.backup_path}")
```

#### 4. `version.py`
Centralized version management template.

**Usage**:
```python
from version import __version__, get_version_string

print(__version__)  # "0.0.9"
print(get_version_string())  # "v0.0.9 2026-01-30 1840 CST"
```

### Test Scripts

#### `test_release_downloader.py`
Tests release downloader functionality without performing actual updates.

**Usage**:
```bash
python test_release_downloader.py
```

#### `test_update_dialog.py`
PyQt6-based GUI test for update dialogs (requires PyQt6 and application context).

**Usage**:
```bash
python test_update_dialog.py
```

## Installation

### As a Git Submodule
```bash
cd your-project
git submodule add https://github.com/yourusername/version-checker-module.git
```

### Direct Copy
Simply copy the required files into your project:
- `github_version_checker.py`
- `git_updater.py`
- `release_downloader.py`
- `version.py`

## Integration Example

```python
import os
from github_version_checker import GitHubVersionChecker
from git_updater import GitUpdater
from release_downloader import ReleaseDownloader

def check_for_updates():
    # Step 1: Check for updates via GitHub API
    checker = GitHubVersionChecker(
        repo_url="owner/repo",
        current_version="0.3.0"
    )
    
    result = checker.get_latest_version()
    
    if not result.has_update:
        print("Already up to date!")
        return
    
    print(f"Update available: {result.latest_version}")
    
    # Step 2: Determine installation type and update
    if os.path.exists(".git"):
        # Git-based installation
        updater = GitUpdater(
            repo_url="https://github.com/owner/repo.git",
            version_file_path="version.py"
        )
        update_result = updater.force_update()
    else:
        # Non-git installation
        downloader = ReleaseDownloader(
            repo_url="owner/repo",
            version_file_path="version.py"
        )
        update_result = downloader.perform_update(result.latest_version)
    
    # Step 3: Handle result
    if update_result.success:
        print(f"✓ Updated to {update_result.new_version}")
    else:
        print(f"✗ Update failed: {update_result.message}")
```

## Platform Considerations

### Windows
- Uses `.zip` format for release downloads
- Requires PowerShell for some operations
- Git must be in PATH for git-based updates

### Linux/macOS
- Uses `.tar.gz` format for release downloads
- Preserves file permissions during updates
- Git must be installed for git-based updates

## Safety Mechanisms

### Backup System
- Creates timestamped backups before updates
- Keeps last 3 backups automatically
- Automatic rollback on failure
- Backups stored in `.backups/` directory

### Error Handling
- Network timeout protection (30 seconds)
- Git operation timeout protection (30 seconds)
- Comprehensive error messages
- Graceful degradation for edge cases

### Validation
- Version format validation
- Archive integrity checks
- Repository detection
- File existence verification

## API Reference

### GitHubVersionChecker

**Methods**:
- `get_latest_version()` → `VersionCheckResult`: Synchronous version check
- `check_for_updates(callback)`: Asynchronous version check with callback
- `compare_versions(v1, v2)` → `int`: Compare two semantic versions

**Result Object**:
```python
class VersionCheckResult:
    has_update: bool
    current_version: str
    latest_version: str
    download_url: str
    release_notes: str
    published_date: str
    error_message: str
    is_newer: bool
```

### GitUpdater

**Methods**:
- `is_git_repository()` → `bool`: Check if in a git repository
- `get_current_version()` → `Optional[str]`: Read local version
- `get_remote_version()` → `Optional[str]`: Read remote version
- `get_update_info()` → `Tuple[bool, str, str]`: Check for updates
- `force_update()` → `GitUpdateResult`: Perform git-based update
- `get_repository_status()` → `Tuple[bool, str]`: Get repo status

**Result Object**:
```python
class GitUpdateResult:
    success: bool
    message: str
    current_version: str
    new_version: str
    command_output: str
    error_output: str
```

### ReleaseDownloader

**Methods**:
- `download_release(version)` → `Tuple[bool, str, str]`: Download release
- `extract_archive(archive_path)` → `Tuple[bool, str, str]`: Extract archive
- `backup_installation()` → `Tuple[bool, str, str]`: Create backup
- `apply_update(extracted_dir)` → `Tuple[bool, str]`: Apply update
- `rollback()` → `Tuple[bool, str]`: Restore from backup
- `perform_update(version)` → `ReleaseDownloadResult`: Complete update process
- `cleanup()`: Remove temporary files

**Result Object**:
```python
class ReleaseDownloadResult:
    success: bool
    message: str
    current_version: str
    new_version: str
    download_url: str
    error_message: str
    backup_path: str
```

## Requirements

- Python 3.6+
- Git (for git-based updates)
- Internet connection (for version checking and downloads)

## Testing

Run the test scripts to verify functionality:

```bash
# Test release downloader
python test_release_downloader.py

# Test update dialogs (requires PyQt6)
python test_update_dialog.py
```

## Documentation

See the planning documents for detailed implementation guidance:
- `PLAN_version-checker-implementation.md`: Original implementation plan
- `PLAN_Non-Git-Update-Support.md`: Non-git update implementation details

## Project History

This module was developed for the MDviewer project and extracted for reusability. It combines lessons learned from multiple projects:

- **HPM (HST-Metadata Photos)**: Original implementation
- **MDviewer**: PyQt6 adaptation and enhancement
- **SysMon**: Additional testing and refinement

## Version History

- **v1.0.0** (2026-01-31): Initial modular release
  - Extracted from MDviewer project
  - Standalone module design
  - Complete test coverage
  - Cross-platform support

## License

This module is released for reuse across projects. Adapt as needed for your specific use case.

## Contributing

This is a personal utility module. Feel free to adapt for your own projects.

## Notes

- The module is designed to be self-contained with no external dependencies beyond Python standard library
- All network operations have timeout protection (30 seconds default)
- The module follows a consistent result object pattern for all operations
- Error handling is comprehensive with detailed error messages
- Thread-safe when used with callbacks and background operations

## Future Enhancements

Potential additions (not currently implemented):
- Auto-check on startup
- Update scheduling
- Beta channel support
- Update history tracking
- Configurable timeout values
- Progress callbacks for downloads

# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a reusable Python module for checking, downloading, and installing application updates from GitHub releases. It supports both git-based installations (using `git reset --hard`) and standalone release archives (ZIP/tarball). The module is designed to be self-contained with no external dependencies beyond Python's standard library.

**Key Design Philosophy**: This is a portable utility module meant to be copied into other projects, not imported as a package. All modules are standalone and can function independently.

## Core Architecture

### Three-Strategy Update System

The module uses a **dual-path strategy** based on installation type:

1. **GitHub API Version Checking** (`github_version_checker.py`)
   - Works for ALL installation types
   - Uses GitHub's releases API to fetch latest version
   - Performs semantic version comparison with prerelease support (alpha/beta/rc)
   - Thread-safe asynchronous checking via background threads

2. **Git-Based Updates** (`git_updater.py`)
   - For git repository installations
   - Uses `git reset --hard origin/{branch}` to force update (avoids merge conflicts)
   - Reads version from remote via `git show origin/{branch}:version.py`
   - 30-second timeout protection on all git operations

3. **Archive-Based Updates** (`release_downloader.py`)
   - For non-git installations (downloaded releases)
   - Downloads source archives (`.zip` on Windows, `.tar.gz` on Unix)
   - Creates timestamped backups before update (keeps last 3)
   - Automatic rollback on failure
   - Platform detection for correct archive format

### Result Object Pattern

All three modules return structured result objects (not exceptions) with consistent fields:
- `success: bool` - Operation success status
- `message: str` - Human-readable message
- `error_message: str` - Detailed error information
- Version information fields specific to each operation

This allows calling code to handle all outcomes uniformly without exception handling.

### Version File Convention

The module expects a `version.py` file at the repository root with this structure:
```python
__version__ = "1.0.0"  # Semantic version (MAJOR.MINOR.PATCH)
__version_date__ = "2026-01-30 1509"  # Date and TIME in CST/CDT (4-digit 24hr format)
__version_info__ = (1, 0, 0)  # Tuple for programmatic comparison
```

**CRITICAL**: Version dates MUST include both date AND time in Central Time USA format (e.g., `"2026-01-30 1509"`), never UTC.

## Testing

### Run Tests
```bash
# Test release downloader (non-destructive)
python test_release_downloader.py

# Test GUI dialogs (requires PyQt6 - may not run standalone)
python test_update_dialog.py
```

### Test Individual Modules
```bash
# Test GitHub version checker
python github_version_checker.py

# Test git updater (safe - checks status only)
python git_updater.py

# Test release downloader (safe - checks status only)
python release_downloader.py
```

Each core module has a `if __name__ == "__main__":` test function that demonstrates functionality without performing actual updates.

## Critical Implementation Details

### Semantic Version Comparison
The version comparison algorithm (`compare_versions()`) handles:
- Standard semantic versioning: `1.2.3` → `(1, 2, 3)`
- Prerelease suffixes: `1.0.0a` < `1.0.0b` < `1.0.0rc` < `1.0.0`
- Version prefix handling: `v1.0.0` → `1.0.0`
- Padding: `1.2` → `(1, 2, 0)`

Returns: `-1` (less than), `0` (equal), `1` (greater than)

### Timeout Protection
All network and subprocess operations have 30-second timeouts:
- GitHub API calls: `urlopen(url, timeout=timeout)`
- Git operations: `subprocess.run(..., timeout=self.timeout)`
- Archive downloads: Same pattern as GitHub API

### Thread Safety
`GitHubVersionChecker.check_for_updates()` spawns daemon threads for async checks. Callbacks execute in background thread context - ensure calling code handles thread safety (e.g., Qt signal/slot for GUI updates).

### Platform-Specific Behavior
- **Windows**: Uses `.zip` archives, requires PowerShell for some operations
- **Linux/macOS**: Uses `.tar.gz` archives, preserves file permissions during extraction
- Platform detection: `sys.platform.startswith("win")` for Windows

### Backup System
`release_downloader.py` creates backups in `.backups/backup_{version}_{timestamp}/`:
- Excludes: `.backups/`, `.git/`, `__pycache__/`, `.pytest_cache/`
- Automatic cleanup: Keeps only 3 most recent backups
- Rollback: Restores from backup on update failure

## Common Development Tasks

### Adapting for a New Project

1. Copy required files into target project:
   ```bash
   cp version.py github_version_checker.py git_updater.py release_downloader.py <target-project>/
   ```

2. Update `version.py` with project's version

3. Integrate based on installation type detection:
   ```python
   if os.path.exists(".git"):
       updater = GitUpdater(repo_url, "version.py")
   else:
       updater = ReleaseDownloader(repo_url, "version.py")
   ```

### Modifying Update Behavior

- **Change timeout**: Pass `timeout` parameter to class constructors (default: 10s for checks, 30s for updates)
- **Change branch**: Pass `branch` parameter to `GitUpdater` (default: "main")
- **Exclude files from archive updates**: Modify `exclude_items` set in `release_downloader.py:apply_update()`
- **Change backup retention**: Modify `keep` parameter in `_cleanup_old_backups()` (default: 3)

### Understanding Update URLs

**Git updater**: Uses git protocol directly
- `repo_url` format: `https://github.com/owner/repo.git`

**GitHub version checker**: Uses GitHub API
- API endpoint: `https://api.github.com/repos/owner/repo/releases/latest`
- `repo_url` format: `owner/repo` (normalized internally)

**Release downloader**: Uses GitHub archive download URLs
- Archive URL: `https://github.com/owner/repo/archive/refs/tags/v{version}.{zip|tar.gz}`
- `repo_url` format: `owner/repo` (normalized internally)

### Version File Parsing

All three modules parse version.py identically:
```python
match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
version = match.group(1) if match else None
```

This regex matches both single and double quotes, handles whitespace variations, and extracts the version string.

## Project Rules and Conventions

### Timezone Convention

**CRITICAL**: ALL timestamps, dates, and times in this project MUST use **Central Time USA (CST/CDT)**, NEVER UTC or any other timezone.

This applies to:
- **Changelog entries** in source code headers
- **Version dates** in `version.py`: `__version_date__ = "2026-01-30 1509"` (4-digit 24hr time)
- **Version labels** and dates in UI elements
- **Git commit messages** (if applicable)
- **Documentation timestamps**
- **Any other date/time references** in the project

Example formats:
- Changelog: `Tue 03 Dec 2025 09:20:00 PM CST`
- Version label: `v0.0.9b 2025-12-03`
- Version date in version.py: `"2026-01-30 1509"` (YYYY-MM-DD HHMM format)
- Always include timezone indicator (CST or CDT) in full timestamps where appropriate

### Version Numbering

This project follows a specific version numbering scheme:
- **Standard releases**: `v0.0.X` format (e.g., `v1.0.0`)
- **Point releases/patches**: `v0.0.Xa`, `v0.0.Xb`, `v0.0.Xc` format (e.g., `v1.0.0a`, `v1.0.0b`)

**When making releases, update version info in:**
- `version.py` file (__version__, __version_date__ with date AND time, __version_info__)
- `README.md` file (Version History section)
- Source code header comments (if applicable)
- Any UI labels or About dialogs (in consuming projects)

**Version info MUST consist of**: Version Number + Date + TIME in CST/CDT  
Example: `v0.2.6  2025-12-22 1125 CST`

## Integration Examples

See `INTEGRATION_GUIDE.md` for complete integration patterns covering:
- CLI applications with argparse
- PyQt6 GUI applications with menu integration
- Background update checking with threading

See README.md for API reference and detailed usage examples.

## Documentation

- **README.md**: Comprehensive API reference and usage examples
- **INTEGRATION_GUIDE.md**: Quick-start guide with integration patterns
- **CONTENTS.md**: File inventory and module structure
- **PLAN_version-checker-implementation.md**: Original design document
- **PLAN_Non-Git-Update-Support.md**: Archive update design rationale

## Project Provenance

Extracted from **MDviewer** project (2026-01-31) which was based on:
- **HPM (HST-Metadata Photos)**: Original implementation
- **SysMon**: Additional refinement

Module version: **1.0.0**

# Non-Git Update Support Implementation

## Problem Statement
The current "Get Latest Version" feature requires a git repository to perform updates. Users who download release archives (ZIP/tarball) from GitHub cannot use the automatic update feature, even though they can check for new versions via the GitHub API.

## Current State
The update system has two components:
1. **github_version_checker.py**: Checks GitHub releases API for new versions (works for all installations)
2. **git_updater.py**: Performs updates via git commands (requires git repository)
3. **viewer/main_window.py**: Lines 1293-1304 show early return with error dialog when not a git repository

The version check works universally, but the update mechanism is git-only.

## Proposed Solution
Add a direct download updater that works alongside the existing git updater, allowing both installation types to update automatically.

### New Module: release_downloader.py
Create a standalone module similar in design to github_version_checker.py and git_updater.py that:
* Downloads release archives (tarball/ZIP) from GitHub releases
* Extracts to temporary directory with safety checks
* Creates backup of current installation
* Replaces application files with new version
* Provides rollback capability on failure
* Returns structured result via ReleaseDownloadResult dataclass
* Uses urllib only (no external dependencies beyond standard library)
* 30-second timeout on download operations

**Key Methods**:
* `download_release(version)`: Downloads specific release archive from GitHub
* `extract_archive(archive_path, target_dir)`: Extracts tarball/ZIP safely
* `backup_installation()`: Creates backup of current files
* `apply_update(extracted_dir)`: Replaces files with new version
* `rollback()`: Restores from backup if update fails
* `cleanup()`: Removes temporary files and old backups

**Platform Considerations**:
* Linux: Use .tar.gz format (tarball)
* Windows: Use .zip format
* Detect platform automatically
* Handle GitHub's source archive naming convention (e.g., v0.3.0.tar.gz)

### Modified Update Flow in viewer/main_window.py
Modify `_on_get_latest_updates()` method (lines 1282-1391):

**Current flow**:
```
1. Show progress dialog
2. Check if git repository → If NO, show error and return
3. Perform version check
4. If update available → Perform git update
```

**New flow**:
```
1. Show progress dialog
2. Detect installation type (git vs non-git)
3. Perform version check via GitHub API
4. If update available:
   a. If git repository → Use GitUpdater (existing)
   b. If non-git → Use ReleaseDownloader (new)
5. Show appropriate result dialog
```

**Specific Changes**:
* Remove early return at lines 1293-1304
* Add installation type detection
* Add conditional branching for update method
* Update progress dialog messages based on method
* Handle download progress updates for non-git installs

### Update Dialogs Enhancement
Modify viewer/update_dialogs.py to support both update methods:
* UpdateProgressDialog: Add download progress bar for non-git updates
* VersionCompareDialog: Clarify update method ("via git" vs "via download")
* UpdateResultDialog: Show method-specific success messages

### Safety Features
1. **Backup Management**:
    * Create timestamped backup before update
    * Keep last 3 backups maximum
    * Automatic rollback on failure

2. **File Validation**:
    * Verify download integrity (check file size > 0)
    * Validate archive structure before extraction
    * Ensure version.py exists in extracted files

3. **Error Handling**:
    * Network timeout handling
    * Disk space verification
    * Permission checks
    * Graceful degradation with informative error messages

4. **Thread Safety**:
    * Downloads run in background thread
    * Progress updates via Qt signals
    * Main thread handles all GUI operations

### Files to be Modified
1. Create: `release_downloader.py` (new standalone module)
2. Modify: `viewer/main_window.py` (_on_get_latest_updates method)
3. Modify: `viewer/update_dialogs.py` (add progress bar support)
4. Update: `AGENTS.md` (document new update mechanism)

### Testing Requirements
1. Test git-based updates (existing functionality)
2. Test non-git updates with downloaded release
3. Test backup and rollback mechanisms
4. Test network failure scenarios
5. Test disk space limitations
6. Test permission issues
7. Verify both Linux (.tar.gz) and Windows (.zip) work correctly

### Implementation Notes
* Use tarfile module for .tar.gz extraction
* Use zipfile module for .zip extraction
* Use shutil for file operations (copy, move, rmtree)
* Use tempfile for temporary directory creation
* Follow existing patterns from github_version_checker.py and git_updater.py
* Maintain standalone module design for reusability
* Keep consistent error handling and timeout patterns (30 seconds)
* Preserve file permissions during update (especially on Linux)
* Handle __pycache__ and .pyc files appropriately (exclude from updates)

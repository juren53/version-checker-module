# Version Checker Module - Contents

This directory contains a reusable version checking and updating system extracted from the MDviewer project.

## Files Copied from MDviewer (2026-01-31)

### Core Modules
1. **version.py**
   - Centralized version management
   - Semantic versioning support
   - Version utility functions
   - Source: `C:\Users\jimur\Projects\MDviewer\version.py`

2. **github_version_checker.py**
   - GitHub release version checking
   - Semantic version comparison
   - Asynchronous checking with callbacks
   - Source: `C:\Users\jimur\Projects\MDviewer\github_version_checker.py`

3. **git_updater.py**
   - Git repository update functionality
   - Force update using `git reset --hard`
   - Version comparison and validation
   - Source: `C:\Users\jimur\Projects\MDviewer\git_updater.py`

4. **release_downloader.py**
   - Release archive download and installation
   - Backup and rollback support
   - Cross-platform archive handling (ZIP/tarball)
   - Source: `C:\Users\jimur\Projects\MDviewer\release_downloader.py`

### Test Scripts
5. **test_release_downloader.py**
   - Non-destructive tests for release downloader
   - URL parsing and version reading tests
   - Source: `C:\Users\jimur\Projects\MDviewer\test_release_downloader.py`

6. **test_update_dialog.py**
   - PyQt6-based GUI test for update dialogs
   - Tests all dialog states without performing updates
   - Requires PyQt6 and application context
   - Source: `C:\Users\jimur\Projects\MDviewer\test_update_dialog.py`

### Documentation
7. **PLAN_version-checker-implementation.md**
   - Original implementation plan for version checker
   - Architecture and design decisions
   - Implementation steps and testing strategy
   - Source: `C:\Users\jimur\Projects\MDviewer\PLAN_MDv-version-checker-implementation.md`

8. **PLAN_Non-Git-Update-Support.md**
   - Implementation plan for non-git updates
   - Release downloader design and safety features
   - Integration details and testing requirements
   - Source: `C:\Users\jimur\Projects\MDviewer\notes\PLAN_Non-Git-Update-Support-Implementation.md`

9. **README.md**
   - Comprehensive module documentation
   - Usage examples and API reference
   - Integration guide and safety mechanisms
   - Created: 2026-01-31

## Pre-existing Files (Not from MDviewer)
These files were already in the version-checker-module directory:
- `.gitattributes`
- `CHANGELOG.md`
- `DOC_GitHub_Verion_Checker.md`
- `Project_Rules.md`
- `Recommendations for version-checker-module project.md`

## Module Structure

```
version-checker-module/
├── Core Modules
│   ├── version.py                              # Version management
│   ├── github_version_checker.py               # GitHub API version checking
│   ├── git_updater.py                          # Git-based updates
│   └── release_downloader.py                   # Archive-based updates
├── Test Scripts
│   ├── test_release_downloader.py              # Release downloader tests
│   └── test_update_dialog.py                   # GUI dialog tests
├── Documentation
│   ├── README.md                               # Main documentation
│   ├── PLAN_version-checker-implementation.md  # Implementation plan
│   ├── PLAN_Non-Git-Update-Support.md          # Non-git update plan
│   ├── CHANGELOG.md                            # Version history
│   ├── DOC_GitHub_Verion_Checker.md            # GitHub checker docs
│   └── CONTENTS.md                             # This file
└── Configuration
    ├── .gitattributes                          # Git attributes
    └── Project_Rules.md                        # Project guidelines
```

## Key Features

### Dual Update Strategy
- **Git-based**: For development installations (uses `git reset --hard`)
- **Archive-based**: For release installations (downloads ZIP/tarball)

### Cross-Platform Support
- Windows (ZIP archives)
- Linux (tar.gz archives)
- macOS (tar.gz archives)

### Safety Features
- Automatic backup before updates
- Rollback capability on failure
- 30-second timeout protection
- Comprehensive error handling

### No External Dependencies
- Uses only Python standard library
- urllib for network operations
- subprocess for git operations
- tarfile/zipfile for archive handling

## Usage Pattern

The typical integration pattern:
1. Copy required modules into your project
2. Create a `version.py` for your application
3. Use `GitHubVersionChecker` to check for updates
4. Use `GitUpdater` or `ReleaseDownloader` based on installation type
5. Handle results and display to user

## Version Information

- **Module Version**: 1.0.0
- **Extract Date**: 2026-01-31
- **Source Project**: MDviewer
- **Author**: Jim Murdock

## Notes

- All files maintain their original functionality
- Test scripts may need adaptation for different PyQt versions
- Planning documents provide implementation context
- Module is designed for easy integration into any Python project

## Future Maintenance

When updating this module:
1. Test all three core update modules independently
2. Verify cross-platform compatibility
3. Update version history in CHANGELOG.md
4. Test with both git and non-git installations
5. Verify backup and rollback mechanisms

## Related Projects

This module has been used in:
- **HPM (HST-Metadata Photos)**: Original implementation
- **MDviewer**: Enhanced with non-git support
- **SysMon**: Additional refinement

The module is designed to be reusable across any Python project that uses GitHub for releases.

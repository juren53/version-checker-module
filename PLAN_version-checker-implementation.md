# PLAN: MDviewer Version Checker Implementation

## Overview

This plan documents the implementation of a "Get Latest Version" feature for MDviewer, based on the successful implementation in HPM (HST-Metadata Photos). The feature allows users to manually update their application to the latest version from GitHub with a single menu click.

## Configuration Decisions

- **Version Format**: Semantic versioning (e.g., 0.3.0)
- **Update Checking**: Manual via Help menu only
- **Beta/Prerelease Support**: Not implemented initially (can be added later)
- **Repository**: https://github.com/juren53/MDviewer.git
- **Branch**: main (current default)

## Architecture Components

### 1. Core Modules

#### Version File (`version.py`)
- **Purpose**: Centralized version management
- **Format**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Location**: Root directory of MDviewer project
- **Initial Version**: 0.3.0 (converting from v0.0.3)

#### GitHub Version Checker (`github_version_checker.py`)
- **Purpose**: Standalone module for checking GitHub releases
- **Status**: ✅ Reusable from HPM implementation
- **Location**: [version-checker-module](https://github.com/juren53/version-checker-module)
- **Key Features**:
  - Semantic version comparison
  - Asynchronous checking with callbacks
  - Robust error handling
  - No external dependencies

#### Git Updater (`git_updater.py`) - To Be Created
- **Purpose**: Handle git repository updates safely
- **Key Methods**:
  - `get_update_info()` - Comprehensive version comparison
  - `force_update()` - Clean update using `git reset --hard`
  - `get_remote_version()` - Reads version from remote file
  - `_compare_versions()` - Semantic version comparison

### 2. UI Components

#### Menu Integration
- Add menu item: **Help → "Get Latest Version"**
- Keyboard shortcut: **Ctrl+U**
- Handler method: `_on_get_latest_updates()`

#### Dialog Components
- **Version Comparison Dialog**: Current vs New version with release notes
- **Progress Dialog**: Shows download/update progress
- **Result Dialogs**: Success, failure, and up-to-date scenarios

## Implementation Steps

### Phase 1: Foundation Setup (High Priority)

#### 1. Create Version File
```python
# version.py
__version__ = "0.3.0"
__version_date__ = "2026-01-25"
__version_info__ = (0, 3, 0)
```

#### 2. Copy GitHub Version Checker
```bash
# Download from HPM repository
wget https://raw.githubusercontent.com/juren53/version-checker-module/main/github_version_checker.py
```

#### 3. Create Git Updater Module
- Adapted from HPM implementation
- PyQt6 compatibility
- 30-second timeout protection
- Comprehensive error handling

### Phase 2: UI Integration (Medium Priority)

#### 4. Add Menu Item
```python
# In setup_menu() method of MainWindow
get_latest_action = QAction("Get Latest Version", self)
get_latest_action.setShortcut("Ctrl+U")
get_latest_action.setStatusTip("Check for and install latest version")
get_latest_action.triggered.connect(self._on_get_latest_updates)
help_menu.addAction(get_latest_action)
```

#### 5. Implement Handler Method
```python
def _on_get_latest_updates(self):
    # Repository validation
    # Version information fetch
    # Comparison dialog display
    # User confirmation handling
    # Update execution with progress
    # Result reporting
```

#### 6. Create Dialog Components
- **VersionCompareDialog**: Shows current vs latest with release notes
- **ProgressDialog**: Real-time progress during git operations
- **UpdateResultDialog**: Success/failure with version info

### Phase 3: Integration & Testing (Low Priority)

#### 7. Update Version References
- Replace hardcoded version in `main.py` (line 13)
- Update `AboutDialog` version string (line 51)
- Update status bar version label (line 827)

#### 8. Create Test Script
```python
# test_update_dialog.py
# Preview all dialog states without performing actual updates
python test_update_dialog.py
```

## Data Flow

```
User Clicks Menu → Git Repo Check → Version Fetch → Version Compare → User Confirmation → Git Update → Result Display
```

### Detailed Flow:

1. **Repository Validation**: Verify current directory is a git repository
2. **Remote Fetch**: `git fetch origin` to get latest state
3. **Version Detection**: 
   - Local version from `version.py`
   - Remote version from `origin/main:version.py`
4. **Version Comparison**: Semantic comparison using github_version_checker
5. **User Confirmation**: Dialog showing current vs new version with release notes
6. **Update Execution**: `git reset --hard origin/main` (force update)
7. **Result Reporting**: Success/failure dialogs with version info

## Safety Mechanisms

### Built-in Safety Features:
- **Git Repository Detection**: Verifies installation is in git repo
- **Force Update Strategy**: Uses `git reset --hard` to avoid merge conflicts
- **Version Validation**: Compares semantic versions before updating
- **Error Handling**: Comprehensive error messages for network/git failures
- **Timeout Protection**: 30-second timeout on git operations
- **Non-blocking UI**: Background threads prevent UI freezing

### User Experience:
- **Clear Version Display**: "Current: 0.3.0 → New: 0.3.1"
- **Progress Feedback**: Real-time progress during download
- **Graceful Degradation**: Works for non-git installations (shows download link)

## Testing Strategy

### Test Script Creation
Create `test_update_dialog.py` to preview all dialog scenarios safely:
```python
# Test all dialog states without performing actual updates
python test_update_dialog.py
```

### Testing Methods
1. **Dialog Preview** (safest): Test all UI scenarios
2. **Temporary Version Modification**: Change local version to trigger update
3. **Test Branch Workflow**: Use separate branch for testing
4. **Mock Git Updater**: For automated testing

## File Structure

```
MDviewer/
├── main.py                          # Updated to import version
├── version.py                       # New: Centralized version
├── github_version_checker.py        # New: From HPM repository
├── git_updater.py                   # New: Git update operations
├── viewer/
│   ├── main_window.py               # Updated: Menu & handler
│   └── update_dialogs.py           # New: Dialog components
└── test_update_dialog.py            # New: Test script
```

## Success Criteria

### Functional Requirements:
- [ ] Users can check for updates via Help menu
- [ ] Semantic version comparison works correctly
- [ ] Updates complete successfully without conflicts
- [ ] Progress indication during updates
- [ ] Clear success/failure messaging
- [ ] Graceful handling of network/git errors

### Non-functional Requirements:
- [ ] Non-blocking UI during operations
- [ ] 30-second timeout protection
- [ ] No external dependencies beyond standard library
- [ ] Works on Windows, macOS, and Linux
- [ ] Maintains application stability during updates

## Version Migration Plan

### Current State:
- `main.py`: version "0.0.2" (application metadata)
- `AboutDialog`: version "v0.0.3 2026-01-25 0525 CST"
- Status bar: version "v0.0.3 2026-01-25 0525 CST"

### Target State:
- `version.py`: version "0.3.0" (semantic)
- All components import from `version.py`
- Consistent version display across application

### Migration Steps:
1. Create `version.py` with version 0.3.0
2. Update `main.py` to import from `version.py`
3. Update `AboutDialog` to import from `version.py`
4. Update status bar to import from `version.py`

## Menu Integration Details

### Help Menu Structure:
```
Help
├── Quick Reference
├── Changelog
├── ─────────────────
├── Get Latest Version (Ctrl+U)
├── ─────────────────
└── About
```

### Keyboard Shortcuts:
- **Ctrl+U**: Get Latest Version

## Error Scenarios & Handling

### Network Errors:
- No internet connection
- GitHub API unavailable
- Repository not found

### Git Errors:
- Not a git repository
- Git not installed/in PATH
- Permission denied
- Remote fetch timeout

### Version Errors:
- Invalid version format
- Version file not found
- Remote version inaccessible

### Fallback Behavior:
- Show download link for manual update
- Display helpful error messages
- Maintain application stability

## Future Enhancements

### Optional Features (not in initial implementation):
- [ ] **Auto-check on startup**: Check for updates automatically
- [ ] **Update scheduling**: Background update checks
- [ ] **Beta channel support**: Allow checking prerelease versions
- [ ] **Update history**: Track update history
- [ ] **Rollback capability**: Ability to revert updates

### Beta/Prerelease Support (if needed later):
- Configuration option for release channel
- Support for versions like `0.3.0-beta.1`
- Separate update streams for stable/beta

## References

### HPM Implementation:
- Location: `Photos/Version-2/Framework/`
- Key files: `utils/github_version_checker.py`, `utils/git_updater.py`
- UI integration: `gui/main_window.py:958`

### Version Checker Module:
- Repository: https://github.com/juren53/version-checker-module
- Documentation: Complete API reference and examples

### MDviewer Current State:
- PyQt6-based application
- Dark theme support
- Existing dialog patterns in `main_window.py`

---

**Version**: 1.0  
**Created**: 2026-01-25  
**Based on**: HPM v0.1.7o+ implementation  
**Adapted for**: MDviewer PyQt6 architecture  
**Author**: Jim Murdock
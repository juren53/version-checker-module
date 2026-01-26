# PLAN: How to Implement a "Get Latest Resource" Feature

## Overview

This plan documents how to implement a "Get Latest Resource" feature based on the successful implementation in HPM (HST-Metadata Photos). The feature allows users to automatically update their application to the latest version from GitHub with a single menu click.

## Architecture Components

### 1. Core Modules

#### GitHub Version Checker (`github_version_checker.py`)
- **Purpose**: Standalone module for checking GitHub releases
- **Status**: ✅ Complete and reusable
- **Location**: [version-checker-module](https://github.com/juren53/version-checker-module)
- **Key Features**:
  - Semantic version comparison (supports prerelease versions)
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
- Add menu item (e.g., Help → "Get Latest Updates")
- Handler method in main window (e.g., `_on_get_latest_updates()`)

#### Dialog Components
- **Progress Dialog**: Shows download/update progress
- **Version Comparison Dialog**: Current vs New version with release notes
- **Result Dialogs**: Success, failure, and up-to-date scenarios

## Implementation Steps

### Phase 1: Setup and Dependencies

1. **Copy Core Module**
   ```bash
   # Clone or copy github_version_checker.py to your project
   wget https://raw.githubusercontent.com/juren53/version-checker-module/main/github_version_checker.py
   ```

2. **Verify Dependencies**
   - Python 3.6+
   - PyQt5/PyQt6/PySide
   - Git command-line tool
   - No additional pip packages required

### Phase 2: Create Git Updater Module

1. **Create `git_updater.py`** with the following structure:
   ```python
   import subprocess
   import os
   from typing import Optional, Tuple
   
   class GitUpdater:
       def __init__(self, repo_url: str, version_file_path: str, branch: str = "main"):
           self.repo_url = repo_url
           self.version_file_path = version_file_path
           self.branch = branch
           
       def get_update_info(self) -> Tuple[bool, str, str]:
           """Returns (has_update, current_version, latest_version)"""
           
       def force_update(self) -> Tuple[bool, str]:
           """Performs git reset --hard update"""
           
       def get_remote_version(self) -> Optional[str]:
           """Reads version from remote repository"""
   ```

2. **Key Implementation Details**:
   - Use `git reset --hard origin/{branch}` for clean updates
   - 30-second timeout on git operations
   - Comprehensive error handling
   - Semantic version comparison

### Phase 3: UI Integration

1. **Menu Item Addition**
   ```python
   # In your main window class
   help_menu = self.menuBar().addMenu("&Help")
   get_latest_action = help_menu.addAction("Get Latest Updates")
   get_latest_action.triggered.connect(self._on_get_latest_updates)
   ```

2. **Handler Method**
   ```python
   def _on_get_latest_updates(self):
       # Check if in git repository
       # Fetch version information
       # Show comparison dialog
       # Perform update if confirmed
       # Show result dialog
   ```

3. **Dialog Templates**
   - **Version Comparison**: Show current vs new version with release notes
   - **Progress**: Real-time progress during git operations
   - **Results**: Success/failure with version information

### Phase 4: Configuration

1. **Repository Configuration**
   ```python
   # Example configuration
   CONFIG = {
       'repo_url': 'https://github.com/owner/repo',
       'version_file': 'path/to/version.py',
       'branch': 'main',
       'api_endpoint': 'https://api.github.com/repos/owner/repo/releases/latest'
   }
   ```

2. **Adapt for Your Project**
   - Change repository URL and paths
   - Update version file location
   - Customize error messages for your application context

## Data Flow

```
User Click → Git Repo Check → Version Fetch → Version Compare → User Confirmation → Git Update → Result Display
```

### Detailed Flow:

1. **Repository Validation**: Verify current directory is a git repository
2. **Remote Fetch**: `git fetch origin` to get latest state
3. **Version Detection**: 
   - Local version from configured version file
   - Remote version from `origin/[branch]:path/to/version_file`
4. **Version Comparison**: Semantic comparison using github_version_checker
5. **User Confirmation**: Dialog showing current vs new version with release notes
6. **Update Execution**: `git reset --hard origin/[branch]` (force update)
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
- **Clear Version Display**: "Current: v1.0.0 → New: v1.1.0"
- **Progress Feedback**: Real-time progress during download
- **Graceful Degradation**: Works for non-git installations (shows download link)

## Testing Strategy

### 1. Test Script Creation
Create `test_update_dialog.py` to preview all dialog scenarios safely:
```python
# Test all dialog states without performing actual updates
python test_update_dialog.py
```

### 2. Testing Methods
1. **Dialog Preview** (safest): Test all UI scenarios
2. **Temporary Version Modification**: Change local version to trigger update
3. **Test Branch Workflow**: Use separate branch for testing
4. **Mock Git Updater**: For automated testing

### 3. Test Documentation
Create `notes/TESTING_update-feature.md` with comprehensive testing guide

## Adaptation Checklist

### Required Modifications:
- [ ] **Repository Configuration**: Change repo URL and paths
- [ ] **Version File Location**: Update path to version file  
- [ ] **Menu Integration**: Adapt to your application's menu structure
- [ ] **Error Messages**: Customize for your application context
- [ ] **Dialog Styling**: Match your application's UI theme

### Optional Enhancements:
- [ ] **Auto-check on startup**: Check for updates automatically
- [ ] **Update scheduling**: Background update checks
- [ ] **Beta channel support**: Allow checking prerelease versions
- [ ] **Update history**: Track update history
- [ ] **Rollback capability**: Ability to revert updates

## Minimal Integration Example

```python
# 1. Copy github_version_checker.py to your project
# 2. Create git_updater.py (adapted from template)
# 3. Add to main window:

from github_version_checker import GitHubVersionChecker
from git_updater import GitUpdater

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_update_feature()
        
    def setup_update_feature(self):
        # Initialize updaters
        self.version_checker = GitHubVersionChecker(
            "owner/repo", 
            "1.0.0"
        )
        self.git_updater = GitUpdater(
            "https://github.com/owner/repo",
            "path/to/version.py"
        )
        
        # Add menu item
        help_menu = self.menuBar().addMenu("&Help")
        update_action = help_menu.addAction("Get Latest Updates")
        update_action.triggered.connect(self._on_get_latest_updates)
        
    def _on_get_latest_updates(self):
        # Implementation following the data flow above
        pass
```

## Success Criteria

### Functional Requirements:
- [ ] Users can check for updates via menu item
- [ ] Version comparison works correctly
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

## Maintenance

### Regular Updates:
- Monitor GitHub API changes
- Update error handling for new edge cases
- Test with new Python/Qt versions
- Update documentation based on user feedback

### Troubleshooting:
- Common issues: git not in PATH, network timeouts, permission errors
- Logging: Add debug logging for troubleshooting
- Fallback: Provide manual download links when automatic update fails

## References

### HPM Implementation:
- Location: `Photos/Version-2/Framework/`
- Key files: `utils/github_version_checker.py`, `utils/git_updater.py`
- UI integration: `gui/main_window.py:958`

### Version Checker Module:
- Repository: https://github.com/juren53/version-checker-module
- Documentation: Complete API reference and examples

### Testing Documentation:
- HPM test guide: `notes/TESTING_HPM-update-route.md`
- Test script: `test_update_dialog.py`

---

**Version**: 1.0  
**Created**: 2026-01-25  
**Based on**: HPM v0.1.7o+ implementation  
**Author**: Jim U'Ren

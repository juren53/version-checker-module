# Version Checker Module - Integration Guide

Quick reference for integrating the version checker module into your Python projects.

## Quick Start (5 Minutes)

### Step 1: Copy Files
Copy these files into your project:
```
your-project/
├── version.py                    # Copy and adapt
├── github_version_checker.py     # Copy as-is
├── git_updater.py               # Copy as-is (if using git updates)
└── release_downloader.py        # Copy as-is (if using archive updates)
```

### Step 2: Configure version.py
Update `version.py` with your project's version:
```python
__version__ = "1.0.0"
__version_date__ = "2026-01-31"
__version_info__ = (1, 0, 0)

def get_version_string():
    return f"v{__version__} {__version_date__}"
```

### Step 3: Basic Integration
```python
import os
from version import __version__
from github_version_checker import GitHubVersionChecker
from git_updater import GitUpdater
from release_downloader import ReleaseDownloader

def check_and_update():
    # Check for updates
    checker = GitHubVersionChecker(
        repo_url="your-username/your-repo",
        current_version=__version__
    )
    
    result = checker.get_latest_version()
    
    if not result.has_update:
        print("✓ Up to date!")
        return
    
    print(f"Update available: {result.latest_version}")
    
    # Perform update based on installation type
    if os.path.exists(".git"):
        # Git installation
        updater = GitUpdater(
            repo_url="https://github.com/your-username/your-repo.git",
            version_file_path="version.py"
        )
        update_result = updater.force_update()
    else:
        # Release installation
        downloader = ReleaseDownloader(
            repo_url="your-username/your-repo",
            version_file_path="version.py"
        )
        update_result = downloader.perform_update(result.latest_version)
    
    if update_result.success:
        print(f"✓ Updated to {update_result.new_version}")
    else:
        print(f"✗ Update failed: {update_result.message}")
```

## Integration Patterns

### Pattern 1: CLI Application
```python
import argparse
from version import __version__, get_version_string
from github_version_checker import GitHubVersionChecker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', 
                       version=get_version_string())
    parser.add_argument('--check-update', action='store_true',
                       help='Check for updates')
    
    args = parser.parse_args()
    
    if args.check_update:
        check_for_updates()
```

### Pattern 2: GUI Application (PyQt6)
```python
from PyQt6.QtWidgets import QMainWindow, QAction
from github_version_checker import GitHubVersionChecker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_menu()
    
    def setup_menu(self):
        help_menu = self.menuBar().addMenu("Help")
        
        update_action = QAction("Check for Updates", self)
        update_action.setShortcut("Ctrl+U")
        update_action.triggered.connect(self.check_updates)
        help_menu.addAction(update_action)
    
    def check_updates(self):
        checker = GitHubVersionChecker(
            repo_url="your-username/your-repo",
            current_version=__version__
        )
        
        # Use async check to avoid blocking UI
        checker.check_for_updates(self.on_update_checked)
    
    def on_update_checked(self, result):
        if result.has_update:
            # Show update dialog
            self.show_update_dialog(result)
        else:
            # Show up-to-date message
            self.show_info("Already up to date!")
```

### Pattern 3: Automatic Background Check
```python
import threading
import time
from github_version_checker import GitHubVersionChecker

class UpdateChecker:
    def __init__(self, repo_url, current_version, check_interval=3600):
        self.checker = GitHubVersionChecker(repo_url, current_version)
        self.check_interval = check_interval
        self.running = False
    
    def start(self):
        self.running = True
        thread = threading.Thread(target=self._check_loop, daemon=True)
        thread.start()
    
    def stop(self):
        self.running = False
    
    def _check_loop(self):
        while self.running:
            self.checker.check_for_updates(self.on_result)
            time.sleep(self.check_interval)
    
    def on_result(self, result):
        if result.has_update:
            print(f"Update available: {result.latest_version}")
```

## Configuration Options

### GitHubVersionChecker Options
```python
checker = GitHubVersionChecker(
    repo_url="owner/repo",           # GitHub repository
    current_version="1.0.0",         # Current version
    timeout=10                       # Network timeout (seconds)
)
```

### GitUpdater Options
```python
updater = GitUpdater(
    repo_url="https://github.com/owner/repo.git",  # Full git URL
    version_file_path="version.py",                # Relative path to version.py
    branch="main",                                 # Git branch (default: main)
    timeout=30                                     # Git operation timeout
)
```

### ReleaseDownloader Options
```python
downloader = ReleaseDownloader(
    repo_url="owner/repo",           # GitHub repository
    version_file_path="version.py",  # Relative path to version.py
    timeout=30                       # Download timeout (seconds)
)
```

## Error Handling

### Basic Error Handling
```python
result = checker.get_latest_version()

if result.error_message:
    # Handle different error types
    if "Network error" in result.error_message:
        print("Check your internet connection")
    elif "timeout" in result.error_message:
        print("Server is not responding")
    else:
        print(f"Error: {result.error_message}")
    return

# Process successful result
if result.has_update:
    print(f"Update available: {result.latest_version}")
```

### Update Error Handling
```python
update_result = updater.force_update()

if not update_result.success:
    # Log error details
    print(f"Update failed: {update_result.message}")
    print(f"Error output: {update_result.error_output}")
    
    # Inform user
    show_error_dialog(
        "Update Failed",
        f"Could not update: {update_result.message}"
    )
```

## Best Practices

### 1. Version Format
Use semantic versioning in `version.py`:
```python
__version__ = "1.2.3"  # MAJOR.MINOR.PATCH
```

### 2. Timeout Configuration
Adjust timeouts based on your needs:
- **Quick check**: 5-10 seconds
- **Standard**: 10-15 seconds
- **Slow connections**: 30 seconds

### 3. Background Checking
Don't check synchronously in the main thread:
```python
# Good: Async with callback
checker.check_for_updates(callback)

# Bad: Blocks UI
result = checker.get_latest_version()
```

### 4. User Experience
- Show progress during updates
- Provide clear error messages
- Allow users to skip updates
- Don't auto-update without permission

### 5. Testing
Test both installation types:
```bash
# Test git installation
python your_app.py --check-update

# Test release installation
# Remove .git directory temporarily
mv .git .git.bak
python your_app.py --check-update
mv .git.bak .git
```

## Platform-Specific Notes

### Windows
```python
# Windows uses ZIP archives
# Ensure proper path separators
version_file = os.path.join(root, "version.py")
```

### Linux/macOS
```python
# Unix uses tar.gz archives
# Preserve file permissions
os.chmod(script_path, 0o755)
```

## Common Issues

### Issue 1: "Not a git repository"
**Solution**: Use `ReleaseDownloader` for non-git installations.

### Issue 2: "Git command not found"
**Solution**: Ensure git is installed and in PATH, or use release downloads.

### Issue 3: "Network timeout"
**Solution**: Increase timeout value or check internet connection.

### Issue 4: "Permission denied"
**Solution**: On Windows, may need admin rights. On Unix, check file permissions.

### Issue 5: "Version file not found"
**Solution**: Verify `version_file_path` is correct relative to project root.

## Testing Your Integration

### Test Checklist
- [ ] Version checking works
- [ ] Git-based updates work (if applicable)
- [ ] Archive-based updates work (if applicable)
- [ ] Error handling is graceful
- [ ] Backup and rollback work
- [ ] UI doesn't freeze during operations
- [ ] Works on all target platforms

### Manual Testing
```bash
# Test version checker
python test_release_downloader.py

# Test full integration (dry run)
python -c "from your_module import check_and_update; check_and_update()"
```

## Example Projects

See these projects for real-world integration examples:
- **MDviewer**: PyQt6 GUI application with menu integration
- **HPM**: Original implementation with auto-update
- **SysMon**: CLI tool with update checks

## Support

For issues or questions:
1. Check CONTENTS.md for file locations
2. Review README.md for API details
3. See planning documents for implementation context
4. Test with provided test scripts

## Next Steps

After integration:
1. Test thoroughly on all platforms
2. Document update process for users
3. Create GitHub releases with tags (v1.0.0 format)
4. Add update notifications to your UI
5. Consider adding auto-check on startup

## Quick Reference Card

```python
# Check for updates
checker = GitHubVersionChecker("user/repo", "1.0.0")
result = checker.get_latest_version()

# Git update
updater = GitUpdater("https://github.com/user/repo.git", "version.py")
updater.force_update()

# Release update
downloader = ReleaseDownloader("user/repo", "version.py")
downloader.perform_update("1.0.1")
```

That's it! You're ready to integrate version checking into your project.

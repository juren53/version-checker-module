#!/usr/bin/env python3
"""
Test Script for MDviewer Update Feature

Safe preview of all update dialog states without performing actual updates.
Tests all scenarios: up-to-date, update available, errors, progress dialogs.

Usage:
    python test_update_dialog.py

Author: MDviewer Project
v1.0.0
Created: 2026-01-25
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from viewer.update_dialogs import (
    VersionCompareDialog,
    UpToDateDialog,
    UpdateProgressDialog,
    UpdateResultDialog,
    ErrorDialog,
)
from github_version_checker import VersionCheckResult
from git_updater import GitUpdateResult


class TestUpdateDialogs(QDialog):
    """Main test dialog to preview all update dialog states"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MDviewer Update Dialog Test")
        self.setFixedSize(400, 300)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Update Dialog Test Suite")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Test buttons
        version_compare_btn = QPushButton("Version Compare Dialog")
        version_compare_btn.clicked.connect(self.test_version_compare)

        up_to_date_btn = QPushButton("Up-to-Date Dialog")
        up_to_date_btn.clicked.connect(self.test_up_to_date)

        progress_btn = QPushButton("Progress Dialog")
        progress_btn.clicked.connect(self.test_progress)

        success_btn = QPushButton("Update Success Dialog")
        success_btn.clicked.connect(self.test_update_success)

        failure_btn = QPushButton("Update Failure Dialog")
        failure_btn.clicked.connect(self.test_update_failure)

        error_btn = QPushButton("Error Dialog")
        error_btn.clicked.connect(self.test_error)

        # Add to layout
        layout.addWidget(title_label)
        layout.addWidget(version_compare_btn)
        layout.addWidget(up_to_date_btn)
        layout.addWidget(progress_btn)
        layout.addWidget(success_btn)
        layout.addWidget(failure_btn)
        layout.addWidget(error_btn)

        self.setLayout(layout)

    def apply_theme(self):
        """Apply MDviewer dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            QLabel {
                color: #c9d1d9;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 10px 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:pressed {
                background-color: #1a7f37;
            }
        """)

    def test_version_compare(self):
        """Test version comparison dialog"""
        check_result = VersionCheckResult()
        check_result.has_update = True
        check_result.current_version = "0.3.0"
        check_result.latest_version = "0.3.1"
        check_result.release_notes = """## New in v0.3.1

### Features
- Added automatic update checking
- Improved dark theme support
- Enhanced markdown rendering

### Bug Fixes
- Fixed scrollbar styling issues
- Resolved font rendering problems
- Improved error handling

### Improvements
- Faster startup times
- Better memory management
- Enhanced user experience"""

        dialog = VersionCompareDialog(check_result, self)
        dialog.exec()

    def test_up_to_date(self):
        """Test up-to-date dialog"""
        dialog = UpToDateDialog("0.3.0", self)
        dialog.exec()

    def test_progress(self):
        """Test progress dialog"""
        dialog = UpdateProgressDialog(self)
        dialog.exec()

    def test_update_success(self):
        """Test update success dialog"""
        update_result = GitUpdateResult()
        update_result.success = True
        update_result.current_version = "0.3.0"
        update_result.new_version = "0.3.1"
        update_result.message = "Successfully updated to 0.3.1"
        update_result.command_output = """Fetching origin...
From https://github.com/juren53/MDviewer
 * branch            main        -> FETCH_HEAD
Resetting to origin/main...
Your branch is up to date with 'origin/main'.

Update completed: 0.3.0 → 0.3.1"""

        dialog = UpdateResultDialog(update_result, self)
        dialog.exec()

    def test_update_failure(self):
        """Test update failure dialog"""
        update_result = GitUpdateResult()
        update_result.success = False
        update_result.current_version = "0.3.0"
        update_result.new_version = ""
        update_result.message = "Network connection failed"
        update_result.error_output = """fatal: unable to access 'https://github.com/juren53/MDviewer.git/':
Could not resolve host: github.com"""

        dialog = UpdateResultDialog(update_result, self)
        dialog.exec()

    def test_error(self):
        """Test error dialog"""
        dialog = ErrorDialog(
            "MDviewer installation is not a git repository.\n\n"
            "To enable automatic updates, please install MDviewer from git:\n"
            "git clone https://github.com/juren53/MDviewer.git",
            self,
        )
        dialog.exec()


def test_version_checker():
    """Test the version checker functionality"""
    print("=== Testing Version Checker ===")

    from github_version_checker import GitHubVersionChecker

    checker = GitHubVersionChecker(
        repo_url="juren53/MDviewer", current_version="0.3.0", timeout=10
    )

    print(f"Repository: {checker.repo_url}")
    print(f"Current version: {checker.current_version}")
    print(f"API URL: {checker.api_url}")

    # Test version comparison
    test_cases = [
        ("0.3.0", "0.3.0", 0),
        ("0.3.0", "0.3.1", -1),
        ("0.3.1", "0.3.0", 1),
        ("0.2.9", "0.3.0", -1),
    ]

    print("\nVersion Comparison Tests:")
    for v1, v2, expected in test_cases:
        actual = checker.compare_versions(v1, v2)
        status = "✅" if actual == expected else "❌"
        print(f"  {status} compare('{v1}', '{v2}') = {actual} (expected {expected})")

    print()


def test_git_updater():
    """Test the git updater functionality"""
    print("=== Testing Git Updater ===")

    from git_updater import GitUpdater

    updater = GitUpdater(
        repo_url="https://github.com/juren53/MDviewer.git",
        version_file_path="version.py",
        branch="main",
    )

    print(f"Repository: {updater.repo_url}")
    print(f"Working directory: {updater.working_dir}")
    print(f"Version file: {updater.version_file_path}")

    # Test repository detection
    is_git = updater.is_git_repository()
    print(f"Is git repository: {is_git}")

    if is_git:
        # Test version reading
        current_version = updater.get_current_version()
        print(f"Current version: {current_version}")

        # Test repository status
        is_clean, status_msg = updater.get_repository_status()
        print(f"Repository status: {status_msg}")

        # Test remote info
        remote_url, current_branch = updater.get_remote_info()
        print(f"Remote URL: {remote_url}")
        print(f"Current branch: {current_branch}")

    print()


def main():
    """Main test function"""
    print("MDviewer Update Feature Test Suite")
    print("=" * 40)

    # Test core components
    test_version_checker()
    test_git_updater()

    # Launch GUI test
    print("Launching GUI dialog test...")
    app = QApplication(sys.argv)

    # Apply MDviewer theme
    from viewer.main_window import ThemeManager

    palette = ThemeManager.get_fusion_dark_palette()
    app.setPalette(palette)

    test_dialog = TestUpdateDialogs()
    test_dialog.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

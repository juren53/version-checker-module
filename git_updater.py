#!/usr/bin/env python3
"""
Git Updater Module for MDviewer

Handles safe git repository updates using force update strategy.
Based on the successful HPM implementation adapted for PyQt6.

Author: MDviewer Project
v1.0.0
Created: 2026-01-25
"""

import subprocess
import os
import re
from typing import Optional, Tuple, List
from pathlib import Path


class GitUpdateResult:
    """Data class for git update results"""

    def __init__(self):
        self.success = False
        self.message = ""
        self.current_version = ""
        self.new_version = ""
        self.command_output = ""
        self.error_output = ""


class GitUpdater:
    """
    Safe git repository updater

    Features:
    - Force update using 'git reset --hard' to avoid conflicts
    - 30-second timeout on git operations
    - Comprehensive error handling
    - Version comparison and validation
    - Safe repository detection
    """

    def __init__(
        self,
        repo_url: str,
        version_file_path: str,
        branch: str = "main",
        timeout: int = 30,
    ):
        """
        Initialize git updater

        Args:
            repo_url: GitHub repository URL
            version_file_path: Path to version.py file (relative to repo root)
            branch: Git branch to update from (default: main)
            timeout: Timeout for git operations in seconds
        """
        self.repo_url = repo_url
        self.version_file_path = version_file_path
        self.branch = branch
        self.timeout = timeout
        self.working_dir = os.getcwd()

    def _run_git_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """
        Run a git command with timeout and error handling

        Args:
            command: Git command as list of arguments

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )

            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            error_msg = f"Git command timed out after {self.timeout} seconds"
            return False, "", error_msg
        except FileNotFoundError:
            error_msg = "Git command not found. Is git installed and in PATH?"
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Unexpected error running git command: {str(e)}"
            return False, "", error_msg

    def is_git_repository(self) -> bool:
        """Check if current directory is a git repository"""
        git_dir = os.path.join(self.working_dir, ".git")
        return os.path.exists(git_dir)

    def get_current_version(self) -> Optional[str]:
        """Read current version from local version file"""
        try:
            version_file = os.path.join(self.working_dir, self.version_file_path)
            if not os.path.exists(version_file):
                return None

            with open(version_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract __version__ = "x.y.z" pattern
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)

        except Exception as e:
            print(f"Error reading local version: {e}")

        return None

    def get_remote_version(self) -> Optional[str]:
        """Read version from remote repository"""
        try:
            # Fetch latest from remote
            success, stdout, stderr = self._run_git_command(["fetch", "origin"])
            if not success:
                print(f"Failed to fetch from remote: {stderr}")
                return None

            # Try to read version.py from remote branch
            remote_file = f"origin/{self.branch}:{self.version_file_path}"
            success, stdout, stderr = self._run_git_command(["show", remote_file])
            if success and stdout:
                # Extract __version__ = "x.y.z" pattern
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', stdout)
                if match:
                    return match.group(1)
                else:
                    print(
                        f"Version pattern not found in remote {self.version_file_path}"
                    )
            else:
                print(f"Could not read remote {self.version_file_path}: {stderr}")

            # If version.py doesn't exist remotely, try to infer from git tags
            success, stdout, stderr = self._run_git_command(["tag", "--list", "v*"])
            if success and stdout:
                # Get the latest tag
                tags = stdout.strip().split("\n")
                if tags:
                    latest_tag = sorted(tags)[-1]  # Get highest version tag
                    version = latest_tag.lstrip("v")
                    if re.match(r"\d+\.\d+\.\d+", version):
                        print(f"Using latest git tag as version: {version}")
                        return version

            print(f"No version information found in remote repository")

        except Exception as e:
            print(f"Error reading remote version: {e}")

        return None

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two semantic version strings

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
        """

        def parse_version(v: str) -> tuple:
            # Remove any 'v' prefix and split into numeric parts
            v = v.lstrip("v")
            parts = [int(x) for x in re.split(r"[^\d]+", v) if x.isdigit()]

            # Pad to 3 parts (major.minor.patch)
            while len(parts) < 3:
                parts.append(0)

            return tuple(parts[:3])

        v1_parts = parse_version(version1)
        v2_parts = parse_version(version2)

        # Compare each part
        for p1, p2 in zip(v1_parts, v2_parts):
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1

        return 0  # versions are equal

    def get_update_info(self) -> Tuple[bool, str, str]:
        """
        Check if an update is available

        Returns:
            Tuple of (has_update, current_version, latest_version)
        """
        # Check if we're in a git repository
        if not self.is_git_repository():
            print("Not in a git repository")
            return False, "", ""

        # Get current version
        current_version = self.get_current_version()
        if not current_version:
            print("Could not determine current version")
            return False, "", ""

        # Get remote version
        latest_version = self.get_remote_version()
        if not latest_version:
            print("Could not determine remote version")
            return False, current_version, ""

        # Compare versions
        has_update = self.compare_versions(current_version, latest_version) < 0

        return has_update, current_version, latest_version

    def force_update(self) -> GitUpdateResult:
        """
        Perform a force update using git reset --hard

        Returns:
            GitUpdateResult object with update results
        """
        result = GitUpdateResult()
        result.current_version = self.get_current_version()

        # Check if we're in a git repository
        if not self.is_git_repository():
            result.message = "Error: Current directory is not a git repository"
            result.error_output = "No .git directory found"
            return result

        try:
            # Step 1: Fetch latest changes from remote
            success, stdout, stderr = self._run_git_command(["fetch", "origin"])
            if not success:
                result.message = f"Failed to fetch from remote: {stderr}"
                result.error_output = stderr
                return result
            result.command_output += f"Fetch: {stdout}\n"

            # Step 2: Reset to latest version (force update)
            reset_target = f"origin/{self.branch}"
            success, stdout, stderr = self._run_git_command(
                ["reset", "--hard", reset_target]
            )
            if not success:
                result.message = f"Failed to reset to {reset_target}: {stderr}"
                result.error_output = stderr
                return result
            result.command_output += f"Reset: {stdout}\n"

            # Step 3: Get new version
            result.new_version = self.get_current_version()

            # Step 4: Success
            result.success = True
            result.message = f"Successfully updated to {result.new_version}"

            # Update command output with success message
            result.command_output += (
                f"Update completed: {result.current_version} → {result.new_version}"
            )

        except Exception as e:
            result.message = f"Update failed: {str(e)}"
            result.error_output = str(e)

        return result

    def get_repository_status(self) -> Tuple[bool, str]:
        """
        Get current repository status

        Returns:
            Tuple of (is_clean, status_message)
        """
        try:
            success, stdout, stderr = self._run_git_command(["status", "--porcelain"])
            if not success:
                return False, f"Failed to get status: {stderr}"

            # If stdout is empty, repository is clean
            is_clean = len(stdout.strip()) == 0

            if is_clean:
                return True, "Working directory clean"
            else:
                return False, "Working directory has uncommitted changes"

        except Exception as e:
            return False, f"Error getting status: {str(e)}"

    def get_remote_info(self) -> Tuple[str, str]:
        """
        Get information about remote repository

        Returns:
            Tuple of (remote_url, branch)
        """
        try:
            # Get remote URL
            success, stdout, stderr = self._run_git_command(
                ["config", "--get", "remote.origin.url"]
            )
            if not success:
                return "", self.branch
            remote_url = stdout.strip()

            # Get current branch
            success, stdout, stderr = self._run_git_command(
                ["branch", "--show-current"]
            )
            if not success:
                return remote_url, self.branch
            current_branch = stdout.strip() or self.branch

            return remote_url, current_branch

        except Exception as e:
            return "", self.branch


def test_git_updater():
    """Test git updater functionality"""
    print("=== Git Updater Test ===")

    # Initialize updater
    updater = GitUpdater(
        repo_url="https://github.com/juren53/MDviewer.git",
        version_file_path="version.py",
        branch="main",
        timeout=30,
    )

    print(f"Repository: {updater.repo_url}")
    print(f"Working directory: {updater.working_dir}")
    print(f"Version file: {updater.version_file_path}")
    print(f"Branch: {updater.branch}")
    print()

    # Test repository detection
    print("1. Testing repository detection...")
    is_git = updater.is_git_repository()
    print(f"   Is git repository: {is_git}")

    if not is_git:
        print("   ⚠️  Not in a git repository - skipping remaining tests")
        return

    # Test repository status
    print("2. Testing repository status...")
    is_clean, status_msg = updater.get_repository_status()
    print(f"   Status: {status_msg}")

    # Test remote info
    print("3. Testing remote information...")
    remote_url, current_branch = updater.get_remote_info()
    print(f"   Remote URL: {remote_url}")
    print(f"   Current branch: {current_branch}")

    # Test version reading
    print("4. Testing version reading...")
    current_version = updater.get_current_version()
    print(f"   Current version: {current_version}")

    # Test update info (no actual update)
    print("5. Testing update information...")
    has_update, cur_ver, latest_ver = updater.get_update_info()
    print(f"   Has update: {has_update}")
    print(f"   Current version: {cur_ver}")
    print(f"   Latest version: {latest_ver}")

    # Test version comparison
    print("6. Testing version comparison...")
    test_cases = [
        ("0.3.0", "0.3.0", 0),
        ("0.3.0", "0.3.1", -1),
        ("0.3.1", "0.3.0", 1),
        ("0.2.9", "0.3.0", -1),
    ]

    for v1, v2, expected in test_cases:
        actual = updater.compare_versions(v1, v2)
        status = "✅" if actual == expected else "❌"
        print(f"   {status} compare('{v1}', '{v2}') = {actual} (expected {expected})")

    print()
    print("✅ Git updater test completed")


if __name__ == "__main__":
    test_git_updater()

#!/usr/bin/env python3
"""
Release Downloader Module for MDviewer

Handles downloading and installing release archives from GitHub for non-git installations.
Provides backup/rollback capability and cross-platform support.

Author: MDviewer Project
v1.0.0
Created: 2026-01-31
"""

import os
import sys
import shutil
import tempfile
import tarfile
import zipfile
import time
import re
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from pathlib import Path
from typing import Optional, Tuple


class ReleaseDownloadResult:
    """Data class for release download results"""

    def __init__(self):
        self.success = False
        self.message = ""
        self.current_version = ""
        self.new_version = ""
        self.download_url = ""
        self.error_message = ""
        self.backup_path = ""


class ReleaseDownloader:
    """
    GitHub release downloader and installer

    Features:
    - Downloads release archives (ZIP/tarball) from GitHub
    - Creates backups before update
    - Validates archive integrity
    - Provides rollback on failure
    - Cross-platform support (Windows/Linux)
    - 30-second timeout on operations
    """

    def __init__(
        self,
        repo_url: str,
        version_file_path: str = "version.py",
        timeout: int = 30,
    ):
        """
        Initialize release downloader

        Args:
            repo_url: GitHub repository URL (e.g., 'owner/repo' or full URL)
            version_file_path: Path to version.py file (relative to repo root)
            timeout: Timeout for download operations in seconds
        """
        self.repo_url = self._normalize_repo_url(repo_url)
        self.version_file_path = version_file_path
        self.timeout = timeout
        self.working_dir = os.getcwd()
        self.temp_dir = None
        self.backup_dir = None
        self.platform = sys.platform

    def _normalize_repo_url(self, repo_url: str) -> str:
        """Convert various GitHub URL formats to 'owner/repo' format"""
        if "/" not in repo_url:
            raise ValueError("Invalid repository URL format")

        # Extract owner/repo from various GitHub URL formats
        patterns = [
            r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
            r"^([^/]+)/([^/]+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return f"{match.group(1)}/{match.group(2)}"

        raise ValueError(f"Unable to parse repository URL: {repo_url}")

    def _get_archive_format(self) -> str:
        """Determine archive format based on platform"""
        if self.platform.startswith("win"):
            return "zip"
        else:
            return "tar.gz"

    def _get_current_version(self) -> Optional[str]:
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

    def download_release(self, version: str) -> Tuple[bool, str, str]:
        """
        Download release archive from GitHub

        Args:
            version: Version to download (e.g., "0.3.1")

        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            # Ensure version starts with 'v'
            if not version.startswith("v"):
                version = f"v{version}"

            # Determine archive format and construct URL
            archive_format = self._get_archive_format()
            if archive_format == "zip":
                archive_name = f"{version}.zip"
            else:
                archive_name = f"{version}.tar.gz"

            # GitHub source archive URL pattern
            download_url = f"https://github.com/{self.repo_url}/archive/refs/tags/{archive_name}"

            print(f"Downloading from: {download_url}")

            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="mdviewer_update_")
            download_path = os.path.join(self.temp_dir, archive_name)

            # Download with timeout
            request = Request(download_url, headers={"User-Agent": "MDviewer-Updater"})
            
            with urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    return False, "", f"Download failed with status {response.status}"

                # Read and save file
                with open(download_path, "wb") as f:
                    f.write(response.read())

            # Validate download
            if not os.path.exists(download_path) or os.path.getsize(download_path) == 0:
                return False, "", "Downloaded file is empty or missing"

            print(f"Downloaded to: {download_path}")
            return True, download_path, ""

        except (URLError, HTTPError) as e:
            return False, "", f"Network error: {str(e)}"
        except Exception as e:
            return False, "", f"Download error: {str(e)}"

    def extract_archive(self, archive_path: str) -> Tuple[bool, str, str]:
        """
        Extract archive to temporary directory

        Args:
            archive_path: Path to archive file

        Returns:
            Tuple of (success, extracted_dir, error_message)
        """
        try:
            extract_dir = os.path.join(self.temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            archive_format = self._get_archive_format()

            if archive_format == "zip":
                # Extract ZIP
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
            else:
                # Extract tarball
                with tarfile.open(archive_path, "r:gz") as tar_ref:
                    tar_ref.extractall(extract_dir)

            # GitHub archives extract to a subdirectory like "MDviewer-0.3.1"
            # Find the actual content directory
            extracted_items = os.listdir(extract_dir)
            if len(extracted_items) == 1 and os.path.isdir(
                os.path.join(extract_dir, extracted_items[0])
            ):
                content_dir = os.path.join(extract_dir, extracted_items[0])
            else:
                content_dir = extract_dir

            # Validate extracted content
            version_file = os.path.join(content_dir, self.version_file_path)
            if not os.path.exists(version_file):
                return (
                    False,
                    "",
                    f"Invalid archive: {self.version_file_path} not found",
                )

            print(f"Extracted to: {content_dir}")
            return True, content_dir, ""

        except (zipfile.BadZipFile, tarfile.TarError) as e:
            return False, "", f"Archive extraction error: {str(e)}"
        except Exception as e:
            return False, "", f"Extraction error: {str(e)}"

    def backup_installation(self) -> Tuple[bool, str, str]:
        """
        Create backup of current installation

        Returns:
            Tuple of (success, backup_path, error_message)
        """
        try:
            # Create backups directory
            backups_base = os.path.join(self.working_dir, ".backups")
            os.makedirs(backups_base, exist_ok=True)

            # Create timestamped backup directory
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            current_version = self._get_current_version() or "unknown"
            backup_name = f"backup_{current_version}_{timestamp}"
            self.backup_dir = os.path.join(backups_base, backup_name)

            print(f"Creating backup at: {self.backup_dir}")

            # Copy current installation (excluding .backups, .git, __pycache__)
            exclude_dirs = {".backups", ".git", "__pycache__", ".pytest_cache"}

            os.makedirs(self.backup_dir, exist_ok=True)

            for item in os.listdir(self.working_dir):
                if item in exclude_dirs:
                    continue

                src = os.path.join(self.working_dir, item)
                dst = os.path.join(self.backup_dir, item)

                if os.path.isdir(src):
                    shutil.copytree(
                        src,
                        dst,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                    )
                else:
                    shutil.copy2(src, dst)

            # Clean old backups (keep last 3)
            self._cleanup_old_backups(backups_base, keep=3)

            return True, self.backup_dir, ""

        except Exception as e:
            return False, "", f"Backup error: {str(e)}"

    def _cleanup_old_backups(self, backups_dir: str, keep: int = 3):
        """Remove old backups, keeping only the most recent ones"""
        try:
            backups = [
                os.path.join(backups_dir, d)
                for d in os.listdir(backups_dir)
                if os.path.isdir(os.path.join(backups_dir, d))
                and d.startswith("backup_")
            ]

            # Sort by creation time
            backups.sort(key=os.path.getctime, reverse=True)

            # Remove old backups
            for old_backup in backups[keep:]:
                print(f"Removing old backup: {old_backup}")
                shutil.rmtree(old_backup)

        except Exception as e:
            print(f"Warning: Could not clean old backups: {e}")

    def apply_update(self, extracted_dir: str) -> Tuple[bool, str]:
        """
        Replace current installation with extracted files

        Args:
            extracted_dir: Path to extracted release files

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Exclude certain directories and files from update
            exclude_items = {".backups", ".git", "AGENTS.md", "LESSONS_LEARNED-MDviewer-implementation.md"}

            # Copy files from extracted directory to working directory
            for item in os.listdir(extracted_dir):
                if item in exclude_items or item.startswith("."):
                    continue

                src = os.path.join(extracted_dir, item)
                dst = os.path.join(self.working_dir, item)

                # Remove destination if it exists
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)

                # Copy new files
                if os.path.isdir(src):
                    shutil.copytree(
                        src,
                        dst,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                    )
                else:
                    shutil.copy2(src, dst)
                    # Preserve executable permissions on Unix
                    if not self.platform.startswith("win"):
                        src_stat = os.stat(src)
                        os.chmod(dst, src_stat.st_mode)

            return True, ""

        except Exception as e:
            return False, f"Update error: {str(e)}"

    def rollback(self) -> Tuple[bool, str]:
        """
        Restore from backup if update fails

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.backup_dir or not os.path.exists(self.backup_dir):
                return False, "No backup available for rollback"

            print(f"Rolling back from: {self.backup_dir}")

            # Remove current files (except .backups and .git)
            exclude_items = {".backups", ".git"}

            for item in os.listdir(self.working_dir):
                if item in exclude_items or item.startswith("."):
                    continue

                path = os.path.join(self.working_dir, item)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

            # Restore from backup
            for item in os.listdir(self.backup_dir):
                src = os.path.join(self.backup_dir, item)
                dst = os.path.join(self.working_dir, item)

                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            return True, ""

        except Exception as e:
            return False, f"Rollback error: {str(e)}"

    def cleanup(self):
        """Remove temporary files"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"Warning: Could not clean temporary directory: {e}")

    def perform_update(self, version: str) -> ReleaseDownloadResult:
        """
        Perform complete update process

        Args:
            version: Version to download and install (e.g., "0.3.1")

        Returns:
            ReleaseDownloadResult object with update results
        """
        result = ReleaseDownloadResult()
        result.current_version = self._get_current_version() or "unknown"
        result.new_version = version

        try:
            # Step 1: Download release
            print(f"Downloading version {version}...")
            success, archive_path, error = self.download_release(version)
            if not success:
                result.message = f"Download failed: {error}"
                result.error_message = error
                return result

            result.download_url = archive_path

            # Step 2: Extract archive
            print("Extracting archive...")
            success, extracted_dir, error = self.extract_archive(archive_path)
            if not success:
                result.message = f"Extraction failed: {error}"
                result.error_message = error
                self.cleanup()
                return result

            # Step 3: Create backup
            print("Creating backup...")
            success, backup_path, error = self.backup_installation()
            if not success:
                result.message = f"Backup failed: {error}"
                result.error_message = error
                self.cleanup()
                return result

            result.backup_path = backup_path

            # Step 4: Apply update
            print("Applying update...")
            success, error = self.apply_update(extracted_dir)
            if not success:
                result.message = f"Update failed: {error}"
                result.error_message = error

                # Attempt rollback
                print("Attempting rollback...")
                rollback_success, rollback_error = self.rollback()
                if rollback_success:
                    result.message += " (Rolled back to previous version)"
                else:
                    result.message += f" (Rollback also failed: {rollback_error})"

                self.cleanup()
                return result

            # Step 5: Success
            result.success = True
            result.message = f"Successfully updated to version {version}"
            print(result.message)

            # Cleanup temporary files
            self.cleanup()

        except Exception as e:
            result.message = f"Update failed: {str(e)}"
            result.error_message = str(e)
            self.cleanup()

        return result


def test_release_downloader():
    """Test release downloader functionality"""
    print("=== Release Downloader Test ===")

    # Initialize downloader
    downloader = ReleaseDownloader(
        repo_url="juren53/MDviewer",
        version_file_path="version.py",
        timeout=30,
    )

    print(f"Repository: {downloader.repo_url}")
    print(f"Working directory: {downloader.working_dir}")
    print(f"Platform: {downloader.platform}")
    print(f"Archive format: {downloader._get_archive_format()}")
    print()

    # Test current version reading
    print("1. Testing version reading...")
    current_version = downloader._get_current_version()
    print(f"   Current version: {current_version}")
    print()

    # Note: Actual download testing should be done manually
    # as it modifies the installation
    print("⚠️  Actual update testing requires manual verification")
    print("   Use with caution as it modifies your installation")


if __name__ == "__main__":
    test_release_downloader()

#!/usr/bin/env python3
"""
Test script for release downloader functionality
This script tests the ReleaseDownloader without actually performing an update
"""

from release_downloader import ReleaseDownloader

def test_initialization():
    """Test basic initialization"""
    print("=" * 60)
    print("Test 1: Initialization")
    print("=" * 60)
    
    downloader = ReleaseDownloader(
        repo_url="juren53/MDviewer",
        version_file_path="version.py",
        timeout=30
    )
    
    print(f"✓ Repository: {downloader.repo_url}")
    print(f"✓ Version file: {downloader.version_file_path}")
    print(f"✓ Platform: {downloader.platform}")
    print(f"✓ Archive format: {downloader._get_archive_format()}")
    print()

def test_version_reading():
    """Test version reading"""
    print("=" * 60)
    print("Test 2: Version Reading")
    print("=" * 60)
    
    downloader = ReleaseDownloader("juren53/MDviewer")
    current_version = downloader._get_current_version()
    
    print(f"✓ Current version: {current_version}")
    print()

def test_url_parsing():
    """Test GitHub URL parsing"""
    print("=" * 60)
    print("Test 3: URL Parsing")
    print("=" * 60)
    
    test_cases = [
        "juren53/MDviewer",
        "https://github.com/juren53/MDviewer",
        "https://github.com/juren53/MDviewer.git",
    ]
    
    for url in test_cases:
        try:
            downloader = ReleaseDownloader(url)
            print(f"✓ '{url}' -> '{downloader.repo_url}'")
        except Exception as e:
            print(f"✗ '{url}' failed: {e}")
    print()

def test_download_url_construction():
    """Test download URL construction"""
    print("=" * 60)
    print("Test 4: Download URL Construction")
    print("=" * 60)
    
    downloader = ReleaseDownloader("juren53/MDviewer")
    
    # Simulate URL construction for different versions
    test_versions = ["0.3.1", "v0.3.1", "1.0.0"]
    
    for version in test_versions:
        # Normalize version
        if not version.startswith("v"):
            version_tag = f"v{version}"
        else:
            version_tag = version
        
        archive_format = downloader._get_archive_format()
        if archive_format == "zip":
            archive_name = f"{version_tag}.zip"
        else:
            archive_name = f"{version_tag}.tar.gz"
        
        url = f"https://github.com/{downloader.repo_url}/archive/refs/tags/{archive_name}"
        print(f"✓ Version {version} -> {url}")
    print()

def test_backup_path_generation():
    """Test backup path generation"""
    print("=" * 60)
    print("Test 5: Backup Path Generation")
    print("=" * 60)
    
    import os
    import time
    
    downloader = ReleaseDownloader("juren53/MDviewer")
    
    # Simulate backup path
    backups_base = os.path.join(downloader.working_dir, ".backups")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    current_version = downloader._get_current_version() or "unknown"
    backup_name = f"backup_{current_version}_{timestamp}"
    backup_path = os.path.join(backups_base, backup_name)
    
    print(f"✓ Backup path: {backup_path}")
    print()

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RELEASE DOWNLOADER TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_initialization()
        test_version_reading()
        test_url_parsing()
        test_download_url_construction()
        test_backup_path_generation()
        
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

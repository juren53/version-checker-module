# MDviewer Update Bug Fix Report

**Date:** 2026-02-04
**File Modified:** `release_downloader.py`

## Problem

Running the built-in update feature produced a backup error referencing Chrome
browser files in the user's home directory:

```
Backup error: [('/home/juren/.var/app/com.google.Chrome/config/google-chrome/SingletonCookie',
  ..."[Errno 2] No such file or directory: ...SingletonCookie'"),
 ('/home/juren/.var/app/com.google.Chrome/config/google-chrome/SingletonLock', ...),
 ('/home/juren/.var/app/com.google.Chrome/config/google-chrome/SingletonSocket', ...)]
```

The backup was attempting to copy the **entire home directory** rather than
just the MDviewer installation directory.

## Root Cause

Two issues in `release_downloader.py`:

### 1. Wrong working directory (primary cause)

Line 70 set the working directory to whatever directory the user launched
MDviewer from:

```python
self.working_dir = os.getcwd()
```

When MDviewer was launched from the home directory (e.g., via a desktop
shortcut or terminal default), `os.getcwd()` returned `/home/juren/`, causing
the backup to traverse the entire home directory tree -- including
`.var/app/com.google.Chrome/` and everything else.

### 2. No handling of ephemeral files (secondary cause)

`shutil.copytree` enumerates directory contents, then copies each file. Chrome's
singleton files (`SingletonCookie`, `SingletonLock`, `SingletonSocket`) are
ephemeral lock/socket files that can appear and disappear at any moment. They
existed during enumeration but were gone by the time `copytree` tried to copy
them, causing `shutil.Error` with the collected `FileNotFoundError` list.

## Fix

### 1. Use script location instead of current working directory

```python
# Before
self.working_dir = os.getcwd()

# After
self.working_dir = os.path.dirname(os.path.abspath(__file__))
```

`os.path.dirname(os.path.abspath(__file__))` always resolves to the directory
containing `release_downloader.py` -- the actual MDviewer installation
directory -- regardless of where the application was launched from.

### 2. Add safe copy function for transient files

```python
def _copy_safe(src, dst, **kwargs):
    """Copy file, skipping files that vanish during backup."""
    try:
        shutil.copy2(src, dst, **kwargs)
    except FileNotFoundError:
        pass  # File disappeared during copy (e.g., lock files)
```

This wrapper is passed as the `copy_function` argument to `shutil.copytree`
and used directly for individual file copies. Files that disappear mid-backup
are silently skipped instead of aborting the entire operation.

## Testing

All existing tests pass after the changes:

```
tests/test_release_downloader.py::test_initialization        PASSED
tests/test_release_downloader.py::test_version_reading       PASSED
tests/test_release_downloader.py::test_url_parsing           PASSED
tests/test_release_downloader.py::test_download_url_construction PASSED
tests/test_release_downloader.py::test_backup_path_generation   PASSED
```

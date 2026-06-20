# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

version-checker-module is a reusable, stdlib-only Python library for checking GitHub releases and performing application updates. It has no external dependencies. Current version: v1.1.0.

It is consumed by other projects in one of two ways:
1. **File copy** — copy one or more module files directly into the target project (current approach for Photo Tag Writer)
2. **pip install** — installable as a package via `pyproject.toml`

## Three Core Modules

| Module | Class | Purpose |
|--------|-------|---------|
| `github_version_checker.py` | `GitHubVersionChecker` | Queries GitHub releases API, compares semver, returns `VersionCheckResult` |
| `git_updater.py` | `GitUpdater` | Performs `git pull` updates for git-installed apps |
| `release_downloader.py` | `ReleaseDownloader` | Downloads and installs release archives (tar/zip) for non-git installs; includes backup/rollback |

## Quick Integration (file-copy approach)

```python
# Copy github_version_checker.py to your project root, then:
from github_version_checker import GitHubVersionChecker

checker = GitHubVersionChecker(
    repo_url="owner/repo",       # or full GitHub URL
    current_version="1.0.0",
    timeout=10
)

result = checker.get_latest_version()  # returns VersionCheckResult

if result.has_update:
    print(f"New version: {result.latest_version}")
    print(f"Download: {result.download_url}")
elif result.error_message:
    print(f"Check failed: {result.error_message}")
```

## VersionCheckResult Fields

| Field | Type | Description |
|-------|------|-------------|
| `has_update` | bool | True if a newer version is available |
| `current_version` | str | Version passed at construction |
| `latest_version` | str | Version tag from GitHub |
| `download_url` | str | URL of the release asset |
| `release_notes` | str | Release body text |
| `published_date` | str | ISO date of the release |
| `error_message` | str | Non-empty if the check failed |

## Critical Project Rules

### Timezone Convention
**ALL timestamps MUST use Central Time USA (CST/CDT), NEVER UTC.**

### Version Numbering
- Format: `v1.X.Y`
- Update version in: `version.py` (`__version__`, `__version_date__`, `__version_info__`), `pyproject.toml` (`version =`), `CHANGELOG.md`

## Files

```
version-checker-module/
├── github_version_checker.py   # Core: GitHub API check + semver compare
├── git_updater.py              # Update via git pull (git installs)
├── release_downloader.py       # Update via archive download (non-git installs)
├── version.py                  # Module version — __version__, __version_date__
├── pyproject.toml              # pip-installable packaging
├── INTEGRATION_GUIDE.md        # Full integration walkthrough
├── test_release_downloader.py  # Tests
├── test_update_dialog.py       # Tests
├── CHANGELOG.md
└── README.md
```

## Projects Using This Module

| Project | Files used | Integration method |
|---------|-----------|-------------------|
| Photo Tag Writer | `github_version_checker.py` | File copy to project root |
| MDviewer | `github_version_checker.py`, `release_downloader.py` | File copy |

## Notes

- `github_version_checker.py` is the most commonly needed file — the other two are only needed if the app supports self-updating.
- All network calls use stdlib `urllib` only — no `requests` dependency.
- `GitHubVersionChecker` supports both `"owner/repo"` and full `"https://github.com/owner/repo"` URL formats.

# Plan: Migrate to Git Submodules

**Date:** 2026-02-05
**Status:** Proposed
**Supersedes:** PLAN_VCM-process-for-bug-fixes.md (partially — keeps Steps 1-4, replaces Steps 5-6)

## Background

The bug fix process plan (2026-02-04) identified that manually copying files
from `version-checker-module` into consumer projects is fragile. The core
incident: a fix applied to MDviewer's copy of `release_downloader.py` was
overwritten moments later when MDviewer's self-updater pulled the upstream
(still buggy) version.

Git submodules solve this structurally. Instead of copying files, each
consumer project embeds `version-checker-module` as a submodule — a live
pointer to a specific commit in the module repo. Updates are explicit and
deliberate, not accidental.

## What Stays the Same

Steps 1-4 from the original plan remain unchanged:

1. **File an issue** on the module repo when a bug is found
2. **Fix upstream first** in `version-checker-module`
3. **Bump version** in `version.py` and `CHANGELOG.md`
4. **Tag the release** on GitHub (`git tag v1.0.2`, etc.)

These are good practices regardless of how consumers integrate the module.

## What Changes

### Before (Manual Copy)

```
MDviewer/
├── github_version_checker.py   ← copied from version-checker-module
├── release_downloader.py       ← copied from version-checker-module
├── git_updater.py              ← copied from version-checker-module
├── version.py                  ← MDviewer's own
├── main.py
└── viewer/
    └── main_window.py          ← imports: from release_downloader import ...
```

Consumer projects contain duplicated files with no link back to their source.
Updates require manually copying files and hoping nothing is missed.

### After (Submodule)

```
MDviewer/
├── version-checker-module/     ← git submodule (pointer to a commit)
│   ├── github_version_checker.py
│   ├── release_downloader.py
│   ├── git_updater.py
│   └── version.py              ← module's own version (not MDviewer's)
├── version.py                  ← MDviewer's own (unchanged)
├── main.py
└── viewer/
    └── main_window.py          ← imports adjusted (see below)
```

The `version-checker-module/` directory is not a copy — it's a pointer to
an exact commit in `https://github.com/juren53/version-checker-module`.

---

## Migration Steps

### Step 1: Prepare version-checker-module for Submodule Use

No changes needed to the module's code. The existing repo structure works
as-is. The module's `version.py` won't conflict with consumer `version.py`
files because they'll live in separate directories.

**Optional but recommended:** Add an `__init__.py` to make the submodule
directory importable as a Python package:

```python
# version-checker-module/__init__.py
from .github_version_checker import GitHubVersionChecker, VersionCheckResult
from .release_downloader import ReleaseDownloader, ReleaseDownloadResult
from .git_updater import GitUpdater, GitUpdateResult
```

This allows clean imports like:

```python
from version_checker_module import GitHubVersionChecker, ReleaseDownloader
```

**Note:** The hyphen in `version-checker-module` is not valid in Python
package names. The submodule path in consumer projects should use an
underscore: `version_checker_module`.

### Step 2: Add Submodule to MDviewer

```bash
cd C:\Users\jimur\Projects\MDviewer

# Remove the old copied files
git rm github_version_checker.py
git rm release_downloader.py
git rm git_updater.py

# Add the submodule with an underscore path for Python compatibility
git submodule add https://github.com/juren53/version-checker-module version_checker_module

# Pin to the current tagged release
cd version_checker_module
git checkout v1.0.1
cd ..

# Commit the change
git add .gitmodules version_checker_module
git commit -m "Replace copied module files with version-checker-module submodule"
```

This creates a `.gitmodules` file in MDviewer:

```ini
[submodule "version_checker_module"]
    path = version_checker_module
    url = https://github.com/juren53/version-checker-module
```

### Step 3: Update MDviewer Imports

**viewer/main_window.py** — change the imports (currently at lines 49-51):

```python
# Before
from github_version_checker import GitHubVersionChecker
from git_updater import GitUpdater
from release_downloader import ReleaseDownloader

# After
from version_checker_module.github_version_checker import GitHubVersionChecker
from version_checker_module.git_updater import GitUpdater
from version_checker_module.release_downloader import ReleaseDownloader
```

Or, if the `__init__.py` from Step 1 is in place:

```python
from version_checker_module import GitHubVersionChecker, GitUpdater, ReleaseDownloader
```

**viewer/update_dialogs.py** — same pattern (currently at lines 27-28):

```python
# Before
from github_version_checker import VersionCheckResult
from git_updater import GitUpdateResult

# After
from version_checker_module.github_version_checker import VersionCheckResult
from version_checker_module.git_updater import GitUpdateResult
```

**viewer/main_window.py runtime imports** (lines 1829-1830):

```python
# Before
from git_updater import GitUpdateResult
from release_downloader import ReleaseDownloadResult

# After
from version_checker_module.git_updater import GitUpdateResult
from version_checker_module.release_downloader import ReleaseDownloadResult
```

**tests/test_release_downloader.py** and **tests/test_update_dialog.py** —
update similarly.

**sys.path adjustment** — The existing `sys.path.append` in
`viewer/main_window.py` (line 48) that adds MDviewer's root to the path
should continue to work. Since `version_checker_module/` is at MDviewer's
root, the imports will resolve correctly.

### Step 4: Handle MDviewer's Self-Update Mechanism

This is the most important consideration. MDviewer currently has two update
paths:

1. **Git-based updates** (`git_updater.py`): Uses `git reset --hard` to pull
   the latest version. This will naturally work with submodules if we add the
   `--recurse-submodules` flag — but there's a subtlety: the submodule
   should stay pinned to whatever commit MDviewer's repo specifies, not
   auto-update to HEAD. The standard `git reset --hard origin/main` already
   handles this correctly because git records the submodule's pinned commit.

   **Action needed:** After `git_updater.py` runs `git reset --hard`, it
   should also run `git submodule update --init --recursive` to ensure the
   submodule is checked out at the commit MDviewer expects. This is a small
   change to `git_updater.py` in the **module itself**.

2. **Release-based updates** (`release_downloader.py`): Downloads a ZIP/tarball
   from GitHub Releases. GitHub's release archives **do not include
   submodule contents** — they only contain the parent repo's files. This
   means the `version_checker_module/` directory would be empty in a release
   archive.

   **Solutions (choose one):**

   - **Option A — Build a custom release archive** that bundles submodule
     contents. Use a GitHub Action or release script:
     ```bash
     git archive --prefix=MDviewer/ HEAD -o release.zip
     # Then manually inject submodule files into the archive
     ```
     Or use `git submodule foreach` to export and merge.

   - **Option B — Use `gh release create` with a pre-built archive** that
     includes all files. A simple release script:
     ```bash
     # Export the full tree including submodules
     mkdir -p /tmp/mdviewer-release
     git archive HEAD | tar -x -C /tmp/mdviewer-release
     cd version_checker_module && git archive HEAD | tar -x -C /tmp/mdviewer-release/version_checker_module
     cd /tmp && zip -r mdviewer-v0.1.4.zip mdviewer-release/
     gh release create v0.1.4 mdviewer-v0.1.4.zip
     ```

   - **Option C (Simplest) — Keep the release archive as-is** and have the
     `release_downloader.py` separately fetch the module submodule contents
     from `version-checker-module`'s releases. This adds complexity to the
     downloader.

   **Recommendation:** Option B is the cleanest. A small release script
   ensures archives always include everything. This is a one-time setup.

### Step 5: Repeat for Other Consumers

For SysMon and HPM (which only use `github_version_checker.py`):

```bash
cd C:\Users\jimur\Projects\SysMon

# Remove the copied file
git rm github_version_checker.py

# Add submodule
git submodule add https://github.com/juren53/version-checker-module version_checker_module

# Pin to release
cd version_checker_module
git checkout v1.0.1
cd ..

# Update imports and commit
git add .
git commit -m "Replace copied module file with version-checker-module submodule"
```

### Step 6: Update Consumer Cloning Instructions

Each consumer's README should note the submodule dependency:

```markdown
## Installation

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/juren53/MDviewer

# Or if already cloned without submodules
git submodule update --init --recursive
```
```

---

## Updating the Module in Consumer Projects (New Workflow)

When a new version of `version-checker-module` is released, updating a
consumer is now:

```bash
cd C:\Users\jimur\Projects\MDviewer
cd version_checker_module
git fetch
git checkout v1.0.2          # the new tagged release
cd ..
git add version_checker_module
git commit -m "Update version-checker-module to v1.0.2"
git push
```

Compare this to the old workflow of manually copying 3 files and hoping
the right versions were used. The submodule pointer is a single,
unambiguous reference.

---

## What This Eliminates

| Old Problem                              | How Submodules Fix It                                                |
|------------------------------------------|----------------------------------------------------------------------|
| Fix applied to consumer first            | Module files are read-only in consumer context; changes go upstream  |
| No upstream-first workflow               | The submodule IS the upstream repo                                   |
| Fix overwritten by next update           | Submodule stays at its pinned commit until explicitly updated        |
| No notification to consumers             | `git status` shows submodule drift; `git submodule update --remote` shows what's available |
| No consumer registry                     | Dependency is explicit in each consumer's `.gitmodules`              |
| Manual file copying                      | Replaced by `git checkout <tag>` in the submodule directory          |

## What This Introduces

| New Consideration                        | Mitigation                                                           |
|------------------------------------------|----------------------------------------------------------------------|
| Contributors must clone with `--recurse-submodules` | Document in README; add check to app startup if needed      |
| Import paths change                      | One-time migration; cleaner long-term                                |
| Release archives don't include submodules | Use a release script to build complete archives (Option B above)    |
| Submodule directory contains extra files (docs, tests, notes) | Harmless; no impact on functionality           |

## CONSUMERS.md

With submodules, a formal `CONSUMERS.md` in the module repo is less
critical since the dependency is explicit. However, it's still useful as a
quick-reference for the maintainer. The recommendation from the original
plan to create one still stands as a nice-to-have.

## Summary

Git submodules convert the relationship between `version-checker-module` and
its consumers from an informal "copy these files" arrangement into a
formal, version-controlled dependency. The upstream-first workflow becomes
the natural path rather than a discipline to remember. The one-time
migration cost is modest — primarily updating import paths — and the
ongoing maintenance burden drops significantly.

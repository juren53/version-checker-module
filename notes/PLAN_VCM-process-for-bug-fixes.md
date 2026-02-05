# Plan: Bug Fix Process for version-checker-module

**Date:** 2026-02-04
**Status:** Proposed
**Scope:** Maintenance workflow for shared module used across multiple projects

## Background

On 2026-02-04, a bug was discovered in `release_downloader.py` while using
MDviewer's built-in update feature. The backup routine was using `os.getcwd()`
instead of the script's own directory, causing it to attempt backing up the
user's entire home directory.

The fix was applied ad-hoc: first to MDviewer (the consumer), then
retroactively to `version-checker-module` (the source). This exposed several
weaknesses in how bug fixes are handled for a shared module.

## Problems Identified

### 1. Fix Applied to Consumer First, Not the Source

The bug was patched directly in MDviewer's copy of `release_downloader.py`.
When the MDviewer update ran moments later, it pulled the upstream (still
buggy) version and **overwrote the fix**. The work had to be redone.

### 2. No Upstream-First Workflow

There was no established process directing that fixes should go to
`version-checker-module` before being applied to any consumer project. Each
consumer got patched independently with no coordination.

### 3. No Notification to Other Consumers

The module is used by multiple projects (MDviewer, and potentially SysMon,
HPM, and others). After fixing the module, there was no mechanism to alert
those projects that a bug fix was available. Other consumers may still be
running the broken code.

### 4. No Tagged Releases

The module tracks its version in `version.py` and `CHANGELOG.md`, but there
are no git tags or GitHub Releases. Consumers have no lightweight way to check
whether they're running the latest version of the module.

### 5. No Consumer Registry

There is no record of which projects depend on `version-checker-module`. When
a fix is made, the maintainer has to remember from memory which projects need
updating.

## Proposed Process

### Step 1: File an Issue on the Module Repo

When a bug is discovered in any consumer project, open a GitHub Issue on
`juren53/version-checker-module` -- even if the bug was found in MDviewer or
another downstream project. This creates a public, searchable record.

### Step 2: Fix Upstream First

Always apply the fix to `version-checker-module` first. Test it there. Only
after the fix is committed and pushed to the module repo should it be
propagated to consumers.

**Workflow:**
```
1. Reproduce / confirm the bug
2. Fix in version-checker-module
3. Run module tests
4. Commit and push to version-checker-module
5. Bump version in version.py and CHANGELOG.md
6. Tag the release (see Step 4)
7. Update each consumer project (see Step 5)
```

### Step 3: Bump Version and Update CHANGELOG

Every bug fix gets a patch version bump (e.g., 1.0.0 -> 1.0.1) with a
corresponding `CHANGELOG.md` entry describing the fix. This follows the
existing project convention of semantic versioning.

### Step 4: Tag Releases on GitHub

After bumping the version, create a git tag and GitHub Release:

```bash
git tag v1.0.1
git push origin v1.0.1
gh release create v1.0.1 --title "v1.0.1" --notes "Bug fix: ..."
```

Tagged releases give consumers a concrete reference point and enable the
version checker to detect available updates for the module itself.

### Step 5: Propagate to Consumer Projects

After the fix is released upstream, update each consumer project listed in
`CONSUMERS.md` (see Step 6). For each consumer:

1. Copy the updated module file(s) into the consumer project
2. Test the consumer project
3. Commit with a message referencing the upstream fix, e.g.:
   `Update release_downloader.py from version-checker-module v1.0.1`

### Step 6: Maintain a Consumer Registry

Add a `CONSUMERS.md` file to `version-checker-module` listing every project
that uses the module:

```markdown
# Consumer Projects

Projects that incorporate files from version-checker-module.

| Project   | Repository                            | Files Used                                           |
|-----------|---------------------------------------|------------------------------------------------------|
| MDviewer  | https://github.com/juren53/MDviewer   | github_version_checker.py, release_downloader.py, git_updater.py |
| SysMon    | https://github.com/juren53/SysMon    | github_version_checker.py                            |
| HPM       | https://github.com/juren53/HPM       | github_version_checker.py                            |
```

This makes it clear at a glance what needs updating after any module change.

## Summary

| Step | Action                        | Purpose                                      |
|------|-------------------------------|----------------------------------------------|
| 1    | File issue on module repo     | Public record, tracks the bug                |
| 2    | Fix upstream first            | Single source of truth, prevents overwrites  |
| 3    | Bump version + CHANGELOG      | Consumers can detect they're outdated        |
| 4    | Tag release on GitHub         | Concrete, referenceable release point        |
| 5    | Propagate to consumers        | All downstream projects get the fix          |
| 6    | Maintain consumer registry    | Know who to notify and update                |

## Lesson Learned

Fixing a bug in a consumer before fixing it in the source module risks having
the fix overwritten by the next update. The source module is the single point
of truth -- all fixes flow from there outward to consumers, never the reverse.

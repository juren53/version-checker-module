#!/usr/bin/env python3
"""
Centralized version management for version-checker-module.
Provides semantic versioning and version-related utilities.
"""

__version__ = "1.0.1"
__version_date__ = "2026-02-04 2157"
__version_info__ = (1, 0, 1)


def get_version_string():
    """Get the full version string including date."""
    return f"v{__version__} {__version_date__} CST"


def get_semver():
    """Get just the semantic version number."""
    return __version__


def get_version_tuple():
    """Get version as a tuple for easy comparison."""
    return __version_info__

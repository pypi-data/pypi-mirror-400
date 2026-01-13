#!/usr/bin/env python

"""Tests for `jps_effort_tracker_utils` package."""

from jps_effort_tracker_utils import __author__, __email__, __version__


class TestPackageMetadata:
    """Tests for package metadata."""

    def test_version_exists(self):
        """Test that version is defined."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert __version__ == "0.5.0"

    def test_author_exists(self):
        """Test that author is defined."""
        assert __author__ is not None
        assert isinstance(__author__, str)

    def test_email_exists(self):
        """Test that email is defined."""
        assert __email__ is not None
        assert isinstance(__email__, str)
        assert "@" in __email__

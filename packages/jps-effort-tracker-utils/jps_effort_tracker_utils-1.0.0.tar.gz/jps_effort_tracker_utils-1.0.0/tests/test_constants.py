"""Tests for constants module."""

import logging
import os

from jps_effort_tracker_utils import constants


class TestConstants:
    """Test suite for constants module."""

    def test_default_project_constant(self):
        """Test DEFAULT_PROJECT constant is set correctly."""
        assert constants.DEFAULT_PROJECT == "jps-effort-tracker-utils"

    def test_default_timestamp_format(self):
        """Test DEFAULT_TIMESTAMP has correct date format."""
        # Should be in format YYYY-MM-DD-HHMMSS (17 chars total)
        timestamp = constants.DEFAULT_TIMESTAMP
        assert len(timestamp) == 17
        assert timestamp[4] == "-"
        assert timestamp[7] == "-"
        assert timestamp[10] == "-"

    def test_default_outdir_base_structure(self):
        """Test DEFAULT_OUTDIR_BASE has correct structure."""
        expected_base = os.path.join("/tmp/", os.getenv("USER"), constants.DEFAULT_PROJECT)
        assert constants.DEFAULT_OUTDIR_BASE == expected_base

    def test_default_config_file_exists(self):
        """Test DEFAULT_CONFIG_FILE path is properly constructed."""
        assert "conf/config.yaml" in constants.DEFAULT_CONFIG_FILE
        assert constants.DEFAULT_CONFIG_FILE.endswith(".yaml")

    def test_default_logging_format(self):
        """Test DEFAULT_LOGGING_FORMAT contains required fields."""
        assert "%(levelname)s" in constants.DEFAULT_LOGGING_FORMAT
        assert "%(asctime)s" in constants.DEFAULT_LOGGING_FORMAT
        assert "%(pathname)s" in constants.DEFAULT_LOGGING_FORMAT
        assert "%(lineno)d" in constants.DEFAULT_LOGGING_FORMAT
        assert "%(message)s" in constants.DEFAULT_LOGGING_FORMAT

    def test_default_logging_level(self):
        """Test DEFAULT_LOGGING_LEVEL is set to INFO."""
        assert constants.DEFAULT_LOGGING_LEVEL == logging.INFO

    def test_default_verbose(self):
        """Test DEFAULT_VERBOSE is set to False."""
        assert constants.DEFAULT_VERBOSE is False

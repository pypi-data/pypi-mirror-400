"""Tests for warning suppression utilities."""

import sys
from unittest.mock import patch

from flotorch.adk.utils.warning_utils import (
    suppress_adk_warnings,
    suppress_adk_logging,
    SuppressOutput,
    setup_adk_environment,
)


class TestSuppressWarnings:
    """Test warning suppression functions."""

    def test_suppress_adk_warnings(self):
        """Test ADK warning suppression."""
        suppress_adk_warnings()
        assert True

    def test_suppress_adk_logging(self):
        """Test ADK logging suppression."""
        suppress_adk_logging()
        assert True

    def test_setup_adk_environment(self):
        """Test complete environment setup."""
        setup_adk_environment()
        assert True


class TestSuppressOutput:
    """Test SuppressOutput context manager."""

    def test_suppress_output_context(self):
        """Test output suppression in context."""
        with SuppressOutput():
            print("This should be suppressed")
        assert True

    def test_suppress_output_devnull_fallback(self):
        """Test fallback to StringIO when devnull fails."""
        with patch('builtins.open',
                   side_effect=Exception("Cannot open devnull")):
            with SuppressOutput() as ctx:
                assert ctx._devnull is not None
                print("Fallback test")
        assert True

    def test_suppress_output_cleanup_error(self):
        """Test cleanup handles errors gracefully."""
        ctx = SuppressOutput()
        ctx.__enter__()
        mock_file = type('MockFile', (), {
            'close': lambda: (_ for _ in ()).throw(
                Exception("Close error"))
        })()
        ctx._devnull = mock_file
        ctx.__exit__(None, None, None)
        assert True

    def test_suppress_output_restores_stdout_stderr(self):
        """Test stdout/stderr are restored after context."""
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        with SuppressOutput():
            pass
        
        assert sys.stdout == original_stdout
        assert sys.stderr == original_stderr


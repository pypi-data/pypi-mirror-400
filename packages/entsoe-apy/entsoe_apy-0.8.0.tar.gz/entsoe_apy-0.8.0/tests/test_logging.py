"""Test module for verifying debug logging functionality."""

from unittest.mock import patch

from entsoe.utils.utils import check_date_range_limit, split_date_range


class TestLogging:
    """Test class for logging functionality."""

    def test_utility_functions_have_trace_logging(self):
        """Test that utility functions log TRACE messages for entry/exit."""
        # Test check_date_range_limit
        with patch("entsoe.utils.utils.logger") as mock_logger:
            check_date_range_limit(202301010000, 202301020000, 365)
            assert mock_logger.trace.called
            # Verify that TRACE logging includes function entry/exit
            trace_calls = [call[0][0] for call in mock_logger.trace.call_args_list]
            assert any("check_date_range_limit: Enter" in arg for arg in trace_calls)
            assert any("check_date_range_limit: Exit" in arg for arg in trace_calls)

    def test_utility_functions_have_debug_logging(self):
        """Test that utility functions log DEBUG messages for processing details."""
        # Test check_date_range_limit
        with patch("entsoe.utils.utils.logger") as mock_logger:
            check_date_range_limit(202301010000, 202301020000, 365)
            assert mock_logger.debug.called
            # Verify that DEBUG logging mentions the processing details
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            assert any("Date range spans" in arg for arg in debug_calls)

    def test_split_date_range_logging(self):
        """Test that split_date_range logs TRACE and DEBUG messages."""
        with patch("entsoe.utils.utils.logger") as mock_logger:
            split_date_range(202301010000, 202301050000)
            # Verify TRACE logging for entry/exit
            assert mock_logger.trace.called
            trace_calls = [call[0][0] for call in mock_logger.trace.call_args_list]
            assert any("split_date_range: Enter" in arg for arg in trace_calls)
            assert any("split_date_range: Exit" in arg for arg in trace_calls)
            # Verify DEBUG logging for processing details
            assert mock_logger.debug.called
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            # The function now returns a list of chunks, so logging changed
            assert any(
                "chunks" in arg.lower() or "split" in arg.lower() for arg in debug_calls
            )

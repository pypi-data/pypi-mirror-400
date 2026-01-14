"""Test module for verifying split_date_range decorator functionality."""

from unittest.mock import patch

import entsoe
from entsoe.query.decorators import (
    max_days_limit_ctx,
    offset_increment_ctx,
    split_date_range,
)


class TestSplitDateRangeDecorator:
    """Test class for split_date_range decorator functionality."""

    def test_split_with_only_period_parameters(self):
        """Test that the decorator splits based on periodStart/periodEnd
        when no update parameters are present."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        # Test with a 2-year range (730 days)
        params = {
            "periodStart": 202001010000,  # 2020-01-01 00:00
            "periodEnd": 202201010000,  # 2022-01-01 00:00
        }

        # Set up required context variables and config
        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            result = mock_query(params)

            # Should split into multiple calls
            assert len(result) > 1
            # Each result should have periodStart and periodEnd
            for item in result:
                assert "periodStart" in item
                assert "periodEnd" in item
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

    def test_no_split_when_within_limit_period_only(self):
        """Test that no split occurs when date range is within limit
        using only period parameters."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        # Test with a 6-month range (180 days)
        params = {
            "periodStart": 202001010000,  # 2020-01-01 00:00
            "periodEnd": 202007010000,  # 2020-07-01 00:00
        }

        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            result = mock_query(params)

            # Should not split
            assert len(result) == 1
            assert result[0]["periodStart"] == 202001010000
            assert result[0]["periodEnd"] == 202007010000
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

    def test_split_with_update_parameters(self):
        """Test that the decorator splits based on update parameters
        when both period and update parameters are present."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        # Test with period parameters spanning 2 years but update parameters
        # spanning only 6 months - should not split
        params = {
            "periodStart": 202001010000,  # 2020-01-01 00:00
            "periodEnd": 202201010000,  # 2022-01-01 00:00 (2 years)
            "periodStartUpdate": 202001010000,  # 2020-01-01 00:00
            "periodEndUpdate": 202007010000,  # 2020-07-01 00:00 (6 months)
        }

        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            result = mock_query(params)

            # Should not split because update range is within limit
            assert len(result) == 1
            assert result[0]["periodStart"] == 202001010000
            assert result[0]["periodEnd"] == 202201010000
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

    def test_split_update_parameters_exceed_limit(self):
        """Test that the decorator splits based on update parameters
        when they exceed the limit."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        # Test with update parameters spanning 2 years
        params = {
            "periodStart": 201901010000,  # 2019-01-01 00:00
            "periodEnd": 202301010000,  # 2023-01-01 00:00 (4 years)
            "periodStartUpdate": 202001010000,  # 2020-01-01 00:00
            "periodEndUpdate": 202201010000,  # 2022-01-01 00:00 (2 years)
        }

        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            result = mock_query(params)

            # Should split because update range exceeds limit
            assert len(result) > 1
            # All results should preserve the original period parameters
            for item in result:
                assert item["periodStart"] == 201901010000
                assert item["periodEnd"] == 202301010000
                # But update parameters should be split
                assert "periodStartUpdate" in item
                assert "periodEndUpdate" in item
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

    def test_no_period_parameters(self):
        """Test that the decorator doesn't split when no period parameters
        are present."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        params = {
            "documentType": "A77",
        }

        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            result = mock_query(params)

            # Should not split
            assert len(result) == 1
            assert result[0] == params
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

    def test_logging_for_update_parameters(self):
        """Test that appropriate log messages are generated when using
        update parameters and they exceed the limit."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        params = {
            "periodStart": 201901010000,
            "periodEnd": 202301010000,
            "periodStartUpdate": 202001010000,  # 2020-01-01
            "periodEndUpdate": 202201010000,  # 2022-01-01 (2 years - exceeds limit)
        }

        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            with patch("entsoe.query.decorators.logger") as mock_logger:
                mock_query(params)

                # Verify logging indicates splitting on update parameters
                # Check INFO level for high-level splitting message
                info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
                assert any(
                    "exceeds" in arg
                    and "day limit" in arg
                    and "splitting" in arg.lower()
                    for arg in info_calls
                ), "Should log INFO that the date range is being split"
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

    def test_logging_for_period_parameters(self):
        """Test that appropriate log messages are generated when using
        only period parameters and the range exceeds the limit."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        params = {
            "periodStart": 202001010000,  # 2020-01-01
            "periodEnd": 202201010000,  # 2022-01-01 (2 years - exceeds limit)
        }

        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            with patch("entsoe.query.decorators.logger") as mock_logger:
                mock_query(params)

                # Verify logging indicates splitting on period parameters
                # Check INFO level for high-level splitting message
                info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
                assert any(
                    "exceeds" in arg
                    and "day limit" in arg
                    and "splitting" in arg.lower()
                    for arg in info_calls
                ), "Should log INFO that the date range is being split"
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

    def test_split_preserves_other_params(self):
        """Test that splitting preserves all other parameters."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        params = {
            "periodStart": 202001010000,
            "periodEnd": 202201010000,
            "documentType": "A77",
            "biddingZone_Domain": "10YDE-VE-------2",
            "businessType": "A53",
        }

        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            result = mock_query(params)

            # All results should preserve other parameters
            for item in result:
                assert item["documentType"] == "A77"
                assert item["biddingZone_Domain"] == "10YDE-VE-------2"
                assert item["businessType"] == "A53"
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

    def test_recursive_splitting(self):
        """Test that the decorator can split very large ranges into multiple parts."""

        @split_date_range
        def mock_query(params):
            """Mock query function that returns params for testing."""
            return [params]

        # Test with a 4-year range (should split into at least 4 parts)
        params = {
            "periodStart": 202001010000,  # 2020-01-01 00:00
            "periodEnd": 202401010000,  # 2024-01-01 00:00 (4 years)
        }

        entsoe.set_config()
        max_days_token = max_days_limit_ctx.set(365)
        offset_token = offset_increment_ctx.set(100)
        try:
            result = mock_query(params)

            # Should split into at least 4 parts
            assert len(result) >= 4
        finally:
            max_days_limit_ctx.reset(max_days_token)
            offset_increment_ctx.reset(offset_token)

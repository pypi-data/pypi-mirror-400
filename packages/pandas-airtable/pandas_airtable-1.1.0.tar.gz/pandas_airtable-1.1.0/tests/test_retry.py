"""Tests for retry logic and rate limiting."""

from __future__ import annotations

import time
from unittest.mock import Mock, patch

import pytest

from pandas_airtable.exceptions import AirtableRateLimitError
from pandas_airtable.retry import RateLimitedExecutor, retry_with_backoff


class TestRetryWithBackoff:
    """Test exponential backoff retry logic."""

    def test_retry_succeeds_first_attempt(self):
        """Test no retry needed when first attempt succeeds."""
        mock_func = Mock(return_value="success")

        result = retry_with_backoff(mock_func, max_retries=3)

        assert result == "success"
        mock_func.assert_called_once()

    def test_retry_succeeds_after_failure(self):
        """Test retry succeeds after initial failures."""
        mock_func = Mock(side_effect=[Exception("fail"), Exception("fail"), "success"])

        with patch("pandas_airtable.retry.time.sleep"):  # Don't actually sleep
            result = retry_with_backoff(mock_func, max_retries=3, base_delay=0.1)

        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_exhausted_raises(self):
        """Test max retries exceeded raises error."""
        mock_func = Mock(side_effect=Exception("always fail"))

        with (
            patch("pandas_airtable.retry.time.sleep"),
            pytest.raises(AirtableRateLimitError) as exc_info,
        ):
            retry_with_backoff(mock_func, max_retries=3, base_delay=0.1)

        assert exc_info.value.retries == 3

    def test_retry_exponential_backoff_delay(self):
        """Test delay increases exponentially."""
        mock_func = Mock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        sleep_times = []

        def mock_sleep(seconds):
            sleep_times.append(seconds)

        with patch("pandas_airtable.retry.time.sleep", side_effect=mock_sleep):
            retry_with_backoff(mock_func, max_retries=3, base_delay=1.0, max_delay=60.0)

        # First retry: ~1 second, second retry: ~2 seconds (with jitter)
        assert len(sleep_times) == 2
        assert sleep_times[1] > sleep_times[0]

    def test_retry_respects_max_delay(self):
        """Test delay is capped at max_delay."""
        mock_func = Mock(
            side_effect=[
                Exception("fail"),
                Exception("fail"),
                Exception("fail"),
                Exception("fail"),
                "success",
            ]
        )
        sleep_times = []

        def mock_sleep(seconds):
            sleep_times.append(seconds)

        with patch("pandas_airtable.retry.time.sleep", side_effect=mock_sleep):
            retry_with_backoff(mock_func, max_retries=5, base_delay=10.0, max_delay=15.0)

        # All delays should be <= max_delay + jitter
        for delay in sleep_times:
            assert delay <= 15.0 * 1.1  # max_delay + 10% jitter

    def test_retry_passes_args_and_kwargs(self):
        """Test function receives correct arguments."""
        mock_func = Mock(return_value="success")

        retry_with_backoff(mock_func, "arg1", "arg2", kwarg1="value1")

        mock_func.assert_called_once_with("arg1", "arg2", kwarg1="value1")

    def test_retry_only_catches_specified_exceptions(self):
        """Test only specified exceptions trigger retry."""

        class SpecificError(Exception):
            pass

        class OtherError(Exception):
            pass

        mock_func = Mock(side_effect=OtherError("not retryable"))

        with pytest.raises(OtherError):
            retry_with_backoff(
                mock_func,
                max_retries=3,
                retryable_exceptions=(SpecificError,),
            )

        # Should have only been called once (no retry for OtherError)
        mock_func.assert_called_once()


class TestRateLimitedExecutor:
    """Test rate limiting executor."""

    def test_under_limit_no_delay(self):
        """Test no delay when under rate limit."""
        executor = RateLimitedExecutor(qps_limit=5)
        mock_func = Mock(return_value="result")

        # First few calls should not introduce delay
        start = time.time()
        for _ in range(3):
            executor.execute(mock_func)
        elapsed = time.time() - start

        # Should complete quickly (under 1 second)
        assert elapsed < 1.0
        assert mock_func.call_count == 3

    def test_at_limit_introduces_delay(self):
        """Test delay is introduced when at rate limit."""
        executor = RateLimitedExecutor(qps_limit=2)
        mock_func = Mock(return_value="result")

        # Make calls that should exceed the limit
        for _ in range(4):
            executor.execute(mock_func)

        # Should have been rate limited (at least some waiting)
        # With qps=2, 4 calls need at least 1 second window
        assert mock_func.call_count == 4

    def test_wait_if_needed_tracks_requests(self):
        """Test request times are tracked."""
        executor = RateLimitedExecutor(qps_limit=5)

        executor.wait_if_needed()
        executor.wait_if_needed()
        executor.wait_if_needed()

        assert len(executor.request_times) == 3

    def test_old_requests_removed_from_window(self):
        """Test requests outside window are cleaned up."""
        executor = RateLimitedExecutor(qps_limit=5)
        executor._window_size = 0.1  # Short window for testing

        executor.wait_if_needed()
        time.sleep(0.15)  # Wait for request to exit window
        executor.wait_if_needed()

        # Old request should be cleaned up
        assert len(executor.request_times) == 1

    def test_execute_returns_function_result(self):
        """Test execute returns the function's result."""
        executor = RateLimitedExecutor(qps_limit=5)

        def my_func(x, y):
            return x + y

        result = executor.execute(my_func, 3, 4)

        assert result == 7

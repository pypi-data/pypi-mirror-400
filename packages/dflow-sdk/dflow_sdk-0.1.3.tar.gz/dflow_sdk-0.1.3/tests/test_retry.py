"""Tests for retry utilities."""

import pytest

from dflow.utils.http import DFlowApiError
from dflow.utils.retry import (
    create_retryable,
    default_should_retry,
    with_retry,
)


class TestDefaultShouldRetry:
    """Tests for default_should_retry function."""

    def test_retry_on_rate_limit(self):
        """Test retry on 429 rate limit."""
        error = DFlowApiError("Rate limited", 429)
        assert default_should_retry(error, 0) is True

    def test_retry_on_server_error(self):
        """Test retry on 5xx server errors."""
        error = DFlowApiError("Server error", 500)
        assert default_should_retry(error, 0) is True
        
        error = DFlowApiError("Bad gateway", 502)
        assert default_should_retry(error, 0) is True

    def test_no_retry_on_client_error(self):
        """Test no retry on 4xx client errors (except 429)."""
        error = DFlowApiError("Not found", 404)
        assert default_should_retry(error, 0) is False
        
        error = DFlowApiError("Bad request", 400)
        assert default_should_retry(error, 0) is False

    def test_retry_on_connection_error(self):
        """Test retry on connection errors."""
        error = ConnectionError("Connection refused")
        assert default_should_retry(error, 0) is True

    def test_retry_on_timeout(self):
        """Test retry on timeout errors."""
        error = TimeoutError("Request timed out")
        assert default_should_retry(error, 0) is True

    def test_no_retry_on_unknown_error(self):
        """Test no retry on unknown errors."""
        error = ValueError("Unknown error")
        assert default_should_retry(error, 0) is False


class TestWithRetry:
    """Tests for with_retry function."""

    def test_success_no_retry(self):
        """Test successful call doesn't retry."""
        call_count = 0
        
        def success_fn():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = with_retry(success_fn)
        assert result == "success"
        assert call_count == 1

    def test_retry_on_failure(self):
        """Test retry on retryable failure."""
        call_count = 0
        
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise DFlowApiError("Rate limited", 429)
            return "success"
        
        result = with_retry(fail_then_succeed, max_retries=3)
        assert result == "success"
        assert call_count == 3

    def test_exhausted_retries(self):
        """Test error raised when retries exhausted."""
        def always_fail():
            raise DFlowApiError("Rate limited", 429)
        
        with pytest.raises(DFlowApiError) as exc_info:
            with_retry(always_fail, max_retries=2, initial_delay_ms=10)
        
        assert exc_info.value.status_code == 429

    def test_no_retry_on_non_retryable_error(self):
        """Test no retry on non-retryable errors."""
        call_count = 0
        
        def fail_with_404():
            nonlocal call_count
            call_count += 1
            raise DFlowApiError("Not found", 404)
        
        with pytest.raises(DFlowApiError):
            with_retry(fail_with_404, max_retries=3)
        
        # Should only be called once (no retries for 404)
        assert call_count == 1

    def test_custom_should_retry(self):
        """Test custom should_retry function."""
        call_count = 0
        
        def custom_should_retry(error, attempt):
            return attempt < 2  # Retry up to 2 times
        
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("Custom error")
        
        with pytest.raises(ValueError):
            with_retry(
                always_fail,
                max_retries=5,
                initial_delay_ms=10,
                should_retry=custom_should_retry,
            )
        
        # Should try 3 times (initial + 2 retries)
        assert call_count == 3


class TestCreateRetryable:
    """Tests for create_retryable function."""

    def test_create_retryable_wrapper(self):
        """Test creating retryable wrapper."""
        def add(a: int, b: int) -> int:
            return a + b
        
        retryable_add = create_retryable(add)
        result = retryable_add(2, 3)
        assert result == 5

    def test_retryable_wrapper_retries(self):
        """Test retryable wrapper retries on failure."""
        call_count = 0
        
        def fail_twice(x: int) -> int:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise DFlowApiError("Rate limited", 429)
            return x * 2
        
        retryable_fn = create_retryable(fail_twice, initial_delay_ms=10)
        result = retryable_fn(5)
        
        assert result == 10
        assert call_count == 3

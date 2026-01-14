"""Tests for djb.core.retry retry utilities.

Tests cover:
- RetryExhausted: Exception for exhausted retry attempts
- RetryAttempt: Dataclass with attempt info and sleep method
- calculate_delay: Exponential backoff calculation with jitter
- retry_attempts: Generator yielding retry attempts
- retry: Decorator for automatic function retry
- retry_context: Context manager for manual retry loops
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from djb.core.exceptions import DjbError
from djb.core.retry import (
    RetryAttempt,
    RetryExhausted,
    calculate_delay,
    retry,
    retry_attempts,
    retry_context,
)


class TestRetryExhausted:
    """Tests for RetryExhausted exception."""

    def test_message_format_without_last_exception(self) -> None:
        """RetryExhausted should format message with attempts count."""
        exc = RetryExhausted(3)
        assert str(exc) == "All 3 retry attempts failed"

    def test_message_format_with_last_exception(self) -> None:
        """RetryExhausted should include last exception in message."""
        last_exc = ValueError("connection refused")
        exc = RetryExhausted(3, last_exc)
        assert str(exc) == "All 3 retry attempts failed: connection refused"

    def test_stores_attempts_attribute(self) -> None:
        """RetryExhausted should store attempts count."""
        exc = RetryExhausted(5)
        assert exc.attempts == 5

    def test_stores_last_exception_attribute(self) -> None:
        """RetryExhausted should store last exception."""
        last_exc = ValueError("test error")
        exc = RetryExhausted(3, last_exc)
        assert exc.last_exception is last_exc

    def test_last_exception_defaults_to_none(self) -> None:
        """RetryExhausted should default last_exception to None."""
        exc = RetryExhausted(3)
        assert exc.last_exception is None

    def test_inherits_from_djb_error(self) -> None:
        """RetryExhausted should inherit from DjbError."""
        assert issubclass(RetryExhausted, DjbError)


class TestRetryAttempt:
    """Tests for RetryAttempt dataclass."""

    def test_is_last_true_on_final_attempt(self) -> None:
        """is_last should return True when on last attempt."""
        attempt = RetryAttempt(number=3, max_attempts=3, delay=1.0)
        assert attempt.is_last is True

    def test_is_last_true_when_exceeds_max(self) -> None:
        """is_last should return True when number exceeds max_attempts."""
        attempt = RetryAttempt(number=5, max_attempts=3, delay=1.0)
        assert attempt.is_last is True

    def test_is_last_false_when_not_final(self) -> None:
        """is_last should return False when not on last attempt."""
        attempt = RetryAttempt(number=1, max_attempts=3, delay=1.0)
        assert attempt.is_last is False

    def test_sleep_calls_time_sleep(self) -> None:
        """sleep should call time.sleep with delay."""
        attempt = RetryAttempt(number=1, max_attempts=3, delay=2.5)
        with patch("djb.core.retry.time.sleep") as mock_sleep:
            attempt.sleep()
            mock_sleep.assert_called_once_with(2.5)

    def test_sleep_does_not_sleep_when_last(self) -> None:
        """sleep should not sleep when is_last is True."""
        attempt = RetryAttempt(number=3, max_attempts=3, delay=2.5)
        with patch("djb.core.retry.time.sleep") as mock_sleep:
            attempt.sleep()
            mock_sleep.assert_not_called()

    def test_sleep_does_not_sleep_when_delay_zero(self) -> None:
        """sleep should not sleep when delay is 0."""
        attempt = RetryAttempt(number=1, max_attempts=3, delay=0)
        with patch("djb.core.retry.time.sleep") as mock_sleep:
            attempt.sleep()
            mock_sleep.assert_not_called()


class TestCalculateDelay:
    """Tests for calculate_delay function."""

    def test_exponential_backoff_formula(self) -> None:
        """calculate_delay should use exponential backoff formula."""
        # delay = initial_delay * (backoff_factor ** attempt)
        # attempt 0: 1.0 * (2.0 ** 0) = 1.0
        delay = calculate_delay(
            attempt=0, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=False
        )
        assert delay == 1.0

        # attempt 1: 1.0 * (2.0 ** 1) = 2.0
        delay = calculate_delay(
            attempt=1, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=False
        )
        assert delay == 2.0

        # attempt 2: 1.0 * (2.0 ** 2) = 4.0
        delay = calculate_delay(
            attempt=2, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=False
        )
        assert delay == 4.0

    def test_max_delay_capping(self) -> None:
        """calculate_delay should cap delay at max_delay."""
        # attempt 10: 1.0 * (2.0 ** 10) = 1024.0, capped to 60.0
        delay = calculate_delay(
            attempt=10, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=False
        )
        assert delay == 60.0

    def test_jitter_adds_up_to_50_percent(self) -> None:
        """calculate_delay should add 0-50% jitter when enabled."""
        with patch("djb.core.retry.random.random", return_value=0.5):
            # delay = 1.0 * (1 + 0.5 * 0.5) = 1.0 * 1.25 = 1.25
            delay = calculate_delay(
                attempt=0, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=True
            )
            assert delay == 1.25

    def test_jitter_max_value(self) -> None:
        """calculate_delay should add up to 50% when random returns 1.0."""
        with patch("djb.core.retry.random.random", return_value=1.0):
            # delay = 1.0 * (1 + 1.0 * 0.5) = 1.0 * 1.5 = 1.5
            delay = calculate_delay(
                attempt=0, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=True
            )
            assert delay == 1.5

    def test_jitter_min_value(self) -> None:
        """calculate_delay should add 0% when random returns 0.0."""
        with patch("djb.core.retry.random.random", return_value=0.0):
            delay = calculate_delay(
                attempt=0, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=True
            )
            assert delay == 1.0

    def test_zero_initial_delay(self) -> None:
        """calculate_delay should handle zero initial delay."""
        delay = calculate_delay(
            attempt=5, initial_delay=0.0, backoff_factor=2.0, max_delay=60.0, jitter=False
        )
        assert delay == 0.0


class TestRetryAttempts:
    """Tests for retry_attempts generator."""

    def test_yields_correct_number_of_attempts(self) -> None:
        """retry_attempts should yield max_attempts RetryAttempt objects."""
        attempts = list(retry_attempts(max_attempts=5, jitter=False))
        assert len(attempts) == 5

    def test_attempt_numbers_are_one_indexed(self) -> None:
        """retry_attempts should yield 1-indexed attempt numbers."""
        attempts = list(retry_attempts(max_attempts=3, jitter=False))
        assert [a.number for a in attempts] == [1, 2, 3]

    def test_all_attempts_have_correct_max_attempts(self) -> None:
        """retry_attempts should set max_attempts on all attempts."""
        attempts = list(retry_attempts(max_attempts=3, jitter=False))
        assert all(a.max_attempts == 3 for a in attempts)

    def test_delays_calculated_correctly(self) -> None:
        """retry_attempts should calculate exponential delays."""
        attempts = list(
            retry_attempts(
                max_attempts=3, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=False
            )
        )
        assert [a.delay for a in attempts] == [1.0, 2.0, 4.0]

    def test_generator_can_exit_early(self) -> None:
        """retry_attempts should support early exit with break."""
        count = 0
        for attempt in retry_attempts(max_attempts=10, jitter=False):
            count += 1
            if attempt.number == 2:
                break
        assert count == 2

    def test_last_attempt_is_last(self) -> None:
        """retry_attempts should mark last attempt as is_last."""
        attempts = list(retry_attempts(max_attempts=3, jitter=False))
        assert not attempts[0].is_last
        assert not attempts[1].is_last
        assert attempts[2].is_last


class TestRetryDecorator:
    """Tests for retry decorator."""

    def test_success_on_first_attempt(self) -> None:
        """retry should return result on first successful attempt."""

        @retry(max_attempts=3, jitter=False)
        def always_succeeds() -> str:
            return "success"

        assert always_succeeds() == "success"

    def test_retries_and_succeeds(self) -> None:
        """retry should retry on exception and return success."""
        call_count = 0

        @retry(max_attempts=3, initial_delay=0.0, jitter=False)
        def fails_then_succeeds() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "success"

        with patch("djb.core.retry.time.sleep"):
            result = fails_then_succeeds()

        assert result == "success"
        assert call_count == 3

    def test_raises_retry_exhausted_after_max_attempts(self) -> None:
        """retry should raise RetryExhausted when all attempts fail."""

        @retry(max_attempts=3, initial_delay=0.0, jitter=False)
        def always_fails() -> str:
            raise ValueError("always fails")

        with patch("djb.core.retry.time.sleep"):
            with pytest.raises(RetryExhausted) as exc_info:
                always_fails()

        assert exc_info.value.attempts == 3

    def test_retry_exhausted_contains_last_exception(self) -> None:
        """RetryExhausted should contain the last exception."""
        original_error = ValueError("final failure")

        @retry(max_attempts=2, initial_delay=0.0, jitter=False)
        def always_fails() -> str:
            raise original_error

        with patch("djb.core.retry.time.sleep"):
            with pytest.raises(RetryExhausted) as exc_info:
                always_fails()

        assert exc_info.value.last_exception is original_error

    def test_only_catches_specified_exceptions(self) -> None:
        """retry should only catch specified exception types."""

        @retry(max_attempts=3, exceptions=(ValueError,), jitter=False)
        def raises_type_error() -> str:
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            raises_type_error()

    def test_catches_multiple_exception_types(self) -> None:
        """retry should catch multiple specified exception types."""
        call_count = 0

        @retry(max_attempts=3, initial_delay=0.0, exceptions=(ValueError, TypeError), jitter=False)
        def raises_different_errors() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("first")
            if call_count == 2:
                raise TypeError("second")
            return "success"

        with patch("djb.core.retry.time.sleep"):
            result = raises_different_errors()

        assert result == "success"
        assert call_count == 3

    def test_preserves_function_metadata(self) -> None:
        """retry should preserve function name and docstring."""

        @retry(max_attempts=3)
        def documented_function() -> str:
            """This is the docstring."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is the docstring."

    def test_works_with_args_and_kwargs(self) -> None:
        """retry should pass args and kwargs to decorated function."""

        @retry(max_attempts=3, jitter=False)
        def with_args(a: int, b: str, c: bool = False) -> tuple[int, str, bool]:
            return (a, b, c)

        result = with_args(1, "two", c=True)
        assert result == (1, "two", True)

    def test_sleeps_between_attempts(self) -> None:
        """retry should sleep between failed attempts."""
        call_count = 0

        @retry(max_attempts=3, initial_delay=1.0, backoff_factor=2.0, jitter=False)
        def fails_twice() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "success"

        with patch("djb.core.retry.time.sleep") as mock_sleep:
            fails_twice()

        # Should sleep twice (after attempt 1 and 2)
        assert mock_sleep.call_count == 2
        # First sleep: 1.0 * (2.0 ** 0) = 1.0
        # Second sleep: 1.0 * (2.0 ** 1) = 2.0
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)


class TestRetryContext:
    """Tests for retry_context context manager."""

    def test_attempt_returns_true_while_attempts_remain(self) -> None:
        """attempt() should return True while attempts remain."""
        attempts_made = 0
        with patch("djb.core.retry.time.sleep"):
            with retry_context(max_attempts=3, jitter=False) as attempt:
                while attempt():
                    attempts_made += 1
                    if attempts_made == 3:
                        break

        assert attempts_made == 3

    def test_attempt_returns_false_when_exhausted(self) -> None:
        """attempt() should return False when all attempts exhausted."""
        attempts_made = 0
        with patch("djb.core.retry.time.sleep"):
            with retry_context(max_attempts=3, jitter=False) as attempt:
                while attempt():
                    attempts_made += 1

        assert attempts_made == 3

    def test_sleeps_between_attempts(self) -> None:
        """retry_context should sleep between attempts."""
        with patch("djb.core.retry.time.sleep") as mock_sleep:
            with retry_context(
                max_attempts=3, initial_delay=1.0, backoff_factor=2.0, jitter=False
            ) as attempt:
                count = 0
                while attempt():
                    count += 1

        # Should sleep after first and second attempt (before second and third call to attempt())
        assert mock_sleep.call_count == 2

    def test_no_sleep_on_first_attempt(self) -> None:
        """retry_context should not sleep before first attempt."""
        with patch("djb.core.retry.time.sleep") as mock_sleep:
            with retry_context(max_attempts=3, initial_delay=1.0, jitter=False) as attempt:
                attempt()  # First call should not sleep
                break_out = True
                if break_out:
                    pass  # Exit early

        # No sleep should have occurred since we only made one attempt
        mock_sleep.assert_not_called()

    def test_works_with_early_break(self) -> None:
        """retry_context should work with early break on success."""
        call_count = 0
        with patch("djb.core.retry.time.sleep"):
            with retry_context(max_attempts=5, jitter=False) as attempt:
                while attempt():
                    call_count += 1
                    if call_count == 2:
                        break  # Simulate success on second attempt

        assert call_count == 2

    def test_manual_retry_pattern(self) -> None:
        """retry_context should work with typical try/except pattern."""
        attempts = 0
        result = None
        mock_operation = MagicMock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])

        with patch("djb.core.retry.time.sleep"):
            with retry_context(max_attempts=3, jitter=False) as attempt:
                while attempt():
                    attempts += 1
                    try:
                        result = mock_operation()
                        break
                    except ValueError:
                        pass  # Will retry

        assert attempts == 3
        assert result == "success"

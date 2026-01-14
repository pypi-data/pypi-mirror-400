"""Tests for djb.config.prompting module; interactive prompting functions."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from djb.config.prompting import PromptResult, confirm, prompt


class TestPromptResult:
    """Tests for PromptResult dataclass."""

    def test_creation_with_user_source(self):
        """PromptResult can be created with user source."""
        result = PromptResult(value="test-value", source="user", attempts=1)

        assert result.value == "test-value"
        assert result.source == "user"
        assert result.attempts == 1

    def test_creation_with_default_source(self):
        """PromptResult can be created with default source."""
        result = PromptResult(value="default-value", source="default", attempts=1)

        assert result.value == "default-value"
        assert result.source == "default"
        assert result.attempts == 1

    def test_creation_with_cancelled_source(self):
        """PromptResult can be created with cancelled source."""
        result = PromptResult(value=None, source="cancelled", attempts=3)

        assert result.value is None
        assert result.source == "cancelled"
        assert result.attempts == 3


class TestPrompt:
    """Tests for prompt() function."""

    def test_returns_user_input(self):
        """Prompt returns user input with 'user' source."""
        with patch("builtins.input", return_value="test-value"):
            result = prompt("Enter value")

        assert result.value == "test-value"
        assert result.source == "user"
        assert result.attempts == 1

    def test_returns_default_on_empty_input(self):
        """Prompt returns default when user enters nothing."""
        with patch("builtins.input", return_value=""):
            result = prompt("Enter value", default="default-value")

        assert result.value == "default-value"
        assert result.source == "default"
        assert result.attempts == 1

    def test_strips_whitespace(self):
        """Prompt strips whitespace from input."""
        with patch("builtins.input", return_value="  test-value  "):
            result = prompt("Enter value")

        assert result.value == "test-value"

    def test_raises_keyboard_interrupt_on_ctrl_c(self):
        """Prompt raises KeyboardInterrupt on Ctrl+C."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                prompt("Enter value")

    def test_raises_keyboard_interrupt_on_eof(self):
        """Prompt raises KeyboardInterrupt on EOFError (Ctrl+D)."""
        with patch("builtins.input", side_effect=EOFError):
            with pytest.raises(KeyboardInterrupt):
                prompt("Enter value")

    def test_prompt_with_default_formatting(self):
        """Prompt displays default value in brackets."""
        with patch("builtins.input", return_value="user-value") as mock_input:
            prompt("Enter value", default="default-value")

        # Check the prompt string includes default in brackets
        mock_input.assert_called_once()
        prompt_text = mock_input.call_args[0][0]
        assert "Enter value [default-value]:" in prompt_text

    def test_prompt_without_default_formatting(self):
        """Prompt without default doesn't show brackets."""
        with patch("builtins.input", return_value="user-value") as mock_input:
            prompt("Enter value")

        mock_input.assert_called_once()
        prompt_text = mock_input.call_args[0][0]
        assert prompt_text == "Enter value: "

    def test_validator_accepts_valid_input(self):
        """Prompt accepts input that passes validator."""
        validator = lambda x: x.startswith("valid-")

        with patch("builtins.input", return_value="valid-input"):
            result = prompt("Enter value", validator=validator)

        assert result.value == "valid-input"
        assert result.source == "user"

    def test_validator_retries_on_invalid_input(self):
        """Prompt retries when validator fails."""
        validator = lambda x: x.startswith("valid-")
        inputs = iter(["invalid", "valid-input"])

        with patch("builtins.input", side_effect=lambda _: next(inputs)):
            result = prompt("Enter value", validator=validator, max_retries=3)

        assert result.value == "valid-input"
        assert result.attempts == 2

    def test_validator_exhausts_retries(self):
        """Prompt returns cancelled when validator fails all retries."""
        validator = lambda x: False  # Always fails

        with patch("builtins.input", return_value="invalid"):
            result = prompt("Enter value", validator=validator, max_retries=3)

        assert result.value is None
        assert result.source == "cancelled"
        assert result.attempts == 3

    def test_normalizer_transforms_input(self):
        """Prompt applies normalizer to input."""
        normalizer = lambda x: x.lower()

        with patch("builtins.input", return_value="TEST-VALUE"):
            result = prompt("Enter value", normalizer=normalizer)

        assert result.value == "test-value"

    def test_normalizer_none_triggers_retry(self):
        """Prompt retries when normalizer returns None."""
        # First input gets None from normalizer, second is valid
        normalize_calls = [0]

        def normalizer(x: str) -> str | None:
            normalize_calls[0] += 1
            if normalize_calls[0] == 1:
                return None  # Invalid
            return x.lower()

        inputs = iter(["invalid", "valid"])

        with patch("builtins.input", side_effect=lambda _: next(inputs)):
            result = prompt("Enter value", normalizer=normalizer, max_retries=3)

        assert result.value == "valid"
        assert result.attempts == 2

    def test_normalizer_runs_before_validator(self):
        """Applies normalizer before validator."""
        normalizer = lambda x: x.lower()
        validator = lambda x: x == "test"  # Expects lowercase

        with patch("builtins.input", return_value="TEST"):
            result = prompt(
                "Enter value",
                normalizer=normalizer,
                validator=validator,
            )

        assert result.value == "test"

    def test_validation_hint_shown_when_normalizer_returns_none(self):
        """validation_hint is shown when normalizer returns None."""
        # Normalizer returns None on first input, valid on second
        normalize_calls = [0]

        def normalizer(x: str) -> str | None:
            normalize_calls[0] += 1
            if normalize_calls[0] == 1:
                return None  # Invalid - triggers retry with hint
            return x.lower()

        inputs = iter(["invalid_format", "valid"])

        with (
            patch("builtins.input", side_effect=lambda _: next(inputs)),
            patch("djb.config.prompting.logger") as mock_logger,
        ):
            result = prompt(
                "Enter value",
                normalizer=normalizer,
                validation_hint="expected: valid format",
                max_retries=3,
            )

        # Check that warning was called with hint when normalizer returned None
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "expected: valid format" in warning_call
        assert result.value == "valid"

    def test_validation_hint_shown_on_failure(self):
        """validation_hint is shown when validation fails."""
        validator = lambda x: x == "valid"
        inputs = iter(["invalid", "valid"])

        with (
            patch("builtins.input", side_effect=lambda _: next(inputs)),
            patch("djb.config.prompting.logger") as mock_logger,
        ):
            prompt(
                "Enter value",
                validator=validator,
                validation_hint="expected: valid",
                max_retries=3,
            )

        # Check that warning was called with hint
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "expected: valid" in warning_call

    def test_empty_input_without_default_retries(self):
        """Empty input without default triggers retry."""
        inputs = iter(["", "", "finally"])

        with patch("builtins.input", side_effect=lambda _: next(inputs)):
            result = prompt("Enter value", max_retries=3)

        assert result.value == "finally"
        assert result.attempts == 3

    def test_empty_input_without_default_exhausts_retries(self):
        """Empty input without default exhausts retries."""
        with patch("builtins.input", return_value=""):
            result = prompt("Enter value", max_retries=2)

        assert result.value is None
        assert result.source == "cancelled"
        assert result.attempts == 2


class TestConfirm:
    """Tests for confirm() function."""

    def test_yes_returns_true(self):
        """confirm returns True for 'y' input."""
        with patch("builtins.input", return_value="y"):
            result = confirm("Proceed?")

        assert result is True

    def test_yes_full_returns_true(self):
        """confirm returns True for 'yes' input."""
        with patch("builtins.input", return_value="yes"):
            result = confirm("Proceed?")

        assert result is True

    def test_yes_case_insensitive(self):
        """confirm is case insensitive."""
        with patch("builtins.input", return_value="Y"):
            result = confirm("Proceed?")

        assert result is True

        with patch("builtins.input", return_value="YES"):
            result = confirm("Proceed?")

        assert result is True

    def test_no_returns_false(self):
        """confirm returns False for 'n' input."""
        with patch("builtins.input", return_value="n"):
            result = confirm("Proceed?")

        assert result is False

    def test_anything_else_returns_false(self):
        """confirm returns False for any non-yes input."""
        with patch("builtins.input", return_value="maybe"):
            result = confirm("Proceed?")

        assert result is False

    def test_empty_returns_default_true(self):
        """confirm returns default True on empty input."""
        with patch("builtins.input", return_value=""):
            result = confirm("Proceed?", default=True)

        assert result is True

    def test_empty_returns_default_false(self):
        """confirm returns default False on empty input."""
        with patch("builtins.input", return_value=""):
            result = confirm("Proceed?", default=False)

        assert result is False

    def test_shows_yn_suffix_default_true(self):
        """confirm shows [Y/n] when default is True."""
        with patch("builtins.input", return_value="y") as mock_input:
            confirm("Proceed?", default=True)

        prompt_text = mock_input.call_args[0][0]
        assert "[Y/n]" in prompt_text

    def test_shows_yn_suffix_default_false(self):
        """confirm shows [y/N] when default is False."""
        with patch("builtins.input", return_value="y") as mock_input:
            confirm("Proceed?", default=False)

        prompt_text = mock_input.call_args[0][0]
        assert "[y/N]" in prompt_text

    def test_raises_keyboard_interrupt_on_ctrl_c(self):
        """confirm raises KeyboardInterrupt on Ctrl+C."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                confirm("Proceed?")

    def test_raises_keyboard_interrupt_on_eof(self):
        """confirm raises KeyboardInterrupt on EOFError (Ctrl+D)."""
        with patch("builtins.input", side_effect=EOFError):
            with pytest.raises(KeyboardInterrupt):
                confirm("Proceed?")

    def test_strips_whitespace(self):
        """confirm strips whitespace from input."""
        with patch("builtins.input", return_value="  y  "):
            result = confirm("Proceed?")

        assert result is True

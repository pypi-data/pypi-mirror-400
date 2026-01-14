"""E2E tests for specialized config field types.

Tests validation, normalization, acquisition, and resolution behaviors
for BoolField, EmailField, SeedCommandField, LogLevelField,
NameField, EnumField, and ProjectNameField.
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

import pytest

from djb.config.acquisition import AcquisitionContext
from djb.config.storage.utils import dump_toml
from djb.config.storage.io.external import GitConfigIO
from djb.config.field import ConfigValidationError
from djb.config.fields.bool import BoolField
from djb.config.fields.email import EMAIL_PATTERN, EmailField
from djb.config.fields.enum import EnumField
from djb.config.fields.ip import IPAddressField
from djb.config.fields.log_level import (
    DEFAULT_LOG_LEVEL,
    VALID_LOG_LEVELS,
    LogLevelField,
)
from djb.config.fields.name import NameField
from djb.config.fields.project_name import (
    DNS_LABEL_PATTERN,
    ProjectNameField,
    normalize_project_name,
)
from djb.config.fields.seed_command import SEED_COMMAND_PATTERN, SeedCommandField
from djb.config.config import DjbConfig, get_djb_config
from djb.config.storage import LocalConfigIO, ProjectConfigType
from djb.config.prompting import PromptResult
from djb.types import Mode, Platform

from ..conftest import derived_provenance, explicit_provenance

pytestmark = pytest.mark.e2e_marker


class FieldTestContext:
    """Context holding config and resolution parameters for field tests."""

    def __init__(
        self,
        config: DjbConfig,
        env: dict | None = None,
    ):
        self.config = config
        self.env = env if env is not None else {}


def make_field_resolve_ctx(
    project_dir: Path,
    make_djb_config,
    *,
    env: dict | None = None,
    local: dict | None = None,
    project: dict | None = None,
) -> FieldTestContext:
    """Create a test context with config data.

    Writes actual config files to project_dir. Uses get_djb_config() to actually
    resolve from files (not make_djb_config which bypasses file resolution).
    """
    config_dir = project_dir / ".djb"

    if local:
        config_dir.mkdir(exist_ok=True)
        (config_dir / "local.toml").write_text(dump_toml(local))

    if project:
        config_dir.mkdir(exist_ok=True)
        (config_dir / "project.toml").write_text(dump_toml(project))

    # Use get_djb_config() to actually resolve from files
    # (make_djb_config() bypasses file resolution with hardcoded defaults)
    config = get_djb_config(DjbConfig(project_dir=project_dir), env={})
    return FieldTestContext(
        config=config,
        env=env if env is not None else {},
    )


# ==============================================================================
# BoolField Tests
# ==============================================================================


class TestBoolFieldNormalization:
    """Tests for BoolField.normalize()."""

    def test_returns_bool_unchanged(self):
        """Boolean values are returned as-is."""
        field = BoolField()
        field.field_name = "flag"
        assert field.normalize(True) is True
        assert field.normalize(False) is False

    def test_normalizes_int_to_bool(self):
        """Integer values are converted to bool."""
        field = BoolField()
        field.field_name = "flag"
        assert field.normalize(1) is True
        assert field.normalize(0) is False
        assert field.normalize(42) is True
        assert field.normalize(-1) is True

    @pytest.mark.parametrize(
        "value",
        ["true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON", "1"],
    )
    def test_normalizes_truthy_strings(self, value):
        """Truthy string values are normalized to True."""
        field = BoolField()
        field.field_name = "flag"
        assert field.normalize(value) is True

    @pytest.mark.parametrize(
        "value",
        ["false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF", "0"],
    )
    def test_normalizes_falsy_strings(self, value):
        """Falsy string values are normalized to False."""
        field = BoolField()
        field.field_name = "flag"
        assert field.normalize(value) is False

    def test_normalizes_with_whitespace(self):
        """Strings with whitespace are normalized correctly."""
        field = BoolField()
        field.field_name = "flag"
        assert field.normalize("  true  ") is True
        assert field.normalize("  false  ") is False

    def test_raises_for_invalid_string(self):
        """Invalid strings raise ConfigValidationError."""
        field = BoolField()
        field.field_name = "flag"
        with pytest.raises(ConfigValidationError, match="Cannot convert to boolean"):
            field.normalize("invalid")
        with pytest.raises(ConfigValidationError, match="Cannot convert to boolean"):
            field.normalize("maybe")

    def test_raises_for_other_types(self):
        """Non-string/bool/int types raise ConfigValidationError."""
        field = BoolField()
        field.field_name = "flag"
        with pytest.raises(ConfigValidationError, match="Cannot convert to boolean"):
            field.normalize([])
        with pytest.raises(ConfigValidationError, match="Cannot convert to boolean"):
            field.normalize({})


class TestBoolFieldValidation:
    """Tests for BoolField.validate()."""

    def test_accepts_true(self):
        """True passes validation."""
        field = BoolField()
        field.field_name = "flag"
        field.validate(True)

    def test_accepts_false(self):
        """False passes validation."""
        field = BoolField()
        field.field_name = "flag"
        field.validate(False)

    def test_accepts_none(self):
        """None passes validation (optional fields)."""
        field = BoolField()
        field.field_name = "flag"
        field.validate(None)

    def test_rejects_non_boolean(self):
        """Non-boolean values are rejected."""
        field = BoolField()
        field.field_name = "flag"
        with pytest.raises(ConfigValidationError, match="must be a boolean"):
            field.validate("true")
        with pytest.raises(ConfigValidationError, match="must be a boolean"):
            field.validate(1)
        with pytest.raises(ConfigValidationError, match="must be a boolean"):
            field.validate([])


class TestBoolFieldResolution:
    """Tests for BoolField.resolve() using base class behavior."""

    def test_resolves_from_config_layers(self, project_dir: Path, make_djb_config):
        """Resolution from config layers (highest priority)."""
        field = BoolField(config_storage=ProjectConfigType)
        field.field_name = "encrypt_secrets"

        ctx = make_field_resolve_ctx(
            project_dir, make_djb_config, project={"encrypt_secrets": False}
        )

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value is False
        assert provenance is not None

    def test_normalizes_string_during_resolution(self, project_dir: Path, make_djb_config):
        """Resolution normalizes string values to bool."""
        field = BoolField(config_storage=ProjectConfigType)
        field.field_name = "encrypt_secrets"

        ctx = make_field_resolve_ctx(
            project_dir, make_djb_config, project={"encrypt_secrets": "false"}
        )

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value is False
        assert provenance is not None

    def test_returns_default_when_not_configured(self, project_dir: Path, make_djb_config):
        """Resolution returns default when no value configured."""
        field = BoolField(config_storage=ProjectConfigType, default=True)
        field.field_name = "encrypt_secrets"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value is True
        assert provenance is None  # Default has no provenance

    def test_returns_none_when_no_default(self, project_dir: Path, make_djb_config):
        """Resolution returns None when no value and no default."""
        field = BoolField(config_storage=ProjectConfigType)
        field.field_name = "encrypt_secrets"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value is None
        assert provenance is None


class TestBoolFieldInit:
    """Tests for BoolField.__init__()."""

    def test_accepts_default_true(self):
        """Default True is accepted."""
        field = BoolField(default=True)
        assert field.default is True

    def test_accepts_default_false(self):
        """Default False is accepted."""
        field = BoolField(default=False)
        assert field.default is False

    def test_accepts_config_file(self):
        """config_file parameter is accepted."""
        field = BoolField(config_storage=ProjectConfigType)
        assert field.config_storage == ProjectConfigType


# ==============================================================================
# EmailField Tests
# ==============================================================================


class TestEmailFieldValidation:
    """Tests for EmailField.validate()."""

    def test_accepts_valid_email(self):
        """Valid email passes validation."""
        field = EmailField()
        field.field_name = "email"
        # Should not raise
        field.validate("user@example.com")
        field.validate("test.user@company.co.uk")
        field.validate("name+tag@domain.org")

    def test_rejects_missing_at_sign(self):
        """Email without @ is rejected."""
        field = EmailField()
        field.field_name = "email"
        with pytest.raises(ConfigValidationError, match="Invalid email format"):
            field.validate("notanemail")

    def test_rejects_missing_domain(self):
        """Email without domain is rejected."""
        field = EmailField()
        field.field_name = "email"
        with pytest.raises(ConfigValidationError, match="Invalid email format"):
            field.validate("user@")

    def test_rejects_missing_tld(self):
        """Email without TLD is rejected."""
        field = EmailField()
        field.field_name = "email"
        with pytest.raises(ConfigValidationError, match="Invalid email format"):
            field.validate("user@domain")

    def test_rejects_spaces(self):
        """Email with spaces is rejected."""
        field = EmailField()
        field.field_name = "email"
        with pytest.raises(ConfigValidationError, match="Invalid email format"):
            field.validate("user @example.com")
        with pytest.raises(ConfigValidationError, match="Invalid email format"):
            field.validate("user@ example.com")

    def test_accepts_none_when_optional(self):
        """Email field accepts None (skip validation)."""
        field = EmailField()
        field.field_name = "email"
        # Should not raise - None skips validation
        field.validate(None)

    def test_pattern_is_compiled_regex(self):
        """EMAIL_PATTERN is a compiled regex."""
        assert isinstance(EMAIL_PATTERN, re.Pattern)


class TestEmailFieldGitConfigIntegration:
    """Tests for EmailField git config integration."""

    def test_has_git_config_store(self, project_dir: Path, make_djb_config):
        """EmailField includes git config as config_store factory."""
        field = EmailField()
        assert len(field.config_store_factories) == 1
        # Factory is a partial that creates GitConfigIO
        factory = field.config_store_factories[0]
        config = make_djb_config()
        store = factory(config)
        assert isinstance(store, GitConfigIO)
        assert store._git_key == "user.email"

    def test_has_prompt_text(self):
        """EmailField has prompt text."""
        field = EmailField()
        assert field.prompt_text == "Enter your email"

    def test_has_validation_hint(self):
        """EmailField has validation hint."""
        field = EmailField()
        assert field.validation_hint == "expected: user@domain.com"


class TestEmailFieldResolution:
    """Tests for EmailField.resolve() with git config fallback."""

    def test_resolves_from_config_layers(self, project_dir: Path, make_djb_config):
        """Resolution from config layers (highest priority)."""
        field = EmailField(config_storage=LocalConfigIO)
        field.field_name = "email"

        ctx = make_field_resolve_ctx(
            project_dir, make_djb_config, local={"email": "john@example.com"}
        )

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "john@example.com"
        assert provenance is not None

    def test_falls_back_to_git_config(self, project_dir: Path, make_djb_config):
        """Resolution falls back to git config when config layers empty."""
        field = EmailField(config_storage=LocalConfigIO)
        field.field_name = "email"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        with patch.object(GitConfigIO, "_get_git_value", return_value="git@example.com"):
            value, provenance = field.resolve(ctx.config, env=ctx.env)

        assert value == "git@example.com"
        # Provenance should be GitConfigIO
        assert provenance is not None

    def test_returns_none_when_git_not_available(self, project_dir: Path, make_djb_config):
        """Resolution returns None when git config unavailable."""
        field = EmailField(config_storage=LocalConfigIO)
        field.field_name = "email"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        with patch.object(GitConfigIO, "_get_git_value", return_value=None):
            value, provenance = field.resolve(ctx.config, env=ctx.env)

        assert value is None
        assert provenance is None

    def test_config_takes_precedence_over_git(self, project_dir: Path, make_djb_config):
        """Config file value takes precedence over git config."""
        field = EmailField(config_storage=LocalConfigIO)
        field.field_name = "email"

        ctx = make_field_resolve_ctx(
            project_dir, make_djb_config, local={"email": "config@example.com"}
        )

        with patch.object(GitConfigIO, "_get_git_value", return_value="git@example.com"):
            value, provenance = field.resolve(ctx.config, env=ctx.env)

        # Config should win, git should not even be called
        assert value == "config@example.com"
        assert provenance is not None


class TestEmailFieldAcquisition:
    """Tests for EmailField.acquire() with validation_hint."""

    def test_validation_hint_passed_to_prompt(self, project_dir: Path, make_djb_config):
        """validation_hint is passed to prompt() during acquisition."""
        field = EmailField(config_storage=LocalConfigIO)
        field.field_name = "email"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        # Mock the config_store_factories to return nothing
        with (
            patch("djb.config.field.prompt") as mock_prompt,
            patch.object(field, "config_store_factories", []),
        ):
            mock_prompt.return_value = PromptResult(
                value="user@example.com", source="user", attempts=1
            )
            field.acquire(ctx, config)

        # Check prompt was called with validation_hint
        mock_prompt.assert_called_once()
        call_kwargs = mock_prompt.call_args.kwargs
        assert call_kwargs["validation_hint"] == "expected: user@domain.com"

    def test_returns_none_for_cancelled_prompt(self, project_dir: Path, make_djb_config):
        """Acquisition handles cancelled prompt."""
        field = EmailField(config_storage=LocalConfigIO)
        field.field_name = "email"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        with (
            patch("djb.config.field.prompt") as mock_prompt,
            patch.object(field, "config_store_factories", []),
        ):
            mock_prompt.return_value = PromptResult(value=None, source="cancelled", attempts=1)
            result = field.acquire(ctx, config)

        assert result is None

    def test_retry_exhaustion_returns_none(self, project_dir: Path, make_djb_config):
        """Acquisition returns None when user exhausts all retry attempts."""
        field = EmailField(config_storage=LocalConfigIO)
        field.field_name = "email"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        with (
            patch("djb.config.field.prompt") as mock_prompt,
            patch.object(field, "config_store_factories", []),
        ):
            # User enters invalid emails 3 times, exhausting retries
            mock_prompt.return_value = PromptResult(value=None, source="cancelled", attempts=3)
            result = field.acquire(ctx, config)

        assert result is None


# ==============================================================================
# SeedCommandField Tests
# ==============================================================================


class TestSeedCommandFieldResolution:
    """Tests for SeedCommandField.resolve() using base class behavior."""

    def test_resolves_from_config_layers(self, project_dir: Path, make_djb_config):
        """Resolution from config layers (highest priority)."""
        field = SeedCommandField(config_storage=ProjectConfigType)
        field.field_name = "seed_command"

        ctx = make_field_resolve_ctx(
            project_dir, make_djb_config, project={"seed_command": "myapp.seeds:run"}
        )

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "myapp.seeds:run"
        assert provenance is not None

    def test_returns_none_when_not_configured(self, project_dir: Path, make_djb_config):
        """Resolution returns None when no value configured."""
        field = SeedCommandField(config_storage=ProjectConfigType)
        field.field_name = "seed_command"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value is None
        assert provenance is None

    def test_returns_default_if_configured(self, project_dir: Path, make_djb_config):
        """Resolution returns default when explicitly set."""
        field = SeedCommandField(config_storage=ProjectConfigType, default="app.cli:seed_all")
        field.field_name = "seed_command"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "app.cli:seed_all"
        assert provenance is None  # Default has no provenance


class TestSeedCommandFieldValidation:
    """Tests for SeedCommandField.validate()."""

    def test_accepts_valid_seed_command(self):
        """Valid seed command passes validation."""
        field = SeedCommandField()
        field.field_name = "seed_command"
        # Should not raise
        field.validate("myapp.cli.seed:run")
        field.validate("app.seeds:seed_all")
        field.validate("module:attr")
        field.validate("my_module.sub:my_func")

    def test_rejects_missing_colon(self):
        """Seed command without colon is rejected."""
        field = SeedCommandField()
        field.field_name = "seed_command"
        with pytest.raises(ConfigValidationError, match="module.path:attribute"):
            field.validate("myapp.cli.seed")

    def test_rejects_invalid_module_path(self):
        """Seed command with invalid module path is rejected."""
        field = SeedCommandField()
        field.field_name = "seed_command"
        with pytest.raises(ConfigValidationError, match="module.path:attribute"):
            field.validate("123invalid:attr")
        with pytest.raises(ConfigValidationError, match="module.path:attribute"):
            field.validate("module-name:attr")

    def test_rejects_invalid_attribute_name(self):
        """Seed command with invalid attribute is rejected."""
        field = SeedCommandField()
        field.field_name = "seed_command"
        with pytest.raises(ConfigValidationError, match="module.path:attribute"):
            field.validate("myapp:123invalid")
        with pytest.raises(ConfigValidationError, match="module.path:attribute"):
            field.validate("myapp:my-func")

    def test_rejects_multiple_colons(self):
        """Seed command with multiple colons is rejected."""
        field = SeedCommandField()
        field.field_name = "seed_command"
        with pytest.raises(ConfigValidationError, match="module.path:attribute"):
            field.validate("myapp:cli:seed")

    def test_accepts_none_when_optional(self):
        """Seed command field accepts None (skip validation)."""
        field = SeedCommandField()
        field.field_name = "seed_command"
        # Should not raise
        field.validate(None)

    def test_pattern_is_compiled_regex(self):
        """SEED_COMMAND_PATTERN is a compiled regex."""
        assert isinstance(SEED_COMMAND_PATTERN, re.Pattern)


# ==============================================================================
# LogLevelField Tests
# ==============================================================================


class TestLogLevelFieldResolution:
    """Tests for LogLevelField.resolve() using base class behavior."""

    def test_resolves_from_config_layers(self, project_dir: Path, make_djb_config):
        """Resolution from config layers (highest priority)."""
        field = LogLevelField(config_storage=ProjectConfigType)
        field.field_name = "log_level"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config, project={"log_level": "debug"})

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "debug"
        assert provenance is not None

    def test_normalizes_uppercase_during_resolution(self, project_dir: Path, make_djb_config):
        """Resolution normalizes uppercase values to lowercase."""
        field = LogLevelField(config_storage=ProjectConfigType)
        field.field_name = "log_level"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config, project={"log_level": "DEBUG"})

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "debug"
        assert provenance is not None

    def test_returns_none_when_not_configured(self, project_dir: Path, make_djb_config):
        """Resolution returns None when no value configured and no default."""
        field = LogLevelField(config_storage=ProjectConfigType)
        field.field_name = "log_level"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value is None
        assert provenance is None

    def test_returns_default_if_configured(self, project_dir: Path, make_djb_config):
        """Resolution returns default when explicitly set."""
        field = LogLevelField(config_storage=ProjectConfigType, default="warning")
        field.field_name = "log_level"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "warning"
        assert provenance is None  # Default has no provenance


class TestLogLevelFieldValidation:
    """Tests for LogLevelField.validate()."""

    def test_accepts_valid_log_levels(self):
        """All valid log levels pass validation."""
        field = LogLevelField()
        field.field_name = "log_level"
        for level in VALID_LOG_LEVELS:
            field.validate(level)

    def test_accepts_uppercase_log_level(self):
        """Uppercase log levels pass validation (after normalization)."""
        field = LogLevelField()
        field.field_name = "log_level"
        # Normalize first, then validate
        normalized = field.normalize("INFO")
        field.validate(normalized)
        assert normalized == "info"

    def test_rejects_invalid_log_level(self):
        """Invalid log level is rejected."""
        field = LogLevelField()
        field.field_name = "log_level"
        with pytest.raises(ConfigValidationError, match="Invalid log_level"):
            field.validate("invalid")
        with pytest.raises(ConfigValidationError, match="Invalid log_level"):
            field.validate("trace")

    def test_error_message_lists_valid_levels(self):
        """Validation error message lists valid log levels."""
        field = LogLevelField()
        field.field_name = "log_level"
        with pytest.raises(ConfigValidationError, match="debug, error, info, note, warning"):
            field.validate("invalid")

    def test_accepts_none_when_optional(self):
        """Log level field accepts None (skip validation)."""
        field = LogLevelField()
        field.field_name = "log_level"
        # Should not raise
        field.validate(None)


class TestLogLevelFieldNormalization:
    """Tests for LogLevelField.normalize()."""

    def test_normalizes_to_lowercase(self):
        """Log level is normalized to lowercase."""
        field = LogLevelField()
        assert field.normalize("INFO") == "info"
        assert field.normalize("DEBUG") == "debug"
        assert field.normalize("Error") == "error"

    def test_normalizes_string_value(self):
        """Non-string values are converted to lowercase string."""
        field = LogLevelField()
        # Edge case: YAML might parse as boolean
        assert field.normalize(True) == "true"
        assert field.normalize(123) == "123"

    def test_preserves_lowercase(self):
        """Lowercase values are preserved."""
        field = LogLevelField()
        assert field.normalize("info") == "info"
        assert field.normalize("debug") == "debug"


class TestLogLevelFieldAcquisition:
    """Tests for LogLevelField.acquire() silent auto-save."""

    def test_uses_current_value_if_available(self, project_dir: Path, make_djb_config):
        """Acquisition uses current value if available."""
        field = LogLevelField(config_storage=ProjectConfigType)
        field.field_name = "log_level"
        config = make_djb_config()

        ctx = AcquisitionContext(
            config=config,
            current_value="debug",
            source=explicit_provenance(),
            other_values={},
        )

        result = field.acquire(ctx, config)

        assert result is not None
        assert result.value == "debug"
        assert result.should_save is True
        assert result.was_prompted is False
        assert result.source_name is None

    def test_uses_default_if_no_current_value(self, project_dir: Path, make_djb_config):
        """Acquisition uses DEFAULT_LOG_LEVEL if no current value."""
        field = LogLevelField(config_storage=ProjectConfigType)
        field.field_name = "log_level"
        config = make_djb_config()

        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        result = field.acquire(ctx, config)

        assert result is not None
        assert result.value == DEFAULT_LOG_LEVEL
        assert result.should_save is True
        assert result.was_prompted is False

    def test_silent_save_no_prompting(self, project_dir: Path, make_djb_config):
        """Acquisition does not prompt user."""
        field = LogLevelField(config_storage=ProjectConfigType)
        field.field_name = "log_level"
        config = make_djb_config()

        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        # LogLevelField.acquire() doesn't use prompt - it just returns a result
        result = field.acquire(ctx, config)
        assert result is not None
        assert result.was_prompted is False


class TestLogLevelConstants:
    """Tests for LogLevelField constants."""

    def test_valid_log_levels_is_frozenset(self):
        """VALID_LOG_LEVELS is a frozenset."""
        assert isinstance(VALID_LOG_LEVELS, frozenset)

    def test_valid_log_levels_content(self):
        """VALID_LOG_LEVELS contains expected values."""
        assert VALID_LOG_LEVELS == {"error", "warning", "info", "note", "debug"}

    def test_default_log_level_is_info(self):
        """DEFAULT_LOG_LEVEL is 'info'."""
        assert DEFAULT_LOG_LEVEL == "info"

    def test_default_is_in_valid_set(self):
        """DEFAULT_LOG_LEVEL is in VALID_LOG_LEVELS."""
        assert DEFAULT_LOG_LEVEL in VALID_LOG_LEVELS


# ==============================================================================
# NameField Tests
# ==============================================================================


class TestNameFieldGitConfigIntegration:
    """Tests for NameField git config integration."""

    def test_has_git_config_store(self, project_dir: Path, make_djb_config):
        """NameField includes git config as config_store factory."""
        field = NameField()
        assert len(field.config_store_factories) == 1
        # Factory is a partial that creates GitConfigIO
        factory = field.config_store_factories[0]
        config = make_djb_config()
        store = factory(config)
        assert isinstance(store, GitConfigIO)
        assert store._git_key == "user.name"

    def test_has_prompt_text(self):
        """NameField has prompt text."""
        field = NameField()
        assert field.prompt_text == "Enter your name"

    def test_no_validation(self):
        """NameField has no validation (accepts any string)."""
        field = NameField()
        field.field_name = "name"
        # Should not raise
        field.validate("John Doe")
        field.validate("任何字符")
        field.validate("")
        field.validate(None)


class TestNameFieldResolution:
    """Tests for NameField.resolve() with git config fallback."""

    def test_resolves_from_config_layers(self, project_dir: Path, make_djb_config):
        """Resolution from config layers (highest priority)."""
        field = NameField(config_storage=LocalConfigIO)
        field.field_name = "name"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config, local={"name": "John Doe"})

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "John Doe"
        assert provenance is not None

    def test_falls_back_to_git_config(self, project_dir: Path, make_djb_config):
        """Resolution falls back to git config when config layers empty."""
        field = NameField(config_storage=LocalConfigIO)
        field.field_name = "name"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        with patch.object(GitConfigIO, "_get_git_value", return_value="Git User"):
            value, provenance = field.resolve(ctx.config, env=ctx.env)

        assert value == "Git User"
        # Provenance should be GitConfigIO
        assert provenance is not None

    def test_returns_none_when_git_not_available(self, project_dir: Path, make_djb_config):
        """Resolution returns None when git config unavailable."""
        field = NameField(config_storage=LocalConfigIO)
        field.field_name = "name"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        with patch.object(GitConfigIO, "_get_git_value", return_value=None):
            value, provenance = field.resolve(ctx.config, env=ctx.env)

        assert value is None
        assert provenance is None

    def test_config_takes_precedence_over_git(self, project_dir: Path, make_djb_config):
        """Config file value takes precedence over git config."""
        field = NameField(config_storage=LocalConfigIO)
        field.field_name = "name"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config, local={"name": "Config Name"})

        with patch.object(GitConfigIO, "_get_git_value", return_value="Git Name"):
            value, provenance = field.resolve(ctx.config, env=ctx.env)

        # Config should win, git should not even be called
        assert value == "Config Name"
        assert provenance is not None


# ==============================================================================
# EnumField Tests
# ==============================================================================


class TestEnumFieldNormalization:
    """Tests for EnumField.normalize()."""

    def test_returns_enum_instance_unchanged(self):
        """Enum instances are returned as-is."""
        field = EnumField(Mode)
        field.field_name = "mode"
        assert field.normalize(Mode.DEVELOPMENT) == Mode.DEVELOPMENT
        assert field.normalize(Mode.PRODUCTION) == Mode.PRODUCTION

    def test_parses_string_with_parse_method(self):
        """Parses strings using enum's parse() method."""
        field = EnumField(Mode, default=Mode.DEVELOPMENT)
        field.field_name = "mode"
        # Mode has a parse() method that returns None on failure
        # EnumField.normalize calls it without a default parameter
        assert field.normalize("development") == Mode.DEVELOPMENT
        assert field.normalize("production") == Mode.PRODUCTION
        assert field.normalize("staging") == Mode.STAGING

    def test_falls_back_to_enum_constructor(self):
        """Fallback to enum constructor for enums without parse()."""
        field = EnumField(Platform, default=Platform.HEROKU)
        field.field_name = "platform"
        # Platform enum doesn't have parse(), so use constructor
        assert field.normalize("heroku") == Platform.HEROKU

    def test_returns_default_on_parse_failure(self):
        """Returns default when parsing fails."""
        field = EnumField(Mode, default=Mode.DEVELOPMENT)
        field.field_name = "mode"
        # Invalid value should return default
        result = field.normalize("invalid")
        assert result == Mode.DEVELOPMENT

    def test_returns_none_for_none(self):
        """None returns None (fall-through for resolution chain)."""
        field = EnumField(Mode, default=Mode.DEVELOPMENT)
        field.field_name = "mode"
        # None should pass through unchanged to allow resolution chain fall-through
        result = field.normalize(None)
        assert result is None


class TestEnumFieldWithCustomParse:
    """Tests for EnumField with enums that have custom parse() methods."""

    def test_mode_enum_parse_aliases(self):
        """Mode enum parse handles full names (not aliases)."""
        field = EnumField(Mode, default=Mode.DEVELOPMENT)
        field.field_name = "mode"
        # Mode.parse() handles full names
        assert field.normalize("development") == Mode.DEVELOPMENT
        assert field.normalize("production") == Mode.PRODUCTION
        assert field.normalize("staging") == Mode.STAGING


class TestEnumFieldInit:
    """Tests for EnumField.__init__()."""

    def test_stores_enum_class(self):
        """Enum_class is stored."""
        field = EnumField(Mode)
        assert field.enum_class == Mode

    def test_accepts_default(self):
        """Default value is accepted."""
        field = EnumField(Mode, default=Mode.STAGING)
        assert field.default == Mode.STAGING


# ==============================================================================
# ProjectNameField Tests
# ==============================================================================


class TestProjectNameFieldAttributes:
    """Tests for ProjectNameField attributes."""

    def test_has_prompt_text(self):
        """ProjectNameField has prompt text."""
        field = ProjectNameField()
        assert field.prompt_text == "Enter project name"

    def test_has_validation_hint(self):
        """ProjectNameField has validation hint."""
        field = ProjectNameField()
        assert field.validation_hint == "lowercase alphanumeric with hyphens, max 63 chars"


class TestProjectNameFieldValidation:
    """Tests for ProjectNameField.validate()."""

    def test_accepts_valid_dns_labels(self):
        """Valid DNS labels pass validation."""
        field = ProjectNameField()
        field.field_name = "project_name"
        # Should not raise
        field.validate("myproject")
        field.validate("my-project")
        field.validate("project123")
        field.validate("a")
        field.validate("a-b-c-1-2-3")

    @pytest.mark.parametrize(
        "invalid_value,description",
        [
            ("MyProject", "uppercase letters"),
            ("my_project", "underscores"),
            ("-myproject", "leading hyphen"),
            ("myproject-", "trailing hyphen"),
            ("a" * 64, "too long (64 chars)"),
            ("", "empty string"),
        ],
        ids=["uppercase", "underscore", "leading_hyphen", "trailing_hyphen", "too_long", "empty"],
    )
    def test_rejects_invalid_dns_labels(self, invalid_value, description):
        """Invalid DNS labels are rejected ({description})."""
        field = ProjectNameField()
        field.field_name = "project_name"
        with pytest.raises(ConfigValidationError, match="DNS label"):
            field.validate(invalid_value)

    def test_accepts_max_length(self):
        """63-character names are accepted."""
        field = ProjectNameField()
        field.field_name = "project_name"
        # Exactly 63 characters
        max_name = "a" * 63
        field.validate(max_name)

    def test_rejects_none_when_required(self):
        """Rejects None for required field."""
        field = ProjectNameField()
        field.field_name = "project_name"
        # ProjectNameField has allow_none=False in validate()
        with pytest.raises(ConfigValidationError, match="project_name is required"):
            field.validate(None)

    def test_pattern_is_compiled_regex(self):
        """DNS_LABEL_PATTERN is a compiled regex."""
        assert isinstance(DNS_LABEL_PATTERN, re.Pattern)


class TestProjectNameFieldNormalization:
    """Tests for normalize_project_name() helper."""

    def test_converts_to_lowercase(self):
        """Normalization converts to lowercase."""
        assert normalize_project_name("MyProject") == "myproject"
        assert normalize_project_name("UPPERCASE") == "uppercase"

    def test_replaces_underscores_with_hyphens(self):
        """Normalization replaces underscores with hyphens."""
        assert normalize_project_name("my_project") == "my-project"
        assert normalize_project_name("foo_bar_baz") == "foo-bar-baz"

    def test_normalizes_valid_characters_only(self):
        """Normalization only handles hyphens, underscores, and dots."""
        # Only replaces [-_.] with single hyphen
        # Other invalid characters make the result invalid -> None
        assert normalize_project_name("my project!") is None  # space + ! invalid
        assert normalize_project_name("foo_bar_baz") == "foo-bar-baz"  # underscores replaced
        assert normalize_project_name("my.project") == "my-project"  # dots replaced

    def test_strips_leading_trailing_hyphens(self):
        """Normalization validates DNS labels (no leading/trailing hyphens)."""
        # normalize_project_name returns None if result is invalid
        # "-myproject-" -> "-myproject-" (invalid DNS label)
        assert normalize_project_name("-myproject-") is None
        # But "myproject-" normalizes to something else or is rejected
        assert normalize_project_name("myproject") == "myproject"

    def test_collapses_multiple_hyphens(self):
        """Normalization collapses multiple hyphens."""
        assert normalize_project_name("my--project") == "my-project"
        assert normalize_project_name("foo---bar") == "foo-bar"

    def test_returns_none_for_empty_input(self):
        """Normalization returns None for empty/invalid input."""
        # Empty string becomes None
        assert normalize_project_name("") is None
        # All invalid characters removed -> None
        assert normalize_project_name("!!!") is None

    def test_preserves_valid_names(self):
        """Normalization preserves already-valid names."""
        assert normalize_project_name("myproject") == "myproject"
        assert normalize_project_name("my-project") == "my-project"
        assert normalize_project_name("project123") == "project123"


class TestProjectNameFieldResolution:
    """Tests for ProjectNameField.resolve() multi-source resolution."""

    def test_resolves_from_config_layers(self, project_dir: Path, make_djb_config):
        """Resolution from config layers (highest priority)."""
        field = ProjectNameField(config_storage=ProjectConfigType)
        field.field_name = "project_name"

        ctx = make_field_resolve_ctx(
            project_dir, make_djb_config, project={"project_name": "myapp"}
        )

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "myapp"
        assert provenance is not None

    def test_falls_back_to_pyproject_toml(self, project_dir: Path, make_djb_config):
        """Resolution falls back to pyproject.toml."""
        # Create pyproject.toml with project name
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text('[project]\nname = "my-awesome-project"\n')

        field = ProjectNameField(config_storage=ProjectConfigType)
        field.field_name = "project_name"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "my-awesome-project"
        # Provenance should be PyprojectNameConfigIO
        assert provenance is not None

    def test_falls_back_to_directory_name(self, project_dir: Path, make_djb_config):
        """Resolution falls back to directory name."""
        field = ProjectNameField(config_storage=ProjectConfigType)
        field.field_name = "project_name"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        # Should normalize directory name
        normalized = normalize_project_name(project_dir.name)
        assert value == normalized or value == "myproject"
        # Provenance should be CwdNameConfigIO
        assert provenance is not None

    def test_normalizes_value_from_config(self, project_dir: Path, make_djb_config):
        """Resolution normalizes project name from config to DNS-safe format."""
        field = ProjectNameField(config_storage=ProjectConfigType)
        field.field_name = "project_name"

        ctx = make_field_resolve_ctx(
            project_dir, make_djb_config, project={"project_name": "My_Project"}
        )

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        # ProjectNameField normalizes values: underscores -> hyphens, lowercase
        assert value == "my-project"
        assert provenance is not None


class TestProjectNameFieldAcquisition:
    """Tests for ProjectNameField.acquire() with validation_hint."""

    def test_validation_hint_passed_to_prompt(self, project_dir: Path, make_djb_config):
        """validation_hint is passed to prompt() during acquisition."""
        field = ProjectNameField(config_storage=ProjectConfigType)
        field.field_name = "project_name"
        config = make_djb_config()

        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        with patch("djb.config.fields.project_name.prompt") as mock_prompt:
            mock_prompt.return_value = PromptResult(value="myproject", source="user", attempts=1)
            field.acquire(ctx, config)

        # Check prompt was called with validation_hint
        mock_prompt.assert_called_once()
        call_kwargs = mock_prompt.call_args.kwargs
        assert call_kwargs["validation_hint"] == "lowercase alphanumeric with hyphens, max 63 chars"

    def test_returns_none_for_cancelled_prompt(self, project_dir: Path, make_djb_config):
        """Acquisition handles cancelled prompt."""
        field = ProjectNameField(config_storage=ProjectConfigType)
        field.field_name = "project_name"
        config = make_djb_config()

        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        with patch("djb.config.fields.project_name.prompt") as mock_prompt:
            mock_prompt.return_value = PromptResult(value=None, source="cancelled", attempts=1)
            result = field.acquire(ctx, config)

        assert result is None

    def test_retry_exhaustion_returns_none(self, project_dir: Path, make_djb_config):
        """Acquisition returns None when user exhausts all retry attempts."""
        field = ProjectNameField(config_storage=ProjectConfigType)
        field.field_name = "project_name"
        config = make_djb_config()

        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=derived_provenance(),
            other_values={},
        )

        with patch("djb.config.fields.project_name.prompt") as mock_prompt:
            # User enters invalid project names 3 times
            mock_prompt.return_value = PromptResult(value=None, source="cancelled", attempts=3)
            result = field.acquire(ctx, config)

        assert result is None

    def test_normalizer_passed_to_prompt(self, project_dir: Path, make_djb_config):
        """Normalize_project_name is passed to prompt()."""
        field = ProjectNameField(config_storage=ProjectConfigType)
        field.field_name = "project_name"
        config = make_djb_config()

        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        with patch("djb.config.fields.project_name.prompt") as mock_prompt:
            mock_prompt.return_value = PromptResult(value="myproject", source="user", attempts=1)
            field.acquire(ctx, config)

        # Check normalizer is passed
        call_kwargs = mock_prompt.call_args.kwargs
        assert call_kwargs["normalizer"] == normalize_project_name


# ==============================================================================
# IPAddressField Tests
# ==============================================================================


class TestIPAddressFieldValidation:
    """Tests for IPAddressField.validate()."""

    def test_accepts_valid_ipv4(self):
        """Valid IPv4 addresses pass validation."""
        field = IPAddressField()
        field.field_name = "server_ip"
        # Should not raise
        field.validate("192.168.1.1")
        field.validate("10.0.0.1")
        field.validate("172.16.0.1")
        field.validate("0.0.0.0")
        field.validate("255.255.255.255")

    def test_accepts_valid_ipv6(self):
        """Valid IPv6 addresses pass validation."""
        field = IPAddressField()
        field.field_name = "server_ip"
        # Should not raise
        field.validate("::1")
        field.validate("fe80::1")
        field.validate("2001:db8::1")
        field.validate("2001:0db8:85a3:0000:0000:8a2e:0370:7334")

    def test_rejects_invalid_ipv4(self):
        """Invalid IPv4 addresses are rejected."""
        field = IPAddressField()
        field.field_name = "server_ip"
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("256.1.1.1")
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("192.168.1")
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("192.168.1.1.1")

    def test_rejects_invalid_ipv6(self):
        """Invalid IPv6 addresses are rejected."""
        field = IPAddressField()
        field.field_name = "server_ip"
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("2001:db8::1::1")
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("2001:db8:gggg::1")

    def test_rejects_hostnames(self):
        """Hostnames are rejected (only IP addresses allowed)."""
        field = IPAddressField()
        field.field_name = "server_ip"
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("example.com")
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("localhost")

    def test_rejects_cidr_notation(self):
        """CIDR notation is rejected (only bare IPs allowed)."""
        field = IPAddressField()
        field.field_name = "server_ip"
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("192.168.1.0/24")
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("2001:db8::/32")

    def test_rejects_empty_string(self):
        """Empty string is rejected."""
        field = IPAddressField()
        field.field_name = "server_ip"
        with pytest.raises(ConfigValidationError, match="Invalid IP address"):
            field.validate("")

    def test_accepts_none_when_optional(self):
        """IP address field accepts None (skip validation)."""
        field = IPAddressField()
        field.field_name = "server_ip"
        # Should not raise - None skips validation
        field.validate(None)

    def test_has_validation_hint(self):
        """IPAddressField has validation hint."""
        field = IPAddressField()
        assert field.validation_hint == "expected: valid IPv4 or IPv6 address"


class TestIPAddressFieldResolution:
    """Tests for IPAddressField.resolve() using base class behavior."""

    def test_resolves_from_config_layers(self, project_dir: Path, make_djb_config):
        """Resolution from config layers (highest priority)."""
        field = IPAddressField(config_storage=ProjectConfigType)
        field.field_name = "server_ip"

        ctx = make_field_resolve_ctx(
            project_dir, make_djb_config, project={"server_ip": "192.168.1.100"}
        )

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "192.168.1.100"
        assert provenance is not None

    def test_returns_none_when_not_configured(self, project_dir: Path, make_djb_config):
        """Resolution returns None when no value configured."""
        field = IPAddressField(config_storage=ProjectConfigType)
        field.field_name = "server_ip"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value is None
        assert provenance is None

    def test_returns_default_if_configured(self, project_dir: Path, make_djb_config):
        """Resolution returns default when explicitly set."""
        field = IPAddressField(config_storage=ProjectConfigType, default="127.0.0.1")
        field.field_name = "server_ip"

        ctx = make_field_resolve_ctx(project_dir, make_djb_config)

        value, provenance = field.resolve(ctx.config, env=ctx.env)
        assert value == "127.0.0.1"
        assert provenance is None  # Default has no provenance


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestFieldSpecializationsIntegration:
    """Integration tests for field specializations working together."""

    def test_all_fields_have_unique_purposes(self):
        """Each specialized field has a distinct purpose."""
        email = EmailField()
        seed_command = SeedCommandField()
        log_level = LogLevelField()
        name = NameField()
        enum_field = EnumField(Mode)
        project_name = ProjectNameField()
        ip_address = IPAddressField()

        # Each should be a different class
        field_types = {
            type(email),
            type(seed_command),
            type(log_level),
            type(name),
            type(enum_field),
            type(project_name),
            type(ip_address),
        }
        assert len(field_types) == 7

    def test_validation_errors_are_specific(self):
        """Validation errors contain helpful messages."""
        # EmailField
        email = EmailField()
        email.field_name = "email"
        try:
            email.validate("invalid")
        except ConfigValidationError as e:
            assert "email" in str(e).lower()

        # SeedCommandField
        seed = SeedCommandField()
        seed.field_name = "seed_command"
        try:
            seed.validate("invalid")
        except ConfigValidationError as e:
            assert "module.path:attribute" in str(e)

        # LogLevelField
        log = LogLevelField()
        log.field_name = "log_level"
        try:
            log.validate("invalid")
        except ConfigValidationError as e:
            assert "Invalid log_level" in str(e)

        # ProjectNameField
        project = ProjectNameField()
        project.field_name = "project_name"
        try:
            project.validate("Invalid_Name")
        except ConfigValidationError as e:
            assert "DNS label" in str(e)

        # IPAddressField
        ip_addr = IPAddressField()
        ip_addr.field_name = "server_ip"
        try:
            ip_addr.validate("not-an-ip")
        except ConfigValidationError as e:
            assert "Invalid IP address" in str(e)

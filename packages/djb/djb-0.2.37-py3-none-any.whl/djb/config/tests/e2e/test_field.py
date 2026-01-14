"""Tests for djb.config.field module - ConfigFieldABC and StringField."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.e2e_marker

from djb.config.acquisition import AcquisitionContext, AcquisitionResult
from djb.config.storage.io.external import GitConfigIO
from djb.config.field import (
    ConfigBase,
    ConfigFieldABC,
    ConfigValidationError,
    NOTHING,
    StringField,
)
from djb.config.storage import LocalConfigIO, ProjectConfigType
from djb.config.prompting import PromptResult
from djb.testing.e2e import make_djb_config  # noqa: F401 - fixture

from ..conftest import derived_provenance, mock_store_factory


class TestConfigValidationError:
    """Tests for ConfigValidationError exception."""

    def test_is_exception(self):
        """ConfigValidationError is an Exception."""
        error = ConfigValidationError("invalid value")
        assert isinstance(error, Exception)

    def test_message_is_preserved(self):
        """Error message is preserved."""
        error = ConfigValidationError("expected: user@domain.com")
        assert str(error) == "expected: user@domain.com"


class TestConfigFieldABCInit:
    """Tests for ConfigFieldABC.__init__()."""

    def test_default_values(self):
        """ConfigFieldABC can be created with default values."""
        field = StringField()

        assert field._env_key is None
        assert field._config_file_key is None
        assert field.config_storage == ProjectConfigType  # Defaults to ProjectConfigType
        assert field.default is NOTHING
        assert field.prompt_text is None
        assert field.validation_hint is None
        assert field.config_store_factories == []

    def test_explicit_values(self):
        """ConfigFieldABC can be created with explicit values."""
        # Factory that creates GitConfigIO with ctx
        store_factory = lambda ctx: GitConfigIO("user.email", ctx)
        field = StringField(
            env_key="DJB_CUSTOM_EMAIL",
            config_file_key="email_address",
            config_storage=LocalConfigIO,
            default="default@example.com",
            prompt_text="Enter email",
            validation_hint="expected: user@domain.com",
            config_store_factories=[store_factory],
        )

        assert field._env_key == "DJB_CUSTOM_EMAIL"
        assert field._config_file_key == "email_address"
        assert field.config_storage == LocalConfigIO
        assert field.default == "default@example.com"
        assert field.prompt_text == "Enter email"
        assert field.validation_hint == "expected: user@domain.com"
        assert len(field.config_store_factories) == 1


class TestConfigFieldABCEnvKey:
    """Tests for ConfigFieldABC.env_key property."""

    def test_returns_explicit_env_key(self):
        """env_key returns explicitly set value."""
        field = StringField(env_key="DJB_CUSTOM")
        assert field.env_key == "DJB_CUSTOM"

    def test_explicit_env_key_works_without_field_name(self):
        """Explicit env_key works even when field_name is not set."""
        field = StringField(env_key="DJB_CUSTOM")
        assert field.field_name is None
        assert field.env_key == "DJB_CUSTOM"

    def test_derives_from_field_name(self):
        """env_key derives from field_name when not set."""
        field = StringField()
        field.field_name = "email"
        assert field.env_key == "DJB_EMAIL"

    def test_derives_uppercase(self):
        """Derived env_key is uppercase."""
        field = StringField()
        field.field_name = "project_name"
        assert field.env_key == "DJB_PROJECT_NAME"

    def test_raises_when_field_name_not_set(self):
        """env_key raises RuntimeError when field_name is not set."""
        field = StringField()
        assert field.field_name is None
        with pytest.raises(RuntimeError, match="env_key accessed before field_name was set"):
            _ = field.env_key


class TestConfigFieldABCConfigFileKey:
    """Tests for ConfigFieldABC.config_file_key property."""

    def test_returns_explicit_config_file_key(self):
        """config_file_key returns explicitly set value."""
        field = StringField(config_file_key="email_address")
        assert field.config_file_key == "email_address"

    def test_explicit_config_file_key_works_without_field_name(self):
        """Explicit config_file_key works even when field_name is not set."""
        field = StringField(config_file_key="custom_key")
        assert field.field_name is None
        assert field.config_file_key == "custom_key"

    def test_derives_from_field_name(self):
        """config_file_key derives from field_name when not set."""
        field = StringField()
        field.field_name = "email"
        assert field.config_file_key == "email"

    def test_raises_when_field_name_not_set(self):
        """config_file_key raises RuntimeError when field_name is not set."""
        field = StringField()
        with pytest.raises(
            RuntimeError, match="config_file_key accessed before field_name was set"
        ):
            _ = field.config_file_key


class TestConfigFieldABCDisplayName:
    """Tests for ConfigFieldABC.display_name property."""

    def test_converts_underscores_to_spaces(self):
        """display_name converts underscores to spaces."""
        field = StringField()
        field.field_name = "project_name"
        assert field.display_name == "Project Name"

    def test_title_cases(self):
        """display_name title cases the result."""
        field = StringField()
        field.field_name = "email"
        assert field.display_name == "Email"

    def test_raises_when_field_name_not_set(self):
        """display_name raises RuntimeError when field_name not set."""
        field = StringField()
        with pytest.raises(RuntimeError, match="display_name accessed before field_name was set"):
            _ = field.display_name


class TestConfigFieldDescriptorProtocol:
    """Tests for ConfigFieldABC descriptor protocol (__get__, __set__, __set_name__)."""

    def test_set_name_captures_field_name(self):
        """__set_name__ sets field_name on the descriptor."""
        field = StringField(default="test")

        class TestConfig(ConfigBase):
            my_field: str = field

        assert field.field_name == "my_field"

    def test_get_on_class_returns_descriptor(self):
        """Accessing field on class returns the descriptor itself."""
        field = StringField(default="test")

        class TestConfig(ConfigBase):
            name: str = field

        assert TestConfig.name is field

    def test_get_on_instance_returns_value(self):
        """Accessing field on instance returns the stored value."""
        field = StringField(default="test")

        class TestConfig(ConfigBase):
            name: str = field

        config = TestConfig()
        assert config.name == "test"

    def test_fields_collected_by_metaclass(self):
        """ConfigMeta collects fields into __fields__ dict."""
        field = StringField(default="test")

        class TestConfig(ConfigBase):
            name: str = field

        assert "name" in TestConfig.__fields__
        assert TestConfig.__fields__["name"] is field


class TestConfigFieldABCNormalize:
    """Tests for ConfigFieldABC.normalize() method."""

    def test_default_is_identity(self):
        """Default normalize() returns value unchanged."""
        field = StringField()
        assert field.normalize("test") == "test"
        assert field.normalize(123) == 123
        assert field.normalize(None) is None


class TestConfigFieldABCValidate:
    """Tests for ConfigFieldABC.validate() method."""

    def test_default_is_noop(self):
        """Default validate() does nothing."""
        field = StringField()
        # Should not raise
        field.validate("anything")
        field.validate(123)
        field.validate(None)


class TestConfigFieldABCGetDefault:
    """Tests for ConfigFieldABC.get_default() method."""

    def test_returns_default_value(self):
        """get_default() returns the default."""
        field = StringField(default="my-default")
        assert field.get_default() == "my-default"

    def test_returns_none_when_nothing(self):
        """get_default() returns None when default is NOTHING."""
        field = StringField()  # No default
        assert field.get_default() is None


class TestConfigFieldABCIsValid:
    """Tests for ConfigFieldABC._is_valid() method."""

    def test_returns_true_when_valid(self):
        """_is_valid returns True when validate() doesn't raise."""
        field = StringField()
        assert field._is_valid("anything") is True

    def test_returns_false_when_validation_error(self):
        """_is_valid returns False when validate() raises ConfigValidationError."""

        class AlwaysInvalidField(ConfigFieldABC):
            def validate(self, value):
                raise ConfigValidationError("always invalid")

        field = AlwaysInvalidField()
        assert field._is_valid("anything") is False

    def test_returns_false_when_value_error(self):
        """_is_valid returns False when validate() raises ValueError."""

        class ValueErrorField(ConfigFieldABC):
            def validate(self, value):
                raise ValueError("bad value")

        field = ValueErrorField()
        assert field._is_valid("anything") is False

    def test_returns_false_when_type_error(self):
        """_is_valid returns False when validate() raises TypeError."""

        class TypeErrorField(ConfigFieldABC):
            def validate(self, value):
                raise TypeError("bad type")

        field = TypeErrorField()
        assert field._is_valid("anything") is False


class TestConfigFieldABCRequireString:
    """Tests for ConfigFieldABC._require_string() method."""

    def test_returns_true_for_string(self):
        """_require_string returns True for string values."""
        field = StringField()
        field.field_name = "test"
        assert field._require_string("hello") is True

    def test_returns_false_for_none_when_allowed(self):
        """_require_string returns False for None when allow_none=True."""
        field = StringField()
        field.field_name = "test"
        assert field._require_string(None) is False

    def test_raises_for_none_when_not_allowed(self):
        """_require_string raises for None when allow_none=False."""
        field = StringField()
        field.field_name = "test"

        with pytest.raises(ConfigValidationError, match="test is required"):
            field._require_string(None, allow_none=False)

    def test_raises_for_non_string(self):
        """_require_string raises for non-string values."""
        field = StringField()
        field.field_name = "test"

        with pytest.raises(ConfigValidationError, match="test must be a string.*int"):
            field._require_string(123)

        with pytest.raises(ConfigValidationError, match="test must be a string.*list"):
            field._require_string([])


class TestConfigFieldABCPromptedResult:
    """Tests for ConfigFieldABC._prompted_result() method."""

    def test_creates_acquisition_result(self):
        """_prompted_result creates correct AcquisitionResult."""
        field = StringField()
        field.field_name = "name"

        with patch("djb.config.field.logger"):
            result = field._prompted_result("John")

        assert isinstance(result, AcquisitionResult)
        assert result.value == "John"
        assert result.should_save is True
        assert result.source_name is None
        assert result.was_prompted is True

    def test_logs_done_message(self):
        """_prompted_result logs done message."""
        field = StringField()
        field.field_name = "email"

        with patch("djb.config.field.logger") as mock_logger:
            field._prompted_result("test@example.com")

        mock_logger.done.assert_called_once()
        call_args = mock_logger.done.call_args[0][0]
        assert "Email" in call_args
        assert "test@example.com" in call_args


class TestConfigFieldABCAcquire:
    """Tests for ConfigFieldABC.acquire() method."""

    def test_acquire_from_config_store(self, make_djb_config, project_dir: Path):
        """acquire() returns value from config_store."""
        field = StringField(
            prompt_text="Enter value",
            config_store_factories=[mock_store_factory("name", "store-value")],
        )
        field.field_name = "name"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        result = field.acquire(ctx, config)

        assert result is not None
        assert result.value == "store-value"
        assert result.source_name == "mock store"
        assert result.was_prompted is False

    def test_acquire_skips_invalid_config_store_value(self, make_djb_config, project_dir: Path):
        """acquire() skips config_store if value is invalid."""

        class ValidatingField(StringField):
            def validate(self, value):
                if value == "invalid":
                    raise ConfigValidationError("invalid value")

        field = ValidatingField(
            prompt_text="Enter value",
            config_store_factories=[mock_store_factory("name", "invalid")],
        )
        field.field_name = "name"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        # Should fall through to prompting
        with patch("djb.config.field.prompt") as mock_prompt:
            mock_prompt.return_value = PromptResult(value="valid", source="user", attempts=1)
            with patch("djb.config.field.logger"):
                result = field.acquire(ctx, config)

        assert result is not None
        assert result.value == "valid"
        assert result.was_prompted is True

    def test_acquire_prompts_user(self, make_djb_config, project_dir: Path):
        """acquire() prompts user when no config_stores."""
        field = StringField(
            prompt_text="Enter your name",
            validation_hint="letters only",
        )
        field.field_name = "name"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value="default-name",
            source=derived_provenance(),
            other_values={},
        )

        with patch("djb.config.field.prompt") as mock_prompt:
            mock_prompt.return_value = PromptResult(value="John", source="user", attempts=1)
            with patch("djb.config.field.logger"):
                result = field.acquire(ctx, config)

        mock_prompt.assert_called_once()
        call_kwargs = mock_prompt.call_args
        assert call_kwargs[0][0] == "Enter your name"
        assert call_kwargs[1]["default"] == "default-name"
        assert call_kwargs[1]["validation_hint"] == "letters only"

        assert result is not None
        assert result.value == "John"
        assert result.was_prompted is True

    def test_acquire_returns_none_on_cancel(self, make_djb_config, project_dir: Path):
        """acquire() returns None when user cancels prompt."""
        field = StringField(prompt_text="Enter value")
        field.field_name = "name"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        with patch("djb.config.field.prompt") as mock_prompt:
            mock_prompt.return_value = PromptResult(value=None, source="cancelled", attempts=3)
            result = field.acquire(ctx, config)

        assert result is None

    def test_acquire_returns_none_on_retry_exhaustion(self, make_djb_config, project_dir: Path):
        """acquire() returns None when user exhausts all retry attempts."""

        class AlwaysInvalidField(StringField):
            def validate(self, value):
                if value != "valid":
                    raise ConfigValidationError("expected: valid")

        field = AlwaysInvalidField(prompt_text="Enter value", validation_hint="expected: valid")
        field.field_name = "test"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        # User enters invalid input 3 times, exhausting retries
        with patch("djb.config.field.prompt") as mock_prompt:
            mock_prompt.return_value = PromptResult(value=None, source="cancelled", attempts=3)
            result = field.acquire(ctx, config)

        assert result is None

    def test_acquire_succeeds_after_retry(self, make_djb_config, project_dir: Path):
        """acquire() succeeds when user provides valid input on retry."""
        field = StringField(prompt_text="Enter value")
        field.field_name = "test"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        # User enters invalid input first, then valid input on second attempt
        with (
            patch("djb.config.field.prompt") as mock_prompt,
            patch("djb.config.field.logger"),
        ):
            mock_prompt.return_value = PromptResult(value="valid-input", source="user", attempts=2)
            result = field.acquire(ctx, config)

        assert result is not None
        assert result.value == "valid-input"
        assert result.was_prompted is True

    def test_acquire_returns_current_value_when_no_prompt_text(
        self, make_djb_config, project_dir: Path
    ):
        """acquire() returns current value when prompt_text not set."""
        field = StringField()  # No prompt_text
        field.field_name = "name"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value="existing-value",
            source=derived_provenance(),
            other_values={},
        )

        result = field.acquire(ctx, config)

        assert result is not None
        assert result.value == "existing-value"
        assert result.should_save is False
        assert result.was_prompted is False

    def test_acquire_returns_none_when_no_prompt_text_and_no_value(
        self, make_djb_config, project_dir: Path
    ):
        """acquire() returns None when no prompt_text and no current value."""
        field = StringField()  # No prompt_text
        field.field_name = "name"

        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value=None,
            source=None,
            other_values={},
        )

        result = field.acquire(ctx, config)
        assert result is None


class TestStringField:
    """Tests for StringField class."""

    def test_is_subclass_of_config_field_abc(self):
        """StringField is a subclass of ConfigFieldABC."""
        assert issubclass(StringField, ConfigFieldABC)

    def test_has_no_custom_behavior(self):
        """StringField has no custom overrides."""
        field = StringField()

        # Should use base class behavior
        assert field.normalize("test") == "test"
        # Should not raise on validate
        field.validate("anything")

    def test_can_be_used_as_field(self):
        """StringField can be used to define a ConfigBase field."""
        field = StringField(default="default-value")

        class TestConfig(ConfigBase):
            name: str = field

        # Verify field_name is set automatically
        assert field.field_name == "name"

        # Verify the field works with default value
        config = TestConfig()
        assert config.name == "default-value"

        # Verify the field works when a value is provided
        config2 = TestConfig(name="test-value")
        assert config2.name == "test-value"

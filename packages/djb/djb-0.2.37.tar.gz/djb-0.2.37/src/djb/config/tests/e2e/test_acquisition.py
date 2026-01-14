"""E2E tests for value acquisition that require file I/O."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from typing import Any

from djb.config.acquisition import (
    AcquisitionContext,
    AcquisitionResult,
    _is_acquirable,
    acquire_all_fields,
)
from djb.config.config import DjbConfigBase
from djb.config.field import StringField
from djb.config.storage import LocalConfigIO, ProjectConfigType
from djb.config.storage.types import DerivedConfigType

from ..conftest import derived_provenance, explicit_provenance

pytestmark = pytest.mark.e2e_marker


class _TestConfigBase(DjbConfigBase):
    """Base class for test configs that need project_dir and mode.

    Extends DjbConfigBase (no inherited fields) and accepts project_dir
    as a required kwarg, setting it directly on the instance.
    """

    def __init__(self, *, project_dir: Path, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.__dict__["project_dir"] = project_dir
        self.__dict__["mode"] = None  # Default for tests


class TestConfigFieldSet:
    """Tests for ConfigFieldABC.set() method with real file I/O."""

    def test_saves_to_local_config(self, make_djb_config):
        """ConfigFieldABC.set() saves to local.toml for LOCAL storage."""
        field = StringField(config_storage=LocalConfigIO)
        field.field_name = "name"
        config = make_djb_config()

        field.set("John", config)

        result = LocalConfigIO(config).load()
        assert result == {"name": "John"}

    def test_saves_to_project_config(self, make_djb_config):
        """ConfigFieldABC.set() saves to project.toml for PROJECT storage."""
        field = StringField(config_storage=ProjectConfigType)
        field.field_name = "seed_command"
        config = make_djb_config()

        field.set("myapp.cli:seed", config)

        result = ProjectConfigType(config).load()
        assert result == {"seed_command": "myapp.cli:seed"}

    def test_derives_key_from_field_name(self, make_djb_config):
        """ConfigFieldABC.set() uses field_name as config_file_key."""
        field = StringField(config_storage=LocalConfigIO)
        field.field_name = "email"
        config = make_djb_config()

        field.set("test@example.com", config)

        result = LocalConfigIO(config).load()
        assert result == {"email": "test@example.com"}

    def test_merges_with_existing_config(self, make_config_file, make_djb_config):
        """ConfigFieldABC.set() merges with existing config."""
        make_config_file({"existing": "value"})

        field = StringField(config_storage=LocalConfigIO)
        field.field_name = "name"
        config = make_djb_config()

        field.set("John", config)

        result = LocalConfigIO(config).load()
        assert result == {"existing": "value", "name": "John"}

    def test_skips_derived_fields(self, project_dir: Path, make_djb_config):
        """ConfigFieldABC.set() skips DERIVED fields - they're never saved."""
        field = StringField(config_storage=DerivedConfigType)
        field.field_name = "key"
        config = make_djb_config()

        field.set("value", config)

        # DERIVED fields should not create any config file
        assert not (project_dir / ".djb" / "project.toml").exists()
        assert not (project_dir / ".djb" / "local.toml").exists()


class TestAcquireAllFieldsFileIO:
    """Tests for acquire_all_fields that require file I/O.

    These tests use _TestConfigBase subclasses with a custom 'test_field' that has
    a mocked acquire method to test save behavior.
    """

    def test_saves_value_when_should_save_is_true(self, project_dir: Path):
        """acquire_all_fields saves value when should_save=True."""
        field = StringField(config_storage=LocalConfigIO, prompt_text="Enter value")
        field.acquire = MagicMock(return_value=AcquisitionResult(value="John", should_save=True))

        class TestConfig(_TestConfigBase):
            test_field: str = field

        config = TestConfig(project_dir=project_dir)
        config._provenance["test_field"] = derived_provenance()

        list(acquire_all_fields(config))

        # Verify config was saved
        config_data = LocalConfigIO(config).load()
        assert config_data == {"test_field": "John"}

    def test_does_not_save_when_should_save_is_false(self, project_dir: Path):
        """acquire_all_fields doesn't save when should_save=False."""
        field = StringField(config_storage=LocalConfigIO, prompt_text="Enter value")
        field.acquire = MagicMock(return_value=AcquisitionResult(value="John", should_save=False))

        class TestConfig(_TestConfigBase):
            test_field: str = field

        config = TestConfig(project_dir=project_dir)
        config._provenance["test_field"] = derived_provenance()

        list(acquire_all_fields(config))

        # Verify config was NOT saved
        config_data = LocalConfigIO(config).load()
        assert config_data == {}

    def test_does_not_save_none_values(self, project_dir: Path):
        """acquire_all_fields doesn't save None values even with should_save=True."""
        field = StringField(config_storage=LocalConfigIO, prompt_text="Enter value")
        field.acquire = MagicMock(return_value=AcquisitionResult(value=None, should_save=True))

        class TestConfig(_TestConfigBase):
            test_field: str = field

        config = TestConfig(project_dir=project_dir)
        config._provenance["test_field"] = derived_provenance()

        list(acquire_all_fields(config))

        # Verify config was NOT saved (None values not saved)
        config_data = LocalConfigIO(config).load()
        assert config_data == {}


class TestAcquireAllFields:
    """Tests for acquire_all_fields behavior."""

    def test_skips_non_acquirable_fields(self, project_dir: Path):
        """acquire_all_fields skips fields without acquire method."""
        # Field without prompt_text is not acquirable
        field = StringField(config_storage=LocalConfigIO)

        class TestConfig(_TestConfigBase):
            test_field: str = field

        config = TestConfig(project_dir=project_dir)

        results = list(acquire_all_fields(config))

        assert results == []

    def test_skips_explicit_fields(self, project_dir: Path):
        """acquire_all_fields skips fields with explicit source."""
        field = StringField(config_storage=LocalConfigIO, prompt_text="Enter value")
        field.acquire = MagicMock()

        class TestConfig(_TestConfigBase):
            test_field: str = field

        config = TestConfig(project_dir=project_dir)
        # Mark field as explicitly set
        config._provenance["test_field"] = explicit_provenance()

        results = list(acquire_all_fields(config))

        assert results == []
        field.acquire.assert_not_called()

    def test_calls_acquire_for_acquirable_field(self, project_dir: Path):
        """acquire_all_fields calls acquire for fields that need values."""
        field = StringField(config_storage=LocalConfigIO, prompt_text="Enter value")
        field.acquire = MagicMock(return_value=AcquisitionResult(value="John", should_save=False))

        class TestConfig(_TestConfigBase):
            test_field: str = field

        config = TestConfig(project_dir=project_dir)
        # Mark as derived (needs acquisition)
        config._provenance["test_field"] = derived_provenance()

        results = list(acquire_all_fields(config))

        assert len(results) == 1
        field_name, result = results[0]
        assert field_name == "test_field"
        assert result.value == "John"
        field.acquire.assert_called_once()

    def test_skips_when_acquire_returns_none(self, project_dir: Path):
        """acquire_all_fields skips when acquire returns None."""
        field = StringField(config_storage=LocalConfigIO, prompt_text="Enter value")
        field.acquire = MagicMock(return_value=None)

        class TestConfig(_TestConfigBase):
            test_field: str = field

        config = TestConfig(project_dir=project_dir)
        config._provenance["test_field"] = derived_provenance()

        results = list(acquire_all_fields(config))

        assert results == []

    def test_passes_other_values_to_context(self, project_dir: Path):
        """acquire_all_fields passes shared other_values dict to context.

        The other_values dict is shared across all fields and accumulates values
        as fields are processed. After acquisition completes, each field's context
        sees all configured values (both explicit and acquired).
        """
        # Both fields need prompt_text to be acquirable (so they're processed)
        # name has explicit provenance (so it's added to configured but not acquired)
        # email has derived provenance (so it's acquired and sees name in other_values)
        field1 = StringField(config_storage=LocalConfigIO, prompt_text="Enter name")
        field2 = StringField(config_storage=LocalConfigIO, prompt_text="Enter email")
        field2.acquire = MagicMock(
            return_value=AcquisitionResult(value="result", should_save=False)
        )

        class TestConfig(_TestConfigBase):
            name: str = field1
            email: str = field2

        config = TestConfig(project_dir=project_dir)
        config.__dict__["name"] = "John"
        config._provenance["name"] = explicit_provenance()
        config._provenance["email"] = derived_provenance()

        list(acquire_all_fields(config))

        # other_values is a shared dict - after acquisition it contains all values
        call_args = field2.acquire.call_args
        ctx = call_args[0][0]
        assert ctx.other_values == {"name": "John", "email": "result"}

    def test_field_name_set_by_descriptor_protocol(self, project_dir: Path):
        """Field name is set correctly via __set_name__."""
        field = StringField(config_storage=LocalConfigIO, prompt_text="Enter value")
        field.acquire = MagicMock(return_value=AcquisitionResult(value="test", should_save=False))

        class TestConfig(_TestConfigBase):
            my_custom_field: str = field

        config = TestConfig(project_dir=project_dir)
        config._provenance["my_custom_field"] = derived_provenance()

        list(acquire_all_fields(config))

        # Verify the field knows its name
        assert field.field_name == "my_custom_field"


# =============================================================================
# Tests merged from unit test file
# =============================================================================


class TestAcquisitionContext:
    """Tests for AcquisitionContext dataclass."""

    def test_creation(self, make_djb_config):
        """AcquisitionContext can be created."""
        source = explicit_provenance()
        config = make_djb_config()
        ctx = AcquisitionContext(
            config=config,
            current_value="test-value",
            source=source,
            other_values={"name": "John"},
        )

        assert ctx.config is config
        assert ctx.current_value == "test-value"
        assert ctx.source == source
        assert ctx.other_values == {"name": "John"}

    def test_is_explicit_with_explicit_source(self, make_djb_config):
        """is_explicit() returns True for explicit sources."""
        ctx = AcquisitionContext(
            config=make_djb_config(),
            current_value="val",
            source=explicit_provenance(),
            other_values={},
        )
        assert ctx.is_explicit() is True

    def test_is_explicit_with_derived_source(self, make_djb_config):
        """is_explicit() returns False for derived sources."""
        ctx = AcquisitionContext(
            config=make_djb_config(),
            current_value="val",
            source=derived_provenance(),
            other_values={},
        )
        assert ctx.is_explicit() is False

    def test_is_explicit_with_none_source(self, make_djb_config):
        """is_explicit() returns False when source is None."""
        ctx = AcquisitionContext(
            config=make_djb_config(),
            current_value=None,
            source=None,
            other_values={},
        )
        assert ctx.is_explicit() is False

    def test_is_derived_with_derived_source(self, make_djb_config):
        """AcquisitionContext.is_derived returns True for derived sources."""
        ctx = AcquisitionContext(
            config=make_djb_config(),
            current_value="val",
            source=derived_provenance(),
            other_values={},
        )
        assert ctx.is_derived() is True

    def test_is_derived_with_explicit_source(self, make_djb_config):
        """AcquisitionContext.is_derived returns False for explicit sources."""
        ctx = AcquisitionContext(
            config=make_djb_config(),
            current_value="val",
            source=explicit_provenance(),
            other_values={},
        )
        assert ctx.is_derived() is False

    def test_is_derived_with_none_source(self, make_djb_config):
        """AcquisitionContext.is_derived returns False when source is None."""
        ctx = AcquisitionContext(
            config=make_djb_config(),
            current_value=None,
            source=None,
            other_values={},
        )
        assert ctx.is_derived() is False


class TestAcquisitionResult:
    """Tests for AcquisitionResult dataclass."""

    def test_creation_with_defaults(self):
        """AcquisitionResult can be created with defaults."""
        result = AcquisitionResult(value="test-value")

        assert result.value == "test-value"
        assert result.should_save is True
        assert result.source_name is None
        assert result.was_prompted is False

    def test_creation_with_all_fields(self):
        """AcquisitionResult can be created with all fields."""
        result = AcquisitionResult(
            value="test@example.com",
            should_save=False,
            source_name="git config",
            was_prompted=True,
        )

        assert result.value == "test@example.com"
        assert result.should_save is False
        assert result.source_name == "git config"
        assert result.was_prompted is True


class TestIsAcquirable:
    """Tests for _is_acquirable helper function."""

    def test_acquirable_field_with_acquire_and_prompt_text(self):
        """_is_acquirable returns True for field with acquire() and prompt_text."""
        field = MagicMock()
        field.prompt_text = "Enter value"

        assert _is_acquirable(field) is True

    def test_not_acquirable_without_prompt_text(self):
        """_is_acquirable returns False when prompt_text is None."""
        field = MagicMock()
        field.prompt_text = None

        assert _is_acquirable(field) is False

    def test_not_acquirable_without_acquire_method(self):
        """_is_acquirable returns False when acquire() doesn't exist."""
        field = MagicMock(spec=["prompt_text"])
        field.prompt_text = "Enter value"

        assert _is_acquirable(field) is False

"""Unit tests for config storage layer.

Tests for the low-level storage primitives:
- navigate_config_path: Dict navigation utility
- ConfigIO.full_path: Path composition from base_prefix / mode_prefix / key
- EnvDict: Smart dict for environment variable access
"""

from __future__ import annotations

from typing import ClassVar

import pytest

pytestmark = pytest.mark.e2e_marker

from djb.config.config import DjbConfig
from djb.config.storage import ConfigIO, navigate_config_path
from djb.config.storage.io.env import EnvDict
from djb.testing.e2e import make_djb_config  # noqa: F401 - fixture


# =============================================================================
# TestNavigateConfigPath - Dict navigation utility
# =============================================================================


class TestNavigateConfigPath:
    """Test navigate_config_path dict navigation."""

    def test_none_path_returns_data(self):
        """None path returns the data unchanged."""
        data = {"a": 1, "b": 2}
        assert navigate_config_path(data, None) == data

    def test_navigates_nested_dict(self):
        """Navigates to nested dict."""
        data = {"a": {"b": {"c": {"d": 42}}}}
        result = navigate_config_path(data, "a.b.c")
        assert result == {"d": 42}

    def test_navigates_with_list_path(self):
        """Navigates with list of path parts."""
        data = {"a": {"b": {"c": {"d": 42}}}}
        result = navigate_config_path(data, ["a", "b", "c"])
        assert result == {"d": 42}

    def test_returns_none_for_missing_path(self):
        """Returns None when path doesn't exist."""
        data = {"a": {"b": 1}}
        assert navigate_config_path(data, "a.x.y") is None

    def test_returns_none_for_non_dict_intermediate(self):
        """Returns None when intermediate is not a dict."""
        data = {"a": "not a dict"}
        assert navigate_config_path(data, "a.b") is None

    def test_ensure_creates_missing_dicts(self):
        """With ensure=True, creates missing intermediate dicts."""
        data: dict = {}
        result = navigate_config_path(data, "a.b.c", ensure=True)
        assert result == {}
        assert data == {"a": {"b": {"c": {}}}}

    def test_ensure_returns_existing_dict(self):
        """With ensure=True, returns existing dict if present."""
        data = {"a": {"b": {"c": {"existing": 1}}}}
        result = navigate_config_path(data, "a.b.c", ensure=True)
        assert result == {"existing": 1}

    def test_object_navigation_with_getattr(self):
        """Navigates objects using getattr."""

        class Nested:
            value = 42

        class Outer:
            inner = Nested()

        obj = Outer()
        assert navigate_config_path(obj, "inner.value") == 42

    def test_object_navigation_returns_none_for_missing(self):
        """Returns None for missing object attributes."""

        class Outer:
            pass

        obj = Outer()
        assert navigate_config_path(obj, "missing.attr") is None


# =============================================================================
# TestConfigIOFullPath - Path composition in ConfigIO
# =============================================================================


class _TestableConfigIO(ConfigIO):
    """Concrete ConfigIO for testing base class methods."""

    # Override base_prefix via class attribute for parametrized tests
    base_prefix: ClassVar[str | None] = None
    name = "test"

    def __init__(
        self,
        config: DjbConfig,
        *,
        base_prefix: str | None = None,
        mode_prefix: str | None = None,
    ) -> None:
        super().__init__(config, mode_prefix=mode_prefix)
        # Override class attribute with instance value
        if base_prefix is not None:
            object.__setattr__(self, "base_prefix", base_prefix)

    def _load_raw_data(self) -> dict:
        return {}


class TestConfigIOFullPath:
    """Test path composition in ConfigIO.full_path().

    The full_path(key) method composes: base_prefix / mode_prefix / key
    and returns a tuple of (nav_path, leaf_key).
    """

    @pytest.mark.parametrize(
        "base_prefix,mode_prefix,key,expected",
        [
            # Key only (no prefix) - leaf is at root
            (None, None, "mode", (None, "mode")),
            # Base + key
            ("tool.djb", None, "mode", ("tool.djb", "mode")),
            # Mode + key
            (None, "staging", "mode", ("staging", "mode")),
            # Base + mode + key
            ("tool.djb", "staging", "mode", ("tool.djb.staging", "mode")),
            # Nested key
            (None, None, "hetzner.server_type", ("hetzner", "server_type")),
            # Full nested path
            (
                "tool.djb",
                "staging",
                "hetzner.server_type",
                ("tool.djb.staging.hetzner", "server_type"),
            ),
        ],
        ids=[
            "key_only",
            "base_key",
            "mode_key",
            "base_mode_key",
            "nested_key",
            "full_nested",
        ],
    )
    def test_full_path_composition(
        self,
        make_djb_config,
        base_prefix: str | None,
        mode_prefix: str | None,
        key: str,
        expected: tuple[str | None, str],
    ):
        """Various combinations of base_prefix / mode_prefix / key."""
        config = make_djb_config()
        io = _TestableConfigIO(config, base_prefix=base_prefix, mode_prefix=mode_prefix)

        result = io.full_path(key)

        assert result == expected

    def test_full_path_returns_tuple(self, make_djb_config):
        """full_path() returns a (nav_path, leaf_key) tuple."""
        config = make_djb_config()
        io = _TestableConfigIO(config, base_prefix="tool.djb", mode_prefix="staging")

        result = io.full_path("hetzner.server_type")

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result == ("tool.djb.staging.hetzner", "server_type")


class TestConfigIOLoadHas:
    """Test load() and has() methods."""

    def test_load_returns_all_keys(self, make_djb_config):
        """load() returns all keys including nested dicts."""
        config = make_djb_config()

        class _DataIO(_TestableConfigIO):
            def _load_raw_data(self) -> dict:
                return {
                    "name": "John",
                    "email": "john@example.com",
                    "hetzner": {"server_type": "cx23"},
                }

        io = _DataIO(config)

        result = io.load()

        assert result == {
            "name": "John",
            "email": "john@example.com",
            "hetzner": {"server_type": "cx23"},
        }

    def test_load_with_mode_prefix(self, make_djb_config):
        """load() respects mode_prefix for navigation."""
        config = make_djb_config()

        class _DataIO(_TestableConfigIO):
            def _load_raw_data(self) -> dict:
                return {
                    "name": "Production",
                    "staging": {"name": "Staging"},
                }

        io = _DataIO(config, mode_prefix="staging")

        result = io.load()

        assert result == {"name": "Staging"}

    def test_has_returns_true_for_existing_key(self, make_djb_config):
        """has() returns True for existing flat key."""
        config = make_djb_config()

        class _DataIO(_TestableConfigIO):
            def _load_raw_data(self) -> dict:
                return {"name": "John"}

        io = _DataIO(config)

        assert io.has("name") is True

    def test_has_returns_false_for_missing_key(self, make_djb_config):
        """has() returns False for missing key."""
        config = make_djb_config()

        class _DataIO(_TestableConfigIO):
            def _load_raw_data(self) -> dict:
                return {"name": "John"}

        io = _DataIO(config)

        assert io.has("missing") is False

    def test_has_returns_true_for_section(self, make_djb_config):
        """has() returns True for section keys (nested dicts)."""
        config = make_djb_config()

        class _DataIO(_TestableConfigIO):
            def _load_raw_data(self) -> dict:
                return {"hetzner": {"server_type": "cx23"}}

        io = _DataIO(config)

        # "hetzner" exists as a section dict
        assert io.has("hetzner") is True


class TestConfigIOSetValue:
    """Test _set_value method."""

    def test_set_value_writes_to_root(self, make_djb_config):
        """_set_value writes to root for simple key."""
        config = make_djb_config()
        io = _WritableTestIO(config, {})

        io._set_value("name", "John")

        assert io._written == {"name": "John"}

    def test_set_value_writes_to_section(self, make_djb_config):
        """_set_value writes to section for dotted key."""
        config = make_djb_config()
        io = _WritableTestIO(config, {})

        io._set_value("hetzner.server_type", "cx23")

        assert io._written == {"hetzner": {"server_type": "cx23"}}

    def test_set_value_with_mode(self, make_djb_config):
        """_set_value respects mode_prefix for write path."""
        config = make_djb_config()
        io = _WritableTestIO(config, {}, mode_prefix="staging")

        io._set_value("hetzner.server_type", "cx23")

        assert io._written == {"staging": {"hetzner": {"server_type": "cx23"}}}


class TestConfigIOGet:
    """Test get() method (returns value and provenance)."""

    def test_get_returns_value_and_provenance(self, make_djb_config):
        """get() returns (value, provenance) tuple."""
        config = make_djb_config()

        class _DataIO(_TestableConfigIO):
            def _load_raw_data(self) -> dict:
                return {"name": "John"}

        io = _DataIO(config)

        value, provenance = io.get("name")

        assert value == "John"
        assert provenance == (io,)

    def test_get_returns_section_dict(self, make_djb_config):
        """get() returns section dict for section keys."""
        config = make_djb_config()

        class _DataIO(_TestableConfigIO):
            def _load_raw_data(self) -> dict:
                return {"hetzner": {"server_type": "cx23", "location": "nbg1"}}

        io = _DataIO(config)

        value, provenance = io.get("hetzner")

        assert value == {"server_type": "cx23", "location": "nbg1"}
        assert provenance == (io,)

    def test_get_returns_none_for_missing(self, make_djb_config):
        """get() returns (None, None) for missing key."""
        config = make_djb_config()

        class _DataIO(_TestableConfigIO):
            def _load_raw_data(self) -> dict:
                return {"name": "John"}

        io = _DataIO(config)

        value, provenance = io.get("missing")

        assert value is None
        assert provenance is None


class TestConfigIOSetDelete:
    """Test set() and delete() public interface methods."""

    def test_set_calls_set_value(self, make_djb_config):
        """set() delegates to _set_value."""
        config = make_djb_config()
        io = _WritableTestIO(config, {})

        io.set("user.name", "John")

        assert io._written == {"user": {"name": "John"}}

    def test_delete_calls_delete_value(self, make_djb_config):
        """delete() delegates to _delete_value."""
        config = make_djb_config()
        io = _WritableTestIO(config, {"name": "John"})

        io.delete("name")

        assert io._written is not None
        assert "name" not in io._written


class TestConfigIOSave:
    """Test save() method."""

    def test_save_writes_data(self, make_djb_config):
        """save() writes data to the store."""
        config = make_djb_config()
        io = _WritableTestIO(config, {"existing": "value"})

        io.save({"name": "John", "email": "john@example.com"})

        assert io._written is not None
        assert io._written["name"] == "John"
        assert io._written["email"] == "john@example.com"
        assert io._written["existing"] == "value"

    def test_save_with_mode(self, make_djb_config):
        """save() respects mode_prefix for write path."""
        config = make_djb_config()
        io = _WritableTestIO(config, {}, mode_prefix="staging")

        io.save({"name": "John"})

        assert io._written == {"staging": {"name": "John"}}


# =============================================================================
# TestEnvDict - Smart dict for environment variable access
# =============================================================================


class TestEnvDict:
    """Test EnvDict Mapping implementation for env var access."""

    def test_getitem_returns_value(self):
        """__getitem__ returns env var value."""
        environ = {"DJB_PROJECT_NAME": "myproject"}
        envdict = EnvDict(environ)

        assert envdict["project_name"] == "myproject"

    def test_getitem_case_insensitive_key(self):
        """Keys are case-insensitive (converted to uppercase)."""
        environ = {"DJB_PROJECT_NAME": "myproject"}
        envdict = EnvDict(environ)

        # Key is lowercase, env var is uppercase
        assert envdict["project_name"] == "myproject"

    def test_getitem_raises_keyerror_for_missing(self):
        """__getitem__ raises KeyError for missing keys."""
        envdict = EnvDict({})

        with pytest.raises(KeyError):
            envdict["missing"]

    def test_getitem_returns_nested_envdict_for_section(self):
        """__getitem__ returns nested EnvDict for section access."""
        environ = {"DJB_HETZNER_SERVER_TYPE": "cx23"}
        envdict = EnvDict(environ)

        nested = envdict["hetzner"]

        assert isinstance(nested, EnvDict)
        assert nested["server_type"] == "cx23"

    def test_get_returns_value(self):
        """get() returns value for existing key."""
        environ = {"DJB_NAME": "John"}
        envdict = EnvDict(environ)

        assert envdict.get("name") == "John"

    def test_get_returns_default_for_missing(self):
        """get() returns default for missing key."""
        envdict = EnvDict({})

        assert envdict.get("missing") is None
        assert envdict.get("missing", "default") == "default"

    def test_len_counts_all_entries_at_prefix(self):
        """__len__ counts all env vars at the current prefix level."""
        environ = {
            "DJB_NAME": "John",
            "DJB_EMAIL": "john@example.com",
            "DJB_HETZNER_SERVER_TYPE": "cx23",  # Nested, still counted
            "OTHER_VAR": "ignored",  # Different prefix
        }
        envdict = EnvDict(environ)

        # Counts DJB_NAME, DJB_EMAIL, DJB_HETZNER_SERVER_TYPE
        assert len(envdict) == 3

    def test_iter_yields_all_keys(self):
        """__iter__ yields all keys at the current prefix level."""
        environ = {
            "DJB_NAME": "John",
            "DJB_EMAIL": "john@example.com",
            "OTHER_VAR": "ignored",
        }
        envdict = EnvDict(environ)

        keys = list(envdict)

        assert "name" in keys
        assert "email" in keys
        assert "other_var" not in keys

    def test_nested_envdict_has_correct_prefix(self):
        """Nested EnvDict has the correct prefix for lookups."""
        environ = {
            "DJB_HETZNER_SERVER_TYPE": "cx23",
            "DJB_HETZNER_LOCATION": "nbg1",
            "DJB_NAME": "John",  # Different section
        }
        envdict = EnvDict(environ)

        hetzner = envdict["hetzner"]

        assert hetzner["server_type"] == "cx23"
        assert hetzner["location"] == "nbg1"
        # Should not see DJB_NAME
        with pytest.raises(KeyError):
            hetzner["name"]

    def test_custom_prefix(self):
        """EnvDict works with custom prefix."""
        environ = {"CUSTOM_FOO": "bar"}
        envdict = EnvDict(environ, prefix="CUSTOM")

        assert envdict["foo"] == "bar"


# =============================================================================
# TestCleanupEmptyParents - Delete cleanup logic
# =============================================================================


class _WritableTestIO(ConfigIO):
    """Writable ConfigIO for testing delete/cleanup logic."""

    name = "writable_test"

    def __init__(
        self,
        config: DjbConfig,
        data: dict,
        *,
        mode_prefix: str | None = None,
    ) -> None:
        super().__init__(config, mode_prefix=mode_prefix)
        self._data = data
        self._written: dict | None = None

    def _load_raw_data(self) -> dict:
        return self._data

    def _write_raw_data(self, data: dict) -> None:
        self._written = data


class TestCleanupEmptyParents:
    """Test _cleanup_empty_parents after key deletion."""

    def test_removes_empty_top_level_dict(self, make_djb_config):
        """Removes empty dict at top level after deletion."""
        config = make_djb_config()
        data = {"staging": {}}
        io = _WritableTestIO(config, data)

        io._cleanup_empty_parents(data, "staging")

        assert "staging" not in data

    def test_removes_empty_nested_dict(self, make_djb_config):
        """Removes empty nested dict after deletion."""
        config = make_djb_config()
        data = {"staging": {"hetzner": {}}}
        io = _WritableTestIO(config, data)

        io._cleanup_empty_parents(data, "staging.hetzner")

        # Both should be removed (hetzner is empty, then staging becomes empty)
        assert "staging" not in data

    def test_preserves_non_empty_parent(self, make_djb_config):
        """Preserves parent dict if it has other keys."""
        config = make_djb_config()
        data = {"staging": {"hetzner": {}, "other": "value"}}
        io = _WritableTestIO(config, data)

        io._cleanup_empty_parents(data, "staging.hetzner")

        # staging.hetzner removed, but staging preserved (has "other")
        assert "staging" in data
        assert "hetzner" not in data["staging"]
        assert data["staging"]["other"] == "value"

    def test_noop_for_empty_path(self, make_djb_config):
        """No-op when path is empty."""
        config = make_djb_config()
        data = {"key": "value"}
        io = _WritableTestIO(config, data)

        io._cleanup_empty_parents(data, "")

        assert data == {"key": "value"}


class TestConfigIODelete:
    """Test _delete_value and delete cleanup."""

    def test_deletes_key_and_writes(self, make_djb_config):
        """Deleting a key writes the updated data."""
        config = make_djb_config()
        data = {"key": "value", "other": "kept"}
        io = _WritableTestIO(config, data)

        io._delete_value("key")

        assert io._written is not None
        assert "key" not in io._written
        assert io._written["other"] == "kept"

    def test_deletes_from_nested_path(self, make_djb_config):
        """Deleting with dotted key path works correctly."""
        config = make_djb_config()
        data = {"hetzner": {"server_type": "cx23", "location": "nbg1"}}
        io = _WritableTestIO(config, data)

        io._delete_value("hetzner.server_type")

        assert io._written is not None
        assert "server_type" not in io._written["hetzner"]
        assert io._written["hetzner"]["location"] == "nbg1"

    def test_cleans_up_empty_section_after_delete(self, make_djb_config):
        """Empty section is cleaned up after last key deleted."""
        config = make_djb_config()
        data = {"hetzner": {"server_type": "cx23"}}
        io = _WritableTestIO(config, data)

        io._delete_value("hetzner.server_type")

        assert io._written is not None
        assert "hetzner" not in io._written

    def test_noop_when_key_does_not_exist(self, make_djb_config):
        """No write when key doesn't exist."""
        config = make_djb_config()
        data = {"key": "value"}
        io = _WritableTestIO(config, data)

        io._delete_value("nonexistent")

        # No write should have happened
        assert io._written is None


class TestConfigIORepr:
    """Test ConfigIO __repr__."""

    def test_repr_format(self, make_djb_config):
        """__repr__ includes class name and name property."""
        config = make_djb_config()
        io = _WritableTestIO(config, {})

        result = repr(io)

        assert result == "<_WritableTestIO name='writable_test'>"

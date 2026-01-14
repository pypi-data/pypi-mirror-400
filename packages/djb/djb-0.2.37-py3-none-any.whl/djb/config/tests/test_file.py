"""Unit tests for deep_merge utility.

ConfigStore.set/delete mode-specific behavior is tested in test_config.py
(TestMultiLevelNesting).
"""

from __future__ import annotations

from djb.config.storage import deep_merge


class TestDeepMerge:
    """Tests for deep_merge function."""

    def test_merges_flat_dicts(self):
        """Flat dicts are merged with override taking precedence."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_does_not_mutate_inputs(self):
        """Neither input dict is mutated."""
        base = {"a": 1}
        override = {"b": 2}
        deep_merge(base, override)
        assert base == {"a": 1}
        assert override == {"b": 2}

    def test_merges_nested_dicts(self):
        """Nested dicts are recursively merged."""
        base = {"hetzner": {"server_type": "cx22", "location": "nbg1"}}
        override = {"hetzner": {"server_type": "cx32"}}
        result = deep_merge(base, override)
        assert result == {"hetzner": {"server_type": "cx32", "location": "nbg1"}}

    def test_partial_nested_override(self):
        """Partial override preserves unspecified nested fields."""
        base = {
            "hetzner": {
                "server_type": "cx22",
                "location": "nbg1",
                "image": "ubuntu-24.04",
            }
        }
        override = {"hetzner": {"server_type": "cx11"}}
        result = deep_merge(base, override)
        assert result == {
            "hetzner": {
                "server_type": "cx11",
                "location": "nbg1",
                "image": "ubuntu-24.04",
            }
        }

    def test_full_nested_override(self):
        """Full override replaces all nested fields."""
        base = {"hetzner": {"server_type": "cx22", "location": "nbg1"}}
        override = {"hetzner": {"server_type": "cx32", "location": "fsn1", "image": "debian-12"}}
        result = deep_merge(base, override)
        assert result == {
            "hetzner": {"server_type": "cx32", "location": "fsn1", "image": "debian-12"}
        }

    def test_override_replaces_non_dict_with_dict(self):
        """A dict in override replaces a non-dict in base."""
        base = {"key": "value"}
        override = {"key": {"nested": "value"}}
        result = deep_merge(base, override)
        assert result == {"key": {"nested": "value"}}

    def test_override_replaces_dict_with_non_dict(self):
        """A non-dict in override replaces a dict in base."""
        base = {"key": {"nested": "value"}}
        override = {"key": "value"}
        result = deep_merge(base, override)
        assert result == {"key": "value"}

    def test_deeply_nested_merge(self):
        """Merge works for arbitrarily deep nesting."""
        base = {"a": {"b": {"c": {"d": 1}}}}
        override = {"a": {"b": {"c": {"e": 2}}}}
        result = deep_merge(base, override)
        assert result == {"a": {"b": {"c": {"d": 1, "e": 2}}}}

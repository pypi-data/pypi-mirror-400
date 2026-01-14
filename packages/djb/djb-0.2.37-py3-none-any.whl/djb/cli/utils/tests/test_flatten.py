"""Tests for djb.cli.utils.flatten module."""

from __future__ import annotations

from djb.cli.utils.flatten import flatten_dict


class TestFlattenDict:
    """Tests for flatten_dict function."""

    def test_empty_dict(self):
        """flatten_dict returns empty dict for empty input."""
        result = flatten_dict({})
        assert result == {}

    def test_flat_dict(self):
        """flatten_dict uppercases keys in already flat dict."""
        result = flatten_dict({"key": "value", "other": "data"})
        assert result == {"KEY": "value", "OTHER": "data"}

    def test_nested_dict(self):
        """flatten_dict flattens nested dict with underscore separator."""
        result = flatten_dict({"db": {"host": "localhost", "port": 5432}})
        assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}

    def test_deeply_nested_dict(self):
        """flatten_dict handles deeply nested dicts."""
        result = flatten_dict({"a": {"b": {"c": "value"}}})
        assert result == {"A_B_C": "value"}

    def test_mixed_nesting(self):
        """flatten_dict handles dict with mixed nesting levels."""
        result = flatten_dict(
            {
                "simple": "value",
                "nested": {"key": "data"},
                "deep": {"level1": {"level2": "deep_value"}},
            }
        )
        assert result == {
            "SIMPLE": "value",
            "NESTED_KEY": "data",
            "DEEP_LEVEL1_LEVEL2": "deep_value",
        }

    def test_converts_non_string_values(self):
        """flatten_dict converts non-string values to strings."""
        result = flatten_dict({"count": 42, "enabled": True, "ratio": 3.14})
        assert result == {"COUNT": "42", "ENABLED": "True", "RATIO": "3.14"}

    def test_uppercase_keys(self):
        """flatten_dict uppercases all keys."""
        result = flatten_dict({"mixedCase": "value", "UPPER": "data", "lower": "test"})
        assert result == {"MIXEDCASE": "value", "UPPER": "data", "LOWER": "test"}

    def test_none_value(self):
        """flatten_dict converts None values to 'None' string."""
        result = flatten_dict({"key": None})
        assert result == {"KEY": "None"}

    def test_empty_string_value(self):
        """flatten_dict preserves empty string values."""
        result = flatten_dict({"key": ""})
        assert result == {"KEY": ""}

    def test_empty_nested_dict(self):
        """flatten_dict produces no output for empty nested dict branch."""
        result = flatten_dict({"outer": {"inner": {}}, "other": "value"})
        assert result == {"OTHER": "value"}

    def test_keys_with_underscores(self):
        """flatten_dict handles keys with underscores correctly."""
        result = flatten_dict({"my_key": "value", "nested": {"sub_key": "data"}})
        assert result == {"MY_KEY": "value", "NESTED_SUB_KEY": "data"}

    def test_keys_with_dashes(self):
        """flatten_dict preserves dashes in keys."""
        result = flatten_dict({"my-key": "value"})
        assert result == {"MY-KEY": "value"}

    def test_keys_with_dots(self):
        """flatten_dict preserves dots in keys."""
        result = flatten_dict({"my.key": "value"})
        assert result == {"MY.KEY": "value"}

    def test_numeric_values_various_types(self):
        """flatten_dict converts various numeric types correctly."""
        result = flatten_dict({"int": 42, "float": 3.14, "negative": -5, "zero": 0})
        assert result == {"INT": "42", "FLOAT": "3.14", "NEGATIVE": "-5", "ZERO": "0"}

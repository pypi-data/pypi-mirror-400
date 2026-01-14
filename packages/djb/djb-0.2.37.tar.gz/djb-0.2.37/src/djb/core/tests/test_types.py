"""Tests for djb.types module."""

from __future__ import annotations


from djb.types import Mode, Platform


class TestMode:
    """Tests for Mode enum."""

    def test_mode_values(self):
        """Mode has expected values."""
        assert Mode.DEVELOPMENT.value == "development"
        assert Mode.STAGING.value == "staging"
        assert Mode.PRODUCTION.value == "production"

    def test_mode_str(self):
        """Mode.__str__ returns value."""
        assert str(Mode.DEVELOPMENT) == "development"
        assert str(Mode.STAGING) == "staging"
        assert str(Mode.PRODUCTION) == "production"

    def test_mode_parse_valid(self):
        """Mode.parse returns correct enum for valid values."""
        assert Mode.parse("development") == Mode.DEVELOPMENT
        assert Mode.parse("staging") == Mode.STAGING
        assert Mode.parse("production") == Mode.PRODUCTION

    def test_mode_parse_case_insensitive(self):
        """Mode.parse is case insensitive."""
        assert Mode.parse("DEVELOPMENT") == Mode.DEVELOPMENT
        assert Mode.parse("Development") == Mode.DEVELOPMENT
        assert Mode.parse("STAGING") == Mode.STAGING

    def test_mode_parse_none(self):
        """Mode.parse handles None input."""
        assert Mode.parse(None) is None
        assert Mode.parse(None, default=Mode.DEVELOPMENT) == Mode.DEVELOPMENT

    def test_mode_parse_invalid(self):
        """Mode.parse returns None for invalid values."""
        assert Mode.parse("invalid") is None
        assert Mode.parse("invalid", default=Mode.DEVELOPMENT) == Mode.DEVELOPMENT
        assert Mode.parse("") is None


class TestPlatform:
    """Tests for Platform enum."""

    def test_platform_values(self):
        """Platform has expected values."""
        assert Platform.HEROKU.value == "heroku"

    def test_platform_str(self):
        """Platform.__str__ returns value."""
        assert str(Platform.HEROKU) == "heroku"

    def test_platform_parse_valid(self):
        """Platform.parse returns correct enum for valid values."""
        assert Platform.parse("heroku") == Platform.HEROKU

    def test_platform_parse_case_insensitive(self):
        """Platform.parse is case insensitive."""
        assert Platform.parse("HEROKU") == Platform.HEROKU
        assert Platform.parse("Heroku") == Platform.HEROKU

    def test_platform_parse_none(self):
        """Platform.parse handles None input."""
        assert Platform.parse(None) is None
        assert Platform.parse(None, default=Platform.HEROKU) == Platform.HEROKU

    def test_platform_parse_invalid(self):
        """Platform.parse returns None for invalid values."""
        assert Platform.parse("invalid") is None
        assert Platform.parse("invalid", default=Platform.HEROKU) == Platform.HEROKU
        assert Platform.parse("") is None


class TestModeIsStrEnum:
    """Tests for Mode StrEnum behavior."""

    def test_mode_in_string_operations(self):
        """Mode works in string operations."""
        mode = Mode.DEVELOPMENT
        assert mode == "development"
        assert f"mode: {mode}" == "mode: development"

    def test_mode_in_dict_keys(self):
        """Mode works as dict keys and compares to strings."""
        config = {Mode.DEVELOPMENT: "dev config", Mode.PRODUCTION: "prod config"}
        # Can access by Mode
        assert config[Mode.DEVELOPMENT] == "dev config"


class TestPlatformIsStrEnum:
    """Tests for Platform StrEnum behavior."""

    def test_platform_in_string_operations(self):
        """Platform works in string operations."""
        platform = Platform.HEROKU
        assert platform == "heroku"
        assert f"platform: {platform}" == "platform: heroku"

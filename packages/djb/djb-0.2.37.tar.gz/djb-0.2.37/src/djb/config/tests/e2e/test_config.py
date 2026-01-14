"""E2E tests for djb.config module."""

from __future__ import annotations

import json

import pytest
import tomlkit.exceptions

pytestmark = pytest.mark.e2e_marker

from djb.config import (
    ConfigValidationError,
    DjbConfig,
    get_djb_config,
    get_config_dir,
    get_field_descriptor,
    get_project_name_from_pyproject,
    normalize_project_name,
)
from djb.config.fields import HetznerConfig
from djb.types import Mode, Platform
from djb.config.storage.base import Provenance
from djb.config.storage.types import (
    CoreConfigIO,
    LocalConfigIO,
    ProjectConfigType,
)
from djb.config.storage.io import (
    DictConfigIO,
    EnvConfigIO,
)

from .conftest import make_local_config_io, make_project_config_type


def _source_matches(
    source: Provenance | None,
    expected: type | object,
) -> bool:
    """Check if a Provenance tuple contains an expected ConfigType/IO.

    Args:
        source: The provenance from cfg.get_source(field).
        expected: Either a ConfigType/IO class (type) or instance.

    Returns:
        True if the source matches.
    """
    if source is None:
        return False

    # Provenance tuple - check if any element matches
    for store in source:
        # Check class type or identity
        if isinstance(expected, type):
            if isinstance(store, expected):
                return True
        elif store == expected or type(store) == type(expected):
            return True
    return False


def _source_is_override(source: Provenance | None) -> bool:
    """Check if a source is the override DictConfigIO (name='override').

    Args:
        source: The provenance from cfg.get_source(field).

    Returns:
        True if the source is a DictConfigIO with name='override'.
    """
    if source is None:
        return False
    for store in source:
        if isinstance(store, DictConfigIO) and store.name == "override":
            return True
    return False


class TestConfigPaths:
    """Tests for config path helpers."""

    def test_get_config_dir(self, project_dir):
        """get_config_dir returns .djb directory."""
        result = get_config_dir(project_dir)
        assert result == project_dir / ".djb"

    def test_get_path_local(self, project_dir, make_djb_config):
        """LOCAL_IO.get_path returns local.toml path."""
        result = make_local_config_io(make_djb_config).resolve_path()
        assert result == project_dir / ".djb" / "local.toml"


class TestLoadSaveConfig:
    """Tests for ConfigStore.load() and ConfigStore.save()."""

    def test_load_missing(self, make_djb_config):
        """load returns empty dict when config file doesn't exist."""
        result = make_local_config_io(make_djb_config).load()
        assert result == {}

    def test_load_exists(self, make_config_file, make_djb_config):
        """load loads existing config file."""
        make_config_file({"name": "John", "email": "john@example.com"})

        result = make_local_config_io(make_djb_config).load()
        assert result == {"name": "John", "email": "john@example.com"}

    def test_load_empty(self, make_config_file, make_djb_config):
        """load returns empty dict for empty config file."""
        make_config_file({})

        result = make_local_config_io(make_djb_config).load()
        assert result == {}

    def test_load_rejects_invalid_toml(self, make_config_file, make_djb_config):
        """load raises when TOML is invalid."""
        make_config_file("invalid = [")  # Invalid TOML syntax

        with pytest.raises(tomlkit.exceptions.ParseError):
            make_local_config_io(make_djb_config).load()

    def test_save_creates_directory(self, project_dir, make_djb_config):
        """save creates .djb directory when needed."""
        data = {"name": "John"}
        make_local_config_io(make_djb_config).save(data)

        assert (project_dir / ".djb").exists()
        assert (project_dir / ".djb" / "local.toml").exists()

    def test_save_content(self, make_djb_config):
        """save writes correct TOML content."""
        data = {"name": "John", "email": "john@example.com"}
        make_local_config_io(make_djb_config).save(data)

        result = make_local_config_io(make_djb_config).load()
        assert result == data

    def test_load_missing_files(self, project_dir, mock_cmd_runner):
        """get_djb_config uses defaults when config files don't exist."""
        # Mock git config to isolate from system git config
        mock_cmd_runner.run.return_value = type("Result", (), {"returncode": 1, "stdout": ""})()
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        # Config uses defaults when no files exist
        assert cfg.name is None
        assert cfg.email is None
        assert cfg.mode == Mode.DEVELOPMENT  # default
        assert cfg.platform == Platform.HEROKU  # default

    def test_load_merges_both(self, project_dir, make_config_file):
        """get_djb_config merges project and local configs."""
        # Project config
        make_config_file(
            {"seed_command": "myapp.cli:seed", "platform": "heroku"}, config_type="project"
        )
        # Local config
        make_config_file({"name": "John", "email": "john@example.com"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.seed_command == "myapp.cli:seed"
        assert cfg.platform == Platform.HEROKU
        assert cfg.name == "John"
        assert cfg.email == "john@example.com"

    def test_local_config_overrides_project_config(self, project_dir, make_config_file):
        """get_djb_config local config takes precedence over project config."""
        # Project config sets seed_command
        make_config_file({"seed_command": "myapp.cli:seed"}, config_type="project")
        # Local config overrides seed_command
        make_config_file({"seed_command": "myapp.cli:local_seed"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.seed_command == "myapp.cli:local_seed"


class TestGetProjectNameFromPyproject:
    """Tests for get_project_name_from_pyproject."""

    def test_reads_project_name(self, project_dir):
        """get_project_name_from_pyproject reads project name from pyproject.toml."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\nversion = "1.0.0"\n')

        result = get_project_name_from_pyproject(project_dir)
        assert result == "myproject"

    def test_normalizes_project_name(self, project_dir):
        """get_project_name_from_pyproject normalizes project name for DNS-safe values."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "My_Project.Name"\nversion = "1.0.0"\n')

        result = get_project_name_from_pyproject(project_dir)
        assert result == "my-project-name"

    def test_invalid_project_name_returns_none(self, project_dir):
        """get_project_name_from_pyproject returns None for invalid project name."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "My Project"\n')

        result = get_project_name_from_pyproject(project_dir)
        assert result is None

    def test_missing_pyproject(self, project_dir):
        """get_project_name_from_pyproject returns None when pyproject.toml doesn't exist."""
        result = get_project_name_from_pyproject(project_dir)
        assert result is None

    def test_missing_project_section(self, project_dir):
        """get_project_name_from_pyproject returns None when no project section."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text("[tool.pytest]\n")

        result = get_project_name_from_pyproject(project_dir)
        assert result is None

    def test_missing_name_field(self, project_dir):
        """get_project_name_from_pyproject returns None when project section has no name."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n')

        result = get_project_name_from_pyproject(project_dir)
        assert result is None

    def test_invalid_toml(self, project_dir):
        """get_project_name_from_pyproject returns None for invalid TOML content."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text("this is not valid toml [[[")

        result = get_project_name_from_pyproject(project_dir)
        assert result is None


class TestDjbConfig:
    """Tests for DjbConfig class."""

    def test_default_values(self, project_dir, mock_cmd_runner):
        """DjbConfig has correct default values."""
        # Mock git config to isolate from system git config
        mock_cmd_runner.run.return_value = type("Result", (), {"returncode": 1, "stdout": ""})()
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.project_dir == project_dir
        # project_name is derived from directory name
        assert cfg.project_name is not None
        assert cfg.mode == Mode.DEVELOPMENT
        assert cfg.platform == Platform.HEROKU
        assert cfg.name is None
        assert cfg.email is None

    def test_project_name_gets_normalized(self, project_dir, make_djb_config):
        """DjbConfig normalizes project_name to DNS-safe format."""
        make_project_config_type(make_djb_config).save({"project_name": "Bad_Project"})
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        # "Bad_Project" normalizes to "bad-project" (lowercase, underscores -> hyphens)
        assert cfg.project_name == "bad-project"

    def test_validation_rejects_invalid_email(self, project_dir, make_djb_config):
        """DjbConfig validation rejects invalid email."""
        make_local_config_io(make_djb_config).save({"email": "not-an-email"})
        make_project_config_type(make_djb_config).save({"project_name": "test"})
        with pytest.raises(ConfigValidationError, match="email"):
            get_djb_config(DjbConfig(project_dir=project_dir))

    def test_validation_rejects_invalid_seed_command(self, project_dir, make_djb_config):
        """DjbConfig validation rejects invalid seed_command."""
        make_project_config_type(make_djb_config).save(
            {"project_name": "test", "seed_command": "not-a-command"}
        )
        with pytest.raises(ConfigValidationError, match="module.path:attribute"):
            get_djb_config(DjbConfig(project_dir=project_dir))

    def test_non_string_yaml_types_fall_back_to_directory_name(self, project_dir, make_djb_config):
        """DjbConfig falls back to directory name for non-normalizable types."""
        # When loading from config files, YAML can produce non-string types.
        # Non-strings like booleans can't be normalized, so they fall back to
        # the next source in the chain (directory name).
        make_project_config_type(make_djb_config).save({"project_name": True})  # YAML boolean
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        # Boolean True can't be normalized, so falls back to directory name
        expected_name = normalize_project_name(project_dir.name)
        assert cfg.project_name == expected_name

    def test_overrides_applied(self, project_dir):
        """get_djb_config applies overrides."""
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                name="John",
                email="john@example.com",
                mode=Mode.PRODUCTION,
            )
        )

        assert cfg.name == "John"
        assert cfg.email == "john@example.com"
        assert cfg.mode == Mode.PRODUCTION

    def test_ignores_none_overrides(self, project_dir, make_djb_config):
        """get_djb_config ignores None values in overrides."""
        # Set up a config file with name
        make_local_config_io(make_djb_config).save({"name": "John"})

        # Override with None should preserve the file value
        # (None kwargs are filtered out before passing to _resolve_config)
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                email="john@example.com",
            )
        )

        # name should be preserved since override was None
        assert cfg.name == "John"
        assert cfg.email == "john@example.com"

    def test_tracks_cli_overrides(self, project_dir):
        """get_djb_config tracks CLI overrides via provenance."""
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
                name="John",
            )
        )

        # Access fields
        assert cfg.mode == Mode.STAGING
        assert cfg.name == "John"

        # CLI overrides are tracked in provenance as explicit sources
        assert cfg.is_explicit("mode")
        assert cfg.is_explicit("name")
        # project_dir is a DERIVED field - doesn't track provenance
        # (it's resolved via find_project_root, not the config layer chain)
        assert cfg.project_dir == project_dir
        # Verify provenance is tracked for regular fields
        assert cfg.get_source("mode") is not None
        assert cfg.get_source("name") is not None

    def test_save(self, project_dir, make_djb_config):
        """DjbConfig.save persists config to file."""
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                name="John",
                email="john@example.com",
                mode=Mode.STAGING,
                platform=Platform.HEROKU,
            )
        )
        cfg.save()

        # User settings go to local config (mode-aware: [staging] section)
        local = make_local_config_io(make_djb_config, Mode.STAGING).load()
        assert local["name"] == "John"
        assert local["email"] == "john@example.com"
        assert local["mode"] == "staging"

        # Project settings go to project config (mode-aware: [staging] section)
        project = make_project_config_type(make_djb_config, Mode.STAGING).load()
        assert project["platform"] == "heroku"

    def test_save_removes_none_values(self, project_dir, mock_cmd_runner, make_djb_config):
        """DjbConfig.save doesn't write None values."""
        # Mock git config to isolate from system git config
        mock_cmd_runner.run.return_value = type("Result", (), {"returncode": 1, "stdout": ""})()
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                name="John",
            )
        )
        cfg.save()

        loaded = make_local_config_io(make_djb_config).load()
        assert loaded["name"] == "John"
        assert "email" not in loaded

    def test_set_mode(self, project_dir, make_djb_config):
        """DjbConfig.set saves mode to local.toml."""
        # Create existing config
        make_local_config_io(make_djb_config).save({"name": "John", "mode": "development"})

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.PRODUCTION,
            )
        )
        cfg.set("mode", str(cfg.mode))

        loaded = make_local_config_io(make_djb_config).load()
        assert loaded["mode"] == "production"
        assert loaded["name"] == "John"  # Preserved

    def test_set_platform(self, project_dir, make_djb_config):
        """DjbConfig.set saves platform to project.toml."""
        # Create existing config
        make_project_config_type(make_djb_config).save({"project_name": "myproject"})

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                platform=Platform.K8S,
            )
        )
        cfg.set("platform", str(cfg.platform))

        # Default mode is DEVELOPMENT, so read from [development] section
        loaded = make_project_config_type(make_djb_config, Mode.DEVELOPMENT).load()
        assert loaded["platform"] == "k8s"
        # project_name was saved to root, check it there
        root_loaded = make_project_config_type(make_djb_config).load()
        assert root_loaded["project_name"] == "myproject"  # Preserved

    def test_to_dict(self, project_dir):
        """DjbConfig.to_dict returns JSON-serializable dictionary."""
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                name="John",
                email="john@example.com",
                mode=Mode.STAGING,
                platform=Platform.HEROKU,
            )
        )
        result = cfg.to_dict()

        assert result["project_dir"] == str(project_dir)
        assert result["name"] == "John"
        assert result["email"] == "john@example.com"
        assert result["mode"] == "staging"
        assert result["platform"] == "heroku"
        assert "_provenance" not in result

    def test_to_dict_excludes_provenance(self, project_dir):
        """DjbConfig.to_dict excludes _provenance."""
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                name="John",
            )
        )

        result = cfg.to_dict()
        assert "_provenance" not in result

    def test_to_json(self, project_dir):
        """DjbConfig.to_json returns valid JSON string."""
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                name="John",
            )
        )
        result = cfg.to_json()

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["project_name"] is not None
        assert parsed["name"] == "John"

    def test_to_json_custom_indent(self, project_dir):
        """DjbConfig.to_json respects indent parameter."""
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
            )
        )

        # Default indent is 2
        result_default = cfg.to_json()
        assert "  " in result_default

        # Custom indent of 4
        result_4 = cfg.to_json(indent=4)
        assert "    " in result_4


class TestDjbGetConfig:
    """Tests for get_djb_config() factory function."""

    def test_loads_from_file(self, project_dir, make_djb_config):
        """get_djb_config loads configuration from config file."""
        make_local_config_io(make_djb_config).save(
            {"name": "John", "email": "john@example.com", "mode": "staging"}
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.name == "John"
        assert cfg.email == "john@example.com"
        assert cfg.mode == Mode.STAGING

    def test_env_overrides_file(self, project_dir, make_djb_config):
        """get_djb_config environment variables override file config."""
        make_local_config_io(make_djb_config).save({"name": "John"})

        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={"DJB_NAME": "Jane"},
        )
        assert cfg.name == "Jane"

    def test_project_name_from_pyproject(self, project_dir):
        """get_djb_config project_name falls back to pyproject.toml."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.project_name == "myproject"

    def test_invalid_pyproject_name_falls_back_to_directory(self, project_dir):
        """get_djb_config falls back to directory name for invalid pyproject name."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "My Project"\n')

        # Invalid pyproject name (contains space) is skipped, falls back to directory
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        expected = normalize_project_name(project_dir.name)
        assert cfg.project_name == expected

    def test_project_name_config_overrides_pyproject(self, project_dir, make_djb_config):
        """get_djb_config config file project_name overrides pyproject.toml."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "pyproject-name"\n')
        make_project_config_type(make_djb_config).save({"project_name": "config-name"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.project_name == "config-name"

    def test_default_mode(self, project_dir):
        """get_djb_config default mode is DEVELOPMENT."""
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.mode == Mode.DEVELOPMENT

    def test_default_target(self, project_dir):
        """get_djb_config default platform is HEROKU."""
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.platform == Platform.HEROKU

    def test_env_mode(self, project_dir):
        """get_djb_config reads DJB_MODE environment variable."""
        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={"DJB_MODE": "production"},
        )
        assert cfg.mode == Mode.PRODUCTION

    def test_env_platform(self, project_dir):
        """get_djb_config reads DJB_PLATFORM environment variable."""
        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={"DJB_PLATFORM": "heroku"},
        )
        assert cfg.platform == Platform.HEROKU

    def test_project_dir_defaults_to_passed_root(self, project_dir):
        """get_djb_config project_dir defaults to passed project_root."""
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.project_dir == project_dir

    def test_env_project_dir_used_for_config_lookup(
        self, project_dir, monkeypatch, make_config_file
    ):
        """get_djb_config uses DJB_PROJECT_DIR to locate config files."""
        make_config_file({"name": "John"})

        other_dir = project_dir / "other"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)
        # Set DJB_PROJECT_DIR in os.environ (find_project_root reads from os.environ)
        monkeypatch.setenv("DJB_PROJECT_DIR", str(project_dir))

        cfg = get_djb_config()
        assert cfg.project_dir == project_dir
        assert cfg.name == "John"

    def test_project_root_overrides_env_project_dir(self, project_dir):
        """get_djb_config explicit project_root wins over DJB_PROJECT_DIR."""
        env_root = project_dir / "env"
        env_root.mkdir()
        (env_root / "pyproject.toml").write_text('[project]\nname = "env"\n')

        project_root = project_dir / "root"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text('[project]\nname = "root"\n')

        cfg = get_djb_config(
            DjbConfig(project_dir=project_root),
            env={"DJB_PROJECT_DIR": str(env_root)},
        )
        assert cfg.project_dir == project_root
        assert cfg.project_name == "root"

    @pytest.mark.parametrize(
        "field,value,expected",
        [
            ("mode", "invalid_mode", Mode.DEVELOPMENT),
            ("platform", "invalid_platform", Platform.HEROKU),
            ("mode", "true", Mode.DEVELOPMENT),  # YAML parses as bool
            ("platform", "true", Platform.HEROKU),  # YAML parses as bool
        ],
    )
    def test_invalid_enum_falls_back_to_default(
        self, project_dir, make_config_file, field, value, expected
    ):
        """get_djb_config invalid enum values fall back to defaults."""
        make_config_file({field: value})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        assert getattr(cfg, field) == expected


class TestConfigPriority:
    """Tests for configuration priority (CLI > env > file > default)."""

    def test_cli_overrides_env(self, project_dir):
        """get_djb_config CLI overrides take precedence over env vars."""
        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir, mode=Mode.PRODUCTION),
            env={"DJB_MODE": "staging"},
        )
        assert cfg.mode == Mode.PRODUCTION


class TestDualSourceConfig:
    """Tests for dual-source configuration (project.toml + local.toml)."""

    def test_load_project_config_missing(self, make_djb_config):
        """PROJECT_TYPE.load returns empty dict when project config doesn't exist."""
        result = make_project_config_type(make_djb_config).load()
        assert result == {}

    def test_load_project_config_exists(self, make_config_file, make_djb_config):
        """PROJECT_TYPE.load loads existing project config file."""
        make_config_file(
            {"seed_command": "myapp.cli:seed", "project_name": "myproject"}, config_type="project"
        )

        # Use production mode to avoid mode-prefixed section reading
        result = make_project_config_type(make_djb_config, mode=Mode.PRODUCTION).load()
        assert result == {"seed_command": "myapp.cli:seed", "project_name": "myproject"}

    def test_save_project_config(self, make_djb_config):
        """PROJECT_TYPE.save saves project config file."""
        make_project_config_type(make_djb_config).save({"seed_command": "myapp.cli:seed"})

        result = make_project_config_type(make_djb_config).load()
        assert result == {"seed_command": "myapp.cli:seed"}


class TestDjbConfigFreshInstances:
    """Tests for get_djb_config() returning fresh instances."""

    def test_returns_fresh_instance_each_call(self, project_dir):
        """get_djb_config returns a fresh instance on each call."""
        cfg1 = get_djb_config(DjbConfig(project_dir=project_dir, mode=Mode.PRODUCTION))
        cfg2 = get_djb_config(DjbConfig(project_dir=project_dir, mode=Mode.PRODUCTION))

        # Different instances
        assert cfg1 is not cfg2
        # But same values
        assert cfg1.mode == cfg2.mode == Mode.PRODUCTION

    def test_can_call_with_different_overrides(self, project_dir):
        """get_djb_config can be called with different overrides each time."""
        cfg1 = get_djb_config(DjbConfig(project_dir=project_dir, mode=Mode.PRODUCTION))
        cfg2 = get_djb_config(DjbConfig(project_dir=project_dir, mode=Mode.STAGING))

        assert cfg1.mode == Mode.PRODUCTION
        assert cfg2.mode == Mode.STAGING


class TestDjbConfigProvenance:
    """Tests for DjbConfig provenance tracking methods."""

    def test_is_explicit_checks_source(self, project_dir, make_djb_config):
        """DjbConfig.is_explicit checks provenance source."""
        # Create actual config file
        make_project_config_type(make_djb_config).save({"project_name": "from-file"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        assert cfg.is_explicit("project_name") is True
        assert cfg.is_explicit("name") is False  # Not in provenance

    def test_is_derived_checks_source(self, project_dir, mock_cmd_runner):
        """DjbConfig.is_derived checks provenance source."""
        # Create pyproject.toml for derived project_name
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "from-pyproject"\n')

        # Mock git config to isolate from system git config
        mock_cmd_runner.run.return_value = type("Result", (), {"returncode": 1, "stdout": ""})()
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        assert cfg.is_derived("project_name") is True
        assert cfg.is_derived("name") is False  # Not in provenance

    def test_has_no_source_returns_true_for_missing(
        self, project_dir, mock_cmd_runner, make_djb_config
    ):
        """DjbConfig.is_configured returns False for fields without provenance."""
        # Create config with project_name only
        make_project_config_type(make_djb_config).save({"project_name": "test"})

        # Mock git config to isolate from system git config
        mock_cmd_runner.run.return_value = type("Result", (), {"returncode": 1, "stdout": ""})()
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # project_name is configured in config file
        assert cfg.is_configured("project_name") is True
        # name has no configured value (just default None)
        assert cfg.is_configured("name") is False

    def test_get_source_returns_source(self, project_dir, mock_cmd_runner):
        """DjbConfig.get_source returns the source for a field."""
        # Create pyproject.toml for derived project_name
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "from-pyproject"\n')

        # Mock git config to isolate from system git config
        mock_cmd_runner.run.return_value = type("Result", (), {"returncode": 1, "stdout": ""})()
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # project_name comes from pyproject.toml (derived source)
        assert cfg.get_source("project_name") is not None
        assert cfg.is_derived("project_name")
        assert cfg.get_source("name") is None


class TestDjbGetConfigProvenance:
    """Tests for get_djb_config() provenance tracking."""

    def test_tracks_project_name_from_config_file(self, project_dir, make_djb_config):
        """get_djb_config tracks project_name provenance from config file."""
        make_project_config_type(make_djb_config).save({"project_name": "myproject"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.project_name == "myproject"
        assert _source_matches(cfg.get_source("project_name"), ProjectConfigType)
        assert cfg.is_explicit("project_name") is True

    def test_tracks_project_name_from_pyproject(self, project_dir):
        """get_djb_config tracks project_name provenance from pyproject.toml."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "pyprojectname"\n')

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.project_name == "pyprojectname"
        # pyproject.toml [project] section is a derived source
        assert cfg.get_source("project_name") is not None
        assert cfg.is_derived("project_name") is True

    def test_tracks_project_name_from_dir_fallback(self, project_dir):
        """get_djb_config tracks project_name provenance from directory name fallback."""
        # No config, no pyproject.toml - should derive from directory name
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.project_name is not None
        # Provenance tuple with CwdNameConfigIO
        source = cfg.get_source("project_name")
        assert source is not None
        assert cfg.is_derived("project_name") is True

    def test_tracks_name_from_local_config(self, project_dir, make_djb_config):
        """get_djb_config tracks name provenance from local config."""
        make_local_config_io(make_djb_config).save({"name": "John"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.name == "John"
        assert _source_matches(cfg.get_source("name"), LocalConfigIO)
        assert cfg.is_explicit("name") is True

    def test_env_overrides_file_config(self, project_dir, make_djb_config):
        """get_djb_config tracks env var provenance when it overrides file."""
        make_project_config_type(make_djb_config).save({"project_name": "filename"})

        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={"DJB_PROJECT_NAME": "envname"},
        )
        assert cfg.project_name == "envname"
        assert _source_matches(cfg.get_source("project_name"), EnvConfigIO)

    def test_overrides_updates_provenance(self, project_dir, make_djb_config):
        """get_djb_config overrides update provenance to CLI source."""
        make_project_config_type(make_djb_config).save({"project_name": "filename"})

        # First get without override
        cfg1 = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg1.project_name == "filename"
        assert _source_matches(cfg1.get_source("project_name"), ProjectConfigType)

        # Second get with override
        # Note: We don't call project_name as CLI override since it's not in the function signature
        # But mode is, so test that instead
        cfg2 = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
            )
        )
        assert cfg2.mode == Mode.STAGING
        assert _source_is_override(cfg2.get_source("mode"))

    def test_project_name_always_has_value(self, project_dir):
        """get_djb_config project_name is always resolved (never None)."""
        # No config, no pyproject - should still derive from dir name
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.project_name is not None
        assert cfg.project_name != ""


class TestLogLevelConfig:
    """Tests for log_level configuration field."""

    def test_default_log_level(self, project_dir):
        """DjbConfig log_level defaults to 'info'."""
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.log_level == "info"

    def test_log_level_from_project_config(self, project_dir, make_djb_config):
        """DjbConfig log_level loaded from project.toml."""
        make_project_config_type(make_djb_config).save({"log_level": "debug"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.log_level == "debug"
        assert _source_matches(cfg.get_source("log_level"), ProjectConfigType)

    def test_log_level_from_local_config(self, project_dir, make_djb_config):
        """DjbConfig log_level loaded from local.toml."""
        make_local_config_io(make_djb_config).save({"log_level": "warning"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.log_level == "warning"
        assert _source_matches(cfg.get_source("log_level"), LocalConfigIO)

    def test_local_config_overrides_project_config(self, project_dir, make_djb_config):
        """DjbConfig local.toml log_level overrides project.toml."""
        make_project_config_type(make_djb_config).save({"log_level": "info"})
        make_local_config_io(make_djb_config).save({"log_level": "debug"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.log_level == "debug"
        assert _source_matches(cfg.get_source("log_level"), LocalConfigIO)

    def test_log_level_from_env(self, project_dir):
        """DjbConfig reads DJB_LOG_LEVEL environment variable."""
        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={"DJB_LOG_LEVEL": "error"},
        )
        assert cfg.log_level == "error"
        assert _source_matches(cfg.get_source("log_level"), EnvConfigIO)

    def test_env_overrides_config_file(self, project_dir, make_djb_config):
        """DjbConfig DJB_LOG_LEVEL overrides config file values."""
        make_project_config_type(make_djb_config).save({"log_level": "info"})

        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={"DJB_LOG_LEVEL": "debug"},
        )
        assert cfg.log_level == "debug"
        assert _source_matches(cfg.get_source("log_level"), EnvConfigIO)

    def test_cli_overrides_env(self, project_dir):
        """DjbConfig CLI override has highest priority."""
        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir, log_level="error"),
            env={"DJB_LOG_LEVEL": "warning"},
        )
        assert cfg.log_level == "error"
        assert _source_is_override(cfg.get_source("log_level"))

    def test_log_level_case_insensitive(self, project_dir, make_djb_config):
        """DjbConfig log_level is normalized to lowercase."""
        make_project_config_type(make_djb_config).save({"log_level": "DEBUG"})

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))
        assert cfg.log_level == "debug"

    @pytest.mark.parametrize("level", ["error", "warning", "info", "note", "debug"])
    def test_log_level_validation_accepts_valid_values(self, project_dir, level):
        """DjbConfig accepts all valid log levels."""
        cfg = get_djb_config(DjbConfig(project_dir=project_dir, log_level=level))
        assert cfg.log_level == level

    def test_log_level_validation_rejects_invalid_value(self, project_dir, make_djb_config):
        """DjbConfig rejects invalid log level."""
        make_project_config_type(make_djb_config).save({"log_level": "verbose"})
        with pytest.raises(ConfigValidationError, match="Invalid log_level"):
            get_djb_config(DjbConfig(project_dir=project_dir))

    def test_log_level_validation_rejects_invalid_yaml_types(self, project_dir, make_djb_config):
        """DjbConfig rejects non-string YAML types for log_level."""
        # When loading from config files, YAML can produce non-string types.
        # Booleans like True normalize to "true" which fails enum validation.
        make_project_config_type(make_djb_config).save({"log_level": True})  # YAML boolean
        with pytest.raises(ConfigValidationError, match="Invalid log_level"):
            get_djb_config(DjbConfig(project_dir=project_dir))


class TestNestedHetznerConfig:
    """Tests for nested HetznerConfig resolution with mode overrides."""

    def test_hetzner_defaults_from_core(self, project_dir):
        """HetznerConfig uses defaults from core.toml."""
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # Defaults from core.toml
        # HetznerServerType/etc inherit from (str, Enum) so direct comparison works
        assert cfg.hetzner.default_server_type == "cx23"
        assert cfg.hetzner.default_location == "nbg1"
        assert cfg.hetzner.default_image == "ubuntu-24.04"

    def test_hetzner_override_from_project_config(self, project_dir):
        """HetznerConfig can be overridden in project.toml [hetzner] section."""
        # Write nested config using raw TOML
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
default_server_type = "cx32"
default_location = "fsn1"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        assert cfg.hetzner.default_server_type == "cx32"
        assert cfg.hetzner.default_location == "fsn1"
        assert cfg.hetzner.default_image == "ubuntu-24.04"  # Still from core.toml

    def test_hetzner_partial_override_in_staging(self, project_dir):
        """HetznerConfig supports partial override in [staging.hetzner] section."""
        # Write root [hetzner] and partial [staging.hetzner] override
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
default_server_type = "cx22"
default_location = "nbg1"
default_image = "ubuntu-24.04"

[staging.hetzner]
default_server_type = "cx32"
"""
        )

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
            )
        )

        # default_server_type is overridden
        assert cfg.hetzner.default_server_type == "cx32"
        # default_location and default_image are inherited from root [hetzner]
        assert cfg.hetzner.default_location == "nbg1"
        assert cfg.hetzner.default_image == "ubuntu-24.04"

    def test_hetzner_full_override_in_staging(self, project_dir):
        """HetznerConfig supports full override in [staging.hetzner] section."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
default_server_type = "cx22"
default_location = "nbg1"
default_image = "ubuntu-24.04"

[staging.hetzner]
default_server_type = "cx42"
default_location = "hel1"
default_image = "debian-12"
"""
        )

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
            )
        )

        assert cfg.hetzner.default_server_type == "cx42"
        assert cfg.hetzner.default_location == "hel1"
        assert cfg.hetzner.default_image == "debian-12"

    def test_hetzner_production_ignores_staging_override(self, project_dir):
        """Production mode ignores [staging.hetzner] override."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
default_server_type = "cx22"
default_location = "nbg1"

[staging.hetzner]
default_server_type = "cx32"
"""
        )

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.PRODUCTION,
            )
        )

        # Production uses root [hetzner], not [staging.hetzner]
        assert cfg.hetzner.default_server_type == "cx22"
        assert cfg.hetzner.default_location == "nbg1"

    def test_hetzner_development_override(self, project_dir):
        """HetznerConfig supports [development.hetzner] override."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
default_server_type = "cx22"

[development.hetzner]
default_server_type = "cx11"
"""
        )

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.DEVELOPMENT,
            )
        )

        assert cfg.hetzner.default_server_type == "cx11"

    def test_hetzner_accepts_unknown_values(self, project_dir):
        """HetznerConfig accepts unknown values with strict=False."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
default_server_type = "cx999"
default_location = "mars1"
default_image = "custom-image"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # Unknown values accepted as-is (for forward compatibility)
        # These are strings, not enums, since they don't match known values
        assert cfg.hetzner.default_server_type == "cx999"
        assert cfg.hetzner.default_location == "mars1"
        assert cfg.hetzner.default_image == "custom-image"

    def test_hetzner_override_from_env_var(self, project_dir):
        """HetznerConfig fields can be overridden via DJB_HETZNER_* env vars."""
        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={"DJB_HETZNER_DEFAULT_SERVER_TYPE": "cx52"},
        )

        # Env var overrides core.toml default
        assert cfg.hetzner.default_server_type == "cx52"
        # Other fields still from core.toml
        assert cfg.hetzner.default_location == "nbg1"
        assert cfg.hetzner.default_image == "ubuntu-24.04"

    def test_hetzner_env_var_overrides_project_config(self, project_dir):
        """Env var takes precedence over project.toml for nested fields."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
default_server_type = "cx32"
"""
        )

        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={"DJB_HETZNER_DEFAULT_SERVER_TYPE": "cx52"},
        )

        # Env var wins over project.toml
        assert cfg.hetzner.default_server_type == "cx52"

    def test_hetzner_instance_field_from_env_var(self, project_dir):
        """Instance fields (server_name, k8s.host) can be set via env vars."""
        cfg = get_djb_config(
            DjbConfig(project_dir=project_dir),
            env={
                "DJB_HETZNER_SERVER_NAME": "my-server",
                "DJB_K8S_HOST": "192.168.1.1",
            },
        )

        assert cfg.hetzner.server_name == "my-server"
        assert cfg.k8s.host == "192.168.1.1"
        # ssh_key_name not set, remains None
        assert cfg.hetzner.ssh_key_name is None

    def test_instance_fields_default_to_none(self, project_dir):
        """server_name/k8s.host/ssh_key_name are None when not configured."""
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        assert cfg.hetzner.server_name is None
        assert cfg.k8s.host is None
        assert cfg.hetzner.ssh_key_name is None

    def test_instance_fields_from_project_hetzner_section(self, project_dir):
        """Instance fields resolve from [hetzner] and [k8s] sections in project.toml."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
server_name = "prod-server"
ssh_key_name = "my-key"

[k8s]
host = "10.0.0.1"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        assert cfg.hetzner.server_name == "prod-server"
        assert cfg.k8s.host == "10.0.0.1"
        assert cfg.hetzner.ssh_key_name == "my-key"

    def test_instance_fields_mode_specific_staging(self, project_dir):
        """Instance fields in [staging.hetzner] and [staging.k8s] only apply in staging mode."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
server_name = "prod-server"

[staging.hetzner]
server_name = "staging-server"

[staging.k8s]
host = "10.0.0.2"
"""
        )

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
            )
        )

        assert cfg.hetzner.server_name == "staging-server"
        assert cfg.k8s.host == "10.0.0.2"

    def test_instance_fields_mode_specific_production(self, project_dir):
        """Production mode uses root [hetzner] and [k8s], ignores [staging.*]."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
server_name = "prod-server"

[k8s]
host = "10.0.0.1"

[staging.hetzner]
server_name = "staging-server"

[staging.k8s]
host = "10.0.0.2"
"""
        )

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.PRODUCTION,
            )
        )

        assert cfg.hetzner.server_name == "prod-server"
        assert cfg.k8s.host == "10.0.0.1"

    def test_default_field_local_overrides_project(self, project_dir):
        """local.toml [hetzner] overrides project.toml values."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()

        # project.toml has default_server_type = cx22
        project_file = config_dir / "project.toml"
        project_file.write_text(
            """
[hetzner]
default_server_type = "cx22"
"""
        )

        # local.toml overrides to cx11
        local_file = config_dir / "local.toml"
        local_file.write_text(
            """
[hetzner]
default_server_type = "cx11"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # local.toml wins over project.toml
        assert cfg.hetzner.default_server_type == "cx11"

    def test_instance_field_local_overrides_project(self, project_dir):
        """local.toml instance field overrides project.toml."""
        config_dir = project_dir / ".djb"
        config_dir.mkdir()

        project_file = config_dir / "project.toml"
        project_file.write_text(
            """
[hetzner]
server_name = "shared-server"
"""
        )

        local_file = config_dir / "local.toml"
        local_file.write_text(
            """
[hetzner]
server_name = "my-local-server"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        assert cfg.hetzner.server_name == "my-local-server"

    # === Mixed source tests (CRITICAL - fields from different config files) ===

    def test_mixed_sources_default_from_core_instance_from_project(self, project_dir):
        """Default fields from core.toml coexist with instance fields from project.toml.

        This is the primary use case: hetzner default_server_type comes from core.toml,
        while server_name/k8s.host come from project.toml after materialize runs.
        Both must resolve correctly in the same config.
        """
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
server_name = "my-server"
ssh_key_name = "deploy-key"

[k8s]
host = "192.168.1.100"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # Default fields from core.toml
        assert cfg.hetzner.default_server_type == "cx23"
        assert cfg.hetzner.default_location == "nbg1"
        assert cfg.hetzner.default_image == "ubuntu-24.04"

        # Instance fields from project.toml
        assert cfg.hetzner.server_name == "my-server"
        assert cfg.k8s.host == "192.168.1.100"
        assert cfg.hetzner.ssh_key_name == "deploy-key"

    def test_mixed_sources_with_mode_override(self, project_dir):
        """Staging mode: default field overridden in project, instance field in staging section.

        - default_server_type: core.toml default, overridden in project.toml [staging.hetzner]
        - server_name: only in project.toml [staging.hetzner]
        Both resolve correctly for staging mode.
        """
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
server_name = "prod-server"

[k8s]
host = "10.0.0.1"

[staging.hetzner]
default_server_type = "cx32"
server_name = "staging-server"

[staging.k8s]
host = "10.0.0.2"
"""
        )

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.PRODUCTION,
            )
        )

        # Production instance fields
        assert cfg.hetzner.server_name == "prod-server"
        assert cfg.k8s.host == "10.0.0.1"

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
            )
        )

        # Staging overrides default_server_type
        assert cfg.hetzner.default_server_type == "cx32"
        # Other defaults from core.toml
        assert cfg.hetzner.default_location == "nbg1"
        assert cfg.hetzner.default_image == "ubuntu-24.04"

        # Staging instance fields
        assert cfg.hetzner.server_name == "staging-server"
        assert cfg.k8s.host == "10.0.0.2"

    def test_mixed_sources_three_layers(self, project_dir):
        """Fields can come from core, project, and local simultaneously.

        - default_server_type: from core.toml (not overridden)
        - default_location: from project.toml [hetzner] (overrides core)
        - default_image: from local.toml [hetzner] (overrides both)
        - server_name: from project.toml [hetzner]
        All four fields resolve correctly in one HetznerConfig.
        """
        config_dir = project_dir / ".djb"
        config_dir.mkdir()

        project_file = config_dir / "project.toml"
        project_file.write_text(
            """
[hetzner]
default_location = "fsn1"
server_name = "my-server"
"""
        )

        local_file = config_dir / "local.toml"
        local_file.write_text(
            """
[hetzner]
default_image = "debian-12"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # default_server_type from core.toml (unchanged)
        assert cfg.hetzner.default_server_type == "cx23"
        # default_location from project.toml
        assert cfg.hetzner.default_location == "fsn1"
        # default_image from local.toml
        assert cfg.hetzner.default_image == "debian-12"
        # server_name from project.toml
        assert cfg.hetzner.server_name == "my-server"


class TestGetFieldDescriptor:
    """Tests for get_field_descriptor with nested path support."""

    def test_returns_descriptor_for_flat_field(self):
        """get_field_descriptor returns descriptor for flat fields."""
        result = get_field_descriptor("project_name")
        assert result.field_name == "project_name"
        assert result.config_storage == ProjectConfigType

    def test_returns_descriptor_for_nested_field(self):
        """get_field_descriptor returns descriptor for nested fields with dot notation."""
        result = get_field_descriptor("hetzner.default_server_type")
        assert result.field_name == "default_server_type"
        assert result.nested_field_prefix == "hetzner"
        assert result.config_storage == CoreConfigIO

    def test_raises_for_unknown_section(self):
        """get_field_descriptor raises AttributeError for unknown section."""
        with pytest.raises(AttributeError):
            get_field_descriptor("nonexistent.field")

    def test_raises_for_unknown_flat_field(self):
        """get_field_descriptor raises AttributeError for unknown flat field."""
        with pytest.raises(AttributeError):
            get_field_descriptor("nonexistent")

    def test_raises_for_unknown_nested_field(self):
        """get_field_descriptor raises AttributeError for unknown nested field."""
        with pytest.raises(AttributeError, match="has no field 'nonexistent'"):
            get_field_descriptor("hetzner.nonexistent")

    def test_raises_for_non_nested_section(self):
        """get_field_descriptor raises AttributeError when section is not a nested config."""
        # project_name is a flat field, not a section
        with pytest.raises(AttributeError):
            get_field_descriptor("project_name.something")

    def test_sets_nested_field_prefix_only_for_nested(self):
        """get_field_descriptor only sets nested_field_prefix for nested fields."""
        flat = get_field_descriptor("project_name")
        nested = get_field_descriptor("hetzner.default_server_type")

        # Nested fields get nested_field_prefix set
        assert nested.nested_field_prefix == "hetzner"
        # For flat fields, nested_field_prefix is not set (or is None)
        assert flat.nested_field_prefix is None


class TestMultiLevelNesting:
    """Tests for arbitrary depth nested config support."""

    def test_get_field_descriptor_with_multi_level_path(self):
        """get_field_descriptor builds correct nested_field_prefix for multi-level paths."""
        # Note: This test uses a hypothetical 2-level nested config.
        # Since we don't have one defined in DjbConfig yet, we test
        # that the parsing logic works correctly by checking the section_parts
        # are built correctly for existing single-level nesting.
        result = get_field_descriptor("hetzner.default_server_type")
        assert result.nested_field_prefix == "hetzner"
        assert result.field_name == "default_server_type"

    def test_env_var_pattern_for_nested_sections(self, project_dir):
        """Environment variables work with nested nested field paths."""
        # Set up project structure
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test-project"\n')

        # Create env var for nested path
        # The pattern is DJB_<nested_field_prefix>_<FIELD> with dots replaced by underscores
        env = {"DJB_HETZNER_DEFAULT_SERVER_TYPE": "cx42"}

        # Resolve config with the env var
        cfg = get_djb_config(DjbConfig(project_dir=project_dir), env=env)

        # The env var should override the default
        assert cfg.hetzner.default_server_type == "cx42"


class TestNestedConfigProvenanceTracking:
    """Tests for nested config source tracking (DERIVED vs DEFAULT)."""

    def test_nested_config_with_values_from_config_returns_derived_source(self, project_dir):
        """Nested config returns DERIVED source when any value comes from config.

        Nested configs aggregate values from multiple sources, so we can't claim
        a single specific source (like PROJECT_CONFIG). Instead, we use DERIVED
        to indicate the value was computed from config sources.
        """
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
default_server_type = "cx32"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # The hetzner config got a value from project.toml, but nested configs
        # aggregate from multiple sources, so they're classified as DERIVED
        assert cfg.get_source("hetzner") is not None
        # It's classified as derived (not explicit)
        assert cfg.is_derived("hetzner") is True
        assert cfg.is_explicit("hetzner") is False

    def test_nested_config_with_only_defaults_returns_derived_source(self, project_dir):
        """Nested config is derived when using core.toml defaults.

        When no local/project config files provide values for a nested config,
        core.toml defaults are still "from config" so the nested config is derived.
        """
        # No config file at all - only core.toml defaults apply
        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # The hetzner config uses only defaults (from core.toml)
        # core.toml IS a config layer, so any value from it counts as "from config"
        # which makes the nested config "derived" (aggregated from config sources)
        assert cfg.get_source("hetzner") is not None
        assert cfg.is_derived("hetzner") is True
        assert cfg.is_explicit("hetzner") is False

    def test_nested_config_source_is_derived_not_explicit(self, project_dir):
        """Verify nested config is derived, not explicit.

        This is the key semantic: nested configs aggregate from multiple
        sources (core, project, local, env), so they are always "derived"
        (not explicit) even when values come from project config.
        """
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text(
            """
[hetzner]
server_name = "my-server"
"""
        )

        cfg = get_djb_config(DjbConfig(project_dir=project_dir))

        # Key assertion: nested config is derived, not explicit
        assert cfg.get_source("hetzner") is not None
        assert cfg.is_derived("hetzner") is True
        assert cfg.is_explicit("hetzner") is False


class TestConfigOverrideExplicitFieldTracking:
    """Tests for override explicit field tracking via _overrides_dict.

    The override layer only returns values for fields that are in _overrides_dict.
    Fields not in _overrides_dict fall through to the next layer in the resolution chain.
    """

    def test_explicitly_set_field_overrides_config(self, project_dir, make_djb_config):
        """Override config with explicitly set field overrides project config."""
        make_project_config_type(make_djb_config).save({"mode": "production"})

        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,  # Explicitly passed
            )
        )

        assert cfg.mode == Mode.STAGING
        assert _source_is_override(cfg.get_source("mode"))

    def test_non_explicit_field_falls_through(self, project_dir):
        """Override config without explicit field falls through to project config."""
        # Create project config directly (not via make_project_config_type which uses mode prefix)
        config_dir = project_dir / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.toml"
        config_file.write_text('mode = "staging"\n')

        # Only pass log_level, not mode
        cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                log_level="debug",  # Explicitly passed
            )
        )

        # log_level comes from override (explicitly set)
        assert cfg.log_level == "debug"
        assert _source_is_override(cfg.get_source("log_level"))

        # mode falls through to project config (not in override)
        assert cfg.mode == Mode.STAGING
        assert _source_matches(cfg.get_source("mode"), ProjectConfigType)

    def test_augment_preserves_mode(self, project_dir, make_djb_config):
        """config.augment() preserves mode from base config.

        This is the critical test for the CLI command chain use case:
        subcommands should be able to add overrides without resetting mode.
        """
        # Base config with staging mode
        base_cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
            )
        )
        assert base_cfg.mode == Mode.STAGING

        # Override config only sets log_level, not mode
        override = DjbConfig(log_level="debug")

        # Augmented config should preserve staging mode
        augmented = base_cfg.augment(override)

        assert augmented.mode == Mode.STAGING  # Preserved from base
        assert augmented.log_level == "debug"  # From override

    def test_augment_override_mode(self, project_dir):
        """config.augment() can override mode when explicitly set."""
        # Base config with development mode
        base_cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.DEVELOPMENT,
            )
        )
        assert base_cfg.mode == Mode.DEVELOPMENT

        # Override config explicitly sets mode to staging
        override = DjbConfig(mode=Mode.STAGING)

        # Augmented config should use staging mode
        augmented = base_cfg.augment(override)

        assert augmented.mode == Mode.STAGING  # From override
        assert _source_is_override(augmented.get_source("mode"))

    def test_overrides_dict_tracks_init_kwargs(self):
        """DjbConfig _overrides_dict tracks which fields were passed to __init__."""
        # Only mode is explicitly passed
        cfg = DjbConfig(mode=Mode.STAGING)

        assert "mode" in cfg._overrides_dict
        assert "log_level" not in cfg._overrides_dict
        assert "project_name" not in cfg._overrides_dict

    def test_overrides_dict_with_multiple_fields(self):
        """DjbConfig _overrides_dict tracks multiple explicitly set fields."""
        cfg = DjbConfig(mode=Mode.STAGING, log_level="debug")

        assert "mode" in cfg._overrides_dict
        assert "log_level" in cfg._overrides_dict
        assert "project_name" not in cfg._overrides_dict

    def test_nested_config_overrides_dict_tracking(self):
        """Nested config fields can be explicitly set."""
        hetzner = HetznerConfig(default_server_type="cx32")

        assert "default_server_type" in hetzner._overrides_dict
        assert "default_location" not in hetzner._overrides_dict
        assert "server_name" not in hetzner._overrides_dict

    def test_default_value_same_as_explicit_still_tracked(self):
        """Explicitly passing a value equal to default is still tracked in _overrides_dict."""
        # The default mode is DEVELOPMENT - passing it explicitly should still be tracked
        cfg = DjbConfig(mode=Mode.DEVELOPMENT)

        assert "mode" in cfg._overrides_dict

    def test_none_value_not_in_overrides_dict(self):
        """Explicitly passing None is NOT tracked in _overrides_dict (falls through)."""
        # server_name defaults to None - passing None explicitly is same as not passing it
        hetzner = HetznerConfig(server_name=None)

        assert "server_name" not in hetzner._overrides_dict

    def test_augmented_config_override_chain(self, project_dir):
        """Multiple augmented configs preserve mode when chaining.

        This tests the CLI command chain scenario:
        1. Root command sets mode=staging
        2. Subcommand adds log_level=debug
        3. The resulting config has both mode and log_level set
        """
        # Base config with staging mode
        base_cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
            )
        )

        # Override adds log_level
        override = DjbConfig(log_level="debug")
        augmented = base_cfg.augment(override)

        # Mode is preserved from base config (staging was explicitly set)
        assert augmented.mode == Mode.STAGING
        # log_level comes from override
        assert augmented.log_level == "debug"

    def test_augmented_config_with_empty_override(self, project_dir):
        """Empty override preserves all explicit fields from base config.

        When an empty DjbConfig() (no explicit fields) is used as override,
        all explicitly set fields from the base config are preserved.
        """
        # Base config with staging mode and debug log level
        base_cfg = get_djb_config(
            DjbConfig(
                project_dir=project_dir,
                mode=Mode.STAGING,
                log_level="debug",
            )
        )

        # Empty override - no explicit fields
        override = DjbConfig()
        augmented = base_cfg.augment(override)

        # All explicitly set fields are preserved
        assert augmented.mode == Mode.STAGING
        assert augmented.log_level == "debug"

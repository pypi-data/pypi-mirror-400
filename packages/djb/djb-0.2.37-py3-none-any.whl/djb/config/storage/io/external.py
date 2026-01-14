"""
External source ConfigIO implementations.

For sources that provide config values but aren't config files:
- GitConfigIO: Reads/writes git config (user.name, user.email)
- CwdPathConfigIO: Infers project_dir from current working directory (read-only)
- CwdNameConfigIO: Infers project_name from directory name (read-only)
- PyprojectNameConfigIO: Reads project name from pyproject.toml [project].name (read-only)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from djb.config.storage.io.base import ConfigIO
from djb.config.storage.utils import load_toml_mapping
from djb.core.cmd_runner import CmdRunner

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase
    from djb.config.storage.base import Provenance


class ExternalConfigIO(ConfigIO):
    """Base class for external sources (git config, cwd inference, etc.).

    External sources are read-only - they provide values but cannot be written to.
    """

    writable = False
    explicit = False  # External sources are derived (git config, cwd inference, etc.)

    def load(self, *, rest: "Provenance" = ()) -> dict[str, Any]:  # noqa: ARG002
        """External sources don't support bulk load."""
        raise NotImplementedError(f"{self.name} does not support load()")

    def save(self, data: dict[str, Any], *, rest: "Provenance" = ()) -> None:  # noqa: ARG002
        raise ValueError(f"Cannot save to external source: {self.name}")

    def _set_value(self, key: str, value: Any) -> None:  # noqa: ARG002
        raise ValueError(f"Cannot set value in external source: {self.name}")


class GitConfigIO(ExternalConfigIO):
    """Single-key git config reader/writer.

    Each instance reads/writes one git config value (e.g., "user.name" or "user.email").
    Used as a field-specific config store for name/email fields.

    Writes go to --global git config.

    Example:
        # In NameField
        config_stores=[GitConfigIO("user.name", ctx)]
    """

    name = "git config"
    writable = True  # Override ExternalConfigIO's read-only default

    def __init__(self, git_key: str, config: "DjbConfigBase"):
        """Initialize with a git config key.

        Args:
            git_key: Full git config key (e.g., "user.name", "user.email").
            config: DjbConfigBase instance (may be partially resolved during bootstrap).
        """
        super().__init__(config)
        self._git_key = git_key
        # Derive config key from last part of git key (user.name -> name)
        self._config_key = git_key.split(".")[-1]

    def _get_git_value(self) -> str | None:
        """Fetch the value from git config."""
        try:
            runner = CmdRunner(verbose=self.config.verbose)
            result = runner.run(["git", "config", "--get", self._git_key])
            if result.returncode == 0:
                return result.stdout.strip() or None
        except (FileNotFoundError, OSError):
            # git not installed or not accessible
            pass
        return None

    def _set_git_value(self, value: str) -> None:
        """Set the value in global git config."""
        runner = CmdRunner(verbose=self.config.verbose)
        result = runner.run(["git", "config", "--global", self._git_key, value])
        if result.returncode != 0:
            raise ValueError(f"Failed to set {self._git_key} in git config: {result.stderr}")

    def _get_value(self, key: str) -> Any | None:
        """Get value from git config if key matches."""
        if key == self._config_key:
            return self._get_git_value()
        return None

    def _set_value(self, key: str, value: Any) -> None:
        """Set value in git config if key matches."""
        if key != self._config_key:
            raise ValueError(f"GitConfigIO for {self._git_key} cannot set key {key}")
        self._set_git_value(str(value))


class CwdPathConfigIO(ExternalConfigIO):
    """Infers project_dir from current working directory.

    Used as a fallback when project_dir is not explicitly configured.
    """

    name = "cwd_path"

    def __init__(self, cwd: Path | None, config: "DjbConfigBase"):
        """Initialize with optional custom cwd.

        Args:
            cwd: Current working directory. None means use Path.cwd().
            config: DjbConfigBase instance (may be partially resolved during bootstrap).
        """
        super().__init__(config)
        self._cwd = cwd if cwd is not None else Path.cwd()

    def _get_value(self, key: str) -> Any | None:
        """Get project_dir from cwd."""
        if key == "project_dir":
            return self._cwd
        return None


class CwdNameConfigIO(ExternalConfigIO):
    """Infers project_name from project directory name.

    Used as a fallback when project_name is not found in config files
    or pyproject.toml.
    """

    name = "cwd_name"

    def _get_value(self, key: str) -> Any | None:
        """Get project_name from project directory name."""
        if key == "project_name":
            return self.config.project_dir.name
        return None


class PyprojectNameConfigIO(ExternalConfigIO):
    """Reads project name from pyproject.toml [project].name.

    This is the standard Python project name, separate from [tool.djb].
    Used as a fallback for project_name when not set in djb config.
    """

    name = "pyproject.toml[project][name]"

    def _get_value(self, key: str) -> Any | None:
        """Get project_name from pyproject.toml [project].name."""
        if key != "project_name":
            return None

        pyproject_path = self.config.project_dir / "pyproject.toml"
        if not pyproject_path.exists():
            return None

        try:
            data = load_toml_mapping(pyproject_path)
            return data.get("project", {}).get("name")
        except Exception:
            return None

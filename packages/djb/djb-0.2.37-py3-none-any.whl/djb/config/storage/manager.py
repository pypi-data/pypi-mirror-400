"""
Config file managers - ABC and subclasses for config file I/O operations.

This module provides:
- ConcreteConfigFile: Enum for concrete config file types
- ConfigFileManager: ABC for config file I/O
- Subclasses for each config file type (local, project, pyproject, core)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

from djb.config.storage.utils import (
    _build_full_path,
    _delete_nested_key,
    load_toml_mapping,
    save_toml_mapping,
    _split_by_mode,
    navigate_config_path,
)


class ConcreteConfigFile(Enum):
    """Enum for concrete config file types.

    Used for provenance tracking to identify which physical file
    a config value came from.
    """

    LOCAL = "local"
    PROJECT = "project"
    PYPROJECT = "pyproject"
    CORE = "core"


class ConfigFileManager(ABC):
    """Abstract base for config file I/O operations.

    Subclasses only provide:
    - path: The file path (property)
    - prefix: Optional TOML prefix like "tool.djb" (property, default None)
    - concrete_file: Which ConcreteConfigFile this is (property)

    All I/O logic is implemented in this ABC.

    Use get_manager() to get the appropriate subclass for a ConcreteConfigFile.
    """

    # Registry mapping ConcreteConfigFile to manager classes
    _registry: dict[ConcreteConfigFile, type["ConfigFileManager"]] = {}

    def __init__(self, project_root: Path):
        """Initialize with project root.

        Args:
            project_root: Path to the project root directory.
        """
        self._project_root = project_root

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register subclasses with their ConcreteConfigFile type."""
        super().__init_subclass__(**kwargs)
        # Only register concrete classes (not intermediate ABCs)
        if not getattr(cls, "__abstractmethods__", None):
            # Get the concrete_file from the class (need to instantiate to get it)
            # Instead, we'll register in the class definition
            pass

    @classmethod
    def register(cls, config_file: ConcreteConfigFile) -> None:
        """Register this manager class for a config file type."""
        ConfigFileManager._registry[config_file] = cls

    @classmethod
    def get_manager(
        cls, config_file: ConcreteConfigFile, project_root: Path
    ) -> "ConfigFileManager":
        """Factory method to get the appropriate manager for a config file type.

        Args:
            config_file: The config file type.
            project_root: Path to the project root.

        Returns:
            The appropriate ConfigFileManager instance.

        Raises:
            ValueError: If config_file is not registered.
        """
        manager_cls = cls._registry.get(config_file)
        if manager_cls is None:
            raise ValueError(f"No manager registered for: {config_file}")
        # CoreConfigFileManager doesn't take project_root
        if config_file == ConcreteConfigFile.CORE:
            return manager_cls()  # type: ignore[call-arg]
        return manager_cls(project_root)

    @property
    @abstractmethod
    def path(self) -> Path:
        """Return the file path for this manager."""

    @property
    def prefix(self) -> str | None:
        """Optional prefix for TOML navigation (e.g., 'tool.djb').

        Returns None by default. Override in subclasses that need a prefix.
        """
        return None

    @property
    @abstractmethod
    def concrete_file(self) -> ConcreteConfigFile:
        """Return which concrete file this manager represents."""

    def load(self) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
        """Load config, returning (root_values, mode_sections).

        Returns:
            Tuple of (root_values, mode_sections) where:
            - root_values: All keys not in MODE_SECTIONS
            - mode_sections: Dict mapping mode names to their override dicts
        """
        if not self.path.exists():
            return {}, {}

        data = load_toml_mapping(self.path)
        if self.prefix:
            data = navigate_config_path(data, self.prefix) or {}

        return _split_by_mode(data)

    def store(self, data: dict[str, Any]) -> None:
        """Store an entire config dict to the file.

        This replaces the djb config section content entirely.
        For files with a prefix (like pyproject.toml), only the prefixed
        section is replaced.

        Args:
            data: Configuration dict to save.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.prefix:
            # Load existing file to preserve non-djb sections
            if self.path.exists():
                existing = load_toml_mapping(self.path)
            else:
                existing = {}
            # Navigate to prefix and replace
            target = navigate_config_path(existing, self.prefix, ensure=True)
            target.clear()
            target.update(data)
            save_toml_mapping(self.path, existing)
        else:
            save_toml_mapping(self.path, data)

    def save_value(
        self,
        key: str,
        value: Any,
        mode: str | None = None,
        nested_field_prefix: str | None = None,
    ) -> None:
        """Save a single value to the appropriate section.

        Args:
            key: Configuration key to set.
            value: Value to set.
            mode: Mode string ("development", "staging", "production", or None).
                If None or "production", writes to root/[nested_field_prefix].
            nested_field_prefix: For nested fields, the dotted nested field path (e.g., "hetzner.eu").
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.path.exists():
            data = load_toml_mapping(self.path)
        else:
            data = {}

        full_path = _build_full_path(mode, nested_field_prefix)
        if self.prefix:
            full_path = f"{self.prefix}.{full_path}" if full_path else self.prefix

        target = navigate_config_path(data, full_path, ensure=True)
        target[key] = value

        save_toml_mapping(self.path, data)

    def delete_value(
        self,
        key: str,
        mode: str | None = None,
        nested_field_prefix: str | None = None,
    ) -> None:
        """Delete a value from the appropriate section.

        Args:
            key: Configuration key to delete.
            mode: Mode string ("development", "staging", "production", or None).
                If None or "production", deletes from root/[nested_field_prefix].
            nested_field_prefix: For nested fields, the dotted nested field path (e.g., "hetzner.eu").
        """
        if not self.path.exists():
            return

        data = load_toml_mapping(self.path)

        full_path = _build_full_path(mode, nested_field_prefix)
        if self.prefix:
            full_path = f"{self.prefix}.{full_path}" if full_path else self.prefix

        path_parts = full_path.split(".") if full_path else []
        _delete_nested_key(data, path_parts, key)

        save_toml_mapping(self.path, data)

    def has_value(self, field_path: str, mode: str | None = None) -> bool:
        """Check if a field value exists in this file.

        Args:
            field_path: Field path - "field_name" or "section.path.field_name"
            mode: Current mode string (e.g., "development", "staging", "production").

        Returns:
            True if the field exists in this file, False otherwise.
        """
        if not self.path.exists():
            return False

        data = load_toml_mapping(self.path)
        if self.prefix:
            data = navigate_config_path(data, self.prefix) or {}

        parts = field_path.split(".")
        nested_field_prefix = ".".join(parts[:-1]) if len(parts) > 1 else None
        field_name = parts[-1]

        # Check mode-specific first (e.g., [development] or [development.hetzner])
        if mode and mode != "production":
            target = navigate_config_path(data, _build_full_path(mode, nested_field_prefix))
            if target and field_name in target:
                return True

        # Then check root/production (e.g., root or [hetzner])
        target = navigate_config_path(data, nested_field_prefix)
        return target is not None and field_name in target


class LocalConfigFileManager(ConfigFileManager):
    """Manager for .djb/local.toml config file."""

    @property
    def path(self) -> Path:
        return self._project_root / ".djb" / "local.toml"

    @property
    def concrete_file(self) -> ConcreteConfigFile:
        return ConcreteConfigFile.LOCAL


LocalConfigFileManager.register(ConcreteConfigFile.LOCAL)


class ProjectConfigFileManager(ConfigFileManager):
    """Manager for .djb/project.toml config file."""

    @property
    def path(self) -> Path:
        return self._project_root / ".djb" / "project.toml"

    @property
    def concrete_file(self) -> ConcreteConfigFile:
        return ConcreteConfigFile.PROJECT


ProjectConfigFileManager.register(ConcreteConfigFile.PROJECT)


class PyprojectConfigFileManager(ConfigFileManager):
    """Manager for pyproject.toml[tool.djb] config section."""

    @property
    def path(self) -> Path:
        return self._project_root / "pyproject.toml"

    @property
    def prefix(self) -> str:
        return "tool.djb"

    @property
    def concrete_file(self) -> ConcreteConfigFile:
        return ConcreteConfigFile.PYPROJECT


PyprojectConfigFileManager.register(ConcreteConfigFile.PYPROJECT)


class CoreConfigFileManager(ConfigFileManager):
    """Manager for djb's bundled core.toml config.

    This is a read-only config file shipped with djb.
    """

    def __init__(self) -> None:
        """Initialize without project_root (core config is bundled with djb)."""
        # Don't call super().__init__() as we don't need project_root
        pass

    @property
    def path(self) -> Path:
        return Path(__file__).parent.parent / "core.toml"

    @property
    def concrete_file(self) -> ConcreteConfigFile:
        return ConcreteConfigFile.CORE

    def save_value(self, *args: Any, **kwargs: Any) -> None:
        """Raise error - core.toml is read-only."""
        raise ValueError("Cannot write to core.toml")

    def delete_value(self, *args: Any, **kwargs: Any) -> None:
        """Raise error - core.toml is read-only."""
        raise ValueError("Cannot delete from core.toml")


CoreConfigFileManager.register(ConcreteConfigFile.CORE)


# Convenience alias for ConfigFileManager.get_manager
def get_manager(config_file: ConcreteConfigFile, project_root: Path) -> ConfigFileManager:
    """Get the appropriate manager for a config file type.

    This is an alias for ConfigFileManager.get_manager().

    Args:
        config_file: The config file type.
        project_root: Path to the project root.

    Returns:
        The appropriate ConfigFileManager instance.
    """
    return ConfigFileManager.get_manager(config_file, project_root)

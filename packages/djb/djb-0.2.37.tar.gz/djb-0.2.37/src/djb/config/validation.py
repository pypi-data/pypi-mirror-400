"""Config validation: detect unrecognized config keys.

This module provides functionality to detect unrecognized keys in config files
(project.toml, local.toml, pyproject.toml[tool.djb]).
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any

from djb.config.fields.nested import NestedConfigField
from djb.config.storage.io.toml import LocalConfigIO, ProjectConfigIO, PyprojectConfigIO
from djb.config.storage.utils import MODE_SECTIONS, navigate_config_path
from djb.core.logging import get_logger

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase

logger = get_logger(__name__)

# Module-level flag to control unrecognized key warnings (used by health check to suppress)
_warn_unrecognized_keys = True

# Track project directories that have already been warned about (prevents duplicate warnings)
_warned_project_dirs: set[str] = set()


def reset_warning_state() -> None:
    """Reset the warning state. Used for testing."""
    _warned_project_dirs.clear()


class suppress_unrecognized_key_warnings:
    """Context manager to suppress unrecognized key warnings during config load.

    Used by health checks to prevent duplicate warnings - the health check
    reports issues in its own format.

    Example:
        with suppress_unrecognized_key_warnings():
            config = get_djb_config()  # Warnings are suppressed
    """

    def __enter__(self) -> "suppress_unrecognized_key_warnings":
        global _warn_unrecognized_keys
        self._old_value = _warn_unrecognized_keys
        _warn_unrecognized_keys = False
        return self

    def __exit__(
        self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object
    ) -> None:
        global _warn_unrecognized_keys
        _warn_unrecognized_keys = self._old_value


def _collect_recognized_paths(
    config_class: type["DjbConfigBase"],
    prefix: str = "",
) -> tuple[set[str], set[str]]:
    """Collect recognized field paths and terminal field paths.

    Recursively traverses nested config fields to build complete paths.

    Args:
        config_class: The config class to collect paths from.
        prefix: Path prefix for nested fields (e.g., "hetzner").

    Returns:
        Tuple of (recognized_paths, terminal_paths).
        - recognized_paths: All valid field paths
        - terminal_paths: Fields that accept arbitrary children (like domain_names maps)
    """
    # Import here to avoid circular import
    from djb.config.fields.domain_names import DomainNamesMapField  # noqa: PLC0415

    recognized: set[str] = set()
    terminal: set[str] = set()

    for field_name, config_field in config_class.__fields__.items():
        full_path = f"{prefix}.{field_name}" if prefix else field_name
        recognized.add(full_path)

        # Check if this is a map field that accepts arbitrary children
        if isinstance(config_field, DomainNamesMapField):
            terminal.add(full_path)
        # For NestedConfigField, recurse into the nested class
        elif isinstance(config_field, NestedConfigField):
            nested_recognized, nested_terminal = _collect_recognized_paths(
                config_field.nested_class, full_path
            )
            recognized.update(nested_recognized)
            terminal.update(nested_terminal)

    return recognized, terminal


def _collect_toml_paths(
    data: dict[str, Any],
    prefix: str = "",
    skip_mode_sections: bool = True,
) -> set[str]:
    """Collect all key paths from TOML data structure.

    Args:
        data: TOML data dict.
        prefix: Path prefix for nested keys.
        skip_mode_sections: If True, process mode sections as if their contents
            were at the root level (for validation purposes).

    Returns:
        Set of key paths found in the data.
    """
    paths: set[str] = set()

    for key, value in data.items():
        # Handle mode sections specially - validate their contents against root paths
        if skip_mode_sections and key in MODE_SECTIONS:
            if isinstance(value, dict):
                # Collect paths from mode section as if they were at root
                paths.update(_collect_toml_paths(value, prefix="", skip_mode_sections=False))
            continue

        full_path = f"{prefix}.{key}" if prefix else key
        paths.add(full_path)

        if isinstance(value, dict):
            paths.update(_collect_toml_paths(value, full_path, skip_mode_sections=False))

    return paths


def _is_valid_path(path: str, recognized: set[str], terminal: set[str]) -> bool:
    """Check if a path is valid (recognized or child of a terminal field).

    Args:
        path: The path to check.
        recognized: Set of recognized field paths.
        terminal: Set of terminal field paths (accept arbitrary children).

    Returns:
        True if the path is valid.
    """
    if path in recognized:
        return True

    # Check if any parent is a terminal field
    parts = path.split(".")
    for i in range(len(parts)):
        parent = ".".join(parts[: i + 1])
        if parent in terminal:
            return True

    return False


def get_unrecognized_keys(
    config: "DjbConfigBase",
    config_class: type["DjbConfigBase"],
) -> dict[str, list[str]]:
    """Get unrecognized keys per config file.

    Checks project.toml, local.toml, and pyproject.toml[tool.djb] for
    keys that don't correspond to known config fields.

    Args:
        config: The loaded config instance.
        config_class: The config class (may be a subclass of DjbConfig).

    Returns:
        Dict mapping file label to list of unrecognized keys.
    """
    recognized, terminal = _collect_recognized_paths(config_class)

    result: dict[str, list[str]] = {}

    # Check project.toml
    project_io = ProjectConfigIO(config)
    if project_io.exists:
        raw_data = project_io._load_raw_data()
        toml_paths = _collect_toml_paths(raw_data)
        unrecognized = [
            p for p in sorted(toml_paths) if not _is_valid_path(p, recognized, terminal)
        ]
        if unrecognized:
            result["project.toml"] = unrecognized

    # Check local.toml
    local_io = LocalConfigIO(config)
    if local_io.exists:
        raw_data = local_io._load_raw_data()
        toml_paths = _collect_toml_paths(raw_data)
        unrecognized = [
            p for p in sorted(toml_paths) if not _is_valid_path(p, recognized, terminal)
        ]
        if unrecognized:
            result["local.toml"] = unrecognized

    # Check pyproject.toml[tool.djb]
    pyproject_io = PyprojectConfigIO(config)
    if pyproject_io.exists:
        raw_data = pyproject_io._load_raw_data()
        # Navigate to tool.djb section
        djb_section = navigate_config_path(raw_data, "tool.djb")
        if djb_section:
            toml_paths = _collect_toml_paths(djb_section)
            unrecognized = [
                p for p in sorted(toml_paths) if not _is_valid_path(p, recognized, terminal)
            ]
            if unrecognized:
                result["pyproject.toml[tool.djb]"] = unrecognized

    return result


def warn_unrecognized_keys(
    config: "DjbConfigBase",
    config_class: type["DjbConfigBase"],
) -> None:
    """Emit warnings for unrecognized config keys.

    Only warns once per project directory per process to avoid duplicate warnings
    (e.g., during Django runserver reloads).

    Args:
        config: The loaded config instance.
        config_class: The config class (may be a subclass of DjbConfig).
    """
    if not _warn_unrecognized_keys:
        return

    # Skip in Django's reloader child process (RUN_MAIN=true).
    # The parent process already warned, and the child is spawned for auto-reload.
    if os.environ.get("RUN_MAIN") == "true":
        return

    # Only warn once per project directory per process
    project_dir_str = str(config.project_dir)
    if project_dir_str in _warned_project_dirs:
        return
    _warned_project_dirs.add(project_dir_str)

    unrecognized = get_unrecognized_keys(config, config_class)
    if unrecognized:
        print(file=sys.stderr)  # Blank line before warnings
        logger.warning("Unrecognized config keys:")
        for file_label, keys in unrecognized.items():
            for key in keys:
                logger.warning(f"  {file_label}: {key}")
        print(file=sys.stderr)  # Blank line after warnings

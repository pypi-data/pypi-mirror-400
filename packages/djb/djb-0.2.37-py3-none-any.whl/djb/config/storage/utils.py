"""
Config file utilities - Helper functions for TOML config file operations.

This module provides low-level utilities for reading and manipulating TOML config files:
- deep_merge: Recursively merge dicts
- navigate_config_path: Navigate to nested paths in dicts/objects
- load_toml_mapping: Load TOML file to TOMLDocument (cached by path+mtime)
- save_toml_mapping: Save TOMLDocument/dict to TOML file
- parse_toml: Parse TOML string to TOMLDocument
- dump_toml: Dump TOMLDocument/dict to TOML string
- clear_toml_cache: Clear the TOML file cache (call on reload)
- _split_by_mode: Separate root values from mode sections
- _build_full_path: Build navigation path from mode and section
- _delete_nested_key: Delete nested key with cleanup
"""

from __future__ import annotations

import tomlkit
import tomlkit.items

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal, cast, overload

from djb.types import Mode


# =============================================================================
# TOML file cache - avoids repeated parsing of the same files
# =============================================================================

# Cache storage: path -> (mtime, parsed_document)
_toml_cache: dict[Path, tuple[float, tomlkit.TOMLDocument]] = {}


def clear_toml_cache() -> None:
    """Clear the TOML file cache.

    Call this when config files may have changed externally (e.g., reload()).
    """
    _toml_cache.clear()


def invalidate_toml_cache(path: Path) -> None:
    """Invalidate cache for a specific file.

    Call this after writing to a TOML file to ensure next read sees the new content.
    """
    _toml_cache.pop(path.resolve(), None)


# Reserved section names for mode-based overrides
# Production values live at root level, so exclude it
MODE_SECTIONS: frozenset[str] = frozenset(mode.value for mode in Mode if mode != Mode.PRODUCTION)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dicts, with override taking precedence.

    For nested dicts, recursively merges rather than replacing.
    For non-dict values, override replaces base.

    Args:
        base: Base dict to merge into.
        override: Dict with values that take precedence.

    Returns:
        New merged dict (does not modify inputs).

    Example:
        >>> base = {"hetzner": {"server_type": "cx23", "location": "nbg1"}}
        >>> override = {"hetzner": {"server_type": "cx11"}}
        >>> deep_merge(base, override)
        {"hetzner": {"server_type": "cx11", "location": "nbg1"}}
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = deep_merge(result[key], value)
        else:
            # Override replaces base
            result[key] = value
    return result


def get_config_dir(project_root: Path) -> Path:
    """Get the djb configuration directory (.djb/ in project root).

    Args:
        project_root: Project root path.

    Returns:
        Path to .djb/ directory in the project.
    """
    return project_root / ".djb"


def load_toml_mapping(path: Path) -> tomlkit.TOMLDocument:
    """Load a TOML file and return its contents as a TOMLDocument.

    Results are cached by file path and mtime. The cached document is returned
    directly (not copied) for performance. Callers should not mutate the returned
    document - use save_toml_mapping() for writes, which invalidates the cache.

    The TOMLDocument preserves comments and key ordering from the original file.
    It implements MutableMapping so it can be used like a dict.

    Raises:
        tomlkit.exceptions.ParseError: If the file contains invalid TOML.
    """
    resolved = path.resolve()
    mtime = resolved.stat().st_mtime

    # Check cache
    if resolved in _toml_cache:
        cached_mtime, cached_doc = _toml_cache[resolved]
        if cached_mtime == mtime:
            return cached_doc

    # Parse and cache
    with open(resolved, "rb") as f:
        doc = tomlkit.load(f)

    _toml_cache[resolved] = (mtime, doc)
    return doc


def save_toml_mapping(path: Path, data: tomlkit.TOMLDocument | dict[str, Any]) -> None:
    """Save a TOMLDocument or dict to a TOML file.

    If data is a TOMLDocument, comments and ordering are preserved.
    Invalidates the cache for this file after writing.
    """
    with open(path, "w") as f:
        tomlkit.dump(data, f)

    # Invalidate cache so next read sees the new content
    invalidate_toml_cache(path)


def parse_toml(content: str) -> tomlkit.TOMLDocument:
    """Parse TOML string to TOMLDocument, preserving comments and ordering."""
    return tomlkit.loads(content)


def dump_toml(data: tomlkit.TOMLDocument | dict[str, Any]) -> str:
    """Dump TOMLDocument or dict to TOML string."""
    return tomlkit.dumps(data)


def _split_by_mode(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Split TOML data into root values and mode sections.

    Args:
        data: Raw TOML data dict.

    Returns:
        Tuple of (root_values, mode_sections) where:
        - root_values: All keys not in MODE_SECTIONS
        - mode_sections: Dict mapping mode names to their override dicts
    """
    root = {k: v for k, v in data.items() if k not in MODE_SECTIONS}
    sections = {k: v for k, v in data.items() if k in MODE_SECTIONS and isinstance(v, dict)}
    return root, sections


@overload
def navigate_config_path(
    data: dict[str, Any],
    path: str | list[str] | None,
    *,
    ensure: Literal[True],
) -> dict[str, Any]: ...


@overload
def navigate_config_path(
    data: dict[str, Any],
    path: str | list[str] | None,
    *,
    ensure: Literal[False] = ...,
) -> dict[str, Any] | None: ...


@overload
def navigate_config_path(
    data: Any,
    path: str | list[str] | None,
) -> Any: ...


def navigate_config_path(
    data: Any,
    path: str | list[str] | None,
    *,
    ensure: bool = False,
) -> Any:
    """Navigate to a nested path in a dict, Mapping, or object.

    Works with:
    - dicts: using key access with optional ensure
    - Mappings (EnvDict, etc.): using key access
    - objects: using getattr

    Args:
        data: Root dict, Mapping, or object to navigate from.
        path: Dotted string ("hetzner.eu"), list of parts, or None.
        ensure: If True and data is a dict, create missing dicts.
            Ignored for non-dict Mappings and objects.

    Returns:
        The nested value at path, or None if not found (when ensure=False).
    """
    if path is None:
        return data

    parts = path.split(".") if isinstance(path, str) else path
    current = data

    for part in parts:
        if isinstance(current, dict):
            # Dict navigation with ensure support
            if part not in current or not isinstance(current[part], dict):
                if ensure:
                    current[part] = {}
                else:
                    return None
            current = current[part]
        elif isinstance(current, Mapping):
            # Mapping navigation (EnvDict, etc.) - no ensure support
            try:
                current = current[part]
            except KeyError:
                return None
        else:
            # Object navigation via getattr
            current = getattr(current, part, None)
            if current is None:
                return None

    return current


def _build_full_path(mode: str | None, nested_field_prefix: str | None) -> str | None:
    """Build full navigation path from mode and section.

    Args:
        mode: Mode string ("development", "staging", "production", or None).
        nested_field_prefix: Dotted nested field path (e.g., "hetzner.eu"), or None.

    Returns:
        Combined path for navigation, or None for root.
    """
    if mode and mode != "production":
        if nested_field_prefix:
            return f"{mode}.{nested_field_prefix}"
        return mode
    return nested_field_prefix


def _delete_nested_key(data: dict[str, Any], path_parts: list[str], key: str) -> None:
    """Delete a key from a nested dict, cleaning up empty parent dicts.

    Args:
        data: Root dict.
        path_parts: List of keys to navigate to the parent.
        key: Key to delete from the innermost dict.
    """
    if not path_parts:
        data.pop(key, None)
        return

    # Build path to parent dicts for cleanup
    parents: list[tuple[dict[str, Any], str]] = []
    current = data
    for part in path_parts:
        if part not in current or not isinstance(current[part], dict):
            return  # Path doesn't exist
        parents.append((current, part))
        current = current[part]

    # Delete the key
    current.pop(key, None)

    # Clean up empty parent dicts (reverse order)
    for parent, part in reversed(parents):
        if not parent[part]:
            del parent[part]
        else:
            break  # Stop if parent is not empty


def insert_key_ordered(
    table: tomlkit.items.Table | tomlkit.TOMLDocument | dict[str, Any],
    key: str,
    value: Any,
) -> None:
    """Insert a key into a TOML table, placing it near related keys.

    Groups keys alphabetically by prefix (e.g., 'hetzner_*' keys together).
    New keys are inserted after the last key with the same prefix,
    or in alphabetical order if no prefix match.

    For plain dicts, falls back to simple assignment (no ordering).

    Args:
        table: TOML table or dict to insert into.
        key: Key to insert.
        value: Value to insert.
    """
    # For plain dicts, just assign (no ordering support)
    if not isinstance(table, (tomlkit.items.Table, tomlkit.TOMLDocument)):
        table[key] = value
        return

    # Extract prefix (before first underscore or the whole key)
    prefix = key.split("_")[0] if "_" in key else key

    # Find insertion position
    keys = list(table.keys())
    insert_after = None

    for existing_key in keys:
        existing_prefix = existing_key.split("_")[0] if "_" in existing_key else existing_key
        if existing_prefix == prefix:
            insert_after = existing_key
        elif insert_after is not None:
            # We've passed the prefix group, stop
            break

    if insert_after is not None:
        # Insert after the last matching prefix
        # tomlkit preserves order, so we rebuild the table
        items = [(k, table[k]) for k in keys]
        table.clear()
        for k, v in items:
            table.add(k, cast(tomlkit.items.Item, v))
            if k == insert_after:
                table.add(key, value)
    else:
        # No matching prefix - insert in alphabetical order
        items = [(k, table[k]) for k in keys]
        items.append((key, value))
        items.sort(key=lambda x: x[0])
        table.clear()
        for k, v in items:
            table.add(k, cast(tomlkit.items.Item, v))


def sort_toml_document(
    doc: tomlkit.TOMLDocument,
    *,
    mode_sections_last: bool = True,
) -> tomlkit.TOMLDocument:
    """Sort a TOML document alphabetically, preserving comments.

    Sorts top-level keys and nested tables recursively.
    Comments attached to keys are preserved and move with their keys.

    Args:
        doc: The TOML document to sort.
        mode_sections_last: If True, mode sections (development, staging)
            are sorted after other keys. Default True.

    Returns:
        The same document, now sorted in place.
    """

    def sort_table(table: tomlkit.items.Table | tomlkit.TOMLDocument) -> None:
        """Sort a single table's keys alphabetically."""
        # Get all items preserving their tomlkit item wrappers
        items: list[tuple[str, Any]] = []
        for key in list(table.keys()):
            items.append((key, table[key]))

        # Sort keys, optionally putting mode sections last
        if mode_sections_last:
            items.sort(key=lambda x: (x[0] in MODE_SECTIONS, x[0]))
        else:
            items.sort(key=lambda x: x[0])

        # Clear and re-add in sorted order
        table.clear()
        for key, value in items:
            table.add(key, value)
            # Recursively sort nested tables
            if isinstance(value, (tomlkit.items.Table, dict)):
                if isinstance(value, tomlkit.items.Table):
                    sort_table(value)

    sort_table(doc)
    return doc

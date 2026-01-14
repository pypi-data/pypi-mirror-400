"""
Environment variable ConfigIO implementation.

Reads config values from environment variables with DJB_ prefix.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from djb.config.storage.io.base import ConfigIO

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase


class EnvDict(dict[str, Any]):
    """Dict that reads from environment variables.

    Enables nested navigation: envdict["hetzner"]["server_type"]
    translates to DJB_HETZNER_SERVER_TYPE.

    This allows the ConfigIO base class to work uniformly across
    all IO types (TOML, Dict, Env) using the same navigate_config_path() logic.

    Inherits from dict for type compatibility, but uses lazy access
    for environment variable lookups.
    """

    def __init__(self, environ: Mapping[str, str], prefix: str = "DJB"):
        """Initialize with environment and prefix.

        Args:
            environ: Environment mapping (os.environ or test dict).
            prefix: Current prefix for lookups (e.g., "DJB", "DJB_HETZNER").
        """
        super().__init__()
        self._environ = environ
        self._prefix = prefix

    def __getitem__(self, key: str) -> Any:
        """Get value or nested EnvDict for section access."""
        # Check if this is a section access (has nested vars)
        nested_prefix = f"{self._prefix}_{key.upper()}_"
        has_nested = any(k.startswith(nested_prefix) for k in self._environ)
        if has_nested:
            # Return nested EnvDict for section navigation
            return EnvDict(self._environ, f"{self._prefix}_{key.upper()}")

        # Direct value access
        env_key = f"{self._prefix}_{key.upper()}"
        if env_key in self._environ:
            return self._environ[env_key]
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        """Check if key exists in environment."""
        if not isinstance(key, str):
            return False
        # Check for nested vars or direct value
        nested_prefix = f"{self._prefix}_{key.upper()}_"
        if any(k.startswith(nested_prefix) for k in self._environ):
            return True
        env_key = f"{self._prefix}_{key.upper()}"
        return env_key in self._environ

    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default fallback."""
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        """Return keys at this prefix level.

        Note: Underscores in env var names are part of the field name,
        not nesting separators. DJB_HETZNER_DEFAULT_SERVER_TYPE yields
        'default_server_type', not 'default'.
        """
        prefix = f"{self._prefix}_"
        result: set[str] = set()
        for env_key in self._environ:
            if env_key.startswith(prefix):
                rest = env_key[len(prefix) :]
                result.add(rest.lower())
        return dict.fromkeys(result).keys()

    def __iter__(self):
        """Iterate over keys at this prefix level."""
        return iter(self.keys())

    def __len__(self) -> int:
        """Count unique keys at this prefix level."""
        return len(self.keys())


class EnvConfigIO(ConfigIO):
    """Config I/O for environment variables with DJB_ prefix.

    Read-only - environment variables are not written by the config system.

    Keys are looked up as DJB_{KEY} in uppercase.
    e.g., "project_name" -> DJB_PROJECT_NAME
    """

    prefix: str = "DJB_"
    name = "env"
    writable = False

    def __init__(
        self,
        config: "DjbConfigBase",
        environ: Mapping[str, str] | None,
    ):
        """Initialize with config reference and optional custom environment.

        Args:
            config: DjbConfig instance (may be partially resolved during bootstrap).
            environ: Environment mapping to use. None means use os.environ.
        """
        super().__init__(config)
        self._environ = environ if environ is not None else os.environ

    def _load_raw_data(self) -> dict[str, Any]:
        """Return EnvDict for navigation."""
        return EnvDict(self._environ)

    def _get_value(self, key: str) -> Any | None:
        """Get a value, converting section EnvDicts to flat dicts.

        Overrides base class to handle the ambiguity of underscores in env var names.
        When accessing a section like "hetzner", we scan for DJB_HETZNER_* vars
        and return a flat dict of {field_name: value}.

        The key can be a dotted path (e.g., "hetzner.default_server_type").
        Full path is composed as: base_prefix.mode_prefix.key
        Then navigates to all-but-last segment, gets value at last segment.

        Args:
            key: Configuration key (may be dotted, e.g., "hetzner.default_server_type").

        Returns:
            The value, or a dict for sections, or None if not found.
        """
        data = self._load_raw_data()

        nav_path, leaf_key = self.full_path(key)

        # Navigate through the path segments (EnvDict requires custom navigation)
        result = data
        if nav_path:
            for segment in nav_path.split("."):
                if result is None:
                    return None
                try:
                    result = result[segment]
                except KeyError:
                    return None

        if result is None:
            return None

        try:
            value = result[leaf_key]
        except KeyError:
            return None

        # If it's a nested EnvDict (section access), convert to flat dict
        if isinstance(value, EnvDict):
            return self._envdict_to_flat_dict(value)
        return value

    def _envdict_to_flat_dict(self, envdict: EnvDict) -> dict[str, Any]:
        """Convert an EnvDict to a flat dict of key-value pairs.

        Scans for all env vars at this level and extracts the flat key names.
        Returns ALL keys after the prefix (underscores are part of the field name).

        Args:
            envdict: The nested EnvDict to convert.

        Returns:
            Flat dict of {field_name: value}.
        """
        full_prefix = f"{envdict._prefix}_"
        result: dict[str, Any] = {}
        for env_key, value in envdict._environ.items():
            if env_key.startswith(full_prefix) and value:
                # Extract field name (may contain underscores)
                field_name = env_key[len(full_prefix) :].lower()
                result[field_name] = value
        return result

    # Everything else inherited from base class (writable=False blocks writes)

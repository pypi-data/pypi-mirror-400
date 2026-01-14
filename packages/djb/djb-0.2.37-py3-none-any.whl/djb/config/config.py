"""
DjbConfig: configuration class with get_djb_config() factory function.

This module provides:
- DjbConfig: Configuration class with field definitions and persistence
- get_djb_config(): Factory function that creates DjbConfig instances

Configuration is loaded with the following priority (highest to lowest):
1. Explicit kwargs passed to get_djb_config()
2. Environment variables (DJB_ prefix)
3. Local config (.djb/local.toml) - user-specific, gitignored
4. Project config (.djb/project.toml) - shared, committed
5. Core config (djb/config/core.toml) - djb defaults
6. Field default values

Each config file can have mode-based sections ([development], [staging]).
For non-production modes, the mode section is merged onto root values within each file.
File priority takes precedence over section priority.

The config_class option allows host projects to extend DjbConfig with custom fields.

Usage:
    # CLI: get config with overrides, attach to context
    cfg = get_djb_config(DjbConfig(project_dir=project_dir, mode=Mode.PRODUCTION))
    ctx.obj.config = cfg

    # Reload config after files change
    cfg.reload()

    # Create augmented config with additional overrides
    prod_config = cfg.augment(DjbConfig(mode=Mode.PRODUCTION))
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Any, Self

from djb.config.storage.base import Provenance
from djb.config.utils import topological_sort
from djb.config.fields import (
    DEFAULT_LOG_LEVEL,
    BoolField,
    EmailField,
    EnumField,
    LogLevelField,
    NameField,
    ProjectDirField,
    ProjectNameField,
    SeedCommandField,
)
from djb.config.fields.cloudflare import CloudflareConfig
from djb.config.fields.domain_config import DomainNameConfig
from djb.config.fields.heroku import HerokuConfig
from djb.config.fields.hetzner import HetznerConfig
from djb.config.fields.k8s import K8sConfig
from djb.config.fields.machine_state import MachineStateConfig
from djb.config.fields.nested import NestedConfigField
from djb.config.fields.secrets import SecretsConfig
from djb.config.field import (
    ClassField,
    ConfigBase,
    ConfigFieldABC,
    ConfigValidationError,
    pass_config,
)
from djb.config.storage import DerivedConfigType, LocalConfigIO, ProjectConfigType
from djb.config.storage.base import ConfigStore
from djb.config.storage.utils import clear_toml_cache
from djb.config.validation import warn_unrecognized_keys
from djb.core.logging import get_logger
from djb.types import Mode, Platform

logger = get_logger(__name__)


# =============================================================================
# LetsEncryptConfig - nested config for Let's Encrypt settings
# =============================================================================


class LetsEncryptConfig(ConfigBase["DjbConfig"]):
    """Let's Encrypt configuration.

    Provides certificate management settings with fallback to global email.
    """

    email: str | None = EmailField(default=None)

    @pass_config.property
    def effective_email(self, config: "DjbConfig") -> str | None:
        """Email for Let's Encrypt, falling back to root config's email."""
        return self.email or config.email


# =============================================================================
# DjbConfig class
# =============================================================================


def _get_resolution_order(fields: dict[str, ConfigFieldABC]) -> list[str]:
    """Get field resolution order: topo-sorted dependent fields first, then rest.

    Fields with depends_on (and fields they depend on) are resolved first
    in topological order. Remaining fields are resolved after.
    """
    # Find all fields that participate in dependency graph
    in_graph: set[str] = set()
    for name, field in fields.items():
        if field.depends_on:
            in_graph.add(name)
            in_graph.update(field.depends_on)

    # Build dependency graph for topo sort
    graph = {
        name: list(fields[name].depends_on) if fields[name].depends_on else []
        for name in in_graph
        if name in fields
    }

    # Topo sort fields in the graph, then append the rest
    sorted_graph = topological_sort(graph) if graph else []
    rest = [name for name in fields if name not in in_graph]
    return sorted_graph + rest


class DjbConfigBase(ConfigBase):
    """Base class with all config infrastructure and bootstrap fields.

    Contains:
    - Bootstrap fields: project_dir, mode (needed by config system)
    - _provenance dict for tracking field sources
    - Provenance methods: is_explicit(), is_derived(), get_source(), is_configured()
    - ConfigStore interface: get(), has(), set(), delete()
    - Serialization: save(), to_json()

    Test configs can extend this to get all infrastructure without
    inheriting DjbConfig's content fields (project_name, email, etc.).
    """

    # === Bootstrap fields ===
    # These are infrastructure fields needed by the config system itself.
    # project_dir: where config files are located
    # mode: affects which config sections are read (development/staging/production)
    # config_class: allows subclassing DjbConfig for custom fields
    # log_level, verbose: logging settings used by config system (e.g., GitConfigIO)
    project_dir: Path = ProjectDirField()
    mode: Mode = EnumField(
        Mode, config_storage=LocalConfigIO, default=Mode.DEVELOPMENT, depends_on=("project_dir",)
    )
    config_class: str = ClassField(
        config_storage=ProjectConfigType,
        default="djb.config.DjbConfig",
        depends_on=("project_dir", "mode"),
    )
    log_level: str = LogLevelField(
        config_storage=ProjectConfigType,
        default=DEFAULT_LOG_LEVEL,
    )
    verbose: bool = BoolField(config_storage=ProjectConfigType, default=False)
    quiet: bool = BoolField(config_storage=ProjectConfigType, default=False)
    yes: bool = BoolField(config_storage=ProjectConfigType, default=False)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Internal state (set during load)
        self._provenance: dict[str, Provenance] = {}
        # Used by djb init to create production-mode config copies
        self._env: Mapping[str, str] | None = None
        # Note: _overrides_dict is inherited from ConfigBase.__init__

    # to_dict() is inherited from ConfigBase

    def to_json(self, indent: int = 2) -> str:
        """Convert config to a JSON string.

        Args:
            indent: Number of spaces for indentation. Default is 2.

        Returns:
            JSON string representation of the config.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save(self) -> None:
        """Save all fields using set() which routes via provenance.

        Each field is saved to its source location (if read from a file)
        or its default destination (based on config_storage).
        """
        for field_name, config_field in type(self).__fields__.items():
            # Skip DERIVED fields (e.g., project_dir) - they're never persisted
            if config_field.config_storage is DerivedConfigType:
                continue

            value = getattr(self, field_name)
            if value is None:
                continue

            # Convert enums to strings for storage
            if isinstance(value, Enum):
                value = str(value)

            # Use set() which routes via provenance
            self.set(field_name, value)

    def is_explicit(self, field_name: str) -> bool:
        """Check if a field was explicitly configured.

        Args:
            field_name: Field name to check.

        Returns:
            True if the field value came from an explicit source
            (CLI, env var, or config file).
        """
        provenance = self.get_source(field_name)
        if not provenance:
            return False
        # The last element in provenance is the ConfigIO - check its explicit property
        return getattr(provenance[-1], "explicit", True)

    def is_derived(self, field_name: str) -> bool:
        """Check if a field was derived from secondary sources.

        Args:
            field_name: Field name to check.

        Returns:
            True if the field value was derived (from pyproject.toml,
            git config, or directory name).
        """
        provenance = self.get_source(field_name)
        if not provenance:
            return False
        # Derived is the opposite of explicit
        return not getattr(provenance[-1], "explicit", True)

    def is_configured(self, field_name: str) -> bool:
        """Check if a field has a configured value.

        Args:
            field_name: Field name to check.

        Returns:
            True if the field has a source in provenance tracking.
        """
        return self.get_source(field_name) is not None

    def get_source(self, field_name: str) -> Provenance | None:
        """Get the source of a field's value.

        Returns the provenance from the _provenance dict.

        Args:
            field_name: Field name to check.

        Returns:
            The Provenance for the field, or None if not tracked.
        """
        return self._provenance.get(field_name)

    # =========================================================================
    # ConfigStore interface
    # =========================================================================

    def get(self, key: str, *, mode: str | None = None) -> tuple[Any, Provenance | None]:
        """Get field value and provenance (ConfigStore interface).

        Returns the already-resolved value from the frozen instance,
        and delegates provenance lookup to the chain.

        Args:
            key: Field name to get.
            mode: Not used (for interface compatibility).

        Returns:
            Tuple of (value, provenance).
        """
        value = getattr(self, key, None)
        provenance = self.get_source(key)
        return (value, provenance)

    def has(self, key: str, *, mode: str | None = None) -> bool:
        """Check if field exists (ConfigStore interface).

        Args:
            key: Field name to check.
            mode: Not used (for interface compatibility).

        Returns:
            True if the field exists and has a value.
        """
        return hasattr(self, key) and getattr(self, key, None) is not None

    def set(
        self,
        key: str,
        value: Any,
        *,
        target_store: ConfigStore | None = None,
    ) -> Any:
        """Set field value via provenance routing.

        Normalizes and validates the value before storing. Routes writes via
        provenance: if the field was read from a writable source, write back
        to that source. If the source is not writable (e.g., CLI, env), use
        the field's default destination instead.

        Args:
            key: Field path to set (e.g., "project_name" or "hetzner.server_name").
            value: Value to set (will be normalized and validated).
            target_store: Explicit storage target (for --project/--local CLI flags).

        Returns:
            The normalized value that was stored.

        Raises:
            ConfigValidationError: If validation fails.
        """
        field_meta = get_field_descriptor(key, type(self))
        provenance = self._provenance.get(key)

        # Normalize and validate
        normalized_value = field_meta.normalize(value)
        if normalized_value is None:
            hint = field_meta.validation_hint or "valid format required"
            raise ConfigValidationError(f"Invalid value for {key}: {value!r}. Expected: {hint}")
        field_meta.validate(normalized_value)

        # Determine target store and rest of provenance chain
        if target_store is not None:
            # Explicit target override (--project/--local flags)
            store = target_store
            rest: Provenance = ()
        elif provenance and provenance[0].writable:
            # Existing value from writable source - write back to same source
            store = provenance[0]
            rest = provenance[1:]
        else:
            # New value or non-writable source - instantiate field's preferred storage
            # Uses config.mode for mode-aware section writing
            store = field_meta.config_storage(self)
            rest = ()

        # Serialize for storage (convert custom objects to TOML-compatible dicts)
        serialized_value = field_meta.serialize(normalized_value)

        store.set(key, serialized_value, rest=rest)

        # Update in-memory value as well (for MachineState and other workflows
        # that need immediate access to the updated value)
        self._set_in_memory(key, normalized_value)

        return normalized_value

    def _set_in_memory(self, key: str, value: Any) -> None:
        """Update in-memory value for a field.

        Handles dotted paths for nested fields (e.g., "hetzner.server_name").

        Args:
            key: Field path (e.g., "project_name" or "hetzner.server_name").
            value: Normalized value to set.
        """
        parts = key.split(".")
        if len(parts) == 1:
            # Top-level field
            setattr(self, key, value)
        else:
            # Nested field - navigate to the nested object and set the attribute
            obj: Any = self
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)

    def delete(
        self,
        key: str,
        *,
        target_store: ConfigStore | None = None,
    ) -> None:
        """Delete field value via provenance routing.

        Routes deletes via provenance: if the field was read from a writable source,
        delete from that source. If target_store is specified, use that instead.

        Args:
            key: Field path to delete (e.g., "project_name" or "hetzner.server_name").
            target_store: Explicit storage target (for --project/--local CLI flags).
        """
        field_meta = get_field_descriptor(key, type(self))
        provenance = self._provenance.get(key)

        # Determine target store and rest of provenance chain
        if target_store is not None:
            # Explicit target override (--project/--local flags)
            store = target_store
            rest: Provenance = ()
        elif provenance and provenance[0].writable:
            # Provenance-based routing - delete from same source
            store = provenance[0]
            rest = provenance[1:]
        else:
            # Fallback to field's preferred storage
            # Uses config.mode for mode-aware section deletion
            store = field_meta.config_storage(self)
            rest = ()

        store.delete(key, rest=rest)

    @property
    def writable(self) -> bool:
        """Whether this store supports writes."""
        return True

    def _resolve_fields(self, env: Mapping[str, str] | None) -> None:
        """Resolve all fields in dependency order.

        Shared implementation used by both _load() and reload().
        Updates self.__dict__ and self._provenance in place.

        Args:
            env: Environment variables mapping.
        """
        config_cls = type(self)
        resolution_order = _get_resolution_order(config_cls.__fields__)

        # Clear provenance
        self._provenance = {}

        # Pre-initialize all fields to None so they're accessible during resolution
        for field_name in resolution_order:
            self.__dict__[field_name] = None

        # Resolve fields in dependency order
        for field_name in resolution_order:
            config_field = config_cls.__fields__[field_name]
            value, provenance = config_field.resolve(self, env=env)
            config_field.validate(value)
            self.__dict__[field_name] = value
            if provenance is not None:
                self._provenance[field_name] = provenance

    def reload(self) -> Self:
        """Reload config from files in-place.

        Re-resolves all fields using the original env and overrides.
        Anyone holding a reference to this config sees the updated values.

        Note:
            config_class changes are not supported by reload. If config_class
            would change (e.g., project.toml now points to a different class),
            you need to create a new config instance via get_djb_config().

        Returns:
            Self for chaining.
        """
        # Clear TOML cache to ensure we read fresh file contents
        clear_toml_cache()
        self._resolve_fields(self._env)
        return self

    @classmethod
    def _load(
        cls,
        env: Mapping[str, str] | None = None,
        *,
        overrides_dict: dict[str, Any] | None = None,
        _config_cls: type["DjbConfigBase"] | None = None,
    ) -> Self:
        """Load config from all sources via incremental bootstrap.

        This is the main entry point for creating a DjbConfig instance.
        Fields are resolved in topological order based on their depends_on
        declarations.

        Bootstrap order (via topological sort):
        1. project_dir - no dependencies
        2. mode - depends on project_dir
        3. config_class - depends on project_dir, mode
        4. All other fields - implicitly depend on project_dir, mode

        The config_class option allows host projects to extend DjbConfig:
        - Create a subclass of DjbConfig with custom fields
        - Set config_class in project.toml or via env/CLI
        - This method will return an instance of that subclass

        Args:
            env: Environment variables mapping (defaults to os.environ).
            overrides_dict: Dict with values to override. Keys present in the dict
                are used as overrides; missing keys fall through to the next layer.
            _config_cls: Internal parameter for recursive load with a different class.
                When set, uses this class instead of cls.

        Returns:
            A fully resolved DjbConfig (or subclass) instance.
        """
        # Use specified class or default to cls (typically DjbConfig)
        config_cls = _config_cls or cls

        # Create empty config instance (bypass __init__ to set fields incrementally)
        config = object.__new__(config_cls)
        config._env = env  # Store env for later use (e.g., creating production-mode copy)
        config._overrides_dict = overrides_dict or {}  # Store for resolution chain

        # Resolve all fields
        config._resolve_fields(env)

        # After resolving, check if config_class switched (only on first load)
        if _config_cls is None:
            cc_field = config_cls.__fields__["config_class"]
            assert isinstance(cc_field, ClassField)
            actual_class = cc_field.import_class(config.config_class)

            # Validate it's a DjbConfig subclass
            if not issubclass(actual_class, DjbConfig):
                raise ConfigValidationError(
                    f"config_class must be a DjbConfig subclass, got: {actual_class}"
                )

            # If config_class is different, let the new class redo the work
            if actual_class is not config_cls:
                return cls._load(env=env, overrides_dict=overrides_dict, _config_cls=actual_class)

        # Warn about unrecognized keys in config files
        warn_unrecognized_keys(config, config_cls)

        return config  # type: ignore[return-value]  # config is Self (created via object.__new__)


class DjbConfig(DjbConfigBase):
    """Configuration for djb CLI - field definitions only.

    Created via get_djb_config() which resolves values from multiple sources.

    Field resolution priority (handled by get_djb_config):
    1. Explicit kwargs passed to get_djb_config()
    2. Environment variables (DJB_ prefix)
    3. Local config (.djb/local.toml)
    4. Project config (.djb/project.toml)
    5. Defaults (e.g. pyproject.toml for project_name)

    Provenance tracking records where each value came from, enabling:
    - Consistent save behavior (preserve original source file)
    - Init workflow (skip already-configured fields)
    - Debugging (show source in `djb config show --provenance`)

    Descriptor behavior:
    - DjbConfig.field_name -> returns ConfigFieldABC instance (for introspection)
    - instance.field_name -> returns actual value
    """

    # === Content fields ===
    # project_dir, mode, and config_class are inherited from DjbConfigBase
    # All use default depends_on=("project_dir", "mode")
    project_name: str = ProjectNameField(config_storage=ProjectConfigType)
    platform: Platform = EnumField(
        Platform,
        config_storage=ProjectConfigType,
        default=Platform.HEROKU,
    )
    name: str | None = NameField(config_storage=LocalConfigIO, default=None)
    email: str | None = EmailField(config_storage=LocalConfigIO, default=None)
    seed_command: str | None = SeedCommandField(config_storage=ProjectConfigType, default=None)

    # === Secrets settings ===
    secrets: SecretsConfig = NestedConfigField(SecretsConfig)

    # === Hetzner Cloud settings ===
    # Nested config for Hetzner Cloud (reads from [hetzner] section)
    hetzner: HetznerConfig = NestedConfigField(HetznerConfig)

    # === Heroku deployment settings ===
    heroku: HerokuConfig = NestedConfigField(HerokuConfig)

    # === Kubernetes deployment settings ===
    k8s: K8sConfig = NestedConfigField(K8sConfig)

    # === Cloudflare DNS settings ===
    cloudflare: CloudflareConfig = NestedConfigField(CloudflareConfig)

    # === Let's Encrypt certificate settings ===
    letsencrypt: LetsEncryptConfig = NestedConfigField(LetsEncryptConfig)

    # === Machine state settings ===
    machine_state: MachineStateConfig = NestedConfigField(MachineStateConfig)

    # === Properties that access specific DjbConfig fields ===

    @property
    def domain_names(self) -> dict[str, DomainNameConfig]:
        """Get domain names map for the active deployment platform.

        This is the primary interface for application code that needs domain names
        without caring about the deployment platform. Returns heroku.domain_names or
        k8s.domain_names based on the current platform setting.

        Example:
            config = get_djb_config()
            for domain, domain_config in config.domain_names.items():
                print(f"Serving on {domain} (manager: {domain_config.manager})")
        """
        if self.platform == Platform.HEROKU:
            return self.heroku.domain_names
        else:  # K8S
            return self.k8s.domain_names

    @property
    def domain_names_list(self) -> list[str]:
        """Get list of domain names for the active deployment platform.

        Convenience property that returns just the domain name strings.

        Example:
            config = get_djb_config()
            for domain in config.domain_names_list:
                print(f"Serving on {domain}")
        """
        return list(self.domain_names.keys())

    @property
    def db_name(self) -> str:
        """Get database name for PostgreSQL.

        Returns k8s.db_name if configured, otherwise derives from project_name
        by replacing hyphens with underscores (PostgreSQL identifier requirement).

        Example:
            config = get_djb_config()
            # For project_name="my-app", returns "my_app"
            # Or returns k8s.db_name if explicitly configured
            print(f"Database: {config.db_name}")
        """
        if self.k8s.db_name:
            return self.k8s.db_name
        return self.project_name.replace("-", "_")

    def augment(self, overrides: "DjbConfig") -> "DjbConfig":
        """Return new config with overrides layered on top.

        The original config is not modified.

        Args:
            overrides: DjbConfig with values to override.

        Returns:
            New DjbConfig with overrides applied.
        """
        parent_overrides = self.to_overrides()
        child_overrides = overrides.to_overrides()
        merged = _deep_merge(parent_overrides, child_overrides)
        return DjbConfig._load(env=self._env, overrides_dict=merged)


# =============================================================================
# Field utilities
# =============================================================================


def get_field_descriptor(
    field_path: str,
    config_class: type[DjbConfigBase] | None = None,
) -> ConfigFieldABC:
    """Get the field descriptor for a DjbConfig field.

    Supports flat fields and nested field paths of arbitrary depth:
    - "project_name" - flat field
    - "hetzner.default_server_type" - one level nesting
    - "hetzner.eu.server_type" - two levels nesting

    Args:
        field_path: Field path - "field_name" or "section.path.field_name"
        config_class: Config class to inspect (default: DjbConfig)

    Returns:
        The ConfigFieldABC instance for the field (a copy with nested_field_prefix set
        for nested fields).

    Raises:
        AttributeError: If the field doesn't exist.
        ValueError: If the path doesn't resolve to a config field.
    """
    cls = config_class or DjbConfig
    parts = field_path.split(".")

    # getattr on class returns descriptor (via __get__(obj=None))
    # Raises AttributeError if field doesn't exist
    result = getattr(cls, parts[0])

    # NestedConfigField.__getattr__ handles chaining and nested_field_prefix accumulation.
    # Each step returns a COPY with the correct nested_field_prefix built up.
    for part in parts[1:]:
        result = getattr(result, part)

    if not isinstance(result, ConfigFieldABC):
        raise ValueError(f"{field_path} is not a config field")

    return result


def normalize_and_validate(field_path: str, value: Any) -> Any:
    """Normalize and validate a config value by field path.

    This is a convenience function that combines field lookup, normalization,
    and validation in a single call. Used by CLI commands to process user input.

    Args:
        field_path: Field path - "field_name" or "section.path.field_name"
        value: Raw value to normalize and validate.

    Returns:
        The normalized value after validation.

    Raises:
        ValueError: If the field doesn't exist.
        ConfigValidationError: If validation fails.
    """
    field_meta = get_field_descriptor(field_path)
    normalized = field_meta.normalize(value)
    field_meta.validate(normalized)
    return normalized


def get_djb_config(
    overrides: DjbConfig | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> DjbConfig:
    """Get the djb configuration, resolving from multiple sources.

    Resolution order (highest to lowest priority):
    1. Overrides passed to this function
    2. Environment variables (DJB_*)
    3. Local config (.djb/local.toml)
    4. Project config (.djb/project.toml)
    5. Core config (djb/config/core.toml) - djb defaults
    6. Field default values

    The config_class option allows host projects to extend DjbConfig:
    - Create a subclass of DjbConfig with custom fields
    - Set config_class in project.toml or pass via CLI/env
    - djb will use your subclass for all config operations

    Each call returns a fresh config instance. If you want to share config
    across your application, store the returned instance in a shared location.
    Use config.reload() to update an existing config in-place after files change.

    Args:
        overrides: DjbConfig with values to override.
        env: Environment variables mapping. If None, uses os.environ.
            Pass an empty dict {} for test isolation.

    Returns:
        A DjbConfig instance (or subclass) with all fields resolved.

    Example:
        # CLI usage
        config = get_djb_config(DjbConfig(project_dir=Path("/my/project"), mode=Mode.PRODUCTION))

        # Reload after config files change
        config.reload()

        # Create augmented config with overrides
        override_config = DjbConfig(mode=Mode.PRODUCTION)
        prod_config = config.augment(override_config)
    """
    overrides_dict = overrides.to_overrides() if overrides else None
    return DjbConfig._load(env=env, overrides_dict=overrides_dict)


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge dicts, overlay wins on conflicts."""
    result = dict(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result

"""
Config field definitions - abstract base class and common field types.

This module provides:
- ConfigValidationError: Exception for validation failures
- NOTHING: Sentinel for "no default value"
- ConfigFieldABC: Abstract base class for declarative config fields (now a descriptor)
- ConfigMeta: Metaclass that collects ConfigFieldABC descriptors
- ConfigBase: Base class for config classes with field introspection
- StringField: Simple string field
"""

from __future__ import annotations

import importlib
from abc import ABC
from collections.abc import Callable, Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Generic, TYPE_CHECKING, TypeVar, dataclass_transform

from djb.core.logging import get_logger
from djb.config.acquisition import AcquisitionContext, AcquisitionResult
from djb.config.prompting import prompt
from djb.config.resolution import ResolutionChain, get_standard_stores

from djb.config.storage import DerivedConfigType, ProjectConfigType
from djb.config.storage.base import ConfigStore, Provenance

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    pass


# =============================================================================
# NOTHING sentinel - replaces attrs.NOTHING
# =============================================================================


class _Nothing:
    """Sentinel value for 'no default provided'.

    Used to distinguish between "no default" and "default is None".
    """

    _instance: "_Nothing | None" = None

    def __new__(cls) -> "_Nothing":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "NOTHING"

    def __bool__(self) -> bool:
        return False


NOTHING = _Nothing()


# =============================================================================
# pass_config decorator - inject config into nested config methods/properties
# =============================================================================

ConfigT = TypeVar("ConfigT", bound="ConfigBase")


class pass_config:
    """Descriptor that passes config as the first positional arg to nested
    config field methods (after self).

    Use @pass_config.property to pass config to properties.

    Usage:
        class LetsEncryptConfig(ConfigBase["DjbConfig"]):
            @pass_config
            def get_effective_email(self, config: DjbConfig) -> str | None:
                return self.email or config.email

            @pass_config.property
            def effective_email(self, config: DjbConfig) -> str | None:
                return self.email or config.email

    Note: The position of `config` depends on decoration order. If stacking with
    other arg-injecting decorators, topmost decorator's arg comes first.
    """

    class property:
        """Property descriptor that injects config as first positional arg."""

        def __init__(self, fn: Callable[..., Any]) -> None:
            self._fn = fn

        def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
            if obj is None:
                return self
            config = getattr(obj, "_config", None)
            return self._fn(obj, config)

    def __init__(self, fn: Callable[..., Any]) -> None:
        self._fn = fn

    def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
        if obj is None:
            return self

        config = getattr(obj, "_config", None)
        fn = self._fn

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(obj, config, *args, **kwargs)

        return wrapper


logger = get_logger(__name__)


# =============================================================================
# ConfigFieldABC - Abstract base class for config fields
# =============================================================================


class ConfigFieldABC(ABC):
    """Abstract base for config fields - now a Python descriptor.

    Subclass this to create reusable field types with custom resolution logic.
    ConfigFieldABC is a descriptor: class-level access returns the descriptor,
    instance-level access returns the value.

    Each field builds its own ResolutionChain for fully customizable resolution.
    Field-specific config_stores (like GitConfigIO) are appended to the standard
    chain: cli > env > local > project > core.

    Override these methods as needed:
    - resolve(ctx): Custom resolution logic (default: chain > default)
    - acquire(ctx): Interactive configuration (default: config_stores > prompt)
    - normalize(value): Transform raw values (default: identity)
    - validate(value): Validate resolved values (default: no-op)
    - get_default(): Computed defaults (default: returns self.default)

    Descriptor behavior:
    - DjbConfig.field_name -> returns this ConfigFieldABC instance
    - instance.field_name -> returns the actual value

    Attributes:
        field_name: Set by __set_name__ based on the attribute name. Used for
            auto-deriving env_key and config_file_key.
        config_storage: Which ConfigStore to save to by default.
            Provenance takes precedence when saving.
        prompt_text: Prompt message for user input during init.
        validation_hint: Hint shown when validation fails.
        config_stores: Field-specific stores appended to default chain.
    """

    # Set by __set_name__ when assigned to class
    field_name: str | None = None

    # Set by get_field_descriptor() or NestedConfigField.__getattr__ for nested fields
    nested_field_prefix: str | None = None

    # Configuration attributes (set by subclasses or __init__)
    prompt_text: str | None = None
    validation_hint: str | None = None
    # Field-specific extra stores - factories that take config and return ConfigStore
    config_store_factories: Sequence[Callable[["DjbConfigBase"], ConfigStore]]
    # Field dependencies for ordered resolution during bootstrap
    depends_on: tuple[str, ...]

    # Per-field resolution state
    _chain: "ResolutionChain | None" = None  # Built lazily during resolution
    _provenance: Provenance | None = None  # Cached provenance from last resolution

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Create field instance. Returns Any to satisfy pyright for field assignments."""
        return super().__new__(cls)

    def __init__(
        self,
        *,
        env_key: str | None = None,
        config_file_key: str | None = None,
        config_storage: type[ConfigStore] = ProjectConfigType,
        default: Any = NOTHING,
        prompt_text: str | None = None,
        validation_hint: str | None = None,
        config_store_factories: Sequence[Callable[["DjbConfigBase"], ConfigStore]] | None = None,
        depends_on: tuple[str, ...] | None = None,
    ):
        """Initialize a config field.

        Args:
            env_key: Full env var name (e.g., "DJB_EMAIL"), or None to derive
                from field name.
            config_file_key: Config file key, or None to derive from field name.
            config_storage: ConfigStore class for saving. Instances are created
                at resolution time with config. Use LocalConfigIO for personal settings,
                ProjectConfigType for shared settings, DerivedConfigType for computed.
            default: Default value if not found in any source.
            prompt_text: Prompt message for user input during init.
            validation_hint: Hint shown when validation fails.
            config_store_factories: Factories that create field-specific stores.
                Each factory takes config and returns a ConfigStore instance.
                Use functools.partial for stores that need args:
                    config_store_factories=[partial(GitConfigIO, "user.name")]
            depends_on: Field names this field depends on for resolution order.
                Used during bootstrap to ensure dependencies are resolved first.
        """
        self._env_key = env_key
        self._config_file_key = config_file_key
        self.config_storage = config_storage
        self.default = default
        self.prompt_text = prompt_text
        self.validation_hint = validation_hint
        self.config_store_factories = config_store_factories or []
        self.depends_on = depends_on or ()
        self._chain = None
        self._provenance = None

    # =========================================================================
    # Descriptor protocol
    # =========================================================================

    def __set_name__(self, owner: type, name: str) -> None:
        """Called when descriptor is assigned to a class.

        Automatically captures the attribute name as field_name.
        """
        self.field_name = name

    def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
        """Descriptor get - return self for class access, value for instance access."""
        if obj is None:
            # Class-level access: DjbConfig.project_name -> ConfigFieldABC
            return self
        # Instance-level access: config.project_name -> actual value
        assert self.field_name is not None, "field_name not set"
        return obj.__dict__.get(self.field_name)

    def _build_chain(
        self,
        config: "DjbConfigBase",
        *,
        env: Mapping[str, str] | None = None,
    ) -> ResolutionChain:
        """Build this field's resolution chain.

        Creates a ResolutionChain with standard stores (override > env > local > project > core)
        plus field-specific stores (from factories) as fallbacks at the end.

        Args:
            config: DjbConfig instance (may be partially resolved during bootstrap).
            env: Environment variables mapping. None means use os.environ.

        Returns:
            ResolutionChain configured for this field.
        """
        # Instantiate field-specific stores from factories
        extra_stores = [factory(config) for factory in self.config_store_factories]
        stores = get_standard_stores(config, env=env) + extra_stores
        return ResolutionChain(stores)

    @property
    def env_key(self) -> str:
        """Get env var name. Derives from field_name if not explicitly set.

        Raises:
            RuntimeError: If accessed before field_name is set.
        """
        if self._env_key is not None:
            return self._env_key
        if self.field_name is None:
            raise RuntimeError(
                "env_key accessed before field_name was set. "
                "Ensure field_name is assigned before accessing env_key."
            )
        return f"DJB_{self.field_name.upper()}"

    @property
    def config_file_key(self) -> str:
        """Get config file key. Derives from field_name if not explicitly set.

        Raises:
            RuntimeError: If accessed before field_name is set.
        """
        if self._config_file_key is not None:
            return self._config_file_key
        if self.field_name is None:
            raise RuntimeError(
                "config_file_key accessed before field_name was set. "
                "Ensure field_name is assigned before accessing config_file_key."
            )
        return self.field_name

    def resolve(
        self,
        config: "DjbConfigBase",
        *,
        key_prefix: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> tuple[Any, Provenance | None]:
        """Resolve this field's value using this field's chain.

        Each field builds its own resolution chain (override > env > local > project > core).
        Override in subclasses for custom resolution logic.

        Args:
            config: DjbConfig instance (may be partially resolved during bootstrap).
            key_prefix: Optional prefix for nested fields (e.g., "hetzner" or "hetzner.eu").
                When set, the full key becomes "{key_prefix}.{config_file_key}".
            env: Environment variables mapping. None means use os.environ.

        Returns:
            Tuple of (resolved_value, provenance). Provenance is a tuple of
            ConfigStore instances representing the path, or None for defaults.
        """
        # Always build fresh chain - config may differ between calls
        # (field instances are shared across DjbConfig instances)
        self._chain = self._build_chain(config, env=env)

        if self.config_file_key:
            # Build full key with prefix for nested fields
            key = f"{key_prefix}.{self.config_file_key}" if key_prefix else self.config_file_key
            # Iterate through all sources, trying each until finding a valid one
            for raw, provenance in self._chain.get_all(key):
                try:
                    normalized = self.normalize(raw)
                    # If normalize returns None, treat as invalid and try next source
                    if normalized is not None:
                        self._provenance = provenance  # Cache on field
                        return (normalized, provenance)
                except (ConfigValidationError, ValueError, TypeError):
                    # Normalization failed, try next source
                    continue

        # Default - no provenance for default values
        self._provenance = None
        default_value = self.get_default()
        if default_value is not None:
            return (default_value, None)
        return (None, None)

    def normalize(self, value: Any) -> Any:
        """Normalize a raw value. Override for custom normalization."""
        return value

    def serialize(self, value: Any) -> Any:
        """Serialize a value for TOML storage. Override for custom objects.

        Called before writing to TOML. Default returns value unchanged.
        Override to convert custom objects (like DomainNameConfig) to dicts.
        """
        return value

    def validate(self, value: Any) -> None:
        """Validate resolved value. Override to add validation.

        Raise ConfigValidationError if validation fails.
        """
        pass

    def get_default(self) -> Any:
        """Get the default value. Override for computed defaults."""
        if self.default is NOTHING:
            return None
        return self.default

    @property
    def display_name(self) -> str:
        """Human-readable name for display.

        Raises:
            RuntimeError: If accessed before field_name is set.
        """
        if self.field_name is None:
            raise RuntimeError(
                "display_name accessed before field_name was set. "
                "Ensure field_name is assigned before accessing display_name."
            )
        return self.field_name.replace("_", " ").title()

    def _is_valid(self, value: str) -> bool:
        """Check if a string value is valid. Returns True if valid."""
        try:
            self.validate(value)
            return True
        except (ConfigValidationError, ValueError, TypeError):
            return False

    def _require_string(self, value: Any, *, allow_none: bool = True) -> bool:
        """Validate that value is a string (or None if allowed).

        Args:
            value: The value to validate.
            allow_none: If True, None values skip validation. Default True.

        Returns:
            True if validation should continue (value is a string).
            False if value is None and allow_none is True (skip further validation).

        Raises:
            ConfigValidationError: If value is not a string (or None when allowed).
        """
        if value is None:
            if allow_none:
                return False  # Skip further validation
            raise ConfigValidationError(f"{self.field_name} is required")
        if not isinstance(value, str):
            raise ConfigValidationError(
                f"{self.field_name} must be a string. Got: {type(value).__name__}"
            )
        return True  # Continue with further validation

    def _prompted_result(self, value: Any) -> AcquisitionResult:
        """Create an AcquisitionResult after successful prompting.

        Logs the 'saved' message and creates the result with standard
        prompted-value settings (should_save=True, was_prompted=True).

        Args:
            value: The value from prompting.

        Returns:
            AcquisitionResult ready for return from acquire().
        """
        logger.done(f"{self.display_name} saved: {value}")
        return AcquisitionResult(
            value=value,
            should_save=True,
            source_name=None,
            was_prompted=True,
        )

    def acquire(
        self, acq_ctx: AcquisitionContext, config: "DjbConfigBase"
    ) -> AcquisitionResult | None:
        """Acquire a value for this field interactively.

        Default implementation:
        1. Try config_stores in order (field-specific stores like GitConfigIO)
        2. Fall back to prompting

        Note: Explicit fields (from config file) are skipped by the orchestrator
        before acquire() is called.

        Override in subclasses for custom behavior (e.g., confirmation flow).

        Args:
            acq_ctx: Acquisition context with project_root, current value, etc.
            config: DjbConfig instance for store instantiation.

        Returns:
            AcquisitionResult with value and metadata, or None to skip this field.
        """
        # 1. Try field-specific stores (like GitConfigIO)
        for factory in self.config_store_factories:
            store = factory(config)
            if store.has(self.config_file_key):
                value, _ = store.get(self.config_file_key)
                if value and self._is_valid(value):
                    return AcquisitionResult(
                        value=value,
                        should_save=True,
                        source_name=store.name,
                        was_prompted=False,
                    )

        # 2. Prompt user (if prompt_text is set)
        if not self.prompt_text:
            # No prompting configured - return current value if any
            if acq_ctx.current_value is not None:
                return AcquisitionResult(
                    value=acq_ctx.current_value,
                    should_save=False,
                    source_name=None,
                    was_prompted=False,
                )
            return None

        result = prompt(
            self.prompt_text,
            default=str(acq_ctx.current_value) if acq_ctx.current_value else None,
            validator=self._is_valid,
            validation_hint=self.validation_hint,
        )

        if result.source == "cancelled":
            return None

        value = self.normalize(result.value) if result.value else result.value
        return self._prompted_result(value)

    def set(self, value: Any, config: "DjbConfigBase") -> None:
        """Save a value to the appropriate config file.

        Uses config_storage metadata to determine storage location:
        - LocalConfigIO: Goes to local.toml (gitignored, user-specific)
        - ProjectConfigType: Goes to project.toml (committed, shared)
        - DerivedConfigType: Never saved (skip silently)

        Args:
            value: The value to save.
            config: DjbConfig instance.
        """
        if self.config_storage is DerivedConfigType:
            return  # DERIVED fields are never persisted

        file_key = self.config_file_key
        assert file_key is not None, "field_name must be set before saving"

        # Create store instance with config and save
        store = self.config_storage(config)
        store.set(key=file_key, value=value)


# =============================================================================
# ConfigMeta metaclass and ConfigBase
# =============================================================================


@dataclass_transform(field_specifiers=(ConfigFieldABC,))
class ConfigMeta(type):
    """Metaclass that collects ConfigFieldABC descriptors into __fields__.

    Any class using this metaclass will have a __fields__ class attribute
    containing a dict mapping field names to ConfigFieldABC instances.
    """

    def __new__(
        mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any
    ) -> "ConfigMeta":
        cls = super().__new__(mcs, name, bases, namespace)

        # Collect all ConfigFieldABC descriptors (including from base classes)
        fields: dict[str, ConfigFieldABC] = {}

        # First, collect from base classes (in MRO order, reversed for correct override)
        for base in reversed(cls.__mro__[1:]):
            if hasattr(base, "__fields__"):
                fields.update(base.__fields__)

        # Then collect from this class's namespace
        for attr_name, value in namespace.items():
            if isinstance(value, ConfigFieldABC):
                fields[attr_name] = value

        cls.__fields__ = fields  # type: ignore[attr-defined]
        return cls


@dataclass_transform(field_specifiers=(ConfigFieldABC,))
class ConfigBase(Generic[ConfigT], metaclass=ConfigMeta):
    """Base class for config classes with field introspection.

    Provides equality, repr, and to_dict() methods. Mutable after initialization.

    Type parameter ConfigT specifies the root config type for @pass_config access.
    Nested configs use this to declare the type they expect, e.g.:
        class LetsEncryptConfig(ConfigBase["DjbConfig"]): ...
    """

    __fields__: ClassVar[dict[str, ConfigFieldABC]]  # Set by ConfigMeta
    _config: ConfigT | None = None  # Set by NestedConfigField for @pass_config access

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with keyword arguments.

        Args:
            **kwargs: Field values to set. Missing fields get their defaults.

        Raises:
            TypeError: If an unknown field is provided.
        """
        # Keep overrides (deep) to enable layering additional overrides once
        # they are known (e.g. in a CLI sub-command).
        self._overrides_dict: dict[str, Any] = {}

        # Track ALL passed kwargs including None values (for mock fixture support)
        self._passed_kwargs: set[str] = set(kwargs.keys())

        # Set provided values via descriptors
        for name, value in kwargs.items():
            if name not in type(self).__fields__:
                raise TypeError(f"Unknown field: {name}")
            setattr(self, name, value)
            if value is not None:
                # Use duck-typing to detect nested ConfigBase (avoid circular import)
                if hasattr(type(value), "__fields__"):
                    # Nested ConfigBase - grab its _overrides_dict
                    nested = getattr(value, "_overrides_dict", {})
                    if nested:
                        self._overrides_dict[name] = nested
                else:
                    # Regular value
                    self._overrides_dict[name] = self._convert_value(value)

        # Apply defaults for missing fields
        for name, field in type(self).__fields__.items():
            if name not in kwargs:
                default = field.get_default()
                setattr(self, name, default)

    def to_overrides(self) -> dict[str, Any]:
        """Return the overrides dict for this config.

        Used by augment() and get_djb_config() to merge overrides from multiple configs.
        Note: None values are excluded (they fall through to lower layers).
        """
        return dict(self._overrides_dict)

    def passed_kwargs(self) -> set[str]:
        """Return the set of field names that were explicitly passed to __init__."""
        return set(self._passed_kwargs)

    def __eq__(self, other: object) -> bool:
        """Equality check based on field values."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return all(getattr(self, name) == getattr(other, name) for name in type(self).__fields__)

    def __repr__(self) -> str:
        """Generate repr showing all field values."""
        fields_str = ", ".join(f"{name}={getattr(self, name)!r}" for name in type(self).__fields__)
        return f"{type(self).__name__}({fields_str})"

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, recursively converting nested configs.

        Path objects are converted to strings, Enum values to their string values.
        Dicts containing ConfigBase instances are recursively converted.
        """
        result: dict[str, Any] = {}
        for field_name in type(self).__fields__:
            value = getattr(self, field_name)
            result[field_name] = self._convert_value(value)
        return result

    def _convert_value(self, value: Any) -> Any:
        """Recursively convert a value for JSON serialization."""
        # Handle nested ConfigBase instances
        if isinstance(value, ConfigBase):
            return value.to_dict()
        # Handle dicts (may contain ConfigBase values)
        if isinstance(value, dict):
            return {k: self._convert_value(v) for k, v in value.items()}
        # Handle lists (may contain ConfigBase values)
        if isinstance(value, list):
            return [self._convert_value(v) for v in value]
        # Convert Path to string
        if isinstance(value, Path):
            return str(value)
        # Convert Enum values to strings
        if isinstance(value, Enum):
            return value.value
        return value


# =============================================================================
# Common field types
# =============================================================================


class StringField(ConfigFieldABC):
    """Simple string field with no special behavior.

    This is just ConfigFieldABC with no overrides - an alias for clarity.
    """

    pass


class ClassField(ConfigFieldABC):
    """Field for Python class paths (module.path.ClassName format).

    Validates format and provides clear error messages. Use import_class()
    to import the class after resolution.
    """

    def __init__(
        self,
        *,
        base_class: type | None = None,
        **kwargs: Any,
    ):
        """Initialize a class field.

        Args:
            base_class: If provided, import_class() validates the imported class
                is a subclass of this type.
            **kwargs: Passed to ConfigFieldABC.__init__().
        """
        super().__init__(**kwargs)
        self.base_class = base_class

    def validate(self, value: Any) -> None:
        """Validate class path format."""
        if not self._require_string(value):
            return

        if "." not in value:
            raise ConfigValidationError(
                f"{self.field_name} must be in 'module.path.ClassName' format, " f"got: {value!r}"
            )

        # Validate the last component looks like a class name (starts with uppercase)
        module_path, class_name = value.rsplit(".", 1)
        if not module_path:
            raise ConfigValidationError(f"{self.field_name} has empty module path: {value!r}")
        if not class_name[0].isupper():
            raise ConfigValidationError(
                f"{self.field_name} class name should start with uppercase: {class_name!r}"
            )

    def import_class(self, class_path: str) -> type:
        """Import the class from the path.

        Args:
            class_path: Dotted path like "module.path.ClassName".

        Returns:
            The imported class.

        Raises:
            ConfigValidationError: If import fails or class is not a subclass
                of base_class (if specified).
        """
        module_path, class_name = class_path.rsplit(".", 1)

        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ConfigValidationError(
                f"Cannot import module '{module_path}' for {self.field_name}: {e}"
            ) from e

        try:
            cls = getattr(module, class_name)
        except AttributeError as e:
            raise ConfigValidationError(
                f"Class '{class_name}' not found in module '{module_path}'"
            ) from e

        if self.base_class is not None:
            if not isinstance(cls, type) or not issubclass(cls, self.base_class):
                raise ConfigValidationError(
                    f"{self.field_name} must be a {self.base_class.__name__} subclass, "
                    f"got: {cls}"
                )

        return cls

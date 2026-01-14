"""
Value acquisition for interactive field configuration.

Fields acquire values in two ways:
- Resolution (resolve()): Automatic - from config files, env vars, defaults
- Acquisition (acquire()): Interactive - from config_stores, user prompts

This module provides:
- AcquisitionContext: Context passed to field.acquire()
- AcquisitionResult: Return value from field.acquire()
- acquire_all_fields(): Generator that acquires values for all interactive fields
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from djb.config.storage.base import Provenance

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase
    from djb.config.field import ConfigFieldABC


# =============================================================================
# Acquisition types
# =============================================================================


@dataclass
class AcquisitionContext:
    """Context passed to field.acquire() during init.

    Provides access to:
    - config: The DjbConfigBase instance (access project_dir, mode, etc.)
    - current_value: The currently resolved value (may be None)
    - source: Where the current value came from (provenance tuple)
    - other_values: Shared dict of configured field values (see note below)

    Note on other_values:
        This is a shared reference to the configured dict, not a snapshot.
        It accumulates values as fields are processed: explicit fields are added
        before acquisition, acquired fields are added after. This means:
        - During acquire(), it contains fields processed so far
        - After acquire_all_fields() completes, it contains all configured values
        - The same dict instance is passed to all fields
    """

    config: "DjbConfigBase"
    current_value: Any
    source: Provenance | None
    other_values: dict[str, Any]

    def is_explicit(self) -> bool:
        """Check if current value was explicitly configured (config file, env var)."""
        if not self.source:
            return False
        # The last element in provenance is the ConfigIO - check its explicit property
        return self.source[-1].explicit

    def is_derived(self) -> bool:
        """Check if current value was derived (pyproject.toml, directory name, etc.)."""
        if not self.source:
            return False
        # Derived is the opposite of explicit
        return not self.source[-1].explicit


@dataclass
class AcquisitionResult:
    """Result of field configuration.

    Attributes:
        value: The configured value.
        should_save: Whether to persist the value to config file.
        source_name: Name of config store used (e.g., "git config"), or None.
        was_prompted: Whether user was prompted for this value.
    """

    value: Any
    should_save: bool = True
    source_name: str | None = None
    was_prompted: bool = False


# =============================================================================
# Field acquisition orchestrator
# =============================================================================


def _is_acquirable(config_field: ConfigFieldABC) -> bool:
    """Check if a field participates in interactive acquisition.

    A field is acquirable if it has an acquire() method and prompt_text.
    """
    return hasattr(config_field, "acquire") and config_field.prompt_text is not None


def acquire_all_fields(
    config: "DjbConfigBase",
) -> Iterator[tuple[str, AcquisitionResult]]:
    """Acquire values for all interactive fields.

    Iterates through fields in declaration order, acquiring values for each
    field that is acquirable (has acquire() method and prompt_text).

    Explicit fields (already configured via config file/env) are skipped.
    Saving is handled internally after each successful acquisition.

    Args:
        config: DjbConfig instance.

    Yields:
        (field_name, AcquisitionResult) for each acquired field.
    """
    configured: dict[str, Any] = {}

    # Iterate fields in declaration order (ConfigBase classes have __fields__)
    for field_name, config_field in type(config).__fields__.items():
        # Skip non-acquirable fields
        if not _is_acquirable(config_field):
            continue

        # Get current value and source
        current_value = getattr(config, field_name)
        source = config.get_source(field_name)

        # Skip explicit fields - they don't need acquisition
        # Check the explicit property on the last element (ConfigIO) of provenance
        if source and source[-1].explicit:
            configured[field_name] = current_value
            continue

        # Build context for this field
        ctx = AcquisitionContext(
            config=config,
            current_value=current_value,
            source=source,
            other_values=configured,
        )

        # Call field's acquire method
        result = config_field.acquire(ctx, config)

        if result is None:
            # Acquisition was cancelled
            continue

        configured[field_name] = result.value

        # Save to config file if needed
        if result.should_save and result.value is not None:
            config_field.set(result.value, config)

        yield field_name, result

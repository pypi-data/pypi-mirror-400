"""
ProjectNameField - Field for the project name with pyproject.toml and directory fallback.

Resolution order:
1. Config layers (cli > env > local > project)
2. pyproject.toml [project.name]
3. Directory name fallback (always succeeds)
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from tomlkit.exceptions import ParseError
from pathlib import Path
from typing import TYPE_CHECKING, Any

from djb.config.storage.utils import load_toml_mapping
from djb.core.logging import get_logger
from djb.config.acquisition import AcquisitionContext, AcquisitionResult
from djb.config.field import ConfigFieldABC, ConfigValidationError
from djb.config.resolution import ResolutionChain, get_standard_stores
from djb.config.prompting import confirm, prompt
from djb.config.storage.io.external import CwdNameConfigIO, PyprojectNameConfigIO

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase

logger = get_logger(__name__)

# DNS label pattern (RFC 1123) for project name validation
DNS_LABEL_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")

# Default project name when all resolution fails
DEFAULT_PROJECT_NAME = "myproject"


def normalize_project_name(name: str | None) -> str | None:
    """Normalize pyproject project names to a DNS-safe label.

    Converts to lowercase and replaces runs of "-", "_", and "." with "-".
    Returns None if the normalized value is not a valid DNS label.
    """
    if not name or not isinstance(name, str):
        return None
    normalized = re.sub(r"[-_.]+", "-", name.strip().lower())
    if not normalized:
        return None
    if DNS_LABEL_PATTERN.match(normalized):
        return normalized
    return None


def get_project_name_from_pyproject(project_root: Path) -> str | None:
    """Extract project name from pyproject.toml if it exists.

    Returns the normalized project name, or None if not found or invalid.
    """
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        return None

    try:
        pyproject = load_toml_mapping(pyproject_path)
    except ParseError:
        return None

    name = pyproject.get("project", {}).get("name")
    if not name:
        return None

    return normalize_project_name(name)


class ProjectNameField(ConfigFieldABC):
    """Field for project_name with pyproject.toml and directory fallback.

    Must be a valid DNS label (RFC 1123): lowercase alphanumeric with hyphens, max 63 chars.
    """

    def __init__(self, **kwargs):
        """Initialize with prompt text and validation hint."""
        super().__init__(
            prompt_text="Enter project name",
            validation_hint="lowercase alphanumeric with hyphens, max 63 chars",
            default=DEFAULT_PROJECT_NAME,
            **kwargs,
        )

    def _build_chain(
        self,
        config: "DjbConfigBase",
        *,
        env: Mapping[str, str] | None = None,
    ) -> ResolutionChain:
        """Build chain with pyproject.toml and directory fallbacks."""
        stores = get_standard_stores(config, env=env) + [
            # Fallbacks - they get project_dir from config
            PyprojectNameConfigIO(config),
            CwdNameConfigIO(config),
        ]
        return ResolutionChain(stores)

    def acquire(
        self, acq_ctx: AcquisitionContext, config: "DjbConfigBase"
    ) -> AcquisitionResult | None:
        """Acquire project_name with provenance-aware confirmation flow."""
        # If derived (pyproject.toml, directory name), ask confirmation
        if acq_ctx.is_derived() and acq_ctx.current_value:
            if confirm(f"Use '{acq_ctx.current_value}'?", default=True):
                logger.done(f"{self.display_name} saved: {acq_ctx.current_value}")
                return AcquisitionResult(
                    value=acq_ctx.current_value,
                    should_save=True,
                    source_name=None,
                    was_prompted=False,
                )
            # User declined - fall through to prompt

        # Prompt user for value
        default = str(acq_ctx.current_value) if acq_ctx.current_value else None
        result = prompt(
            self.prompt_text or "Enter project name",
            default=default,
            normalizer=normalize_project_name,
            validator=self._is_valid,
            validation_hint=self.validation_hint,
        )

        if result.source == "cancelled":
            return None

        return self._prompted_result(result.value)

    def normalize(self, value: str) -> str:
        """Normalize project name to DNS-safe format.

        Converts to lowercase and normalizes separators.

        Raises:
            ConfigValidationError: If value cannot be normalized to a valid DNS label.
        """
        normalized = normalize_project_name(value)
        if normalized is None:
            raise ConfigValidationError(
                f"Cannot normalize project name: {value!r}. "
                "Must be normalizable to a valid DNS label (RFC 1123): "
                "lowercase alphanumeric with hyphens, max 63 chars."
            )
        return normalized

    def validate(self, value: Any) -> None:
        """Validate project_name as DNS label (RFC 1123)."""
        self._require_string(value, allow_none=False)
        if not DNS_LABEL_PATTERN.match(value):
            raise ConfigValidationError(
                f"project_name must be a valid DNS label (RFC 1123): "
                f"lowercase alphanumeric with hyphens, max 63 chars. Got: {value!r}"
            )

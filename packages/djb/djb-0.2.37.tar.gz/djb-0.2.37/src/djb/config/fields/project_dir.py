"""
ProjectDirField - Field for the project root directory.

Also provides project detection utilities:
- find_project_root: Find the djb project root directory
- find_pyproject_root: Find nearest pyproject.toml
- _is_djb_project: Check if a directory is a djb project
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping

from tomlkit.exceptions import ParseError
from pathlib import Path
from typing import TYPE_CHECKING

from djb.cli.utils import has_dependency
from djb.config.field import ConfigFieldABC
from djb.config.storage import DerivedConfigType
from djb.config.storage.base import Provenance
from djb.core.exceptions import ProjectNotFound

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase

# Environment variable name for project directory
PROJECT_DIR_ENV_KEY = "DJB_PROJECT_DIR"


def find_pyproject_root(
    start_path: Path | None = None,
    *,
    predicate: Callable[[Path], bool] | None = None,
) -> Path:
    """Find the nearest directory containing pyproject.toml that matches predicate.

    Walks up from start_path (or cwd) looking for pyproject.toml files.
    If a predicate is provided, the directory must also satisfy the predicate.

    Args:
        start_path: Starting directory for search. Defaults to current working directory.
        predicate: Optional function to test each candidate directory.
                   If provided, directory must satisfy predicate(path) == True.
                   If None, just checks for pyproject.toml existence.

    Returns:
        Path to the directory containing pyproject.toml (that matches predicate).

    Raises:
        FileNotFoundError: If no matching pyproject.toml is found.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    while current != current.parent:
        if (current / "pyproject.toml").exists():
            if predicate is None or predicate(current):
                return current
        current = current.parent

    raise FileNotFoundError(f"Could not find pyproject.toml starting from {start_path}")


def _is_djb_project(path: Path) -> bool:
    """Check if a directory is a djb project (has pyproject.toml with djb dependency).

    Uses packaging.requirements.Requirement for proper PEP 508 parsing.
    This correctly handles:
    - Version specifiers: djb>=0.1.0, djb~=1.0, djb>=0.2,<1.0
    - Extras: djb[dev], djb[dev,test]
    - Environment markers: djb>=0.1; python_version >= "3.10"
    - Name normalization: DJB, Djb (PEP 503 normalized to "djb")

    Excludes packages like "djb-tools" or "djb_something" because
    canonicalize_name() normalizes them to "djb-tools" which != "djb".

    Note: Only checks regular dependencies (not optional-dependencies).
    Returns False for invalid TOML (safe default for project detection).
    """
    pyproject_path = path / "pyproject.toml"
    try:
        return has_dependency("djb", pyproject_path, include_optional=False)
    except ParseError:
        return False


def find_project_root(
    project_root: Path | None = None,
    start_path: Path | None = None,
    *,
    fallback_to_cwd: bool = False,
) -> tuple[Path, str]:
    """Find the project root directory.

    Called during bootstrap before config files are loaded.
    All project_dir discovery logic lives here.

    Priority:
    1. Explicit project_root (trusted when provided) -> "cli"
    2. DJB_PROJECT_DIR environment variable (trusted when set) -> "env"
    3. Search for djb project in parent directories -> "pyproject"
    4. Fall back to cwd (if fallback_to_cwd=True) -> "cwd"

    Args:
        project_root: Explicit project root to use. If provided, returned directly.
        start_path: Starting directory for search. Defaults to cwd.
        fallback_to_cwd: If True, return cwd when no project is found.

    Returns:
        Tuple of (path, source) where source is a string indicating how it was found.

    Raises:
        ProjectNotFound: If no djb project is found and fallback_to_cwd is False.
    """
    # 1. Explicit project_root takes precedence (CLI override)
    if project_root is not None:
        return (project_root, "cli")

    # 2. Check environment variable - trust it when set
    env_project_dir = os.getenv(PROJECT_DIR_ENV_KEY)
    if env_project_dir:
        return (Path(env_project_dir), "env")

    # 3. Search for djb project in parent directories
    try:
        found_path = find_pyproject_root(start_path, predicate=_is_djb_project)
        return (found_path, "pyproject")
    except FileNotFoundError:
        if fallback_to_cwd:
            return (Path.cwd(), "cwd")
        raise ProjectNotFound()


class ProjectDirField(ConfigFieldABC):
    """Field for project_dir - the root directory of the project.

    This is a DERIVED field - it's resolved at runtime and never saved to config files.

    Resolution order:
    1. CLI overrides (project_dir in overrides dict)
    2. DJB_PROJECT_DIR environment variable
    3. Search for djb project in parent directories
    4. Fall back to cwd
    """

    def __init__(self) -> None:
        super().__init__(config_storage=DerivedConfigType)

    def resolve(
        self,
        config: "DjbConfigBase",
        *,
        key_prefix: str | None = None,  # noqa: ARG002 - unused, bootstrap field
        env: Mapping[str, str] | None = None,  # noqa: ARG002 - unused
    ) -> tuple[Path, Provenance | None]:
        """Resolve project_dir using special bootstrap logic.

        Uses find_project_root() which checks override_config, env, pyproject discovery, and cwd.
        This runs before other fields since project_dir has no dependencies.

        Args:
            config: DjbConfigBase instance (project_dir will be None at this point).
            key_prefix: Ignored for bootstrap fields (always resolved at root level).
            env: Environment variables mapping (unused - find_project_root uses os.environ).

        Returns:
            Tuple of (path, provenance). Provenance is None for DERIVED fields.
        """
        # Check _overrides_dict first for explicit project_dir override
        override_project_dir = None
        overrides_dict = getattr(config, "_overrides_dict", None)
        if overrides_dict and "project_dir" in overrides_dict:
            raw_value = overrides_dict["project_dir"]
            # Convert to Path if stored as string (from _convert_value)
            override_project_dir = Path(raw_value) if raw_value else None

        # Use find_project_root for discovery
        path, _ = find_project_root(
            project_root=override_project_dir,
            fallback_to_cwd=True,
        )

        # DERIVED fields don't track provenance
        self._provenance = None
        return (path, None)

    def normalize(self, value: str | Path) -> Path:
        """Normalize project_dir to Path."""
        return Path(value)

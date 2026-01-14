"""Constants and base exception for buildpacks module."""

from __future__ import annotations

from djb.core.exceptions import DjbError
from djb.templates import BUILDPACKS_DOCKERFILES_DIR as DOCKERFILES_DIR

__all__ = ["DOCKERFILES_DIR", "BuildpackError"]


class BuildpackError(DjbError):
    """Exception raised for buildpack-related errors."""

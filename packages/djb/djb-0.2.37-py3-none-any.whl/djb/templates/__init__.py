"""
djb.templates - Template files for djb project scaffolding.

This module provides access to template files used by djb commands
for generating project files like Dockerfiles, K8s manifests, etc.

Exports:
    DJB_TEMPLATES_DIR - Path to the templates directory
    BUILDPACKS_DOCKERFILES_DIR - Path to buildpack Dockerfiles
"""

from __future__ import annotations

from pathlib import Path

# Path to the templates directory
DJB_TEMPLATES_DIR = Path(__file__).parent

# Path to buildpack Dockerfiles (used by k8s/generator.py and buildpacks modules)
# Defined here to avoid circular imports between k8s.generator and buildpacks
BUILDPACKS_DOCKERFILES_DIR = Path(__file__).parent.parent / "buildpacks" / "dockerfiles"

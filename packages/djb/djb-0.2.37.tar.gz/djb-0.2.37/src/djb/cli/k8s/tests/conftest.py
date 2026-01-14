"""Shared fixtures for deploy_k8s unit tests.

Provides common fixtures for testing K8s deployment commands.
Unit tests in this directory test help text and argument validation only.
E2E tests that need real I/O (make_djb_config, project_dir) are in e2e/.
"""

from __future__ import annotations

from djb.cli.tests import cli_runner

__all__ = ["cli_runner"]

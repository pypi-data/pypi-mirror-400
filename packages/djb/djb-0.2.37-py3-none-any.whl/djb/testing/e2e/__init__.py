"""E2E testing fixtures for djb.

This module provides fixtures for E2E tests that need real file I/O.
Import these in your E2E conftest.py to override unit test defaults.

Usage in E2E conftest.py:
    from djb.testing.e2e import (
        project_dir,
        make_pyproject,
        make_cli_ctx,
        cli_runner,
        make_cmd_runner,
        make_age_key,
        alice_key,
        bob_key,
        make_djb_config,
    )
"""

from djb.testing.e2e.fixtures import (
    EDITABLE_PYPROJECT_TEMPLATE,
    AgePathAndPublicKey,
    alice_key,
    bob_key,
    isolate_git_config,
    make_age_key,
    make_cli_ctx,
    cli_runner,
    make_cmd_runner,
    make_djb_config,
    make_editable_pyproject,
    make_pyproject,
    project_dir,
)

__all__ = [
    # Project directory
    "project_dir",
    # Pyproject factory
    "make_pyproject",
    # CLI context and runner
    "make_cli_ctx",
    "make_cmd_runner",
    "cli_runner",
    # Age keys
    "AgePathAndPublicKey",
    "make_age_key",
    "alice_key",
    "bob_key",
    # Config
    "make_djb_config",
    # Editable pyproject
    "EDITABLE_PYPROJECT_TEMPLATE",
    "make_editable_pyproject",
    # Git isolation
    "isolate_git_config",
]

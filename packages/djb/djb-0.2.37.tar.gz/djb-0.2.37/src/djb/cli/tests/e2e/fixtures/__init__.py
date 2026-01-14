"""
E2E test fixtures for djb CLI.

This module provides fixtures organized by concern:
- Prerequisites: check_age_installed, check_sops_installed, check_postgres_available,
                 require_gpg, require_age, require_sops, require_postgres
- CLI: cli_runner, configure_logging
- Secrets: gpg_home, secrets_dir, setup_sops_config, TEST_PASSPHRASE, TEST_SECRET_VALUE
- Project: age_key_dir, project_dir, make_pyproject_dir_with_git, make_pyproject_dir_with_git_with_secrets
- Database: make_pg_test_database
- Mocks: mock_heroku_cli, mock_pypi_publish
- Git: make_project_with_git_repo, make_project_with_git_repo_with_commits,
        make_pyproject_toml_with_git_repo, make_project_with_editable_djb_repo

Note: Tests should pass --project-dir to CLI commands to specify the project directory.
"""

from __future__ import annotations

from djb.cli.tests.e2e.fixtures.prerequisites import (
    check_age_installed,
    check_postgres_available,
    check_sops_installed,
    require_age,
    require_gpg,
    require_postgres,
    require_sops,
)
from djb.cli.tests.e2e.fixtures.cli import (
    configure_logging,
    cli_runner,
)
from djb.cli.tests.e2e.fixtures.secrets import (
    gpg_home,
    gpg_test_profile,
    secrets_dir,
    setup_sops_config,
    TEST_GPG_EMAIL,
    TEST_GPG_NAME,
    TEST_PASSPHRASE,
    TEST_SECRET_VALUE,
)
from djb.cli.tests.e2e.fixtures.project import (
    age_key_dir,
    deploy_project,
    deps_project,
    django_project,
    djb_package_dir,
    djb_project_with_src,
    health_project,
    host_project,
    k8s_project,
    make_pyproject,
    project_with_djb,
    make_config_file,
    project_dir,
    project_with_editable_djb,
    make_pyproject_dir_with_git,
    make_pyproject_dir_with_git_with_secrets,
)
from djb.testing import DJB_PYPROJECT_CONTENT
from djb.testing.e2e import (
    EDITABLE_PYPROJECT_TEMPLATE,
    make_cmd_runner,
    make_editable_pyproject,
)
from djb.cli.tests.e2e.fixtures.database import (
    make_pg_test_database,
)
from djb.cli.tests.e2e.fixtures.mocks import (
    mock_cloudflare_provider,
    mock_heroku_cli,
    mock_hetzner_provider,
    mock_pypi_publish,
)
from djb.cli.tests.e2e.fixtures.git import (
    make_project_with_editable_djb_repo,
    make_project_with_git_repo,
    make_project_with_git_repo_with_commits,
    make_pyproject_toml_with_git_repo,
)

__all__ = [
    # Prerequisites
    "check_age_installed",
    "check_sops_installed",
    "check_postgres_available",
    "require_gpg",
    "require_age",
    "require_sops",
    "require_postgres",
    # CLI
    "configure_logging",
    "cli_runner",
    # Environment / Secrets
    "gpg_home",
    "gpg_test_profile",
    "TEST_GPG_EMAIL",
    "TEST_GPG_NAME",
    "TEST_PASSPHRASE",
    "TEST_SECRET_VALUE",
    # Project
    "age_key_dir",
    "deploy_project",
    "deps_project",
    "django_project",
    "djb_package_dir",
    "djb_project_with_src",
    "health_project",
    "host_project",
    "k8s_project",
    "make_cmd_runner",
    "make_pyproject",
    "project_with_djb",
    "DJB_PYPROJECT_CONTENT",
    "EDITABLE_PYPROJECT_TEMPLATE",
    "make_config_file",
    "make_editable_pyproject",
    "project_dir",
    "project_with_editable_djb",
    "make_pyproject_dir_with_git",
    "make_pyproject_dir_with_git_with_secrets",
    "secrets_dir",
    "setup_sops_config",
    # Database
    "make_pg_test_database",
    # Mocks
    "mock_cloudflare_provider",
    "mock_heroku_cli",
    "mock_hetzner_provider",
    "mock_pypi_publish",
    # Git
    "make_project_with_editable_djb_repo",
    "make_project_with_git_repo",
    "make_project_with_git_repo_with_commits",
    "make_pyproject_toml_with_git_repo",
]

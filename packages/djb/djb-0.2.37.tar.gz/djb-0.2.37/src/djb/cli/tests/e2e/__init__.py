"""
djb.tests.e2e - E2E tests and utilities for djb CLI.

Tests exercise the djb CLI against real external tools (GPG, age, SOPS,
PostgreSQL) while mocking cloud services (Heroku, PyPI).

CLI Invocation Pattern
======================

Tests should pass --project-dir explicitly to CLI commands::

    def test_my_command(cli_runner, make_pyproject_dir_with_git):
        result = cli_runner.invoke(djb_cli, ["--project-dir", str(make_pyproject_dir_with_git), "my-command"])
        assert result.exit_code == 0

Project fixtures create git repos with user.name/user.email configured.
GitConfigSource reads from the repo's local config.

Fixtures (organized under fixtures/ subdirectory, auto-discovered by pytest from conftest.py):

    Prerequisite checks (fixtures/prerequisites.py):
        require_gpg, require_age, require_sops, require_postgres

    CLI runners (fixtures/cli.py):
        cli_runner, configure_logging

    Environment isolation (fixtures/environment.py):
        gpg_home, TEST_PASSPHRASE, TEST_SECRET_VALUE

    Project setup (fixtures/project.py):
        project_dir - Empty project directory (simplest case)
        make_mode - Default mode for tests (override to test mode behavior)
        make_config_file - Factory for creating .djb/local.toml or .djb/project.toml
        make_pyproject_dir_with_git - Project with pyproject.toml and git
        make_pyproject_dir_with_git_with_secrets - Project with secrets configured
        secrets_dir, setup_sops_config

    Age keys (from djb.testing.fixtures):
        make_age_key (factory), alice_key, bob_key

    PostgreSQL (fixtures/database.py):
        make_pg_test_database

    Git repos (fixtures/git.py):
        project_with_git_repo, make_project_with_git_repo_with_commits

    Cloud mocks (fixtures/mocks.py):
        mock_heroku_cli, mock_pypi_publish

Utilities:
    GPG:
        gpg_encrypt, gpg_decrypt

    Age/SOPS:
        create_sops_config, sops_encrypt, sops_decrypt, sops_decrypt_in_place
        age_encrypt, age_decrypt

    Project setup (composable helpers):
        add_initial_commit - Stage files and create commit
        create_pyproject_toml - Create pyproject.toml with djb config
        add_django_settings - Create minimal Django settings structure
        add_django_settings_from_startproject - Create realistic Django settings via startproject
        add_frontend_package - Create frontend dir with package.json
        add_python_package - Create Python package with __init__.py

    Assertions:
        assert_gpg_encrypted, assert_sops_encrypted
        assert_not_contains_secrets, assert_contains

    Context managers:
        temporarily_decrypted_gpg, temporarily_decrypted_sops
"""

from __future__ import annotations

from djb.cli.tests.e2e.fixtures.secrets import TEST_PASSPHRASE, TEST_SECRET_VALUE
from djb.cli.tests.e2e.fixtures.project import (
    DJB_PYPROJECT_CONTENT,
    ProjectWithSecrets,
    make_config_file,
    make_editable_pyproject,
)
from djb.cli.tests.e2e.utils import (
    add_django_settings_from_startproject,
    add_frontend_package,
    add_initial_commit,
    add_python_package,
    age_decrypt,
    age_encrypt,
    assert_gpg_encrypted,
    assert_not_contains_secrets,
    assert_sops_encrypted,
    create_pyproject_toml,
    create_sops_config,
    gpg_decrypt,
    gpg_decrypt_with_profile,
    gpg_encrypt,
    gpg_encrypt_with_profile,
    sops_decrypt,
    sops_encrypt,
)

__all__ = [
    "DJB_PYPROJECT_CONTENT",
    "ProjectWithSecrets",
    "TEST_PASSPHRASE",
    "TEST_SECRET_VALUE",
    "make_config_file",
    "make_editable_pyproject",
    "add_django_settings_from_startproject",
    "add_frontend_package",
    "add_initial_commit",
    "add_python_package",
    "age_decrypt",
    "age_encrypt",
    "assert_gpg_encrypted",
    "assert_not_contains_secrets",
    "assert_sops_encrypted",
    "create_pyproject_toml",
    "create_sops_config",
    "gpg_decrypt",
    "gpg_decrypt_with_profile",
    "gpg_encrypt",
    "gpg_encrypt_with_profile",
    "sops_decrypt",
    "sops_encrypt",
]

"""Reusable pytest plugin for e2e test support.

This module provides the e2e marker and options to control whether E2E tests run.
E2E tests run by default; use --no-e2e to skip them.

The marker name is intentionally distinct to avoid conflicts with test parameters
that might contain "e2e" (e.g., testing an "e2e" subcommand).

Usage in conftest.py:
    from djb.testing.pytest_e2e import (
        pytest_addoption,
        pytest_configure,
        pytest_collection_modifyitems,
    )

Usage in tests:
    @pytest.mark.e2e_marker
    def test_something():
        ...

    # Or at module level:
    pytestmark = pytest.mark.e2e_marker
"""

from __future__ import annotations

import pytest

# Marker name - distinct to avoid conflicts with test names/parameters containing "e2e"
E2E_MARKER = "e2e_marker"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add e2e test options.

    Safely adds options only if they haven't been registered already.
    This prevents conflicts when the plugin is loaded multiple times
    (e.g., via conftest.py import and pytest plugin discovery).
    """
    group = parser.getgroup("e2e")

    # Check if options are already registered to avoid conflicts
    existing_options = {opt.names()[0] for opt in parser._anonymous.options}
    for grp in parser._groups:
        existing_options.update(opt.names()[0] for opt in grp.options)

    if "--no-e2e" not in existing_options:
        group.addoption(
            "--no-e2e",
            action="store_true",
            help="Exclude E2E tests (included by default).",
        )
    if "--only-e2e" not in existing_options:
        group.addoption(
            "--only-e2e",
            action="store_true",
            help="Run only E2E tests (skips everything else).",
        )


def pytest_configure(config: pytest.Config) -> None:
    """Register e2e marker."""
    config.addinivalue_line(
        "markers",
        f"{E2E_MARKER}: end-to-end tests requiring external tools (GPG, age, SOPS)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip e2e tests if --no-e2e is provided, or run only e2e tests if --only-e2e is provided."""
    try:
        no_e2e = config.getoption("--no-e2e")
        only_e2e = config.getoption("--only-e2e")
    except ValueError:
        return

    if only_e2e:
        skip_non_e2e = pytest.mark.skip(reason="skipped because --only-e2e was provided")
        for item in items:
            if E2E_MARKER not in item.keywords:
                item.add_marker(skip_non_e2e)
        return

    if no_e2e:
        skip_e2e = pytest.mark.skip(reason="skipped because --no-e2e was provided")
        for item in items:
            if E2E_MARKER in item.keywords:
                item.add_marker(skip_e2e)

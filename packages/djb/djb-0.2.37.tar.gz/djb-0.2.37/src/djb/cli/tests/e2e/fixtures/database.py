"""PostgreSQL fixtures for E2E tests.

These fixtures create and manage isolated test databases.
"""

from __future__ import annotations

import subprocess  # noqa: TID251 - invoking createdb/dropdb directly
import uuid
from collections.abc import Generator

import pytest

# Template database with PostGIS extension (created by djb db init)
TEMPLATE_DB_NAME = "template_postgis"


@pytest.fixture
def make_pg_test_database(require_postgres) -> Generator[str, None, None]:
    """Create an isolated PostgreSQL database for testing.

    Creates a uniquely named database from the template_postgis template
    (which has PostGIS pre-installed), yields the name, then drops it.

    Falls back to a plain database if template doesn't exist.
    """
    db_name = f"djb_e2e_test_{uuid.uuid4().hex[:8]}"

    # Try to create database from template (inherits PostGIS)
    result = subprocess.run(
        ["createdb", "-T", TEMPLATE_DB_NAME, db_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Fall back to plain database if template doesn't exist
        result = subprocess.run(
            ["createdb", db_name],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            pytest.skip(f"Could not create test database: {result.stderr}")

    try:
        yield db_name
    finally:
        # Drop the database
        subprocess.run(
            ["dropdb", "--if-exists", db_name],
            capture_output=True,
            text=True,
        )

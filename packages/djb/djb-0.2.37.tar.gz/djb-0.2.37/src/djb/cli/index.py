"""
djb index CLI - Generate documentation indexes.

Provides subcommands for generating various documentation indexes,
such as test and fixture package indexes.
"""

from __future__ import annotations

import click

from djb.cli.index_fixtures import fixtures_cmd
from djb.cli.indexer import tests_cmd


@click.group()
def index():
    """Generate documentation indexes.

    \b
    Subcommands:
        tests      Generate test package indexes
        fixtures   Generate fixture package indexes
    """
    pass


index.add_command(tests_cmd, name="tests")
index.add_command(fixtures_cmd, name="fixtures")

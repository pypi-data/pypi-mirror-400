"""Lazy loading utilities for Click CLI commands.

Provides a LazyGroup class that defers importing subcommands until they're
actually invoked. This significantly speeds up CLI startup by avoiding
importing heavy dependencies (django, yaml, jinja2, etc.) on every command.

Usage:
    from djb.cli.lazy import LazyGroup

    @click.group(cls=LazyGroup)
    def cli():
        pass

    cli.add_lazy_command("djb.cli.secrets:secrets", "secrets")
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from collections.abc import Sequence


class LazyGroup(click.Group):
    """Click group that lazily imports subcommands.

    Instead of importing commands at module load time, commands are
    imported only when invoked. This significantly speeds up CLI startup
    by deferring heavy dependency imports until needed.

    Lazy commands are specified as import paths in the format
    "module.path:attribute_name". The module is only imported when
    the command is actually invoked.
    """

    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, click.Command] | Sequence[click.Command] | None = None,
        lazy_commands: dict[str, str] | None = None,
        **attrs,
    ) -> None:
        """Initialize LazyGroup.

        Args:
            name: Group name.
            commands: Dict or sequence of eager (already imported) commands.
            lazy_commands: Dict mapping command names to import paths.
                           Format: {"cmd_name": "module.path:attribute"}
            **attrs: Additional attributes passed to click.Group.
        """
        super().__init__(name=name, commands=commands, **attrs)
        self._lazy_commands: dict[str, str] = lazy_commands or {}

    def add_lazy_command(self, import_path: str, name: str | None = None) -> None:
        """Register a command to be lazily imported.

        Args:
            import_path: Module path in format "module.path:command_name"
            name: Command name to register. If not provided, uses the
                  attribute name from import_path.

        Example:
            group.add_lazy_command("djb.cli.secrets:secrets")
            # Registers "secrets" command, imports djb.cli.secrets only when invoked

            group.add_lazy_command("djb.cli.superuser:sync_superuser", "sync-superuser")
            # Registers as "sync-superuser", imports djb.cli.superuser when invoked
        """
        if name is None:
            name = import_path.split(":")[-1]
        self._lazy_commands[name] = import_path

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List all commands including lazy ones."""
        eager = super().list_commands(ctx)
        lazy = list(self._lazy_commands.keys())
        return sorted(set(eager + lazy))

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Get command, importing lazily if needed."""
        # Check if already loaded (eager command)
        if cmd := super().get_command(ctx, cmd_name):
            return cmd

        # Try lazy import
        if cmd_name in self._lazy_commands:
            import_path = self._lazy_commands[cmd_name]
            module_path, attr_name = import_path.rsplit(":", 1)
            module = importlib.import_module(module_path)
            cmd = getattr(module, attr_name)
            # Cache it for subsequent calls
            self.add_command(cmd, cmd_name)
            return cmd

        return None

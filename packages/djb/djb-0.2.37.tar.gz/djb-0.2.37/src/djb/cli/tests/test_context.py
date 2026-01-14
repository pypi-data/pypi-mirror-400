"""Tests for djb.cli.context module."""

from __future__ import annotations

from unittest.mock import MagicMock

import click
import pytest
from click.testing import CliRunner

from djb.cli.context import (
    CliContext,
    CliHealthContext,
    CliHerokuContext,
    djb_pass_context,
)


class TestCliContext:
    """Tests for the CliContext dataclass."""

    def test_default_values(self):
        """CliContext has correct default values."""
        ctx = CliContext()
        assert ctx.verbose is False
        assert ctx.quiet is False
        assert ctx.config is None
        assert ctx.scope_frontend is False
        assert ctx.scope_backend is False

    def test_custom_values(self):
        """CliContext can be initialized with custom values."""
        config = MagicMock()
        ctx = CliContext(
            verbose=True,
            quiet=True,
            config=config,
            scope_frontend=True,
            scope_backend=True,
        )
        assert ctx.verbose is True
        assert ctx.quiet is True
        assert ctx.config is config
        assert ctx.scope_frontend is True
        assert ctx.scope_backend is True


class TestContextInheritance:
    """Tests for context class inheritance."""

    @pytest.mark.parametrize(
        "context_class",
        [CliHealthContext, CliHerokuContext],
        ids=["health", "heroku"],
    )
    def test_inherits_from_cli_context(self, context_class):
        """Context subclasses inherit from CliContext."""
        assert issubclass(context_class, CliContext)


class TestCliHealthContext:
    """Tests for the CliHealthContext dataclass."""

    def test_default_values(self):
        """CliHealthContext has correct default values."""
        ctx = CliHealthContext()
        # Inherited fields
        assert ctx.verbose is False
        assert ctx.quiet is False
        assert ctx.config is None
        # Specialized fields
        assert ctx.fix is False
        assert ctx.cov is False

    def test_specialized_values(self):
        """CliHealthContext can set specialized fields."""
        ctx = CliHealthContext(fix=True, cov=True)
        assert ctx.fix is True
        assert ctx.cov is True

    def test_combined_inheritance_and_specialized(self):
        """CliHealthContext supports both inherited and specialized values."""
        config = MagicMock()
        ctx = CliHealthContext(
            verbose=True,
            config=config,
            fix=True,
            cov=True,
        )
        assert ctx.verbose is True
        assert ctx.config is config
        assert ctx.fix is True
        assert ctx.cov is True


class TestCliHerokuContext:
    """Tests for the CliHerokuContext dataclass."""

    def test_default_values(self):
        """CliHerokuContext inherits defaults and requires app."""
        ctx = CliHerokuContext(app="test-app")
        # Inherited fields have defaults
        assert ctx.verbose is False
        assert ctx.quiet is False
        assert ctx.config is None
        # App is required (kw_only=True)
        assert ctx.app == "test-app"

    def test_specialized_values(self):
        """CliHerokuContext can set specialized fields."""
        ctx = CliHerokuContext(app="my-app")
        assert ctx.app == "my-app"

    def test_combined_inheritance_and_specialized(self):
        """CliHerokuContext supports both inherited and specialized values."""
        config = MagicMock()
        ctx = CliHerokuContext(
            verbose=True,
            config=config,
            app="production-app",
        )
        assert ctx.verbose is True
        assert ctx.config is config
        assert ctx.app == "production-app"


class TestPassContext:
    """Tests for the pass_context decorator."""

    def test_pass_context_without_parentheses(self):
        """@pass_context without parentheses works."""
        cli_ctx = CliContext(verbose=True)

        @djb_pass_context
        def my_command(ctx: CliContext):
            return ctx.verbose

        @click.command()
        @click.pass_context
        def wrapper(ctx):
            ctx.obj = cli_ctx
            return my_command()

        runner = CliRunner()
        result = runner.invoke(wrapper)
        assert result.exit_code == 0

    def test_pass_context_with_parentheses(self):
        """@pass_context() with parentheses works."""
        cli_ctx = CliContext(verbose=True)

        @djb_pass_context()
        def my_command(ctx: CliContext):
            return ctx.verbose

        @click.command()
        @click.pass_context
        def wrapper(ctx):
            ctx.obj = cli_ctx
            return my_command()

        runner = CliRunner()
        result = runner.invoke(wrapper)
        assert result.exit_code == 0

    def test_pass_context_with_health_context(self):
        """@pass_context(CliHealthContext) works."""
        health_ctx = CliHealthContext(fix=True)

        @djb_pass_context(CliHealthContext)
        def lint_command(ctx: CliHealthContext):
            return ctx.fix

        @click.command()
        @click.pass_context
        def wrapper(ctx):
            ctx.obj = health_ctx
            return lint_command()

        runner = CliRunner()
        result = runner.invoke(wrapper)
        assert result.exit_code == 0

    def test_pass_context_with_heroku_context(self):
        """@pass_context(CliHerokuContext) works."""
        heroku_ctx = CliHerokuContext(app="test-app")

        @djb_pass_context(CliHerokuContext)
        def deploy_command(ctx: CliHerokuContext):
            return ctx.app

        @click.command()
        @click.pass_context
        def wrapper(ctx):
            ctx.obj = heroku_ctx
            return deploy_command()

        runner = CliRunner()
        result = runner.invoke(wrapper)
        assert result.exit_code == 0

    def test_pass_context_wrong_type_raises(self):
        """@pass_context raises when context type mismatches."""
        cli_ctx = CliContext()  # Not CliHealthContext

        @djb_pass_context(CliHealthContext)
        def lint_command(ctx: CliHealthContext):
            return ctx.fix

        @click.command()
        @click.pass_context
        def wrapper(ctx):
            ctx.obj = cli_ctx
            return lint_command()

        runner = CliRunner()
        result = runner.invoke(wrapper)
        # Should fail due to assertion error
        assert result.exit_code != 0

    def test_pass_context_preserves_function_name(self):
        """@pass_context preserves the wrapped function's name."""

        @djb_pass_context
        def my_special_command(ctx: CliContext):
            pass

        assert my_special_command.__name__ == "my_special_command"

    def test_pass_context_passes_additional_args(self):
        """@pass_context passes additional arguments to the function."""
        cli_ctx = CliContext()
        received_args = []

        @djb_pass_context
        def my_command(ctx: CliContext, name: str, count: int):
            received_args.append((name, count))
            return f"{name}: {count}"

        @click.command()
        @click.pass_context
        def wrapper(ctx):
            ctx.obj = cli_ctx
            return my_command("test", count=42)

        runner = CliRunner()
        result = runner.invoke(wrapper)
        assert result.exit_code == 0
        assert received_args == [("test", 42)]

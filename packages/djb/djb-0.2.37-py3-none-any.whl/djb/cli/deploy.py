"""
djb deploy CLI - Deployment command group.

This module provides the top-level `djb deploy` command that delegates to
platform-specific subcommands:

- `djb deploy heroku` - Deploy to Heroku
- `djb deploy k8s` - Deploy to Kubernetes

Each platform has its own subcommand group with platform-specific options
and workflows. See the respective modules for details:

- djb.cli.heroku - Heroku deployment commands
- djb.cli.k8s - Kubernetes deployment commands
"""

from __future__ import annotations

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.deploy_seed import deploy_seed
from djb.cli.deploy_superuser import deploy_superuser
from djb.cli.heroku import heroku
from djb.cli.k8s import k8s
from djb.types import Platform


@click.group(invoke_without_command=True)
@djb_pass_context
@click.pass_context
def deploy(ctx: click.Context, cli_ctx: CliContext) -> None:
    """Deploy application to configured platform.

    Routes to heroku or k8s based on --platform setting.

    \b
    Heroku deployment:
      djb deploy heroku                     # Deploy to Heroku
      djb deploy heroku setup               # Configure Heroku app
      djb deploy heroku revert              # Revert to previous deployment

    \b
    Kubernetes deployment:
      djb deploy k8s                        # Deploy to K8s
      djb deploy k8s terraform              # Provision infrastructure
      djb deploy k8s local dev              # Start local dev loop
    """
    if ctx.invoked_subcommand is not None:
        # Subcommand specified (e.g., djb deploy heroku) - let it run
        return

    # Auto-route based on platform
    if cli_ctx.config is None:
        raise click.ClickException("No configuration found")

    config = cli_ctx.config
    if config.platform == Platform.HEROKU:
        ctx.invoke(heroku)
    else:
        ctx.invoke(k8s)


# Register platform-specific subcommands
deploy.add_command(heroku)
deploy.add_command(k8s)

# Register cross-platform deployment commands
deploy.add_command(deploy_superuser)
deploy.add_command(deploy_seed)

"""
djb config CLI - Manage djb configuration.

Provides a discoverable, documented interface for viewing and modifying
djb settings. Each config option is a subcommand with its own documentation.
"""

from __future__ import annotations

import json
from typing import Any

import click

from djb.cli.context import CliConfigContext, CliContext, djb_pass_context
from djb.config import (
    ConfigValidationError,
    DjbConfig,
    get_field_descriptor,
    navigate_config_path,
)
from djb.config.storage import get_config_dir
from djb.config.storage.utils import (
    dump_toml,
    load_toml_mapping,
    save_toml_mapping,
    sort_toml_document,
)
from djb.core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Helpers
# =============================================================================


def _format_json_with_provenance(config: DjbConfig) -> str:
    """Format config as JSON with provenance comments on separate lines.

    Produces output like:
        {
        // project_name: PROJECT > project.toml
          "project_name": "beachresort25",
        // mode: LOCAL > local.toml
          "mode": "production"
        }
    """
    config_dict = config.to_dict()
    output_lines = ["{"]

    items = list(config_dict.items())
    for i, (key, value) in enumerate(items):
        # Get provenance
        source = config.get_source(key)
        if source is not None:
            provenance = " > ".join(s.name for s in source)
        else:
            provenance = "(not set)"

        # Provenance comment line (no indentation)
        output_lines.append(f"// {key}: {provenance}")

        # Format value with indentation for nested objects
        json_value = json.dumps(value, indent=2)
        comma = "," if i < len(items) - 1 else ""

        if "\n" in json_value:
            # Multi-line value - indent all lines
            value_lines = json_value.split("\n")
            output_lines.append(f'  "{key}": {value_lines[0]}')
            for line in value_lines[1:-1]:
                output_lines.append(f"  {line}")
            output_lines.append(f"  {value_lines[-1]}{comma}")
        else:
            output_lines.append(f'  "{key}": {json_value}{comma}')

    output_lines.append("}")
    return "\n".join(output_lines)


def _get_write_destination_name(display_key: str, config: DjbConfig) -> str:
    """Get the file name where a value will be written.

    Uses provenance if available, otherwise falls back to field's default storage.
    Resolves through get_io() to get the actual file name (e.g., project.toml).
    """
    field_meta = get_field_descriptor(display_key)
    provenance = field_meta._provenance

    if provenance and provenance[0].writable:
        # provenance[-1] is already an instance
        store = provenance[-1]
    else:
        # config_storage is a class - instantiate it with config
        store = field_meta.config_storage(config)

    # Get the actual ConfigIO to resolve the file name
    return store.get_io().name


def _config_get_set_delete(
    config_ctx: CliConfigContext,
    key: str,
    value: Any | None,
    delete: bool,
) -> None:
    """Handle get/set/delete for a config field.

    Delegates to DjbConfig.set() and DjbConfig.delete() for provenance-based
    routing. Supports --project/--local flag overrides via target_store.

    Args:
        config_ctx: CLI config context with target file flags.
        key: Field path to get/set/delete (e.g., "project_name" or "hetzner.server_name").
        value: New value to set, or None to show current.
        delete: If True, remove the field from config.
    """
    # Validate key exists before proceeding
    try:
        get_field_descriptor(key)
    except AttributeError as e:
        raise click.ClickException(str(e))

    config = config_ctx.config
    mode = str(config.mode)
    target_store = config_ctx.target_store  # From --project/--local flags

    # Get current value - navigate to parent section if nested
    if "." in key:
        section_path, field_name = key.rsplit(".", 1)
        target_config = navigate_config_path(config, section_path)
        if target_config is None:
            raise click.ClickException(f"Unknown config section: {section_path}")
    else:
        target_config = config
        field_name = key
    current_value = getattr(target_config, field_name, None)

    # Show current value (GET operation)
    if value is None and not delete:
        if current_value is not None:
            logger.info(f"{key}: {current_value}")
        else:
            logger.info(f"{key}: (not set)")
        return

    # Format section info for logging
    section_info = f" in [{mode}]" if mode != "production" else ""

    # Instantiate target_store class with config if specified
    target_store_instance = None
    if target_store is not None:
        target_store_instance = target_store(config)
        file_name = target_store_instance.get_io().name
    else:
        file_name = _get_write_destination_name(key, config)

    if delete:
        config.delete(key, target_store=target_store_instance)
        logger.done(f"{key} removed from {file_name}{section_info}")
    else:
        try:
            normalized_value = config.set(key, value, target_store=target_store_instance)
        except ConfigValidationError as e:
            raise click.ClickException(str(e))

        logger.done(f"{key} set to: {normalized_value} in {file_name}{section_info}")


@click.group("config", invoke_without_command=True)
@click.option(
    "--project",
    "target_project",
    is_flag=True,
    help="Write to project.toml (overrides provenance-based target).",
)
@click.option(
    "--local",
    "target_local",
    is_flag=True,
    help="Write to local.toml (overrides provenance-based target).",
)
@djb_pass_context
@click.pass_context
def config_group(
    ctx: click.Context,
    cli_ctx: CliContext,
    target_project: bool,
    target_local: bool,
) -> None:
    """Manage djb configuration.

    View and modify djb settings. Each subcommand manages a specific
    configuration option with its own documentation.

    Environment variables (DJB_*) are documented in each subcommand's help.

    \b
    Write target flags (--project, --local):
      By default, writes go to the file where the value currently resides.
      For core.toml defaults being overridden for the first time, use
      --project or --local to specify where to write.

    \b
    Examples:
      djb config show                             # Show all config as JSON
      djb config show --with-provenance           # Show config with sources
      djb config seed_command                     # Show current value
      djb config seed_command myapp.cli:seed      # Set seed command
      djb config hetzner.default_server_type cx32 --project  # Override core default
    """
    # Set up CliConfigContext for subcommands
    config_ctx = CliConfigContext()
    config_ctx.__dict__.update(cli_ctx.__dict__)
    config_ctx.target_project = target_project
    config_ctx.target_local = target_local
    ctx.obj = config_ctx

    if ctx.invoked_subcommand is None:
        # No subcommand, show help
        logger.info(ctx.get_help())


@config_group.command("show")
@click.option(
    "--with-provenance",
    "with_provenance",
    is_flag=True,
    help="Include provenance comments showing where each value came from.",
)
@djb_pass_context(CliConfigContext)
def config_show(config_ctx: CliConfigContext, with_provenance: bool) -> None:
    """Show all config as JSON.

    Displays the merged configuration from all sources (environment, local,
    project, and core defaults).

    \b
    Examples:
      djb config show                     # Show all config as JSON
      djb config show --with-provenance   # Include source comments
    """
    if with_provenance:
        logger.info(_format_json_with_provenance(config_ctx.config))
    else:
        logger.info(config_ctx.config.to_json())


@config_group.command("seed_command")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the seed_command setting.",
)
@djb_pass_context(CliConfigContext)
def config_seed_command(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the host project's seed command.

    The seed command is a Click command from your project that djb will:

    \b
    * Register as 'djb seed' for manual execution
    * Run automatically during 'djb init' after migrations

    The value should be a module:attribute path to a Click command.
    Stored in .djb/project.yaml (shared, committed).

    Can also be set via the DJB_SEED_COMMAND environment variable.

    \b
    Examples:
      djb config seed_command                           # Show current
      djb config seed_command myapp.cli.seed:seed       # Set command
      djb config seed_command --delete                  # Remove setting

    \b
    Your seed command should:
      * Be a Click command (decorated with @click.command())
      * Handle Django setup internally (call django.setup())
      * Be idempotent (safe to run multiple times)
    """
    _config_get_set_delete(config_ctx, "seed_command", value, delete)


@config_group.command("project_name")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the project_name setting.",
)
@djb_pass_context(CliConfigContext)
def config_project_name(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the project name.

    The project name is used for deployment identifiers, Heroku app names,
    and Kubernetes labels. Must be a valid DNS label (lowercase alphanumeric
    with hyphens, max 63 chars, starts/ends with alphanumeric).

    If not set explicitly, defaults to the project name from pyproject.toml.

    Can also be set via the DJB_PROJECT_NAME environment variable.

    \b
    Examples:
      djb config project_name                  # Show current
      djb config project_name my-app           # Set name
      djb config project_name --delete         # Remove (use pyproject.toml)
    """
    _config_get_set_delete(config_ctx, "project_name", value, delete)


@config_group.command("name")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the name setting.",
)
@djb_pass_context(CliConfigContext)
def config_name(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the user name.

    The name is used for git commits and secrets management (GPG key
    generation). Stored in .djb/local.yaml (gitignored, per-user).

    Can also be set via the DJB_NAME environment variable.

    \b
    Examples:
      djb config name                          # Show current
      djb config name "Jane Doe"               # Set name
      djb config name --delete                 # Remove setting
    """
    _config_get_set_delete(config_ctx, "name", value, delete)


@config_group.command("email")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the email setting.",
)
@djb_pass_context(CliConfigContext)
def config_email(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the user email.

    The email is used for git commits and secrets management (GPG key
    generation). Stored in .djb/local.yaml (gitignored, per-user).

    Can also be set via the DJB_EMAIL environment variable.

    \b
    Examples:
      djb config email                         # Show current
      djb config email jane@example.com        # Set email
      djb config email --delete                # Remove setting
    """
    _config_get_set_delete(config_ctx, "email", value, delete)


@config_group.command("secrets.encrypt")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the setting (use default: true).",
)
@djb_pass_context(CliConfigContext)
def config_secrets_encrypt(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure encryption for secrets.

    When enabled (default), secrets are encrypted with SOPS/age.
    When disabled, secrets are stored as plaintext YAML.

    Uses mode-based overrides. Set for current mode with --mode flag,
    or configure per-mode in .djb/project.toml:

    \b
        [secrets]
        encrypt = true

        [development.secrets]
        encrypt = false

    Stored in .djb/project.toml (shared, committed).
    Can also be set via DJB_SECRETS_ENCRYPT environment variable.

    Accepts: true/false, yes/no, on/off, 1/0 (case-insensitive).

    \b
    Examples:
      djb config secrets.encrypt                      # Show current (for active mode)
      djb config secrets.encrypt false                # Disable for active mode
      djb --mode development config secrets.encrypt false  # Disable for development
      djb config secrets.encrypt --delete             # Use default (true)
    """
    _config_get_set_delete(config_ctx, "secrets.encrypt", value, delete)


# =============================================================================
# Nested config: hetzner.*
# =============================================================================


@config_group.command("hetzner.default_server_type")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_default_server_type(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the default Hetzner server type.

    Used when creating new servers with `djb deploy k8s materialize`.
    Can be overridden per-mode in [development.hetzner] or [staging.hetzner].

    Common server types: cx11, cx21, cx22, cx31, cx32, cx41, cx42, cx51, cx52

    Default is defined in core.toml. Use --project or --local to override.

    \b
    Examples:
      djb config hetzner.default_server_type                      # Show current
      djb config hetzner.default_server_type cx32 --project       # Override in project.toml
      djb config hetzner.default_server_type --delete             # Remove override
    """
    _config_get_set_delete(config_ctx, "hetzner.default_server_type", value, delete)


@config_group.command("hetzner.default_location")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_default_location(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the default Hetzner datacenter location.

    Used when creating new servers with `djb deploy k8s materialize`.

    Locations: nbg1 (Nuremberg), fsn1 (Falkenstein), hel1 (Helsinki),
               ash (Ashburn, VA), hil (Hillsboro, OR)

    Default is defined in core.toml. Use --project or --local to override.

    \b
    Examples:
      djb config hetzner.default_location                     # Show current
      djb config hetzner.default_location fsn1 --project      # Override in project.toml
      djb config hetzner.default_location --delete            # Remove override
    """
    _config_get_set_delete(config_ctx, "hetzner.default_location", value, delete)


@config_group.command("hetzner.default_image")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_default_image(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the default Hetzner OS image.

    Used when creating new servers with `djb deploy k8s materialize`.

    Common images: ubuntu-24.04, ubuntu-22.04, debian-12, debian-11,
                   fedora-40, rocky-9, alma-9

    Default is defined in core.toml. Use --project or --local to override.

    \b
    Examples:
      djb config hetzner.default_image                            # Show current
      djb config hetzner.default_image ubuntu-22.04 --project     # Override in project.toml
      djb config hetzner.default_image --delete                   # Remove override
    """
    _config_get_set_delete(config_ctx, "hetzner.default_image", value, delete)


# =============================================================================
# Nested config: hetzner.* (instance fields - set by materialize)
# =============================================================================


@config_group.command("hetzner.server_name")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_server_name(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the Hetzner server name.

    Set by `djb deploy k8s materialize`. Used to identify the provisioned server.
    Stored in .djb/project.toml under [hetzner] or [mode.hetzner].

    \b
    Examples:
      djb config hetzner.server_name                      # Show current
      djb config hetzner.server_name myproject-staging    # Set server name
      djb config hetzner.server_name --delete             # Remove setting
    """
    _config_get_set_delete(config_ctx, "hetzner.server_name", value, delete)


@config_group.command("hetzner.ssh_key_name")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_ssh_key_name(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the Hetzner SSH key name.

    Set by `djb deploy k8s materialize`. The SSH key name registered in Hetzner Cloud.
    Stored in .djb/project.toml under [hetzner] or [mode.hetzner].

    \b
    Examples:
      djb config hetzner.ssh_key_name                 # Show current
      djb config hetzner.ssh_key_name my-key          # Set SSH key name
      djb config hetzner.ssh_key_name --delete        # Remove setting
    """
    _config_get_set_delete(config_ctx, "hetzner.ssh_key_name", value, delete)


# =============================================================================
# Nested config: k8s.*
# =============================================================================


@config_group.command("k8s.host")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_k8s_host(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the SSH host for K8s deployment.

    Set automatically by HetznerVPSMaterialized (when using --provider hetzner),
    or via --host flag when deploying to any remote server.
    Stored in .djb/project.toml under [k8s] or [mode.k8s].

    \b
    Examples:
      djb config k8s.host                    # Show current
      djb config k8s.host 192.168.1.100      # Set host IP/hostname
      djb config k8s.host --delete           # Remove setting
    """
    _config_get_set_delete(config_ctx, "k8s.host", value, delete)


# =============================================================================
# Nested config: k8s.backend.*
# =============================================================================


@config_group.command("k8s.backend.managed_dockerfile")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting (use default: true).")
@djb_pass_context(CliConfigContext)
def config_k8s_backend_managed_dockerfile(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure whether djb manages the Dockerfile template.

    When enabled (default), djb will automatically create and update the
    Dockerfile template at deployment/k8s/backend/Dockerfile.j2 during deployment.
    When disabled, djb will not create or overwrite existing Dockerfiles,
    allowing you to maintain full control over the Dockerfile.

    Use this setting if you need custom build steps or dependencies that
    differ from the djb default Django deployment template.

    Stored in .djb/project.toml under [k8s.backend].
    Can also be set via the DJB_K8S_BACKEND_MANAGED_DOCKERFILE env var.

    Accepts: true/false, yes/no, on/off, 1/0 (case-insensitive).

    \b
    Examples:
      djb config k8s.backend.managed_dockerfile           # Show current
      djb config k8s.backend.managed_dockerfile false     # Disable auto-management
      djb config k8s.backend.managed_dockerfile true      # Enable (default)
      djb config k8s.backend.managed_dockerfile --delete  # Use default (true)
    """
    _config_get_set_delete(config_ctx, "k8s.backend.managed_dockerfile", value, delete)


# =============================================================================
# Nested config: letsencrypt.*
# =============================================================================


@config_group.command("letsencrypt.email")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_letsencrypt_email(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the Let's Encrypt email address.

    Used for certificate registration and expiry notifications.
    If not set, falls back to the global email setting.

    Stored in .djb/project.toml under [letsencrypt].
    Can also be set via the DJB_LETSENCRYPT_EMAIL env var.

    \b
    Examples:
      djb config letsencrypt.email                        # Show current
      djb config letsencrypt.email certs@example.com      # Set email
      djb config letsencrypt.email --delete               # Remove (use global email)
    """
    _config_get_set_delete(config_ctx, "letsencrypt.email", value, delete)


# =============================================================================
# Generic get/set/delete commands
# =============================================================================


@config_group.command("get")
@click.argument("key")
@djb_pass_context(CliConfigContext)
def config_get(config_ctx: CliConfigContext, key: str) -> None:
    """Get a config value by key.

    Dedicated subcommands exist for standard fields (e.g., 'djb config project_name').
    This generic command is useful for custom DjbConfig subclasses with additional fields.

    Supports flat and nested keys (e.g., 'project_name' or 'hetzner.server_name').

    \b
    Examples:
      djb config get project_name
      djb config get k8s.host
      djb config get letsencrypt.email
    """
    _config_get_set_delete(config_ctx, key, value=None, delete=False)


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@djb_pass_context(CliConfigContext)
def config_set(config_ctx: CliConfigContext, key: str, value: str) -> None:
    """Set a config value by key.

    Dedicated subcommands exist for standard fields (e.g., 'djb config project_name').
    This generic command is useful for custom DjbConfig subclasses with additional fields.

    Supports flat and nested keys (e.g., 'project_name' or 'hetzner.server_name').

    \b
    Examples:
      djb config set project_name my-app
      djb config set k8s.host 192.168.1.100
      djb config set letsencrypt.email certs@example.com
    """
    _config_get_set_delete(config_ctx, key, value=value, delete=False)


@config_group.command("delete")
@click.argument("key")
@djb_pass_context(CliConfigContext)
def config_delete(config_ctx: CliConfigContext, key: str) -> None:
    """Delete a config value by key.

    Dedicated subcommands exist for standard fields (e.g., 'djb config project_name').
    This generic command is useful for custom DjbConfig subclasses with additional fields.

    Supports flat and nested keys (e.g., 'project_name' or 'hetzner.server_name').

    \b
    Examples:
      djb config delete seed_command
      djb config delete hetzner.server_name
    """
    _config_get_set_delete(config_ctx, key, value=None, delete=True)


@config_group.command("lint")
@click.option("--fix", is_flag=True, help="Apply fixes (sort keys alphabetically)")
@click.option("--check", is_flag=True, help="Check only, exit 1 if changes needed")
@djb_pass_context(CliConfigContext)
def config_lint(config_ctx: CliConfigContext, fix: bool, check: bool) -> None:
    """Lint and organize config files.

    Sorts keys alphabetically in local.toml and/or project.toml while
    preserving comments and formatting.

    Use --local or --project to target a specific file (from parent config command).
    Without either flag, both files are checked.

    \b
    Examples:
      djb config lint                  # Preview what would change in both files
      djb config lint --fix            # Sort keys in both files
      djb config --project lint        # Preview project.toml only
      djb config --local lint --fix    # Sort keys in local.toml only
      djb config lint --check          # CI mode (exit 1 if unsorted)
    """
    config_dir = get_config_dir(config_ctx.config.project_dir)

    # Determine which files to lint based on --local/--project flags
    files_to_lint: list[str] = []
    if config_ctx.target_local:
        files_to_lint = ["local.toml"]
    elif config_ctx.target_project:
        files_to_lint = ["project.toml"]
    else:
        # Default: both files
        files_to_lint = ["local.toml", "project.toml"]

    changes_needed = False

    for filename in files_to_lint:
        path = config_dir / filename
        if not path.exists():
            continue

        doc = load_toml_mapping(path)
        original = dump_toml(doc)
        sorted_doc = sort_toml_document(doc)
        sorted_content = dump_toml(sorted_doc)

        if original != sorted_content:
            changes_needed = True
            if fix:
                save_toml_mapping(path, sorted_doc)
                logger.info(f"{filename}: sorted keys alphabetically")
            else:
                logger.warning(f"{filename}: keys not sorted alphabetically")
        else:
            if not check:
                logger.info(f"{filename}: already sorted")

    if check and changes_needed:
        raise SystemExit(1)

    if not changes_needed and not check:
        logger.info("All config files are properly sorted")

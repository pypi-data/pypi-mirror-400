"""
djb domain - Top-level domain management commands.

Manage the domain registry that tracks all domains and their DNS managers.
Commands operate on the active platform (heroku or k8s based on config.platform).

Commands
--------
- init: Interactive prompt to add first domain
- add: Add a domain to the registry
- remove: Remove a domain from configuration
- list: List all registered domains
- sync: Sync DNS records with the platform

Usage Examples
--------------
# Add a domain with cloudflare DNS management
djb domain add example.com --manager cloudflare

# List configured domains
djb domain list

# Remove a domain
djb domain remove example.com
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.config.fields.domain import DomainNameField
from djb.core.logging import get_logger
from djb.dns import CloudflareDnsProvider, CloudflareError
from djb.secrets import GpgError, ProtectedFileError, SecretsManager, SopsError
from djb.types import DomainNameManager, Platform

if TYPE_CHECKING:
    from djb.config import DjbConfig

logger = get_logger(__name__)


def _get_platform_section(platform: Platform) -> str:
    """Get the TOML section name for a platform."""
    return platform.value  # "heroku" or "k8s"


def _add_domain(config: "DjbConfig", domain: str, manager: DomainNameManager) -> None:
    """Add domain to platform's domain_names section in project.toml."""
    section = _get_platform_section(config.platform)
    # Get current domain_names and convert to serializable dicts
    current = {d: {"manager": c.manager.value} for d, c in config.domain_names.items()}
    current[domain] = {"manager": manager.value}
    # Set the entire domain_names field
    config.set(f"{section}.domain_names", current)


def _remove_domain(config: "DjbConfig", domain: str) -> bool:
    """Remove domain from platform's domain_names section.

    Returns True if domain was found and removed, False otherwise.
    """
    # Check if domain exists before trying to delete
    if domain not in config.domain_names:
        return False

    section = _get_platform_section(config.platform)
    # Get current domain_names (excluding the one to remove) and convert to serializable dicts
    current = {
        d: {"manager": c.manager.value} for d, c in config.domain_names.items() if d != domain
    }
    # Set the entire domain_names field (empty dict if no domains left)
    config.set(f"{section}.domain_names", current)
    return True


def _get_manager_display(manager: DomainNameManager, platform: Platform) -> str:
    """Get display name for manager, translating PLATFORM to actual platform."""
    if manager == DomainNameManager.PLATFORM:
        return platform.value
    return manager.value


def _list_domains(config: "DjbConfig") -> None:
    """Display all registered domains for the active platform."""
    domains = config.domain_names
    if not domains:
        logger.info(f"No domains configured for {config.platform.value}")
        return

    logger.info(f"Domains for {config.platform.value}:")
    for domain, domain_config in domains.items():
        manager_display = _get_manager_display(domain_config.manager, config.platform)
        logger.info(f"  {domain} (manager: {manager_display})")


# Domain name validator for prompting
_domain_validator = DomainNameField()


def _validate_domain(domain: str) -> str:
    """Validate domain name format, raising click.BadParameter on error."""
    _domain_validator.field_name = "domain"
    try:
        _domain_validator.validate(domain)
        return domain
    except Exception as e:
        raise click.BadParameter(str(e))


@click.group("domain")
def domain() -> None:
    """Manage domain names for the active deployment platform.

    Domain names are stored in the platform-specific section of project.toml.
    Commands operate on the current platform (heroku or k8s) based on config.
    """
    pass


def _prompt_manager() -> DomainNameManager:
    """Prompt user to select DNS manager with numbered options."""
    logger.info("\nSelect DNS manager:")
    logger.info("  1. Cloudflare")
    logger.info("  2. Manual")

    while True:
        choice = click.prompt("Choice", type=str, default="1")
        if choice == "1":
            return DomainNameManager.CLOUDFLARE
        elif choice == "2":
            return DomainNameManager.MANUAL
        else:
            logger.warning("Invalid choice. Enter 1 or 2.")


@domain.command("init")
@djb_pass_context
def domain_init(cli_ctx: CliContext) -> None:
    """Initialize domain registry with first domain.

    Prompts for:
    1. Domain name (with validation)
    2. DNS manager (cloudflare or manual - auto-detects herokuapp.com)
    """
    config = cli_ctx.config

    # Check if domains already exist
    if config.domain_names:
        logger.info(f"Domain registry already initialized for {config.platform.value}:")
        _list_domains(config)
        if not click.confirm("\nAdd another domain?"):
            return

    # Prompt for domain
    domain_name = click.prompt(
        "Domain name",
        type=str,
        value_proc=_validate_domain,
    )

    # Auto-detect manager for platform-provided domains
    if domain_name.endswith(".herokuapp.com"):
        manager = DomainNameManager.PLATFORM
        logger.note(f"Auto-selected 'platform' manager for {domain_name}")
    else:
        manager = _prompt_manager()

    _add_domain(config, domain_name, manager)
    logger.done(f"Added {domain_name} (manager: {manager.value})")


@domain.command("add")
@click.argument("domain_name")
@click.option(
    "--manager",
    "-m",
    type=click.Choice(["cloudflare", "platform", "manual"]),
    default=None,
    help="DNS manager for this domain. Defaults to 'platform' for *.herokuapp.com, 'cloudflare' otherwise.",
)
@djb_pass_context
def domain_add(cli_ctx: CliContext, domain_name: str, manager: str | None) -> None:
    """Add a domain to the registry.

    \\b
    Examples:
      djb domain add example.com
      djb domain add example.com --manager cloudflare
      djb domain add myapp-abc123.herokuapp.com --manager heroku
    """
    config = cli_ctx.config

    # Validate domain
    _validate_domain(domain_name)

    # Check if domain already exists
    if domain_name in config.domain_names:
        existing = config.domain_names[domain_name]
        logger.warning(f"Domain {domain_name} already exists (manager: {existing.manager.value})")
        if not click.confirm("Update manager?"):
            return

    # Determine manager
    if manager is None:
        if domain_name.endswith(".herokuapp.com"):
            manager = "platform"
            logger.note(f"Auto-selected 'platform' manager for {domain_name}")
        else:
            manager = "cloudflare"

    domain_manager = DomainNameManager(manager)
    _add_domain(config, domain_name, domain_manager)
    logger.done(f"Added {domain_name} (manager: {manager})")


@domain.command("remove")
@click.argument("domain_name")
@djb_pass_context
def domain_remove(cli_ctx: CliContext, domain_name: str) -> None:
    """Remove a domain from the registry.

    \\b
    Examples:
      djb domain remove example.com
    """
    config = cli_ctx.config

    if domain_name not in config.domain_names:
        raise click.ClickException(
            f"Domain '{domain_name}' not found in {config.platform.value}.domain_names"
        )

    removed = _remove_domain(config, domain_name)
    if removed:
        logger.done(f"Removed {domain_name}")
    else:
        raise click.ClickException(f"Failed to remove {domain_name}")


@domain.command("list")
@djb_pass_context
def domain_list(cli_ctx: CliContext) -> None:
    """List all registered domains for the active platform."""
    _list_domains(cli_ctx.config)


@domain.command("sync")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without applying.",
)
@djb_pass_context
def domain_sync(cli_ctx: CliContext, dry_run: bool) -> None:
    """Sync DNS records with the deployment platform.

    For Heroku:
    - Adds domains to Heroku app
    - Creates CNAME records in Cloudflare (if configured)

    For K8s:
    - Creates A records pointing to server IP (if configured)

    \\b
    Examples:
      djb domain sync
      djb domain sync --dry-run
    """
    config = cli_ctx.config

    if not config.domain_names:
        logger.info(f"No domains configured for {config.platform.value}")
        return

    if config.platform == Platform.HEROKU:
        _sync_heroku_domains(cli_ctx, dry_run)
    else:
        _sync_k8s_domains(cli_ctx, dry_run)


def _sync_heroku_domains(cli_ctx: CliContext, dry_run: bool) -> None:
    """Sync domains with Heroku."""
    config = cli_ctx.config

    # Get cloudflare API token if available
    api_token = None
    try:
        manager = SecretsManager(cli_ctx.runner, config.project_dir)
        secrets = manager.load_secrets(config.mode)
        api_token = secrets.get("cloudflare", {}).get("api_token")
    except SopsError:
        pass

    cloudflare_provider = None
    if api_token and config.cloudflare.auto_dns:
        cloudflare_provider = CloudflareDnsProvider(api_token=str(api_token))
    elif config.cloudflare.auto_dns:
        logger.info("Cloudflare API token not configured - DNS will need manual setup")

    if dry_run:
        logger.info("Dry run - would configure:")

    # Get heroku app name
    app_name = config.project_name

    for domain, domain_config in config.domain_names.items():
        # Skip herokuapp.com domains for custom domain setup
        if domain.endswith(".herokuapp.com"):
            continue

        logger.info(f"Configuring domain: {domain}")

        if dry_run:
            logger.info(f"  Would add to Heroku: {domain}")
            logger.info(f"  Would add to Heroku: www.{domain}")
            if cloudflare_provider and domain_config.manager == DomainNameManager.CLOUDFLARE:
                logger.info(f"  Would configure Cloudflare CNAME: {domain}")
                logger.info(f"  Would configure Cloudflare CNAME: www.{domain}")
            continue

        # Add domain to Heroku
        for d in [domain, f"www.{domain}"]:
            result = cli_ctx.runner.run(
                ["heroku", "domains:add", d, "--app", app_name, "--json"],
                quiet=True,
            )
            if result.returncode == 0:
                logger.done(f"  Added to Heroku: {d}")
                try:
                    data = json.loads(result.stdout)
                    dns_target = data.get("cname")

                    # Configure Cloudflare if appropriate
                    if (
                        cloudflare_provider
                        and domain_config.manager == DomainNameManager.CLOUDFLARE
                        and dns_target
                    ):
                        try:
                            zone_id = cloudflare_provider.get_zone_id(domain)
                            cloudflare_provider.set_cname_record(
                                zone_id=zone_id,
                                name=d,
                                target=dns_target,
                                ttl=config.cloudflare.ttl,
                                proxied=config.cloudflare.proxied,
                            )
                            logger.done(f"  Cloudflare CNAME: {d} -> {dns_target}")
                        except CloudflareError as e:
                            logger.warning(f"  Cloudflare DNS failed: {e}")
                except json.JSONDecodeError:
                    pass
            elif "already" in result.stderr.lower():
                logger.debug(f"  Domain {d} already exists on Heroku")
            else:
                logger.warning(f"  Failed to add {d}: {result.stderr}")

    if not dry_run:
        logger.done("Domain sync complete")


def _sync_k8s_domains(cli_ctx: CliContext, dry_run: bool) -> None:
    """Sync domains with K8s (Cloudflare A records).

    Queries current DNS state and shows diffs before making changes.
    """
    config = cli_ctx.config

    # Get server IP
    server_ip = config.k8s.host
    if not server_ip:
        raise click.ClickException("No server IP configured. Run `djb deploy k8s terraform` first.")

    # Get cloudflare API token (SecretsManager handles GPG-protected keys)
    api_token = None
    try:
        manager = SecretsManager(cli_ctx.runner, config.project_dir)
        secrets = manager.load_secrets(config.mode)
        api_token = secrets.get("cloudflare", {}).get("api_token")
    except (GpgError, ProtectedFileError) as e:
        raise click.ClickException(f"Failed to decrypt secrets: {e}")
    except SopsError as e:
        logger.debug(f"Failed to load secrets: {e}")

    if not api_token:
        raise click.ClickException(
            "Cloudflare API token not configured. Run `djb secrets set cloudflare.api_token`."
        )

    cloudflare_provider = CloudflareDnsProvider(api_token=str(api_token))

    for domain, domain_config in config.domain_names.items():
        if domain_config.manager != DomainNameManager.CLOUDFLARE:
            logger.info(f"Skipping {domain} (manager: {domain_config.manager.value})")
            continue

        logger.next(f"Syncing domain: {domain}")

        try:
            zone_id = cloudflare_provider.get_zone_id(domain)

            for d in [domain, f"www.{domain}"]:
                # Query current state
                existing = cloudflare_provider.get_record(zone_id, d, "A")
                current_ip = existing.content if existing else None

                # Show diff
                if current_ip == server_ip:
                    logger.done(f"  {d} -> {server_ip} (already correct)")
                    continue
                elif current_ip:
                    logger.info(f"  {d}: {current_ip} -> {server_ip}")
                else:
                    logger.info(f"  {d}: (new) -> {server_ip}")

                if dry_run:
                    continue

                # Apply change
                cloudflare_provider.set_a_record(
                    zone_id=zone_id,
                    name=d,
                    ip=server_ip,
                    ttl=config.cloudflare.ttl,
                    proxied=config.cloudflare.proxied,
                )
                logger.done(f"  {d} -> {server_ip}")

        except CloudflareError as e:
            logger.warning(f"  Cloudflare DNS failed for {domain}: {e}")

    if dry_run:
        logger.note("Dry run complete - no changes made")
    else:
        logger.done("Domain sync complete")

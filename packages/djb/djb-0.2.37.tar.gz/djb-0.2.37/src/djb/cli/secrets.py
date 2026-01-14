"""
djb secrets CLI - Manage encrypted secrets with SOPS.

Provides commands for initializing, editing, and managing encrypted secrets
using SOPS with age encryption (X25519 + ChaCha20-Poly1305).

Why SOPS?
---------
- Native support for age encryption and multi-recipient
- Built-in editor integration
- Preserves YAML structure while encrypting values

Why Age Encryption Over PGP/GPG?
--------------------------------
- Age has a single key format vs PGP's complex keyring
- A single line for private key, easy to backup

Key Management
--------------
- Private key stored at .age/keys.txt in project root (NEVER committed)
- Each project has its own key for better isolation
- Public key shared with team members for multi-recipient encryption
- The `djb init` command generates keys and template files
- Backup your private key: `djb secrets export-key | pbcopy` (saves to clipboard)

Editing Workflow
----------------
The `djb secrets edit <env>` command uses SOPS to:
1. Decrypt the secrets file in-memory
2. Open your $EDITOR (or vim)
3. Re-encrypt on save

This ensures plaintext secrets never persist on disk.
"""

from __future__ import annotations

import platform
import readline  # noqa: F401 - enables line editing for input()
import secrets as py_secrets
import shutil
import string
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import click
import yaml

# Length of generated Django secret keys (50 characters is Django's default)
DJANGO_SECRET_KEY_LENGTH: Final[int] = 50

# Characters for generated Django secret keys (letters, digits, safe special chars)
DJANGO_SECRET_KEY_CHARS: Final[str] = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"

# Expected length of age public keys (age1... format, 62 chars)
AGE_PUBLIC_KEY_LENGTH: Final[int] = 62

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.init.shared import read_clipboard
from djb.core.logging import get_logger


from djb.secrets import (
    GpgError,
    ProtectedFileError,
    SecretsManager,
    SopsError,
    check_age_installed,
    check_gpg_installed,
    check_sops_installed,
    format_identity,
    generate_age_key,
    generate_gpg_key,
    get_default_key_path,
    get_default_secrets_dir,
    get_public_key_from_private,
    has_gpg_secret_key,
    init_gpg_agent_config,
    is_valid_age_public_key,
    parse_identity,
)
from djb.types import Mode

# Import GPG protection functions directly (this file is excluded from TID251)
from djb.secrets.protected import (
    is_age_key_protected,
    protect_age_key,
    protected_age_key,  # noqa: F401 - imported for test patching
    unprotect_age_key,
)

# Internal imports for CLI-specific needs (not part of public API)
from djb.secrets.init import (
    _deep_merge_missing,
    _get_template,
)

logger = get_logger(__name__)


# Template for secrets directory README, accepts {key_path} and {public_key} format args
_README_TEMPLATE = """# Secrets Directory

This directory contains SOPS-encrypted secrets for different environments.

## Your Age Key

- **Private key**: `{key_path}`
- **Public key**: `{public_key}`

**IMPORTANT:** Never commit your private key to git! It should stay at `~/.age/keys.txt`.

## Files

| File                | Purpose                                                |
|---------------------|--------------------------------------------------------|
| `development.yaml`  | Development secrets (local machine)                    |
| `staging.yaml`      | Staging environment secrets                            |
| `production.yaml`   | Production secrets                                     |
| `.sops.yaml`        | SOPS configuration with team member keys (commit this) |

## Managing Secrets

### Edit secrets
```bash
djb secrets edit               # Edit secrets for current mode
djb secrets edit production    # Edit production secrets
```

### View secrets (careful in shared environments)
```bash
djb secrets view dev
djb secrets view production --key django_secret_key
```

### List available environments
```bash
djb secrets list
```

### Generate a random string (50 chars)
```bash
djb secrets generate-key
```

## Adding Team Members

To add a new team member:

1. Have them run `djb init` (sets up email, generates age key, initializes secrets)
2. They share their public key (starts with `age...`) with you
3. Add their key and re-encrypt: `djb secrets rotate --add-key age1... --add-email their@email.com`
4. Commit the updated `.sops.yaml` and secrets files

To remove a team member:

```bash
djb secrets rotate --remove-key their@email.com
```

## How It Works

Secrets are encrypted using SOPS with age encryption:
- Keys are visible in git diffs (e.g., `django_secret_key:`)
- Values are encrypted inline in the YAML
- Safe to commit encrypted files to git
- Decryption requires the private key at `~/.age/keys.txt`

## Security Best Practices

1. **Never commit `~/.age/keys.txt`** - it's your private key
2. **Backup your key** - store it in a password manager
3. **Use strong secrets** - run `djb secrets generate-key` for Django keys
4. **Rotate secrets** after team changes or suspected compromise
5. **Different secrets per environment** - never reuse prod secrets in dev
"""


def _check_homebrew_installed() -> bool:
    """Check if Homebrew is installed."""
    return shutil.which("brew") is not None


def _install_with_homebrew(cli_ctx: CliContext, package: str) -> bool:
    """Install a package using Homebrew.

    Returns True if installation succeeded.
    """
    logger.next(f"Installing {package} with Homebrew")
    result = cli_ctx.runner.run(["brew", "install", package])
    if result.returncode == 0:
        logger.done(f"Installed {package}")
        return True
    else:
        logger.fail(f"Failed to install {package}: {result.stderr}")
        return False


def _ensure_prerequisites(
    cli_ctx: CliContext, quiet: bool = False, include_gpg: bool = True
) -> bool:
    """Ensure SOPS, age, and GPG are installed, auto-installing if possible.

    This function handles the complete prerequisite workflow:
    1. Check which tools (sops, age, gnupg) are already installed
    2. Report status of installed tools (unless quiet=True)
    3. On macOS with Homebrew: auto-install missing tools
    4. On other platforms: show manual installation instructions

    Args:
        cli_ctx: CLI context with runner.
        quiet: If True, don't log "already installed" messages
        include_gpg: If True, also check for GPG (default True)

    Returns:
        True if all prerequisites are met, False otherwise
    """
    missing = []
    installed = []

    if not check_sops_installed():
        missing.append("sops")
    else:
        installed.append("sops")

    if not check_age_installed():
        missing.append("age")
    else:
        installed.append("age")

    if include_gpg:
        if not check_gpg_installed():
            missing.append("gnupg")
        else:
            installed.append("gnupg")

    # Report already installed tools
    if not quiet:
        for tool in installed:
            logger.done(f"{tool} already installed")

    if not missing:
        return True

    # Check if we can install
    is_macos = platform.system() == "Darwin"
    has_brew = _check_homebrew_installed()

    if is_macos and has_brew:
        # Auto-install missing tools
        for package in missing:
            if not _install_with_homebrew(cli_ctx, package):
                return False
        return True
    else:
        logger.fail(f"Missing required tools: {', '.join(missing)}")
        logger.info("Please install:")
        if is_macos:
            logger.info("  First install Homebrew: https://brew.sh")
        for package in missing:
            if is_macos:
                logger.info(f"  brew install {package}")
            else:
                install_urls = {
                    "sops": "https://github.com/getsops/sops#install",
                    "age": "https://github.com/FiloSottile/age#installation",
                    "gnupg": "https://gnupg.org/download/",
                }
                logger.info(f"  See: {install_urls.get(package, package)}")
        return False


def _check_prerequisites(cli_ctx: CliContext) -> None:
    """Check that SOPS and age are installed, exit if not."""
    if not _ensure_prerequisites(cli_ctx):
        sys.exit(1)


@click.group()
def secrets():
    """Manage encrypted secrets for different environments."""
    pass


def _ensure_gpg_setup(cli_ctx: CliContext) -> bool:
    """Ensure GPG is properly configured with a secret key.

    Sets up GPG agent configuration and generates a GPG keypair if needed.
    Uses the user's configured email and name from config.

    Args:
        cli_ctx: CLI context with runner and config.

    Returns:
        True if GPG is ready to use, False if setup failed.
    """
    # Initialize GPG agent config if not exists
    if init_gpg_agent_config(cli_ctx.runner):
        logger.done("Created GPG agent config with passphrase caching")

    # Check if user has a GPG key
    if has_gpg_secret_key(cli_ctx.runner):
        return True

    # Need to generate a GPG key
    logger.warning("No GPG key found - one is needed for age key protection")

    user_email = cli_ctx.config.email
    user_name = cli_ctx.config.name

    if not user_email:
        logger.fail("Email not configured. Run 'djb init' first.")
        return False

    if not user_name:
        user_name = user_email.split("@")[0]

    logger.next(f"Generating GPG key for {user_name} <{user_email}>")

    try:
        generate_gpg_key(cli_ctx.runner, user_name, user_email)
        logger.done("Generated GPG keypair")
        return True
    except GpgError as e:
        logger.fail(f"Failed to generate GPG key: {e}")
        logger.info("You can generate one manually with: gpg --gen-key")
        return False


@secrets.command("init")
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to store age key (default: .age/keys.txt in project root)",
)
@click.option(
    "--secrets-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for secrets files (default: ./secrets)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing key file if it exists",
)
@djb_pass_context
def init(cli_ctx: CliContext, key_path: Path | None, secrets_dir: Path | None, force: bool):
    """Initialize secrets management for this project.

    NOTE: `djb init` automatically runs this command. You typically don't need
    to run `djb secrets init` directly unless you need advanced options.

    Sets up SOPS with age encryption:

    \b
    - Generates an age encryption key (.age/keys.txt in project root)
    - Creates encrypted secrets files for dev/staging/production
    - Sets up .sops.yaml configuration for multi-recipient encryption
    - Displays your public key for sharing with team members
    - Configures GPG agent for passphrase caching
    - Generates a GPG key if needed (for age key protection)

    Safe to run if key already exists - you'll be prompted to reuse it.

    \b
    Examples:
      djb secrets init --force          # Regenerate key
      djb secrets init --key-path ./my.key  # Custom key location

    \b
    Backup your private key:
      djb secrets export-key | pbcopy   # Copy to clipboard for password manager
    """
    # Ensure SOPS, age, and GPG are installed (auto-installs on macOS with Homebrew)
    if not _ensure_prerequisites(cli_ctx):
        sys.exit(1)

    # Ensure GPG is configured with a key for age key protection
    if not _ensure_gpg_setup(cli_ctx):
        sys.exit(1)

    project_dir = cli_ctx.config.project_dir
    if key_path is None:
        key_path = get_default_key_path(project_dir)

    if secrets_dir is None:
        secrets_dir = get_default_secrets_dir(project_dir)

    # Check if key already exists
    if key_path.exists() and not force:
        public_key = get_public_key_from_private(cli_ctx.runner, key_path)
        logger.info(f"Using existing age key at {key_path}")
    else:
        # Generate new age key
        public_key, _ = generate_age_key(cli_ctx.runner, key_path)
        logger.done(f"Generated age key at {key_path}")

    # Display public key
    logger.info("\nYour public key (share with team members):")
    logger.highlight(f"  {public_key}")

    # Create secrets directory and manager
    secrets_dir.mkdir(parents=True, exist_ok=True)
    manager = SecretsManager(
        cli_ctx.runner, project_dir, secrets_dir=secrets_dir, key_path=key_path
    )

    # Get existing recipients from .sops.yaml (if any)
    user_email = cli_ctx.config.email or "unknown@example.com"
    user_name = cli_ctx.config.name
    user_identity = format_identity(user_name, user_email)
    recipients = manager.recipients

    # Add user's key if not already present
    if public_key not in recipients:
        recipients[public_key] = user_identity
        logger.done(f"Added your public key to .sops.yaml")
    else:
        existing_identity = recipients[public_key]
        if existing_identity:
            logger.info(f"Public key already in .sops.yaml ({existing_identity})")
        else:
            # Update identity for existing key
            recipients[public_key] = user_identity

    # Create/update .sops.yaml configuration with identity comments
    manager.save_config(recipients)
    logger.done("Updated .sops.yaml configuration")

    # Create .gitignore for secrets directory
    gitignore_path = secrets_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# Decrypted secrets (never commit these)\n"
            "*.decrypted.yaml\n"
            "*.plaintext.yaml\n"
            "*.secret\n"
            "*.tmp.yaml\n"
        )

    # Create template secrets files for each mode
    for mode in Mode.all():
        secrets_file = secrets_dir / f"{mode}.yaml"
        if not secrets_file.exists():
            template = _get_template(mode)
            manager.save_secrets(mode, template)
            logger.done(f"Created {mode}.yaml")

    # Create README for secrets directory
    readme_path = secrets_dir / "README.md"
    if not readme_path.exists():
        readme_content = _README_TEMPLATE.format(key_path=key_path, public_key=public_key)
        readme_path.write_text(readme_content)
        logger.done("Created README.md")

    logger.done(f"Secrets management initialized in {secrets_dir}")
    logger.info("\nNext steps:")
    logger.info("  1. Edit your secrets: djb secrets edit dev")
    logger.info(f"  2. Add secrets to git: git add {secrets_dir}/*.yaml {secrets_dir}/.sops.yaml")
    logger.info(f"  3. Keep your key safe: backup {key_path}")


@secrets.command("edit")
@djb_pass_context
def edit(cli_ctx: CliContext):
    """Edit secrets for the current mode.

    Uses SOPS to decrypt the secrets file, open it in your editor ($EDITOR or vim),
    then automatically re-encrypts when you save and close.

    Creates a new secrets file if it doesn't exist yet.

    The environment is determined by the current mode (from djb --mode or DJB_MODE).

    \b
    Examples:
      djb secrets edit                  # Edit development secrets (default mode)
      djb --mode staging secrets edit   # Edit staging secrets
      DJB_MODE=production djb secrets edit  # Edit production secrets
    """
    mode = cli_ctx.config.mode
    _check_prerequisites(cli_ctx)

    project_dir = cli_ctx.config.project_dir
    manager = SecretsManager(cli_ctx.runner, project_dir)
    secrets_file = manager.secrets_dir / f"{mode}.yaml"
    encrypt = cli_ctx.config.secrets.encrypt

    # Check if file exists, create if not
    if not secrets_file.exists():
        logger.warning(f"Secrets file for '{mode}' not found.")
        if click.confirm("Create new secrets file?"):
            template = _get_template(mode, project_name=cli_ctx.config.project_name)
            manager.save_secrets(mode, template)
            logger.done(f"Created {mode}.yaml" + (" (plaintext)" if not encrypt else ""))
        else:
            sys.exit(1)

    try:
        returncode = manager.edit_secrets(mode)
        if returncode == 0:
            logger.done(f"Saved secrets for {mode}")
        else:
            logger.fail("SOPS edit failed")
            sys.exit(1)
    except ProtectedFileError as e:
        logger.fail(str(e))
        sys.exit(1)


@secrets.command("view")
@click.option(
    "--key",
    "secret_key",
    default=None,
    help="Show only this specific key",
)
@djb_pass_context
def view(cli_ctx: CliContext, secret_key: str | None):
    """View decrypted secrets without editing.

    Displays secrets in plaintext - use carefully in secure environments only.

    The environment is determined by the current mode (from djb --mode or DJB_MODE).

    \b
    Examples:
      djb secrets view                  # View development secrets (default mode)
      djb --mode staging secrets view   # View staging secrets
      djb secrets view --key django_secret_key  # View one key
    """
    mode = cli_ctx.config.mode
    _check_prerequisites(cli_ctx)

    project_dir = cli_ctx.config.project_dir
    manager = SecretsManager(cli_ctx.runner, project_dir)

    try:
        if secret_key:
            value = manager.view_secrets(mode, secret_key)
            logger.info(f"{secret_key}: {value}")
        else:
            secrets_data = manager.view_secrets(mode)
            logger.info(f"Secrets for {mode.value}:")
            logger.info(yaml.dump(secrets_data, default_flow_style=False, sort_keys=False))
    except KeyError:
        logger.fail(f"Key '{secret_key}' not found")
        sys.exit(1)
    except SopsError as e:
        logger.fail(f"Failed to decrypt: {e}")
        sys.exit(1)
    except ProtectedFileError as e:
        logger.fail(str(e))
        sys.exit(1)


@dataclass
class SecretsSetContext(CliContext):
    """Context for secrets set subcommands.

    Holds options shared across all set subcommands.
    """

    from_clipboard: bool = False
    hidden: bool = False


@secrets.group("set", invoke_without_command=True)
@click.option(
    "--from-clipboard",
    is_flag=True,
    help="Read value from system clipboard",
)
@click.option(
    "--hidden",
    is_flag=True,
    help="Hide input when prompting (no readline, requires confirmation)",
)
@djb_pass_context
@click.pass_context
def secrets_set(
    ctx: click.Context,
    cli_ctx: CliContext,
    from_clipboard: bool,
    hidden: bool,
) -> None:
    """Set secret values.

    Each secret key is a subcommand with its own documentation.
    Use 'djb secrets set --help' to see available keys.

    The environment is determined by the current mode (from djb --mode or DJB_MODE).

    \b
    Options (apply to all subcommands):
      --from-clipboard   Read value from system clipboard
      --hidden           Hide input when prompting (requires confirmation)

    \b
    Examples:
      djb secrets set --from-clipboard hetzner.api_token
      djb secrets set hetzner.api_token "my-token"
      djb secrets set --hidden hetzner.api_token
      djb --mode staging secrets set hetzner.api_token
    """
    # Set up SecretsSetContext for subcommands
    set_ctx = SecretsSetContext()
    set_ctx.__dict__.update(cli_ctx.__dict__)
    set_ctx.from_clipboard = from_clipboard
    set_ctx.hidden = hidden
    ctx.obj = set_ctx

    if ctx.invoked_subcommand is None:
        logger.info(ctx.get_help())


def _secrets_set_handler(
    set_ctx: SecretsSetContext,
    key: str,
    value: str | None,
) -> None:
    """Shared handler for secrets set subcommands.

    Handles value acquisition (argument, clipboard, or prompt) and delegates
    to SecretsManager.set_secret() for the actual secret modification.
    """
    _check_prerequisites(set_ctx)

    from_clipboard = set_ctx.from_clipboard
    hidden = set_ctx.hidden

    # Determine the value
    if from_clipboard:
        if value is not None:
            raise click.ClickException("Cannot specify both VALUE argument and --from-clipboard")
        value = read_clipboard(set_ctx.runner)
        if not value:
            raise click.ClickException("Clipboard is empty")
    elif value is None:
        # Prompt for value
        if hidden:
            value = click.prompt(
                f"Enter value for '{key}'",
                hide_input=True,
                confirmation_prompt=True,
            )
        else:
            value = input(f"Enter value for '{key}': ")

    # At this point value is guaranteed to be a string
    assert value is not None

    mode = set_ctx.config.mode
    project_dir = set_ctx.config.project_dir
    manager = SecretsManager(set_ctx.runner, project_dir)

    try:
        manager.set_secret(mode, key, value)
        logger.done(f"Set '{key}' in {mode.value} secrets")
    except FileNotFoundError:
        logger.fail(f"Secrets file not found for {mode.value}")
        logger.info(f"Run 'djb secrets init' to create secrets for {mode.value}")
        sys.exit(1)
    except SopsError as e:
        logger.fail(f"Failed to save secrets: {e}")
        sys.exit(1)
    except ProtectedFileError as e:
        logger.fail(str(e))
        sys.exit(1)


@secrets_set.command("hetzner.api_token")
@click.argument("value", required=False, default=None)
@djb_pass_context(SecretsSetContext)
def set_hetzner_api_token(
    set_ctx: SecretsSetContext,
    value: str | None,
) -> None:
    """Set the Hetzner Cloud API token.

    The Hetzner API token is used for provisioning servers with 'djb deploy k8s'.
    Get your token from https://console.hetzner.cloud/projects/<project>/security/tokens

    \b
    Examples:
      djb secrets set --from-clipboard hetzner.api_token
      djb secrets set hetzner.api_token "abc123..."
      djb secrets set --hidden hetzner.api_token
    """
    _secrets_set_handler(set_ctx, "hetzner.api_token", value)


@secrets_set.command("cloudflare.api_token")
@click.argument("value", required=False, default=None)
@djb_pass_context(SecretsSetContext)
def set_cloudflare_api_token(
    set_ctx: SecretsSetContext,
    value: str | None,
) -> None:
    """Set the Cloudflare API token.

    The Cloudflare API token is used for DNS management with 'djb deploy k8s domain add'
    and 'djb deploy heroku domain add'.
    Get your token from https://dash.cloudflare.com/profile/api-tokens
    Required permissions: Zone:DNS:Edit

    \b
    Examples:
      djb secrets set --from-clipboard cloudflare.api_token
      djb secrets set cloudflare.api_token "abc123..."
      djb secrets set --hidden cloudflare.api_token
    """
    _secrets_set_handler(set_ctx, "cloudflare.api_token", value)


@secrets.command("list")
@djb_pass_context
def list_environments(cli_ctx: CliContext):
    """List available secret environments.

    Shows all encrypted secrets files in the secrets directory.
    The current environment (based on mode) is marked with *.

    \b
    Example:
      djb secrets list
    """
    project_dir = cli_ctx.config.project_dir
    secrets_dir = get_default_secrets_dir(project_dir)

    current_env = cli_ctx.config.mode.value

    if not secrets_dir.exists():
        logger.warning("No secrets directory found.")
        logger.info("Run 'djb init' to get started.")
        return

    # Find all .yaml files (excluding .sops.yaml)
    secret_files = sorted(f for f in secrets_dir.glob("*.yaml") if f.name != ".sops.yaml")

    if not secret_files:
        logger.warning("No secret files found.")
        return

    logger.info("Available environments:")
    for file in secret_files:
        env_name = file.stem
        if env_name == current_env:
            logger.info(f"  * {env_name} (current)")
        else:
            logger.info(f"  - {env_name}")


@secrets.command("generate-key")
def generate_key():
    """Generate a new random Django secret key.

    Creates a cryptographically secure 50-character secret key
    suitable for Django's SECRET_KEY setting.

    \b
    Example:
      djb secrets generate-key
    """
    secret_key = "".join(
        py_secrets.choice(DJANGO_SECRET_KEY_CHARS) for _ in range(DJANGO_SECRET_KEY_LENGTH)
    )

    logger.info("Generated Django secret key:")
    logger.highlight(secret_key)
    logger.info("\nAdd this to your secrets file with:")
    logger.info("  djb secrets edit <environment>")


@secrets.command("export-key")
@djb_pass_context
def export_key(cli_ctx: CliContext):
    """Export the private key for backup.

    Outputs only the secret key line (AGE-SECRET-KEY-...) which can be
    copied to a password manager for safekeeping.

    \b
    Examples:
      djb secrets export-key              # Print to stdout
      djb secrets export-key | pbcopy     # Copy to clipboard (macOS)
      djb secrets export-key | xclip      # Copy to clipboard (Linux)

    \b
    Important:
      - Store this key securely in a password manager
      - Never commit the key to version control
      - If lost, you won't be able to decrypt existing secrets
    """
    project_dir = cli_ctx.config.project_dir
    manager = SecretsManager(cli_ctx.runner, project_dir)

    try:
        private_key = manager.export_private_key()
        # Output just the key, no newline for clean piping
        sys.stdout.write(private_key)
    except FileNotFoundError as e:
        logger.fail(str(e))
        logger.info("\nTo create a key, run:")
        logger.info("  djb init")
        sys.exit(1)
    except SopsError as e:
        logger.fail(str(e))
        sys.exit(1)
    except ProtectedFileError as e:
        logger.fail(str(e))
        sys.exit(1)


@secrets.command("upgrade")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be added without making changes",
)
@click.option(
    "--all",
    "all_envs",
    is_flag=True,
    help="Upgrade all environments",
)
@djb_pass_context
def upgrade(cli_ctx: CliContext, dry_run: bool, all_envs: bool):
    """Add missing secrets from template to existing secrets files.

    Upgrades secrets files by adding any new keys from the template while
    preserving existing values. Useful when djb adds new secret fields.

    Uses the current mode by default (from djb --mode or DJB_MODE).

    \b
    Examples:
      djb secrets upgrade                 # Upgrade secrets for current mode
      djb --mode staging secrets upgrade  # Upgrade staging secrets
      djb secrets upgrade --all           # Upgrade all environments
      djb secrets upgrade --dry-run       # Preview changes
    """
    _check_prerequisites(cli_ctx)

    project_dir = cli_ctx.config.project_dir
    manager = SecretsManager(cli_ctx.runner, project_dir)

    # Determine which modes to upgrade
    modes = Mode.all() if all_envs else [cli_ctx.config.mode]

    try:
        for mode in modes:
            secrets_file = manager.secrets_dir / f"{mode}.yaml"
            if not secrets_file.exists():
                logger.warning(f"Skipping {mode}: secrets file not found")
                continue

            # Load existing secrets
            try:
                existing = manager.load_secrets(mode)
            except (FileNotFoundError, SopsError) as e:
                logger.fail(f"Skipping {mode}: failed to load ({e})")
                continue

            # Get template and merge
            template = _get_template(mode)
            merged, added = _deep_merge_missing(existing, template)

            if not added:
                logger.info(f"{mode}: already up to date")
                continue

            if dry_run:
                logger.warning(f"{mode}: would add {len(added)} key(s):")
                for key in added:
                    logger.info(f"  + {key}")
            else:
                manager.save_secrets(mode, merged)
                logger.done(f"{mode}: added {len(added)} key(s):")
                for key in added:
                    logger.info(f"  + {key}")
    except ProtectedFileError as e:
        logger.fail(str(e))
        sys.exit(1)


@secrets.command("rotate")
@click.argument(
    "environment",
    type=click.Choice([str(m) for m in Mode.public()] + ["all"]),
    required=False,
    default="all",
)
@click.option(
    "--new-key",
    is_flag=True,
    help="Generate a new key (rotates your personal key)",
)
@click.option(
    "--add-key",
    type=str,
    default=None,
    help="Add a new public key (age...) to encrypt for",
)
@click.option(
    "--add-email",
    type=str,
    default=None,
    help="Email for the new key being added (used with --add-key)",
)
@click.option(
    "--add-name",
    type=str,
    default=None,
    help="Name for the new key being added (used with --add-key, optional)",
)
@click.option(
    "--remove-key",
    type=str,
    default=None,
    help="Remove a public key (age... or identity) from recipients",
)
@djb_pass_context
def rotate(
    cli_ctx: CliContext,
    environment: str,
    new_key: bool,
    add_key: str | None,
    add_email: str | None,
    add_name: str | None,
    remove_key: str | None,
):
    """Re-encrypt project secrets with updated recipient keys.

    This command manages project secrets (staging, production) which are
    shared among team members. User secrets (dev) are encrypted with each
    user's own key and don't need rotation.

    Use this command for:
    - Adding a new team member (--add-key)
    - Removing a team member (--remove-key)
    - Rotating your own key (--new-key)
    - Re-encrypting after updating .sops.yaml (no flags)

    By default, re-encrypts all project secrets. Specify an environment
    to only re-encrypt that one.

    \b
    Examples:
      djb secrets rotate                           # Re-encrypt all project secrets
      djb secrets rotate --add-key age1abc... --add-email bob@example.com --add-name "Bob Smith"
      djb secrets rotate --remove-key bob@example.com
      djb secrets rotate --new-key                 # Rotate your personal key
      djb secrets rotate staging                   # Only re-encrypt staging
    """
    _check_prerequisites(cli_ctx)

    project_dir = cli_ctx.config.project_dir
    manager = SecretsManager(cli_ctx.runner, project_dir)

    try:
        # Load existing recipients from .sops.yaml
        recipients = manager.recipients
        old_public_key = manager.get_public_key()

        # Handle --new-key: generate new key and update .sops.yaml
        if new_key:
            logger.warning("This will generate a new encryption key!")
            logger.info("Your old key will be backed up.")

            if not click.confirm("Continue?"):
                logger.info("Aborted.")
                return

            # Backup old key
            key_path = manager.key_path
            backup_path = key_path.with_suffix(".txt.backup")
            old_key_content = key_path.read_text()
            backup_path.write_text(old_key_content)
            backup_path.chmod(0o600)
            logger.info(f"Old key backed up to {backup_path}")

            # Generate new key
            new_public_key, _ = generate_age_key(cli_ctx.runner, key_path)

            logger.done(f"Generated new key at {key_path}")
            logger.info("\nNew public key:")
            logger.highlight(f"  {new_public_key}")

            # Update recipients: remove old key, add new key with same identity
            old_identity = recipients.pop(old_public_key, None)
            if old_identity:
                recipients[new_public_key] = old_identity
                logger.done("Updated .sops.yaml with new key")
            else:
                user_email = cli_ctx.config.email or "unknown@example.com"
                user_name = cli_ctx.config.name
                user_identity = format_identity(user_name, user_email)
                recipients[new_public_key] = user_identity
                logger.done("Added new key to .sops.yaml")

        # Handle --add-key: add a new public key
        if add_key:
            if not is_valid_age_public_key(add_key):
                logger.fail(f"Invalid age public key: {add_key}")
                logger.info(
                    f"Age public keys start with 'age1' and are {AGE_PUBLIC_KEY_LENGTH} characters long."
                )
                logger.info(
                    "Example: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p"
                )
                sys.exit(1)

            if add_key in recipients:
                logger.warning("Key already exists in .sops.yaml")
            else:
                email = add_email or input("Email for the new key: ").strip()
                identity = format_identity(add_name, email)
                recipients[add_key] = identity
                logger.done(f"Added key for {identity}")

        # Handle --remove-key: remove a public key (by key, email, or identity)
        if remove_key:
            # Find the key to remove
            key_to_remove = None
            if remove_key.startswith("age"):
                # Remove by key
                if remove_key in recipients:
                    key_to_remove = remove_key
            else:
                # Remove by email or identity match
                for key, identity in recipients.items():
                    # Match exact identity or just the email part
                    _, stored_email = parse_identity(identity)
                    if identity == remove_key or stored_email == remove_key:
                        key_to_remove = key
                        break

            if key_to_remove:
                # Prevent removing the last decryptor
                if len(recipients) == 1:
                    logger.fail("Cannot remove the last recipient!")
                    logger.info("This would make all secrets permanently unrecoverable.")
                    logger.info("Add another recipient first, then remove this one.")
                    sys.exit(1)

                del recipients[key_to_remove]
                logger.done(f"Removed key: {remove_key}")
            else:
                logger.warning(f"Key not found: {remove_key}")

        # Validate we have recipients
        if not recipients:
            logger.fail("No public keys found in .sops.yaml")
            sys.exit(1)

        # Update .sops.yaml with new keys
        manager.save_config(recipients)
        logger.done("Updated .sops.yaml configuration")

        logger.info(f"Re-encrypting for {len(recipients)} recipient(s)")

        # Determine which modes to re-encrypt (only public modes)
        modes_to_rotate = list(Mode.public()) if environment == "all" else [Mode(environment)]

        # Re-encrypt each public secret
        results = manager.rotate_all_secrets(modes_to_rotate)
        for mode, error in results.items():
            if error is None:
                logger.done(f"Re-encrypted {mode.value}")
            else:
                logger.fail(f"Failed to re-encrypt {mode.value}: {error}")

        logger.info("\nDon't forget to commit the updated secrets files!")

    except ProtectedFileError as e:
        logger.fail(str(e))
        sys.exit(1)


@secrets.command("protect")
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to age key file to protect",
)
@djb_pass_context
def protect(cli_ctx: CliContext, key_path: Path | None):
    """Enable GPG protection for the age private key.

    Encrypts the age private key using your GPG public key.
    GPG agent caches the private key passphrase for decryption.

    After protection:
    - The plaintext .age/keys.txt is replaced with .age/keys.txt.gpg
    - All secrets operations automatically decrypt/re-encrypt the key
    - GPG agent caches the passphrase for the session

    \b
    Example:
        djb secrets protect
    """
    if not _ensure_prerequisites(cli_ctx):
        sys.exit(1)

    # Ensure GPG is configured with a key
    if not _ensure_gpg_setup(cli_ctx):
        sys.exit(1)

    if key_path is None:
        key_path = get_default_key_path(cli_ctx.config.project_dir)

    if not key_path.exists():
        # Check if already protected
        encrypted_path = key_path.parent / (key_path.name + ".gpg")
        if encrypted_path.exists():
            logger.info("Age key is already GPG protected")
            return
        logger.fail(f"Age key not found at {key_path}")
        logger.info("Run 'djb init' first.")
        sys.exit(1)

    project_dir = cli_ctx.config.project_dir
    if is_age_key_protected(project_dir, cli_ctx.runner):
        logger.info("Age key is already GPG protected")
        return

    if not check_gpg_installed():
        logger.fail("GPG is not installed")
        logger.info("Install with: brew install gnupg")
        sys.exit(1)

    try:
        protect_age_key(project_dir, cli_ctx.runner)
        logger.done("Protected age key with GPG encryption")
        logger.info(f"Encrypted key at: {key_path.parent / (key_path.name + '.gpg')}")
    except GpgError as e:
        logger.fail(f"Failed to protect key: {e}")
        sys.exit(1)


@secrets.command("unprotect")
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to GPG-encrypted age key file",
)
@djb_pass_context
def unprotect(cli_ctx: CliContext, key_path: Path | None):
    """Remove GPG protection from the age private key.

    Decrypts the GPG-protected key back to plaintext.
    Use this for troubleshooting or if you want to disable GPG protection.

    \b
    Example:
        djb secrets unprotect
    """
    project_dir = cli_ctx.config.project_dir
    if key_path is None:
        key_path = get_default_key_path(project_dir)

    if not is_age_key_protected(project_dir, cli_ctx.runner):
        logger.info("Age key is not GPG protected")
        return

    try:
        unprotect_age_key(project_dir, cli_ctx.runner)
        logger.done("Removed GPG protection from age key")
        logger.info(f"Plaintext key at: {key_path}")
    except GpgError as e:
        logger.fail(f"Failed to unprotect key: {e}")
        sys.exit(1)

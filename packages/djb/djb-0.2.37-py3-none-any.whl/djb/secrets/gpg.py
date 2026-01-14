"""
GPG encryption operations for protecting sensitive files.

Provides GPG public key encryption for age keys and other sensitive files.
The user's GPG key (identified by email) is used for encryption, and the
GPG agent caches the private key passphrase for decryption.

Key features:
- Public key encryption (uses recipient's GPG key)
- GPG agent handles passphrase caching automatically
- TTY handling for pinentry (GPG_TTY must be set)
- State detection (is file encrypted or not?)
- Atomic file operations
- Subprocess timeouts to prevent hanging
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from djb.core.cmd_runner import CmdRunner, CmdTimeout
from djb.core.logging import get_logger

logger = get_logger(__name__)

# Default timeout for non-interactive GPG operations (in seconds)
# Used for operations that don't require user input (key listing, encryption, etc.)
GPG_TIMEOUT = 5

# Timeout for interactive GPG operations (in seconds)
# Used for operations that may require passphrase entry via pinentry
# Set to 5 minutes to give users time to enter their passphrase
GPG_INTERACTIVE_TIMEOUT = 300

# Default GPG agent configuration for secrets management
_GPG_AGENT_CONFIG = """\
# Cache passphrases for 8 hours (28800 seconds)
default-cache-ttl 28800
max-cache-ttl 28800

# Allow loopback pinentry mode for programmatic passphrase entry.
# This allows GPG to prompt for passphrases directly via stdin/stdout
# instead of spawning a separate pinentry process, which is more reliable
# in nested process chains and non-standard terminal environments.
allow-loopback-pinentry
"""


class GpgError(Exception):
    """Error from GPG command."""


class GpgTimeoutError(GpgError):
    """GPG operation timed out, typically waiting for passphrase entry.

    This error indicates that a GPG operation (usually decryption) exceeded
    the timeout while waiting for user input. This commonly happens when:
    - The user took too long to enter their passphrase
    - The pinentry dialog was dismissed without entering a passphrase
    - The GPG agent is unresponsive

    Attributes:
        timeout: The timeout value in seconds that was exceeded.
        operation: Description of the operation that timed out.
    """

    def __init__(self, timeout: float, operation: str = "GPG operation"):
        self.timeout = timeout
        self.operation = operation
        super().__init__(
            f"{operation} timed out after {timeout} seconds.\n\n"
            f"This usually means:\n"
            f"  • You didn't enter your GPG passphrase in time\n"
            f"  • The passphrase dialog was dismissed\n"
            f"  • The GPG agent is unresponsive\n\n"
            f"Please try again and enter your passphrase when prompted."
        )


def check_gpg_installed() -> bool:
    """Check if GPG is installed and available."""
    return shutil.which("gpg") is not None


def get_gpg_key_id(runner: CmdRunner, email: str) -> str | None:
    """Get the GPG key ID for an email address.

    Args:
        runner: Command runner instance.
        email: Email address associated with the GPG key.

    Returns:
        The key ID if found, None otherwise.
    """
    try:
        result = runner.run(
            ["gpg", "--list-secret-keys", "--with-colons", email],
            timeout=GPG_TIMEOUT,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("sec:"):
                    parts = line.split(":")
                    if len(parts) > 4:
                        return parts[4]
    except (CmdTimeout, FileNotFoundError):
        pass
    return None


def get_default_gpg_email(runner: CmdRunner) -> str | None:
    """Get the email from the user's default GPG key.

    Args:
        cmd_runner: Command runner instance.

    Returns:
        The email address if found, None otherwise.
    """
    try:
        result = runner.run(
            ["gpg", "--list-secret-keys", "--with-colons"],
            timeout=GPG_TIMEOUT,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("uid:"):
                    parts = line.split(":")
                    if len(parts) > 9:
                        # UID format: "Name <email>"
                        uid = parts[9]
                        if "<" in uid and ">" in uid:
                            return uid.split("<")[1].split(">")[0]
    except (CmdTimeout, FileNotFoundError):
        pass
    return None


def has_gpg_secret_key(runner: CmdRunner) -> bool:
    """Check if the user has any GPG secret keys.

    Args:
        cmd_runner: Command runner instance.

    Returns:
        True if at least one secret key exists.
    """
    try:
        result = runner.run(
            ["gpg", "--list-secret-keys", "--with-colons"],
            timeout=GPG_TIMEOUT,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("sec:"):
                    return True
    except (CmdTimeout, FileNotFoundError):
        pass
    return False


def get_gpg_home() -> Path:
    """Get the GPG home directory.

    Returns:
        Path to GPG home directory (~/.gnupg by default).
    """
    gnupghome = os.environ.get("GNUPGHOME")
    if gnupghome:
        return Path(gnupghome)
    return Path.home() / ".gnupg"


def init_gpg_agent_config(runner: CmdRunner) -> bool:
    """Initialize GPG agent configuration with sensible defaults.

    Creates ~/.gnupg/gpg-agent.conf with passphrase caching settings
    if it doesn't already exist. Does nothing if the user already has
    a custom configuration.

    Args:
        cmd_runner: Command runner instance.

    Returns:
        True if config was created, False if it already exists.
    """
    gpg_home = get_gpg_home()
    config_path = gpg_home / "gpg-agent.conf"

    if config_path.exists():
        # User has existing config, don't touch it
        return False

    # Create .gnupg directory if needed
    gpg_home.mkdir(mode=0o700, parents=True, exist_ok=True)

    # Write default config
    config_path.write_text(_GPG_AGENT_CONFIG)
    config_path.chmod(0o600)

    # Reload GPG agent to pick up new config
    try:
        runner.run(["gpgconf", "--reload", "gpg-agent"], timeout=GPG_TIMEOUT)
    except (CmdTimeout, FileNotFoundError, OSError):
        pass

    return True


def ensure_loopback_pinentry(runner: CmdRunner) -> bool:
    """Ensure gpg-agent allows loopback pinentry mode.

    Loopback mode is required for GPG to prompt for passphrases directly via
    stdin/stdout instead of spawning a separate pinentry process. This is more
    reliable in nested process chains and non-standard terminal environments.

    If the gpg-agent.conf already contains allow-loopback-pinentry, does nothing.
    If not, appends the option and reloads the agent.

    Args:
        runner: Command runner instance.

    Returns:
        True if config was modified, False if already configured or no config exists.
    """
    gpg_home = get_gpg_home()
    config_path = gpg_home / "gpg-agent.conf"

    if not config_path.exists():
        # No config exists - init_gpg_agent_config should be called first
        # Just create a minimal config with loopback enabled
        gpg_home.mkdir(mode=0o700, parents=True, exist_ok=True)
        config_path.write_text("allow-loopback-pinentry\n")
        config_path.chmod(0o600)
        try:
            runner.run(["gpgconf", "--reload", "gpg-agent"], timeout=GPG_TIMEOUT)
        except (CmdTimeout, FileNotFoundError, OSError):
            pass
        return True

    # Check if loopback is already enabled
    config_content = config_path.read_text()
    if "allow-loopback-pinentry" in config_content:
        return False

    # Append loopback option to existing config
    with config_path.open("a") as f:
        f.write("\n# Added by djb for reliable passphrase entry\n")
        f.write("allow-loopback-pinentry\n")

    # Reload GPG agent to pick up new config
    try:
        runner.run(["gpgconf", "--reload", "gpg-agent"], timeout=GPG_TIMEOUT)
    except (CmdTimeout, FileNotFoundError, OSError):
        pass

    return True


def generate_gpg_key(runner: CmdRunner, name: str, email: str) -> bool:
    """Generate a new GPG keypair for the user.

    Creates a GPG key using modern defaults (Ed25519 for signing,
    Curve25519 for encryption) with no expiration.

    Args:
        runner: Command runner instance.
        name: User's full name.
        email: User's email address.

    Returns:
        True if key was generated successfully.

    Raises:
        GpgError: If key generation fails or times out.
    """
    env = setup_gpg_tty(runner)

    # Use GPG's quick-generate-key for modern defaults
    # This creates an Ed25519 signing key with a Curve25519 encryption subkey
    # Key generation can take a while (entropy collection), use longer timeout
    try:
        result = runner.run(
            [
                "gpg",
                "--batch",
                "--quick-generate-key",
                f"{name} <{email}>",
                "default",
                "default",
                "never",  # No expiration
            ],
            env=env,
            timeout=GPG_TIMEOUT,
        )
    except CmdTimeout as e:
        raise GpgError(
            f"GPG key generation timed out after {GPG_TIMEOUT}s. "
            f"This may indicate a problem with entropy collection."
        ) from e

    if result.returncode != 0:
        raise GpgError(f"Failed to generate GPG key: {result.stderr}")

    return True


def setup_gpg_tty(runner: CmdRunner) -> dict[str, str]:
    """Set up GPG_TTY environment variable for pinentry.

    GPG (pinentry) requires GPG_TTY to be set to the current tty.
    Without this, gpg commands will fail with misleading error messages.

    Also updates the GPG agent to use the current TTY, which is necessary
    when running in nested process chains where the agent may have cached
    a different TTY.

    Args:
        cmd_runner: Command runner instance.

    Returns:
        Environment dict with GPG_TTY set appropriately.
    """
    # Determine the TTY to use
    # First check existing GPG_TTY, then try to get actual tty name
    gpg_tty = os.environ.get("GPG_TTY")

    if not gpg_tty:
        # Try to get actual tty name by opening /dev/tty
        try:
            tty_fd = os.open("/dev/tty", os.O_RDONLY)
            try:
                gpg_tty = os.ttyname(tty_fd)
            finally:
                os.close(tty_fd)
        except OSError:
            # Fallback to /dev/tty if we can't get the actual name
            gpg_tty = "/dev/tty"

    env = {"GPG_TTY": gpg_tty}

    # Update GPG agent to use the current TTY.
    # This is critical when running in nested process chains (like Click's
    # ctx.invoke) where the agent may have cached a different TTY.
    try:
        runner.run(
            ["gpg-connect-agent", "updatestartuptty", "/bye"],
            env=env,
            timeout=GPG_TIMEOUT,
        )
    except (CmdTimeout, FileNotFoundError):
        # If gpg-connect-agent isn't available, continue anyway
        pass

    return env


def is_gpg_encrypted(runner: CmdRunner, file_path: Path) -> bool:
    """Check if a file is GPG-encrypted.

    Uses `gpg --list-packets` to detect GPG encryption markers.
    For symmetric encryption (passphrase-based), GPG may return non-zero
    because it tries to decrypt, so we check the output for packet markers
    rather than relying on the return code.

    Note: We check both stdout and stderr because GPG outputs packet
    information to stdout but may output warnings/errors to stderr,
    and the encryption markers can appear in either stream depending
    on the GPG version and file state.

    Args:
        runner: Command runner instance.
        file_path: Path to the file to check.

    Returns:
        True if the file appears to be GPG-encrypted.
    """
    if not file_path.exists():
        return False

    try:
        result = runner.run(
            ["gpg", "--list-packets", str(file_path)],
            timeout=GPG_TIMEOUT,
        )
        # Check output for GPG encryption markers (works for both symmetric
        # and public key encryption, regardless of return code)
        output = result.stdout + result.stderr
        return ":symkey enc packet:" in output or ":pubkey enc packet:" in output
    except (CmdTimeout, FileNotFoundError):
        return False


def gpg_encrypt_file(
    runner: CmdRunner,
    input_path: Path,
    output_path: Path | None = None,
    armor: bool = True,
    recipient: str | None = None,
) -> Path:
    """Encrypt a file with GPG public key encryption.

    Uses the recipient's GPG public key for encryption. No passphrase is
    needed for encryption - the private key (and its passphrase) is only
    needed for decryption, where GPG agent handles caching.

    Args:
        runner: Command runner instance.
        input_path: Path to plaintext file.
        output_path: Path for encrypted output (default: replaces input file).
        armor: Use ASCII armor output (default: True for text files).
        recipient: Email/key ID for encryption (default: user's default key).

    Returns:
        Path to the encrypted file.

    Raises:
        GpgError: If encryption fails, times out, or no GPG key found.
    """
    if output_path is None:
        output_path = input_path

    # Get recipient if not specified
    if recipient is None:
        recipient = get_default_gpg_email(runner)
        if recipient is None:
            raise GpgError("No GPG key found. Create one with: gpg --gen-key")

    env = setup_gpg_tty(runner)

    # Use a temp file for atomic operation
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    # Public key encryption - no passphrase needed
    cmd = ["gpg", "--encrypt", "--yes", "--batch", "--recipient", recipient]
    if armor:
        cmd.append("--armor")
    cmd.extend(["--output", str(temp_path), str(input_path)])

    try:
        result = runner.run(cmd, env=env, timeout=GPG_TIMEOUT)
    except CmdTimeout:
        # Clean up temp file on timeout
        if temp_path.exists():
            temp_path.unlink()
        raise GpgError(
            f"GPG encryption timed out after {GPG_TIMEOUT}s. " f"GPG agent may be unresponsive."
        )

    if result.returncode != 0:
        # Clean up temp file on failure
        if temp_path.exists():
            temp_path.unlink()
        raise GpgError(f"GPG encryption failed: {result.stderr}")

    # Atomic rename
    temp_path.rename(output_path)

    return output_path


def gpg_decrypt_file(
    runner: CmdRunner,
    input_path: Path,
    output_path: Path | None = None,
) -> str:
    """Decrypt a GPG-encrypted file.

    For public key encrypted files, GPG agent handles passphrase caching
    automatically. The first decryption prompts for the private key passphrase,
    subsequent decryptions within the cache TTL use the cached passphrase.

    Uses loopback pinentry mode for reliable passphrase entry. This is necessary
    because GPG's default pinentry spawns as a child of gpg-agent (a daemon),
    which can't access PTYs created by the calling process::

        Without loopback (broken):
        ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
        │ djb deploy  │────▶│ gpg command │────▶│  gpg-agent   │
        │   (PTY)     │     │             │     │   (daemon)   │
        └─────────────┘     └─────────────┘     └──────┬───────┘
               │                                       │
               │ Our PTY                               │ spawns
               ▼                                       ▼
          ┌─────────┐                            ┌──────────┐
          │ stdin   │ ◀──────── X ───────────────│ pinentry │
          │ stdout  │    Can't access PTY!       │          │
          └─────────┘                            └──────────┘

        With loopback (works):
        ┌─────────────┐     ┌─────────────┐
        │ djb deploy  │────▶│ gpg command │
        │   (PTY)     │     │  (loopback) │
        └─────────────┘     └─────────────┘
               │                   │
               │ Our PTY           │ Prompts directly
               ▼                   ▼
          ┌─────────┐         ┌─────────┐
          │ stdin   │◀────────│ GPG I/O │
          │ stdout  │────────▶│         │
          └─────────┘         └─────────┘

    Args:
        runner: Command runner instance.
        input_path: Path to encrypted file.
        output_path: Path for decrypted output (if None, returns content).

    Returns:
        Decrypted content as string (if output_path is None).

    Raises:
        GpgError: If decryption fails or times out.
    """
    # Ensure loopback pinentry is allowed in gpg-agent config
    ensure_loopback_pinentry(runner)

    env = setup_gpg_tty(runner)

    # Use loopback pinentry mode so GPG prompts directly via stdin/stdout
    # instead of spawning a separate pinentry process. This is more reliable
    # in nested process chains and non-standard terminal environments.
    # Requires 'allow-loopback-pinentry' in gpg-agent.conf (set by init_gpg_agent_config).
    cmd = ["gpg", "--decrypt", "--quiet", "--pinentry-mode", "loopback"]
    if output_path:
        cmd.extend(["--output", str(output_path)])
    cmd.append(str(input_path))

    try:
        if output_path:
            # Output goes to file - use interactive mode for GPG to display prompts
            # and read passphrase from terminal (loopback mode)
            result = runner.run(cmd, env=env, interactive=True)

            if result.returncode != 0:
                raise GpgError("GPG decryption failed")

            # Set secure permissions on decrypted file
            output_path.chmod(0o600)
            return ""
        else:
            # Need to capture stdout - interactive mode gives TTY access for
            # passphrase input while capturing output (stderr is empty for PTY)
            result = runner.run(cmd, env=env, interactive=True)

            if result.returncode != 0:
                raise GpgError(f"GPG decryption failed: {result.stdout}")

            return result.stdout
    except CmdTimeout as e:
        raise GpgTimeoutError(timeout=e.timeout, operation="GPG decryption") from e

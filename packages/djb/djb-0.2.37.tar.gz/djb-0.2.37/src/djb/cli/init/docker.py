"""djb init docker - Configure Docker for development.

On macOS, uses Colima (lightweight Docker runtime) instead of Docker Desktop.
On Linux/WSL2, uses native Docker with systemctl.

Cross-platform builds:
  Sets up QEMU emulation and Docker buildx for building linux/amd64 images
  on ARM Macs. This is required for deploying to x86_64 cloud servers.

  Architecture (macOS with Colima):

  1. docker-buildx CLI plugin (host, via Homebrew):
     - Provides `docker buildx` command on macOS
     - Communicates with Docker daemon running inside Colima VM
     - Installed via: brew install docker-buildx
     - Config: ~/.docker/config.json cliPluginsExtraDirs

  2. QEMU emulators (inside Colima VM):
     - Installed via tonistiigi/binfmt container
     - Enables Linux kernel to execute foreign architecture binaries
     - Required for BuildKit to run x86_64 commands during image build

  3. docker-container driver builder:
     - Created on host with `docker buildx create --driver docker-container`
     - Uses BuildKit container with full cross-platform support
     - More reliable than default docker driver for cross-arch builds
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import click

from djb.cli.context import djb_pass_context
from djb.cli.init.shared import InitContext
from djb.core.cmd_runner import CmdRunner, CmdTimeout
from djb.core.logging import get_logger

logger = get_logger(__name__)

# How long to wait for Docker daemon to start (seconds)
DOCKER_START_TIMEOUT = 60

# Buildx builder name for multi-arch builds
BUILDX_BUILDER_NAME = "djb-multiarch"


def is_wsl2() -> bool:
    """Check if running under WSL2."""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except (FileNotFoundError, PermissionError):
        return False


def check_colima_installed(runner: CmdRunner) -> bool:
    """Check if Colima is installed (macOS only)."""
    result = runner.run(["which", "colima"])
    return result.returncode == 0


def check_colima_running(runner: CmdRunner) -> bool:
    """Check if Colima VM is running."""
    try:
        result = runner.run(["colima", "status"], timeout=10)
        return result.returncode == 0
    except CmdTimeout:
        return False


def _stop_colima(runner: CmdRunner) -> bool:
    """Force stop Colima VM."""
    try:
        result = runner.run(["colima", "stop", "-f"], timeout=30)
        return result.returncode == 0
    except CmdTimeout:
        return False


def _delete_colima(runner: CmdRunner) -> bool:
    """Force delete Colima VM (destroys all images/volumes)."""
    try:
        result = runner.run(["colima", "delete", "-f"], timeout=30)
        return result.returncode == 0
    except CmdTimeout:
        return False


def _wait_for_docker(runner: CmdRunner, timeout: int = 30) -> bool:
    """Wait for Docker daemon to become accessible."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_docker_running(runner):
            return True
        time.sleep(1)
    return False


def check_docker_installed(runner: CmdRunner) -> bool:
    """Check if Docker CLI is installed."""
    result = runner.run(["which", "docker"])
    return result.returncode == 0


def check_docker_running(runner: CmdRunner) -> bool:
    """Check if Docker daemon is running and accessible."""
    try:
        result = runner.run(["docker", "info"], timeout=10)
        return result.returncode == 0
    except CmdTimeout:
        return False


def install_docker_macos(runner: CmdRunner) -> bool:
    """Install Colima, Docker CLI, and buildx on macOS via Homebrew.

    Returns:
        True if installation succeeded or already installed.
    """
    if check_colima_installed(runner) and check_docker_installed(runner):
        logger.info("Colima and Docker CLI already installed")
        # Still ensure buildx is installed
        _ensure_buildx_cli_installed(runner)
        return True

    logger.next("Installing Colima, Docker CLI, and buildx via Homebrew")

    # docker-buildx provides the buildx CLI plugin for cross-platform builds
    packages = ["colima", "docker", "docker-compose", "docker-buildx"]
    result = runner.run(["brew", "install", *packages])
    if result.returncode != 0:
        logger.error(f"Failed to install Docker tools: {result.stderr}")
        return False

    logger.done("Colima and Docker CLI installed")
    return True


def _ensure_buildx_cli_installed(runner: CmdRunner) -> bool:
    """Ensure docker-buildx CLI plugin is installed on macOS.

    Returns:
        True if buildx is available.
    """
    # Check if buildx command works
    result = runner.run(["docker", "buildx", "version"], timeout=5)
    if result.returncode == 0:
        return True

    # Install via Homebrew
    logger.next("Installing docker-buildx CLI plugin")
    result = runner.run(["brew", "install", "docker-buildx"])
    if result.returncode != 0:
        logger.warning("Failed to install docker-buildx")
        return False

    # Configure Docker to find the plugin
    # The Homebrew formula installs to /opt/homebrew/lib/docker/cli-plugins
    docker_config_path = Path.home() / ".docker" / "config.json"
    plugins_dir = "/opt/homebrew/lib/docker/cli-plugins"

    try:
        docker_config_path.parent.mkdir(parents=True, exist_ok=True)

        if docker_config_path.exists():
            config = json.loads(docker_config_path.read_text())
        else:
            config = {}

        # Add cliPluginsExtraDirs if not present
        extra_dirs = config.get("cliPluginsExtraDirs", [])
        if plugins_dir not in extra_dirs:
            extra_dirs.append(plugins_dir)
            config["cliPluginsExtraDirs"] = extra_dirs
            docker_config_path.write_text(json.dumps(config, indent=2))
            logger.info(f"Configured Docker to use plugins from {plugins_dir}")

        logger.done("docker-buildx installed")
        return True
    except Exception as e:
        logger.warning(f"Failed to configure Docker plugins directory: {e}")
        return False


def install_docker_linux(runner: CmdRunner) -> bool:
    """Check Docker installation on Linux/WSL2.

    Returns:
        True if Docker is installed.
    """
    if check_docker_installed(runner):
        logger.info("Docker CLI already installed")
        return True

    logger.error("Docker is not installed")
    if is_wsl2():
        logger.info("To install Docker on WSL2:")
        logger.info("  sudo apt update && sudo apt install docker.io docker-compose")
        logger.info("  sudo usermod -aG docker $USER")
        logger.info("  (Log out and back in for group changes to take effect)")
    else:
        logger.info("To install Docker on Linux:")
        logger.info("  Ubuntu/Debian: sudo apt install docker.io docker-compose")
        logger.info("  Fedora: sudo dnf install docker docker-compose")
        logger.info("  Then: sudo usermod -aG docker $USER")
    return False


def start_docker_daemon(runner: CmdRunner) -> bool:
    """Start Docker daemon.

    On macOS: starts Colima VM
    On Linux: starts systemd docker service

    Returns:
        True if Docker is running after this call.
    """
    if check_docker_running(runner):
        logger.info("Docker daemon already running")
        return True

    if sys.platform == "darwin":
        return _start_colima(runner)
    else:
        return _start_docker_linux(runner)


def _try_colima_start(runner: CmdRunner) -> bool:
    """Single attempt to start Colima and wait for Docker."""
    try:
        result = runner.run(["colima", "start"], timeout=120)  # First start can be slow
        if result.returncode != 0:
            return False
        return _wait_for_docker(runner)
    except CmdTimeout:
        return False


def _start_colima(runner: CmdRunner) -> bool:
    """Start Colima on macOS with automatic recovery."""
    if not check_colima_installed(runner):
        logger.error("Colima not installed. Run: brew install colima")
        return False

    # Attempt 1: Normal start
    logger.next("Starting Colima")
    if _try_colima_start(runner):
        logger.done("Colima started")
        return True

    # Attempt 2: Stop + start
    logger.warning("Colima start failed, attempting recovery...")
    logger.next("Stopping Colima")
    _stop_colima(runner)
    logger.next("Starting Colima (retry)")
    if _try_colima_start(runner):
        logger.done("Colima started")
        return True

    # Attempt 3: Delete + start (prompt first)
    logger.warning("Recovery failed. Colima VM may be corrupted.")
    if click.confirm(
        "Delete and recreate Colima VM? (This will remove all cached images/volumes)",
        default=True,
    ):
        logger.next("Deleting Colima VM")
        _delete_colima(runner)
        logger.next("Starting Colima (fresh)")
        if _try_colima_start(runner):
            logger.done("Colima started")
            return True

    logger.error("Failed to start Colima after all recovery attempts")
    return False


def _start_docker_linux(runner: CmdRunner) -> bool:
    """Start Docker daemon on Linux/WSL2."""
    logger.next("Starting Docker daemon")

    result = runner.run(["sudo", "systemctl", "start", "docker"])
    if result.returncode != 0:
        logger.error(f"Failed to start Docker: {result.stderr}")
        logger.info("You may need to install Docker first")
        return False

    # Wait for Docker to be ready
    start_time = time.time()
    while time.time() - start_time < DOCKER_START_TIMEOUT:
        if check_docker_running(runner):
            logger.done("Docker daemon started")
            return True
        time.sleep(1)

    logger.error(f"Docker did not become ready within {DOCKER_START_TIMEOUT}s")
    return False


def configure_docker_autostart(runner: CmdRunner) -> bool:
    """Configure Docker to start automatically on login/boot.

    On macOS: uses brew services for Colima
    On Linux: uses systemctl enable

    Returns:
        True if configuration succeeded.
    """
    if sys.platform == "darwin":
        return _configure_colima_autostart(runner)
    else:
        return _configure_docker_linux_autostart(runner)


def _is_colima_autostart_configured(runner: CmdRunner) -> bool:
    """Check if Colima is already configured to start on login."""
    result = runner.run(["brew", "services", "info", "colima"])
    # "Loaded: true" means plist is registered with launchd
    return "loaded: true" in result.stdout.lower()


def _try_brew_services_start(runner: CmdRunner) -> bool:
    """Try to start colima via brew services."""
    result = runner.run(["brew", "services", "start", "colima"])
    if result.returncode == 0:
        return True
    # Already started is also success
    if "already started" in (result.stdout + result.stderr).lower():
        return True
    return False


def _brew_services_stop(runner: CmdRunner) -> None:
    """Stop colima via brew services."""
    runner.run(["brew", "services", "stop", "colima"])


def _brew_services_restart(runner: CmdRunner) -> bool:
    """Restart colima via brew services."""
    result = runner.run(["brew", "services", "restart", "colima"])
    return result.returncode == 0


def _configure_colima_autostart(runner: CmdRunner) -> bool:
    """Configure Colima to start on login via brew services."""
    # Check if already configured (plist already loaded)
    if _is_colima_autostart_configured(runner):
        logger.info("Colima already configured to start on login")
        return True

    logger.next("Configuring Colima to start on login")

    # Attempt 1: Normal start
    if _try_brew_services_start(runner):
        logger.done("Colima configured to start on login")
        return True

    # Attempt 2: Stop + start (clears stale launchd state)
    logger.warning("Autostart failed, attempting recovery...")
    _brew_services_stop(runner)
    if _try_brew_services_start(runner):
        logger.done("Colima configured to start on login")
        return True

    # Attempt 3: Restart (handles edge cases)
    if _brew_services_restart(runner):
        logger.done("Colima configured to start on login")
        return True

    logger.warning("Could not configure autostart")
    logger.info("You can manually run: brew services start colima")
    return False


def _configure_docker_linux_autostart(runner: CmdRunner) -> bool:
    """Configure Docker to start on boot via systemctl."""
    logger.next("Enabling Docker to start on boot")

    result = runner.run(["sudo", "systemctl", "enable", "docker"])

    if result.returncode == 0:
        logger.done("Docker enabled to start on boot")
        return True
    else:
        logger.warning(f"Could not enable Docker autostart: {result.stderr}")
        return False


def _check_qemu_installed(runner: CmdRunner) -> bool:
    """Check if QEMU emulators are installed for cross-platform builds."""
    if sys.platform == "darwin":
        # On macOS with Colima, check inside the VM
        result = runner.run(
            ["colima", "ssh", "--", "cat", "/proc/sys/fs/binfmt_misc/qemu-x86_64"],
            timeout=10,
        )
        return result.returncode == 0 and "enabled" in result.stdout.lower()
    else:
        # On Linux, check directly
        result = runner.run(
            ["cat", "/proc/sys/fs/binfmt_misc/qemu-x86_64"],
            timeout=10,
        )
        return result.returncode == 0 and "enabled" in result.stdout.lower()


def _install_qemu_emulators(runner: CmdRunner) -> bool:
    """Install QEMU emulators for cross-platform Docker builds.

    Uses the tonistiigi/binfmt image to install QEMU handlers for
    running binaries from different architectures.

    Returns:
        True if QEMU emulators are installed and ready.
    """
    if _check_qemu_installed(runner):
        logger.info("QEMU emulators already installed")
        return True

    logger.next("Installing QEMU emulators for cross-platform builds")

    if sys.platform == "darwin":
        # On macOS, run inside Colima VM
        result = runner.run(
            [
                "colima",
                "ssh",
                "--",
                "docker",
                "run",
                "--privileged",
                "--rm",
                "tonistiigi/binfmt",
                "--install",
                "all",
            ],
            timeout=120,
        )
    else:
        # On Linux, run directly
        result = runner.run(
            [
                "docker",
                "run",
                "--privileged",
                "--rm",
                "tonistiigi/binfmt",
                "--install",
                "all",
            ],
            timeout=120,
        )

    if result.returncode == 0:
        logger.done("QEMU emulators installed")
        return True
    else:
        logger.warning(f"Failed to install QEMU emulators: {result.stderr}")
        return False


def _check_buildx_builder_exists(runner: CmdRunner) -> bool:
    """Check if our multi-arch buildx builder exists.

    Runs from host - buildx CLI communicates with Docker daemon (in Colima on macOS).
    """
    result = runner.run(["docker", "buildx", "ls"], timeout=10)
    return BUILDX_BUILDER_NAME in result.stdout


def _setup_buildx_builder(runner: CmdRunner) -> bool:
    """Set up a Docker buildx builder for multi-arch builds.

    Creates a buildx builder using docker-container driver that can build
    for linux/amd64 and linux/arm64. This is required for building x86_64
    images on ARM Macs.

    The builder is created from the host and uses the Docker daemon
    (running in Colima on macOS). The docker-container driver spawns a
    BuildKit container with proper QEMU support for cross-platform builds.

    Returns:
        True if builder is ready.
    """
    if _check_buildx_builder_exists(runner):
        logger.info(f"Buildx builder '{BUILDX_BUILDER_NAME}' already exists")
        return True

    logger.next("Setting up Docker buildx for multi-arch builds")

    # Create builder from host - it communicates with Docker daemon (Colima on macOS)
    # Use docker-container driver for reliable cross-platform builds
    result = runner.run(
        [
            "docker",
            "buildx",
            "create",
            "--name",
            BUILDX_BUILDER_NAME,
            "--platform",
            "linux/amd64,linux/arm64",
            "--driver",
            "docker-container",
            "--use",  # Make this the default builder
        ],
        timeout=30,
    )

    if result.returncode == 0:
        logger.done(f"Buildx builder '{BUILDX_BUILDER_NAME}' created and set as default")
        return True
    else:
        logger.warning(f"Failed to create buildx builder: {result.stderr}")
        return False


def setup_cross_platform_builds(runner: CmdRunner) -> bool:
    """Set up cross-platform Docker builds.

    Installs QEMU emulators and creates a buildx builder for building
    linux/amd64 images on ARM Macs or vice versa.

    Returns:
        True if cross-platform builds are ready.
    """
    logger.next("Setting up cross-platform Docker builds")

    # Step 1: Install QEMU emulators
    if not _install_qemu_emulators(runner):
        logger.warning("QEMU installation failed - cross-platform builds may not work")
        return False

    # Step 2: Create buildx builder
    if not _setup_buildx_builder(runner):
        logger.warning("Buildx setup failed - cross-platform builds may not work")
        return False

    logger.done("Cross-platform builds ready")
    return True


def setup_docker(runner: CmdRunner, *, skip: bool = False) -> None:
    """Full Docker setup: install, start, configure autostart, and cross-platform builds.

    Args:
        runner: Command runner instance.
        skip: If True, skip Docker setup entirely.
    """
    if skip:
        logger.skip("Docker setup")
        return

    logger.section("Docker Setup")

    # Step 1: Ensure Docker is installed
    if sys.platform == "darwin":
        if not install_docker_macos(runner):
            raise click.ClickException("Failed to install Colima/Docker")
    else:
        if not install_docker_linux(runner):
            raise click.ClickException("Docker is required but not installed")

    # Step 2: Start Docker daemon
    if not start_docker_daemon(runner):
        raise click.ClickException("Failed to start Docker daemon")

    # Step 3: Configure autostart
    configure_docker_autostart(runner)

    # Step 4: Set up cross-platform builds (QEMU + buildx)
    setup_cross_platform_builds(runner)

    logger.done("Docker is ready")


@click.command("docker")
@click.option("--no-autostart", is_flag=True, help="Don't configure Docker to start on login")
@click.option("--no-buildx", is_flag=True, help="Skip cross-platform build setup (QEMU/buildx)")
@djb_pass_context(InitContext)
@click.pass_context
def docker(ctx: click.Context, init_ctx: InitContext, no_autostart: bool, no_buildx: bool) -> None:
    """Set up Docker for development.

    On macOS, installs and configures Colima (a lightweight Docker runtime).
    On Linux/WSL2, uses native Docker with systemctl.

    \b
    Steps (macOS):
      1. Install Colima and Docker CLI via Homebrew
      2. Start Colima VM
      3. Configure Colima to start on login (unless --no-autostart)
      4. Set up QEMU and buildx for cross-platform builds (unless --no-buildx)

    \b
    Steps (Linux/WSL2):
      1. Check Docker installation (guides through manual install if needed)
      2. Start the Docker daemon
      3. Enable Docker on boot (unless --no-autostart)
      4. Set up QEMU and buildx for cross-platform builds (unless --no-buildx)

    \b
    Cross-platform builds:
      Required for building linux/amd64 images on ARM Macs for deployment
      to x86_64 cloud servers. Uses QEMU emulation with Docker buildx.
    """
    skip = init_ctx.skip_docker

    runner = init_ctx.runner

    if skip:
        logger.skip("Docker setup")
        return

    logger.section("Docker Setup")

    # Step 1: Ensure Docker is installed
    if sys.platform == "darwin":
        if not install_docker_macos(runner):
            raise click.ClickException("Failed to install Colima/Docker")
    else:
        if not install_docker_linux(runner):
            raise click.ClickException("Docker is required but not installed")

    # Step 2: Start Docker daemon
    if not start_docker_daemon(runner):
        raise click.ClickException("Failed to start Docker daemon")

    # Step 3: Configure autostart (unless disabled)
    if not no_autostart:
        configure_docker_autostart(runner)

    # Step 4: Set up cross-platform builds (unless disabled)
    if not no_buildx:
        setup_cross_platform_builds(runner)

    logger.done("Docker is ready")

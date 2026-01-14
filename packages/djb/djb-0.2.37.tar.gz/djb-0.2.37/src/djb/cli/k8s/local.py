"""
djb deploy k8s local - Local Skaffold-based development commands.

Provides local Kubernetes development with hot-reload using Skaffold.
Supports both k3d (fast, ~30s startup) and microk8s (production-like).

Key Features:
- Cluster lifecycle management (create, delete, status)
- Skaffold dev loop with file sync for hot reload
- One-time build and deploy for testing
- Shell access to running pods

Workflow:
1. djb deploy k8s local cluster create  # Create cluster (once)
2. djb deploy k8s local dev             # Start dev loop
3. Edit Python/templates                # Changes sync instantly
4. Ctrl+C                               # Quit dev loop (keeps cluster)
5. djb deploy k8s local cluster delete  # Clean up when done
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from djb.buildpacks import BuildpackError
from djb.cli.context import CliContext, djb_pass_context
from djb.cli.docker import build_buildpacks_for_registry
from djb.cli.k8s.constants import (
    DEFAULT_DEV_PORT,
    DOCKER_CHECK_TIMEOUT,
    TOOL_AVAILABILITY_TIMEOUT,
)
from djb.core.cmd_runner import CmdRunner, CmdTimeout
from djb.core.logging import get_logger
from djb.k8s import (
    Addon,
    ClusterError,
    SkaffoldConfig,
    SkaffoldGenerator,
    get_cluster_provider,
)

logger = get_logger(__name__)


def _check_tool_available(runner: CmdRunner, tool: str) -> bool:
    """Check if a command-line tool is available."""
    try:
        return runner.check(["which", tool], timeout=TOOL_AVAILABILITY_TIMEOUT)
    except CmdTimeout:
        return False


def _check_docker_available(runner: CmdRunner) -> bool:
    """Check if Docker is available and daemon is running."""
    try:
        return runner.check(["docker", "info"], timeout=DOCKER_CHECK_TIMEOUT)
    except CmdTimeout:
        return False


@click.group("local")
def local():
    """Manage local Kubernetes development with Skaffold.

    Uses k3d or microk8s for local clusters with Skaffold for
    hot-reload development. Changes to Python, templates, and
    static files sync instantly to the running container.

    \b
    Workflow:
      djb deploy k8s local cluster create  # Create cluster (once)
      djb deploy k8s local dev             # Start dev with hot reload
      # Edit code - changes sync instantly!
      Ctrl+C                               # Stop dev loop
      djb deploy k8s local cluster delete  # Clean up when done
    """


# =============================================================================
# Cluster management commands
# =============================================================================


@local.group("cluster")
def cluster():
    """Manage local Kubernetes cluster lifecycle.

    Create, delete, and check status of local K8s clusters.
    Clusters persist across restarts for fast dev loop startup.
    """


@cluster.command("create")
@click.option(
    "--type",
    "cluster_type",
    type=click.Choice(["k3d", "microk8s"]),
    default="k3d",
    help="Cluster type: k3d (fast, default) or microk8s (production-like).",
)
@djb_pass_context
def cluster_create(cli_ctx: CliContext, cluster_type: str):
    """Create a local Kubernetes cluster.

    Creates a new cluster with:
    - Built-in container registry
    - Port forwarding for ingress
    - Required addons enabled

    The cluster persists until deleted with 'cluster delete'.

    \b
    Examples:
      djb deploy k8s local cluster create            # k3d (default)
      djb deploy k8s local cluster create --type microk8s
    """
    if not _check_docker_available(cli_ctx.runner):
        raise click.ClickException(
            "Docker is not available. Please ensure Docker Desktop or Colima is running.\n\n"
            "macOS: Run 'colima start' or open Docker Desktop\n"
            "Linux: Run 'sudo systemctl start docker'"
        )

    if cluster_type == "k3d" and not _check_tool_available(cli_ctx.runner, "k3d"):
        raise click.ClickException("k3d is not installed. Install with: brew install k3d")

    project_name = cli_ctx.config.project_name
    cluster_name = f"djb-{project_name}"

    logger.next(f"Creating {cluster_type} cluster '{cluster_name}'")

    try:
        provider = get_cluster_provider(cluster_type, cli_ctx.runner, cli_ctx.config)

        created = provider.create(cluster_name)
        if created:
            logger.done(f"Cluster '{cluster_name}' created")
        else:
            logger.info(f"Cluster '{cluster_name}' already exists")

        started = provider.start(cluster_name)
        if started:
            logger.done(f"Cluster '{cluster_name}' started")
        elif not created:
            logger.info(f"Cluster '{cluster_name}' already running")

        # Enable required addons
        addons = [Addon.DNS, Addon.REGISTRY]
        if cluster_type == "microk8s":
            addons.extend([Addon.STORAGE, Addon.INGRESS])
        logger.next("Enabling addons")
        provider.enable_addons(cluster_name, addons)
        logger.done("Addons enabled")

        logger.note()
        logger.info("Cluster is ready!")
        logger.tip("Start development with: djb deploy k8s local dev")

    except ClusterError as e:
        raise click.ClickException(str(e))


@cluster.command("delete")
@click.option(
    "--type",
    "cluster_type",
    type=click.Choice(["k3d", "microk8s"]),
    default="k3d",
    help="Cluster type to delete.",
)
@djb_pass_context
def cluster_delete(cli_ctx: CliContext, cluster_type: str):
    """Delete the local Kubernetes cluster.

    Destroys the cluster and all its state. This cannot be undone.
    """
    project_name = cli_ctx.config.project_name
    cluster_name = f"djb-{project_name}"

    try:
        provider = get_cluster_provider(cluster_type, cli_ctx.runner, cli_ctx.config)

        if not provider.exists(cluster_name):
            logger.info(f"Cluster '{cluster_name}' does not exist.")
            return

        if not cli_ctx.yes:
            if not click.confirm(
                f"This will destroy cluster '{cluster_name}' and all its data. Continue?",
                default=False,
            ):
                raise click.ClickException("Cancelled")

        logger.next(f"Deleting cluster '{cluster_name}'")
        provider.delete(cluster_name)
        logger.done("Cluster deleted")

    except ClusterError as e:
        raise click.ClickException(str(e))


@cluster.command("status")
@click.option(
    "--type",
    "cluster_type",
    type=click.Choice(["k3d", "microk8s"]),
    default="k3d",
    help="Cluster type to check.",
)
@djb_pass_context
def cluster_status(cli_ctx: CliContext, cluster_type: str):
    """Show status of the local Kubernetes cluster."""
    project_name = cli_ctx.config.project_name
    cluster_name = f"djb-{project_name}"

    try:
        provider = get_cluster_provider(cluster_type, cli_ctx.runner, cli_ctx.config)

        if not provider.exists(cluster_name):
            logger.info(f"Cluster '{cluster_name}' does not exist.")
            logger.tip("Create with: djb deploy k8s local cluster create")
            return

        running = provider.is_running(cluster_name)
        status_str = "running" if running else "stopped"

        logger.info(f"Cluster: {cluster_name}")
        logger.info(f"Type: {cluster_type}")
        logger.info(f"Status: {status_str}")
        logger.info(f"Registry: {provider.registry_address}")

        if running:
            logger.tip("Start development with: djb deploy k8s local dev")
        else:
            logger.tip("Start cluster with: djb deploy k8s local cluster create")

    except ClusterError as e:
        raise click.ClickException(str(e))


# =============================================================================
# Development commands
# =============================================================================


@local.command("dev")
@click.option(
    "--port",
    default=DEFAULT_DEV_PORT,
    help=f"Local port for port forwarding (default: {DEFAULT_DEV_PORT}).",
)
@click.option(
    "--trigger",
    type=click.Choice(["notify", "polling", "manual"]),
    default="notify",
    help="Skaffold trigger mode: notify (default), polling, or manual.",
)
@click.option(
    "--type",
    "cluster_type",
    type=click.Choice(["k3d", "microk8s"]),
    default="k3d",
    help="Cluster type (default: k3d).",
)
@djb_pass_context
def dev(cli_ctx: CliContext, port: int, trigger: str, cluster_type: str):
    """Start Skaffold dev loop with hot reload.

    Builds the container, deploys to the local cluster, and watches
    for file changes. Python, templates, and static files sync
    instantly to the running container without rebuilding.

    Press Ctrl+C to stop the dev loop. The cluster stays running
    for fast restart.

    \b
    Examples:
      djb deploy k8s local dev                # Start with defaults
      djb deploy k8s local dev --port 8080    # Custom port
      djb deploy k8s local dev --trigger polling  # Use polling
    """
    if not _check_docker_available(cli_ctx.runner):
        raise click.ClickException("Docker is not available.")

    if not _check_tool_available(cli_ctx.runner, "skaffold"):
        raise click.ClickException("Skaffold is not installed. Install with: brew install skaffold")

    project_name = cli_ctx.config.project_name
    cluster_name = f"djb-{project_name}"

    # Check cluster exists and is running
    try:
        provider = get_cluster_provider(cluster_type, cli_ctx.runner, cli_ctx.config)

        if not provider.exists(cluster_name):
            raise click.ClickException(
                f"Cluster '{cluster_name}' does not exist.\n"
                "Create with: djb deploy k8s local cluster create"
            )

        if not provider.is_running(cluster_name):
            raise click.ClickException(
                f"Cluster '{cluster_name}' is not running.\n"
                "Start with: djb deploy k8s local cluster create"
            )

    except ClusterError as e:
        raise click.ClickException(str(e))

    # Build buildpack chain
    try:
        buildpack_image = build_buildpacks_for_registry(
            cli_ctx=cli_ctx,
            registry=provider.registry_address,
        )
    except BuildpackError as e:
        raise click.ClickException(str(e))

    # Generate skaffold.yaml
    logger.next("Generating Skaffold configuration")
    skaffold_config = SkaffoldConfig(
        project_name=project_name,
        project_package=project_name,
        registry_address=provider.registry_address,
        buildpack_image=buildpack_image,
        local_port=port,
    )
    generator = SkaffoldGenerator()

    # Write to project root
    skaffold_path = cli_ctx.config.project_dir / "skaffold.yaml"
    generator.write(skaffold_config, skaffold_path)
    logger.done(f"Generated {skaffold_path}")

    # Start Skaffold dev
    logger.next("Starting Skaffold dev loop")
    logger.info(f"Port forwarding: localhost:{port}")
    logger.info("Watching for changes. Press Ctrl+C to exit.")
    logger.note()

    # Run Skaffold dev - replaces current process
    cmd = [
        "skaffold",
        "dev",
        "--port-forward",
        f"--trigger={trigger}",
    ]

    # Execute Skaffold - replaces current process, never returns
    cli_ctx.runner.exec(cmd)


@local.command("build")
@click.option(
    "--type",
    "cluster_type",
    type=click.Choice(["k3d", "microk8s"]),
    default="k3d",
    help="Cluster type (default: k3d).",
)
@djb_pass_context
def build(cli_ctx: CliContext, cluster_type: str):
    """Build and deploy to local cluster (one-time, no watch).

    Useful for testing the full build/deploy cycle without the
    continuous dev loop.
    """
    if not _check_docker_available(cli_ctx.runner):
        raise click.ClickException("Docker is not available.")

    if not _check_tool_available(cli_ctx.runner, "skaffold"):
        raise click.ClickException("Skaffold is not installed. Install with: brew install skaffold")

    project_name = cli_ctx.config.project_name
    cluster_name = f"djb-{project_name}"

    # Check cluster exists and is running
    try:
        provider = get_cluster_provider(cluster_type, cli_ctx.runner, cli_ctx.config)

        if not provider.is_running(cluster_name):
            raise click.ClickException(
                f"Cluster '{cluster_name}' is not running.\n"
                "Start with: djb deploy k8s local cluster create"
            )

    except ClusterError as e:
        raise click.ClickException(str(e))

    # Build buildpack chain
    try:
        buildpack_image = build_buildpacks_for_registry(
            cli_ctx=cli_ctx,
            registry=provider.registry_address,
        )
    except BuildpackError as e:
        raise click.ClickException(str(e))

    # Generate skaffold.yaml
    skaffold_config = SkaffoldConfig(
        project_name=project_name,
        project_package=project_name,
        registry_address=provider.registry_address,
        buildpack_image=buildpack_image,
    )
    generator = SkaffoldGenerator()

    skaffold_path = cli_ctx.config.project_dir / "skaffold.yaml"
    generator.write(skaffold_config, skaffold_path)

    # Run Skaffold build + deploy (one-time)
    cli_ctx.runner.run(
        ["skaffold", "run"],
        label="Building and deploying",
        show_output=True,
        fail_msg=click.ClickException("Build/deploy failed"),
        done_msg="Build and deploy complete",
    )


@local.command("shell")
@click.option(
    "--type",
    "cluster_type",
    type=click.Choice(["k3d", "microk8s"]),
    default="k3d",
    help="Cluster type (default: k3d).",
)
@djb_pass_context
def shell(cli_ctx: CliContext, cluster_type: str):
    """Open a shell in the running application pod.

    Equivalent to: kubectl exec -it <pod> -- /bin/bash
    """
    project_name = cli_ctx.config.project_name
    cluster_name = f"djb-{project_name}"

    try:
        provider = get_cluster_provider(cluster_type, cli_ctx.runner, cli_ctx.config)

        if not provider.is_running(cluster_name):
            raise click.ClickException(
                f"Cluster '{cluster_name}' is not running.\n"
                "Start with: djb deploy k8s local cluster create"
            )

        # Get the first pod for the deployment
        returncode, stdout, stderr = provider.kubectl(
            cluster_name,
            "get",
            "pods",
            "-l",
            f"app={project_name}",
            "-o",
            "jsonpath={.items[0].metadata.name}",
        )

        if returncode != 0 or not stdout.strip():
            raise click.ClickException(
                f"No running pods found for '{project_name}'.\n"
                "Start the app with: djb deploy k8s local dev"
            )

        pod_name = stdout.strip()
        logger.info(f"Connecting to pod: {pod_name}")

        # Get kubeconfig
        kubeconfig = provider.get_kubeconfig(cluster_name)

        # Write kubeconfig to temp file and exec into pod
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(kubeconfig)
            kubeconfig_path = f.name

        try:
            # Run interactive kubectl session
            cli_ctx.runner.run(
                [
                    "kubectl",
                    "--kubeconfig",
                    kubeconfig_path,
                    "exec",
                    "-it",
                    pod_name,
                    "--",
                    "/bin/bash",
                ],
                interactive=True,
            )
        finally:
            Path(kubeconfig_path).unlink(missing_ok=True)

    except ClusterError as e:
        raise click.ClickException(str(e))

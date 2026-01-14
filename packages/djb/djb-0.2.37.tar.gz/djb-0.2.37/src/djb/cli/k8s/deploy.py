"""
djb deploy k8s - Kubernetes deployment command.

Builds, pushes, and deploys the application to a Kubernetes cluster.

Deployment Workflow:
1. Pre-flight checks (SSH, microk8s status)
2. Build container image
3. Push to cluster registry
4. Sync secrets from djb secrets
5. Apply K8s manifests
6. Wait for rollout
7. Run migrations
8. Clean up old images (preserves buildpack cache)
9. Tag deployment in git

Dockerfile Resolution:
The build process looks for a Dockerfile in this order:
1. deployment/k8s/backend/Dockerfile.j2 (project template, rendered at build time)
2. deployment/k8s/backend/Dockerfile (non-template)
3. Copy djb template to deployment/k8s/backend/Dockerfile.j2

The .j2 template allows customization while still using Jinja2 variables
like {{ config.project_name }} for project-specific values.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

import click
import requests

from djb.buildpacks import LocalBuildpackChain, RemoteBuildpackChain
from djb.cli.domain import _sync_k8s_domains, domain_init
from djb.cli.utils import CmdRunner
from djb.ssh import SSHClient, SSHError
from djb.config import DjbConfig
from djb.core.logging import get_logger
from djb.types import DomainNameManager
from djb.k8s import (
    DatabaseCtx,
    DeploymentCtx,
    K8sManifestGenerator,
    MigrationCtx,
    SecretsCtx,
    render_template,
)
from djb.secrets import SecretsManager, find_placeholder_secrets
from djb.types import Mode

if TYPE_CHECKING:
    from djb.cli.k8s.k8s import CliK8sContext

logger = get_logger(__name__)


def _get_dockerfile(djb_config: DjbConfig, managed_dockerfile: bool) -> Path:
    """Resolve and render the Dockerfile for building.

    Uses render_template for project-first resolution:
    1. If Dockerfile exists in project → use it directly
    2. If Dockerfile.j2 exists in project → render it
    3. If managed_dockerfile is True → copy from djb, render, write both
    4. Otherwise → raise error

    Args:
        djb_config: DjbConfig for template variables and project_dir
        managed_dockerfile: If True, copy template from djb when not found

    Returns:
        Path to the Dockerfile (rendered if from .j2)

    Raises:
        click.ClickException: If Dockerfile not found and managed_dockerfile is False
    """
    project_dir = djb_config.project_dir
    backend_dir = project_dir / "deployment" / "k8s" / "backend"
    dockerfile_path = backend_dir / "Dockerfile"
    template_path = backend_dir / "Dockerfile.j2"

    # Check if any Dockerfile exists before calling render_template
    # (render_template will copy from djb if nothing exists)
    has_dockerfile = dockerfile_path.exists() or template_path.exists()

    if not has_dockerfile and not managed_dockerfile:
        raise click.ClickException(
            "Dockerfile not found and k8s.backend.managed_dockerfile is False.\n"
            "Either create deployment/k8s/backend/Dockerfile.j2 manually,\n"
            "or set managed_dockerfile = true in .djb/project.toml [k8s.backend]."
        )

    # render_template handles resolution, copying, and rendering
    render_template("Dockerfile", djb_config, subdir="backend")

    # Return path to the rendered Dockerfile
    return dockerfile_path


def _get_git_commit_sha(runner: CmdRunner) -> str:
    """Get the current git commit SHA (short form)."""
    result = runner.run(
        ["git", "rev-parse", "--short", "HEAD"],
        quiet=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "latest"


def _get_project_info(k8s_ctx: "CliK8sContext") -> tuple[str, Path, bool, DjbConfig]:
    """Get project name, directory, managed_dockerfile, and config from context.

    Returns:
        Tuple of (project_name, project_dir, managed_dockerfile, djb_config)

    Raises:
        click.ClickException: If no djb configuration is found.
    """
    if k8s_ctx.config is not None:
        config = k8s_ctx.config
        return (
            config.project_name,
            config.project_dir,
            config.k8s.backend.managed_dockerfile,
            config,
        )

    raise click.ClickException(
        "No djb configuration found. Run from a directory with .djb/project.toml"
    )


def _verify_microk8s_ready(ssh: SSHClient) -> None:
    """Verify microk8s is running on the target host."""
    logger.next("Verifying microk8s status")
    returncode, stdout, stderr = ssh.run("microk8s status")
    if returncode != 0 or "microk8s is running" not in stdout:
        raise click.ClickException(
            "microk8s is not running on the target host.\n"
            "Run: djb deploy k8s terraform --host ... to provision first."
        )
    logger.done("microk8s is running")


def _build_container(
    runner: CmdRunner,
    djb_config: DjbConfig,
    commit_sha: str,
    buildpack_image: str,
    registry_host: str = "localhost:32000",
) -> str:
    """Build the container image locally.

    Dockerfile resolution order:
    1. deployment/k8s/backend/Dockerfile.j2 (project template, rendered at build time)
    2. deployment/k8s/backend/Dockerfile (non-template)
    3. Copy djb template to deployment/k8s/backend/Dockerfile.j2 (if managed_dockerfile=True)

    Args:
        runner: CmdRunner instance for executing commands.
        djb_config: DjbConfig for project settings.
        commit_sha: Git commit SHA for tagging
        buildpack_image: Pre-built buildpack chain image to use as base
        registry_host: Registry host:port for tagging

    Returns:
        The full image tag.
    """
    project_name = djb_config.project_name
    project_dir = djb_config.project_dir
    managed_dockerfile = djb_config.k8s.backend.managed_dockerfile

    image_tag = f"{registry_host}/{project_name}:{commit_sha}"

    logger.next(f"Building container image: {image_tag}")

    # Resolve and render Dockerfile
    dockerfile_path = _get_dockerfile(djb_config, managed_dockerfile)

    # Build with buildx for cross-platform support (target x86_64 for cloud servers)
    # Uses QEMU emulation when building on ARM Macs for x86_64 servers
    runner.run(
        [
            "docker",
            "buildx",
            "build",
            "--platform",
            "linux/amd64",
            "--load",  # Load into local docker images
            "--build-arg",
            f"BUILDPACK_IMAGE={buildpack_image}",
            "-f",
            str(dockerfile_path),
            "-t",
            image_tag,
            str(project_dir),
        ],
        label="Building container",
        done_msg="Image built",
        fail_msg=click.ClickException("Container build failed"),
        show_output=True,  # Stream build output for visibility during long builds
    )
    return image_tag


def _push_to_registry(
    runner: CmdRunner,
    ssh: SSHClient,
    image_tag: str,
    registry_port: int = 32000,
) -> None:
    """Push the container image to the cluster registry.

    Uses an SSH tunnel to forward the local Docker push to the
    microk8s registry on the remote host.
    """
    logger.next("Pushing image to cluster registry")

    # Save the image to a tarball and load it on the remote
    # This avoids the complexity of SSH tunneling to the registry
    tar_path = "/tmp/djb-deploy-image.tar"

    # Save image locally
    runner.run(
        ["docker", "save", "-o", tar_path, image_tag],
        label="Saving image",
        fail_msg=click.ClickException("Failed to save Docker image"),
    )

    # Copy to remote
    ssh.copy_to(Path(tar_path), "/tmp/djb-deploy-image.tar", timeout=600)

    # Import into microk8s containerd
    returncode, stdout, stderr = ssh.run(
        "microk8s ctr image import /tmp/djb-deploy-image.tar",
        timeout=300,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to import image: {stderr}")

    # Push to the microk8s registry so kubelet can pull it
    returncode, stdout, stderr = ssh.run(
        f"microk8s ctr image push --plain-http {image_tag}",
        timeout=300,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to push image to registry: {stderr}")

    # Cleanup
    ssh.run("rm -f /tmp/djb-deploy-image.tar")
    Path(tar_path).unlink(missing_ok=True)

    logger.done("Image pushed")


def _sync_project_to_remote(
    runner: CmdRunner,
    ssh: SSHClient,
    djb_config: DjbConfig,
) -> Path:
    """Sync project files to remote server for building.

    Uses rsync with gitignore filtering for efficient transfer.
    Includes untracked files but excludes gitignored patterns.

    Args:
        runner: CmdRunner instance for executing commands.
        ssh: SSHClient for remote operations.
        djb_config: DjbConfig for project settings.

    Returns:
        Remote path where project was synced.
    """
    project_name = djb_config.project_name
    project_dir = djb_config.project_dir
    remote_build_dir = Path(f"/tmp/djb-build/{project_name}")

    logger.next("Syncing project to remote")

    # Create remote build directory
    ssh.run(f"mkdir -p {remote_build_dir}")

    # Build rsync command with gitignore filtering
    # Note: Order matters - excludes must come before includes for nested paths
    rsync_cmd = [
        "rsync",
        "-avz",
        "--delete",  # Remove files on remote that don't exist locally
        "--exclude=.git",  # Always exclude any .git directories first
        "--exclude=.venv",  # Exclude venv - uv will create on server
        "--exclude=.uv-cache",  # Exclude uv cache
        "--exclude=__pycache__",  # Exclude Python bytecode
        "--include=djb/",  # Include djb directory (may be gitignored but needed for build)
        "--include=djb/**",  # Include all contents of djb
        "--filter=:- .gitignore",  # Read .gitignore and exclude matching patterns
        "-e",
        f"ssh -p {ssh.port}",
        f"{project_dir}/",
        f"{ssh.host}:{remote_build_dir}/",
    ]

    runner.run(
        rsync_cmd,
        label="Syncing files",
        fail_msg=click.ClickException("Failed to sync files to remote"),
        show_output=True,
    )

    logger.done("Project synced")
    return remote_build_dir


def _build_container_remote(
    runner: CmdRunner,
    ssh: SSHClient,
    djb_config: DjbConfig,
    commit_sha: str,
    buildpack_image: str,
    registry_host: str = "localhost:32000",
) -> str:
    """Build container image on remote server (native x86_64).

    Builds directly on the target server, avoiding QEMU emulation overhead
    when building on ARM Macs for x86_64 servers.

    Dockerfile resolution (before syncing to remote):
    1. deployment/k8s/backend/Dockerfile.j2 (project template)
    2. deployment/k8s/backend/Dockerfile (non-template)
    3. Copy djb template to deployment/k8s/backend/Dockerfile.j2 (if managed_dockerfile=True)

    Args:
        runner: CmdRunner instance for executing commands.
        ssh: SSHClient for remote operations.
        djb_config: DjbConfig for project settings.
        commit_sha: Git commit SHA for tagging.
        buildpack_image: Pre-built buildpack chain image to use as base.
        registry_host: Registry host:port for tagging.

    Returns:
        The full image tag.
    """
    project_name = djb_config.project_name
    project_dir = djb_config.project_dir
    managed_dockerfile = djb_config.k8s.backend.managed_dockerfile

    image_tag = f"{registry_host}/{project_name}:{commit_sha}"

    # Ensure Dockerfile exists locally before syncing to remote
    # This copies the template from djb if needed (respecting managed_dockerfile)
    # Note: We don't render here - rendering happens on remote for remote builds
    backend_dir = project_dir / "deployment" / "k8s" / "backend"
    has_dockerfile = (backend_dir / "Dockerfile").exists() or (
        backend_dir / "Dockerfile.j2"
    ).exists()

    if not has_dockerfile:
        if managed_dockerfile:
            # Use render_template to copy template from djb (it will also render, but
            # the rendered file won't be synced - only .j2 is synced for remote builds)
            render_template("Dockerfile", djb_config, subdir="backend")
        else:
            raise click.ClickException(
                "Dockerfile not found and k8s.backend.managed_dockerfile is False.\n"
                "Either create deployment/k8s/backend/Dockerfile.j2 manually,\n"
                "or set managed_dockerfile = true in .djb/project.toml [k8s.backend]."
            )

    # Sync project files to remote (now includes Dockerfile template if copied)
    remote_build_dir = _sync_project_to_remote(runner, ssh, djb_config)

    logger.next(f"Building container on remote: {image_tag}")

    # Resolve Dockerfile (check if exists on remote)
    dockerfile_rel = "deployment/k8s/backend/Dockerfile"
    dockerfile_j2_rel = "deployment/k8s/backend/Dockerfile.j2"

    # Check what exists on remote
    returncode, _, _ = ssh.run(f"test -f {remote_build_dir}/{dockerfile_j2_rel}")
    has_template = returncode == 0
    returncode, _, _ = ssh.run(f"test -f {remote_build_dir}/{dockerfile_rel}")
    has_dockerfile = returncode == 0

    if has_template:
        # Render the template on remote using Python
        render_script = f"""
import sys
sys.path.insert(0, "{remote_build_dir}")
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

template_path = Path("{remote_build_dir}/{dockerfile_j2_rel}")
env = Environment(loader=FileSystemLoader(str(template_path.parent)), trim_blocks=True, lstrip_blocks=True)
template = env.get_template(template_path.name)

# Simple config object for template
class Config:
    project_name = "{project_name}"
djb_config = Config()

rendered = template.render(djb_config=djb_config)
output_path = template_path.parent / "Dockerfile"
output_path.write_text(rendered)
print(f"Rendered: {{output_path}}")
"""
        returncode, stdout, stderr = ssh.run(f"python3 -c '{render_script}'")
        if returncode != 0:
            raise click.ClickException(f"Failed to render Dockerfile template: {stderr}")
        dockerfile_path = f"{remote_build_dir}/{dockerfile_rel}"
    elif has_dockerfile:
        dockerfile_path = f"{remote_build_dir}/{dockerfile_rel}"
    else:
        # This should not happen if local resolution worked correctly
        # The Dockerfile should have been copied locally and synced to remote
        raise click.ClickException(
            "Dockerfile not found on remote after sync.\n"
            "Expected: deployment/k8s/backend/Dockerfile or Dockerfile.j2\n"
            "This may indicate a sync issue. Check rsync output above."
        )

    # Build on remote - native x86_64, no QEMU needed
    build_cmd = (
        f"cd {remote_build_dir} && "
        f"docker build --build-arg BUILDPACK_IMAGE={buildpack_image} "
        f"-f {dockerfile_path} -t {image_tag} ."
    )
    returncode, stdout, stderr = ssh.run(build_cmd, timeout=600)
    if returncode != 0:
        raise click.ClickException(f"Failed to build container on remote:\n{stderr}")

    logger.done("Container built on remote")

    # Import to containerd and push to registry
    logger.next("Pushing to registry")

    # Save and import to containerd
    returncode, _, stderr = ssh.run(
        f"docker save {image_tag} | microk8s ctr image import -",
        timeout=300,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to import image to containerd: {stderr}")

    # Push to microk8s registry
    returncode, _, stderr = ssh.run(
        f"microk8s ctr image push --plain-http {image_tag}",
        timeout=300,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to push image to registry: {stderr}")

    logger.done("Image pushed to registry")

    # Cleanup remote build dir
    ssh.run(f"rm -rf {remote_build_dir}")

    return image_tag


def _secrets_exist_in_cluster(ssh: SSHClient, project_name: str) -> bool:
    """Check if K8s secrets already exist in the cluster.

    Args:
        ssh: SSH client for remote commands.
        project_name: Project name (used for namespace and secret name).

    Returns:
        True if secrets exist, False otherwise.
    """
    returncode, _, _ = ssh.run(
        f"microk8s kubectl get secret {project_name}-secrets -n {project_name} -o name",
    )
    return returncode == 0


def _sync_secrets(
    runner: CmdRunner,
    ssh: SSHClient,
    djb_config: DjbConfig,
    yes: bool = False,
) -> dict[str, str] | None:
    """Sync secrets from djb secrets to K8s cluster.

    If secrets cannot be decrypted (e.g., GPG not available), existing secrets
    in the cluster are preserved and reused. This allows deploys to succeed
    without requiring access to the decryption key every time.

    Args:
        runner: Command runner for subprocess execution.
        ssh: SSH client for remote commands.
        djb_config: Project configuration.
        yes: If True, skip confirmation prompts.

    Returns:
        The secrets dict if synced, or a sentinel dict {"_reuse_existing": "true"}
        if sync failed but existing secrets are available. Returns None only if
        no secrets exist at all.
    """
    logger.next("Syncing secrets")

    try:
        # Load secrets for production mode (SecretsManager handles GPG-protected keys)
        manager = SecretsManager(runner, djb_config.project_dir)
        secrets = manager.load_secrets(Mode.PRODUCTION)
        if not secrets:
            logger.skip("No secrets to sync")
            return None
    except Exception as e:
        logger.warning(f"Failed to load secrets: {e}")
        # Check if secrets already exist in cluster - if so, we can continue
        if _secrets_exist_in_cluster(ssh, djb_config.project_name):
            logger.done("Using existing secrets in cluster")
            return {"_reuse_existing": "true"}
        logger.error("No existing secrets in cluster - deployment may fail")
        return None

    # Check for placeholder secrets that need to be changed
    placeholders = find_placeholder_secrets(secrets)
    if placeholders:
        logger.warning(f"Found {len(placeholders)} secret(s) with placeholder values:")
        for key in placeholders:
            logger.info(f"   * {key}")
        logger.note()
        logger.warning("These secrets contain values like 'CHANGE-ME' that must be updated.")
        logger.info("Run 'djb secrets edit' to set real values.")
        logger.note()
        if not yes and not click.confirm(
            "Continue deployment with placeholder secrets?", default=False
        ):
            raise click.ClickException("Deployment cancelled - update secrets first")

    # Generate K8s secret manifest
    secrets_ctx = SecretsCtx(secrets=secrets)
    generator = K8sManifestGenerator()
    secret_manifest = generator.render("secrets.yaml.j2", djb_config, secrets_ctx)

    # Apply via kubectl (escape single quotes for shell)
    escaped_manifest = secret_manifest.replace("'", "'\"'\"'")
    returncode, stdout, stderr = ssh.run(
        f"echo '{escaped_manifest}' | microk8s kubectl apply -f -",
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to apply secrets: {stderr}")

    logger.done("Secrets synced")
    return secrets


def _apply_manifests(
    ssh: SSHClient,
    djb_config: DjbConfig,
    image_tag: str,
    has_secrets: bool = False,
    has_database: bool = True,
    env_vars: dict[str, str] | None = None,
) -> None:
    """Apply all K8s manifests to the cluster."""
    logger.next("Applying manifests")

    deployment_ctx = DeploymentCtx(
        image=image_tag,
        has_secrets=has_secrets,
        has_database=has_database,
        env_vars=env_vars or {},
        # Timestamp forces pod restart even when image tag is unchanged
        deploy_timestamp=datetime.now(timezone.utc).isoformat(),
    )
    database_ctx = DatabaseCtx() if has_database else None

    generator = K8sManifestGenerator()
    manifests = generator.render_all(
        djb_config,
        deployment=deployment_ctx,
        database=database_ctx,
    )

    # Apply in order: namespace, database, secrets, deployment, service, ingress
    order = [
        "namespace.yaml",
        "cnpg-cluster.yaml",
        "secrets.yaml",
        "deployment.yaml",
        "service.yaml",
        "ingress.yaml",
    ]

    for manifest_name in order:
        if manifest_name not in manifests:
            continue

        manifest_content = manifests[manifest_name]
        logger.info(f"  Applying {manifest_name}...")

        # Escape single quotes for shell
        escaped_content = manifest_content.replace("'", "'\"'\"'")
        returncode, _, stderr = ssh.run(
            f"echo '{escaped_content}' | microk8s kubectl apply -f -",
        )
        if returncode != 0:
            raise click.ClickException(f"Failed to apply {manifest_name}: {stderr}")

    logger.done("Manifests applied")


def _wait_for_rollout(
    ssh: SSHClient,
    project_name: str,
    timeout: int = 300,
) -> None:
    """Wait for the deployment rollout to complete."""
    logger.next("Waiting for rollout")

    returncode, stdout, stderr = ssh.run(
        f"microk8s kubectl rollout status deployment/{project_name} "
        f"-n {project_name} --timeout={timeout}s",
        timeout=timeout + 30,
    )

    if returncode != 0:
        # Try to get pod status for better debugging
        pod_status_cmd = (
            f"microk8s kubectl get pods -n {project_name} -o wide && "
            f"microk8s kubectl describe pods -n {project_name} | tail -50"
        )
        _, pod_info, _ = ssh.run(pod_status_cmd, timeout=30)

        raise click.ClickException(f"Rollout failed: {stderr}\n\n" f"Pod status:\n{pod_info}")

    logger.done("Rollout complete")


def _run_migrations(
    ssh: SSHClient,
    djb_config: DjbConfig,
    image_tag: str,
    has_secrets: bool = False,
    env_vars: dict[str, str] | None = None,
    timeout: int = 120,
) -> None:
    """Run database migrations as a K8s Job.

    Args:
        ssh: SSH client for remote commands.
        djb_config: Project configuration.
        image_tag: Docker image tag for the migration job.
        has_secrets: Whether K8s secrets are available.
        env_vars: Environment variables to pass to the migration job.
        timeout: Timeout in seconds for the migration job (default 120s).
            Use 0 for no timeout (wait forever).
    """
    logger.next("Running migrations")

    migration_ctx = MigrationCtx(
        image=image_tag,
        has_secrets=has_secrets,
        env_vars=env_vars or {},
    )
    generator = K8sManifestGenerator()
    job_manifest = generator.render("migration-job.yaml.j2", djb_config, migration_ctx)

    # Delete any existing migration job with the same name
    project_name = djb_config.project_name
    job_name = f"{project_name}-migrate-{image_tag.split(':')[-1][:8]}"
    ssh.run(
        f"microk8s kubectl delete job {job_name} -n {project_name} --ignore-not-found",
    )

    # Apply the migration job
    # Escape single quotes for shell
    escaped_manifest = job_manifest.replace("'", "'\"'\"'")
    returncode, _, stderr = ssh.run(
        f"echo '{escaped_manifest}' | microk8s kubectl apply -f -",
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to create migration job: {stderr}")

    # Wait for job to complete
    # timeout=0 means no timeout (use kubectl's default which is infinite wait)
    if timeout > 0:
        timeout_arg = f"--timeout={timeout}s"
        ssh_timeout = timeout + 60  # Extra margin for SSH
    else:
        timeout_arg = ""  # No --timeout means infinite wait
        ssh_timeout = 3600 * 24  # 24 hours as "effectively infinite" for SSH

    wait_cmd = f"microk8s kubectl wait --for=condition=complete job/{job_name} -n {project_name}"
    if timeout_arg:
        wait_cmd = f"{wait_cmd} {timeout_arg}"

    returncode, _, stderr = ssh.run(wait_cmd, timeout=ssh_timeout)

    if returncode != 0:
        # Get job logs for debugging
        ssh.run(
            f"microk8s kubectl logs job/{job_name} -n {project_name}",
        )
        raise click.ClickException(f"Migration failed: {stderr}")

    logger.done("Migrations complete")


def _tag_deployment(runner: CmdRunner, commit_sha: str) -> None:
    """Tag the deployment in git."""
    tag_name = f"deploy-k8s-{commit_sha}"

    result = runner.run(
        ["git", "tag", "-f", tag_name],
        quiet=True,
    )

    if result.returncode == 0:
        logger.info(f"Tagged as {tag_name}")


def _cleanup_old_images(ssh: SSHClient, project_name: str, current_image_tag: str) -> None:
    """Clean up old Docker images and registry storage on remote server.

    This helps prevent disk pressure issues by:
    1. Removing old app deployment images from Docker
    2. Pruning dangling Docker images
    3. Running registry garbage collection to reclaim storage

    Preserved images:
    - Buildpack chain images (python, bun, postgres, gdal combinations)
    - The current deployment image
    - Base images needed for builds (ghcr.io/astral-sh/uv, etc.)

    Removed images:
    - Old app deployment images (localhost:32000/{project_name}:*)
    - Dangling/unused images
    - Unreferenced registry blobs

    Args:
        ssh: SSH client for remote commands.
        project_name: Project name to identify app images.
        current_image_tag: The current deployment image tag to preserve.
    """
    logger.next("Cleaning up old images")

    # Get all images on the server
    returncode, stdout, _ = ssh.run(
        "docker images --format '{{.Repository}}:{{.Tag}}'",
        timeout=30,
    )
    if returncode != 0:
        logger.warning("Failed to list images, skipping cleanup")
        return

    # Parse current tag to get just the tag portion (e.g., "abc1234" from "localhost:32000/project:abc1234")
    current_tag = current_image_tag.split(":")[-1] if ":" in current_image_tag else ""

    # Identify old app images to remove
    images_to_remove = []
    for line in stdout.strip().split("\n"):
        if not line or line == "<none>:<none>":
            continue

        # Preserve buildpack chain images (they don't have the project name as the image name)
        # Buildpack images look like: localhost:32000/python3.14-slim-bunlatest-...
        # App images look like: localhost:32000/beachresort25:commit_sha
        if f"/{project_name}:" in line:
            # This is an app image - check if it's old
            tag = line.split(":")[-1]
            if tag != current_tag and tag != "latest":
                images_to_remove.append(line)

    # Remove old app images
    for image in images_to_remove:
        ssh.run(f"docker rmi {image} 2>/dev/null || true", timeout=30)

    # Prune dangling images and build cache
    ssh.run("docker image prune -f 2>/dev/null || true", timeout=60)

    # Run registry garbage collection to reclaim storage
    # This removes unreferenced blobs from the microk8s registry
    ssh.run(
        "microk8s kubectl exec -n container-registry deployment/registry -- "
        "/bin/registry garbage-collect /etc/docker/registry/config.yml --delete-untagged "
        "2>/dev/null || true",
        timeout=120,
    )

    if images_to_remove:
        logger.done(f"Cleaned up {len(images_to_remove)} old image(s)")
    else:
        logger.done("Registry cleaned")


def _verify_health(djb_config: DjbConfig, expected_sha: str) -> None:
    """Verify the health endpoint returns correct status and version.

    Makes an HTTP request to the health endpoint and verifies:
    1. Returns HTTP 200
    2. X-Version header matches the deployed commit SHA

    Args:
        djb_config: DjbConfig with domain configuration.
        expected_sha: The git commit SHA that should be in the X-Version header.

    Raises:
        click.ClickException: If health check fails.
    """
    logger.next("Verifying deployment health")

    # Get primary domain
    domains = list(djb_config.k8s.domain_names.keys())
    if not domains:
        logger.skip("No domains configured, skipping health check")
        return

    domain = domains[0]
    health_url = f"https://{domain}/health/"
    headers = {"User-Agent": "djb-health-check/1.0"}

    # Retry with backoff - give the app time to become fully ready
    max_retries = 5
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            response = requests.get(health_url, headers=headers, timeout=10)
            status = response.status_code
            version = response.headers.get("X-Version", "")

            if status != 200:
                if attempt < max_retries - 1:
                    logger.debug(f"Health check returned {status}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise click.ClickException(
                    f"Health check failed: expected status 200, got {status}"
                )

            if version != expected_sha:
                if attempt < max_retries - 1:
                    # Old version still serving, wait for rollout
                    logger.debug(
                        f"Version mismatch (got {version[:7]}, expected {expected_sha[:7]}), "
                        f"retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                raise click.ClickException(
                    f"Health check failed: X-Version header mismatch\n"
                    f"  Expected: {expected_sha}\n"
                    f"  Got: {version or '(not set)'}"
                )

            logger.done(f"Health OK (version: {version[:7]})")

            # Verify readiness endpoint (validates homepage URLs internally)
            logger.next("Checking readiness (homepage URL validation)")
            ready_url = f"https://{domain}/health/ready/"
            try:
                ready_response = requests.get(ready_url, headers=headers, timeout=60)
                data = ready_response.json()
                urls_checked = data.get("urls_checked", 0)
                if data.get("status") == "ok":
                    logger.done(f"Readiness OK ({urls_checked} URLs validated)")
                else:
                    errors = data.get("errors", [])
                    logger.warning(f"Readiness check found {len(errors)} issue(s):")
                    for error in errors:
                        logger.warning(f"  - {error}")
            except requests.exceptions.HTTPError as e:
                logger.warning(f"Readiness check failed: {e}")
            except Exception as e:
                logger.warning(f"Readiness check failed: {e}")
            return

        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                logger.debug(f"Health check connection error, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise click.ClickException(f"Health check failed: connection error - {e}")
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                logger.debug(f"Health check timeout, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise click.ClickException("Health check failed: timeout")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                logger.debug(f"Health check error: {e}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise click.ClickException(f"Health check failed: {e}")

    raise click.ClickException("Health check failed after maximum retries")


def _ensure_domain_configured(ctx: click.Context, djb_config: DjbConfig) -> None:
    """Ensure at least one domain is configured for K8s deployment.

    If no domains exist, prompts the user to add one. This is a noop if
    domains are already configured (like beachresort.me).

    Args:
        ctx: Click context for invoking subcommands.
        djb_config: DjbConfig with domain configuration.
    """
    domains = djb_config.k8s.domain_names
    if domains:
        # Domains already configured, check if any are eligible for K8s
        cloudflare_domains = [
            d for d, cfg in domains.items() if cfg.manager == DomainNameManager.CLOUDFLARE
        ]
        if cloudflare_domains:
            logger.debug(f"Using configured domains: {', '.join(cloudflare_domains)}")
            return

        # Has domains but none managed by cloudflare
        logger.warning("No Cloudflare-managed domains configured for K8s deployment")
        logger.info("  Hint: Add a domain with: djb domain add example.com --manager cloudflare")
        return

    # No domains configured - prompt to add one
    logger.next("No domains configured for K8s deployment")
    if click.confirm("Would you like to add a domain now?"):
        # Invoke domain init
        ctx.invoke(domain_init)
    else:
        logger.warning("Skipping domain configuration")
        logger.info("  Add later with: djb domain add example.com --manager cloudflare")


def _sync_domain_dns(cli_ctx: "CliK8sContext") -> None:
    """Sync DNS records for all configured domains.

    Creates/updates Cloudflare A records pointing to the server IP.
    """
    domains = cli_ctx.config.k8s.domain_names
    cloudflare_domains = [
        d for d, cfg in domains.items() if cfg.manager == DomainNameManager.CLOUDFLARE
    ]

    if not cloudflare_domains:
        logger.debug("No Cloudflare-managed domains to sync")
        return

    _sync_k8s_domains(cli_ctx, dry_run=False)


def deploy_k8s(ctx: click.Context, k8s_ctx: "CliK8sContext") -> None:
    """Execute the K8s deployment workflow.

    This is called from the k8s command group when no subcommand is specified.

    Args:
        ctx: Click context for invoking subcommands.
        k8s_ctx: K8s CLI context with deployment options.
    """
    if k8s_ctx.host is None:
        raise click.ClickException("No host specified for deployment")

    # Create runner from context (CliK8sContext extends CliContext)
    runner = k8s_ctx.runner

    _, _, _, djb_config = _get_project_info(k8s_ctx)
    project_name = djb_config.project_name
    commit_sha = _get_git_commit_sha(runner)

    logger.info(f"Deploying {project_name} to {k8s_ctx.host}:{k8s_ctx.port}")

    # Ensure domain is configured (noop if already set up)
    _ensure_domain_configured(ctx, djb_config)

    # Create SSH client
    try:
        ssh = SSHClient(
            host=k8s_ctx.host,
            cmd_runner=runner,
            port=k8s_ctx.port,
            key_path=k8s_ctx.ssh_key,
        )
    except SSHError as e:
        raise click.ClickException(f"SSH connection failed: {e}")

    # Pre-flight checks
    _verify_microk8s_ready(ssh)

    # Build buildpack chain and container
    if not k8s_ctx.skip_build:
        buildpacks = djb_config.k8s.backend.buildpacks
        if not buildpacks:
            raise click.ClickException(
                "No buildpacks configured.\n"
                "Add buildpacks to .djb/project.toml under [k8s.backend]"
            )

        if djb_config.k8s.backend.remote_build:
            # Build buildpack chain on remote server
            logger.next("Building buildpack chain on remote")
            logger.info(f"Buildpacks: {' -> '.join(buildpacks)}")
            buildpack_chain = RemoteBuildpackChain(
                registry="localhost:32000",
                ssh=ssh,
                pyproject_path=djb_config.project_dir / "pyproject.toml",
                djb_config=djb_config,
            )
            buildpack_image = buildpack_chain.build(buildpacks)
            logger.done(f"Buildpack chain ready: {buildpack_image}")

            # Build app container on remote server (native x86_64, no QEMU)
            image_tag = _build_container_remote(
                runner, ssh, djb_config, commit_sha, buildpack_image
            )
        else:
            # Build buildpack chain locally
            logger.next("Building buildpack chain locally")
            logger.info(f"Buildpacks: {' -> '.join(buildpacks)}")
            buildpack_chain = LocalBuildpackChain(
                registry="localhost:32000",
                runner=runner,
                pyproject_path=djb_config.project_dir / "pyproject.toml",
                djb_config=djb_config,
            )
            buildpack_image = buildpack_chain.build(buildpacks)
            logger.done(f"Buildpack chain ready: {buildpack_image}")

            # Build locally and transfer (uses QEMU on ARM Macs)
            image_tag = _build_container(runner, djb_config, commit_sha, buildpack_image)
            _push_to_registry(runner, ssh, image_tag)
    else:
        image_tag = f"localhost:32000/{project_name}:{commit_sha}"
        logger.skip("Container build (--skip-build)")

    # Sync secrets (returns secrets dict if any exist, or sentinel if reusing existing)
    has_secrets = False
    if not k8s_ctx.skip_secrets:
        secrets = _sync_secrets(runner, ssh, djb_config, yes=k8s_ctx.yes)
        has_secrets = secrets is not None
    else:
        logger.skip("Secrets sync (--skip-secrets)")
        # Even with --skip-secrets, check if secrets exist in cluster
        has_secrets = _secrets_exist_in_cluster(ssh, project_name)

    # Build environment variables for K8s deployment and migrations
    env_vars: dict[str, str] = {}
    # GIT_COMMIT_SHA for version tracking in health endpoint
    env_vars["GIT_COMMIT_SHA"] = commit_sha
    # DJB_DOMAINS for ALLOWED_HOSTS configuration
    if domains := ",".join(djb_config.domain_names_list):
        env_vars["DJB_DOMAINS"] = domains
    # DJB_INTERNAL_HOST for K8s health probe Host header matching
    env_vars["DJB_INTERNAL_HOST"] = djb_config.project_name

    # Apply manifests
    _apply_manifests(ssh, djb_config, image_tag, has_secrets=has_secrets, env_vars=env_vars)

    # Wait for rollout
    _wait_for_rollout(ssh, project_name)

    # Run migrations
    if not k8s_ctx.skip_migrate:
        _run_migrations(ssh, djb_config, image_tag, has_secrets=has_secrets, env_vars=env_vars)
    else:
        logger.skip("Migrations (--skip-migrate)")

    # Clean up old images to prevent disk pressure
    _cleanup_old_images(ssh, project_name, image_tag)

    # Verify health endpoint responds correctly with new version
    _verify_health(djb_config, commit_sha)

    # Tag deployment
    _tag_deployment(runner, commit_sha)

    # Sync DNS records for domains
    _sync_domain_dns(k8s_ctx)

    # Done
    logger.note()
    logger.done("Deployment complete!")
    for domain in djb_config.k8s.domain_names:
        logger.info(f"  URL: https://{domain}")
    logger.note()

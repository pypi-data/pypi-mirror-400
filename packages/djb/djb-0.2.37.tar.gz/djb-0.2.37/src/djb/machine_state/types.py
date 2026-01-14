"""Types and context for MachineState system.

Command Execution Principle:
    All commands should go through the MachineContext methods:
    - Local commands: ctx.runner.run(...)
    - Remote commands: ctx.run_remote(...)

    This ensures:
    1. Commands are logged in --verbose mode
    2. Users can reproduce commands manually (e.g., `djb run <command>`)
    3. Consistent error handling and timeout management
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Generic, TypeVar

from djb.core.cmd_runner import CmdError

if TYPE_CHECKING:
    from djb.config import DjbConfig
    from djb.core.cmd_runner import CmdRunner
    from djb.core.logging import DjbLogger
    from djb.secrets import SecretsManager

    from .base import MachineStateABC

TOptions = TypeVar("TOptions")


class SearchStrategy(str, Enum):
    """Search strategy for find_divergence().

    AUTO - Use binary search for linear chains, linear for DAGs (default)
    LINEAR - Always use linear scan O(n)
    BINARY - Always use binary search O(log n) - only valid for linear chains
    """

    AUTO = "auto"
    LINEAR = "linear"
    BINARY = "binary"


@dataclass
class BaseOptions:
    """Base options for all MachineState operations.

    Attributes:
        search_strategy: Strategy for finding first unsatisfied task.
    """

    search_strategy: SearchStrategy = SearchStrategy.AUTO


@dataclass
class ForceCreateOptions(BaseOptions):
    """Options for states that support force creation.

    Attributes:
        force_create: Force creation of a new resource even if one exists.

    Inherited from BaseOptions:
        search_strategy: Strategy for finding first unsatisfied task.
    """

    force_create: bool = False


@dataclass
class ExecuteResult:
    """Result of reconciling a MachineState.

    Attributes:
        source: The MachineState instance that produced this result
        success: Whether execution completed successfully
        changed: Whether any changes were made
        message: Human-readable description of what happened
    """

    source: MachineStateABC
    success: bool
    changed: bool
    message: str = ""

    def __repr__(self) -> str:
        if self.success:
            status = "changed" if self.changed else "unchanged"
        else:
            status = "failed"
        return f"ExecuteResult({self.source.__class__.__name__}, {status})"


@dataclass
class CacheConfig:
    """Cache configuration for a MachineContext.

    Attributes:
        mode: The deployment mode (staging, production, etc.)
        enabled: Whether caching is enabled
        max_entries: Maximum number of cache entries before pruning
    """

    mode: str
    enabled: bool = True
    max_entries: int = 100

    @property
    def cache_dir(self) -> Path:
        """Cache directory scoped by mode."""
        return Path(f".djb/cache/{self.mode}")


@dataclass
class MachineContext(Generic[TOptions]):
    """Shared context passed to all MachineState methods.

    This is the stateless context that provides access to configuration,
    command execution, logging, and typed CLI options.

    Generic Parameters:
        TOptions: Type of CLI options for this context. Each command defines
                  its own options dataclass (e.g., HetznerMaterializeOptions).

    Command Execution:
        - Local commands: Use runner.run() directly
        - Remote commands: Use run_remote() method (uses `djb run` internally)

    Attributes:
        config: The DjbConfig instance
        runner: For executing local shell commands
        logger: For logging operations
        secrets: Optional secrets manager for accessing encrypted values
        options: Typed CLI options passed from the command
        cache: Optional cache configuration (defaults to per-mode cache)
    """

    config: DjbConfig
    runner: CmdRunner
    logger: DjbLogger
    secrets: SecretsManager | None = None
    options: TOptions | None = None
    cache: CacheConfig | None = None
    depth: int = 0  # Nesting depth for indented output

    def __post_init__(self) -> None:
        """Initialize cache config if not provided."""
        if self.cache is None:
            self.cache = CacheConfig(mode=self.config.mode)

    def _build_djb_run_cmd(
        self,
        command: str,
        *,
        user: str = "root",
        timeout: int = 60,
        streaming: bool = False,
    ) -> list[str]:
        """Build the djb run command with all propagated options."""
        cmd = ["djb"]

        overrides = getattr(self.config, "_overrides", None) or {}

        if "mode" in overrides:
            cmd.extend(["--mode", str(overrides["mode"])])
        else:
            cmd.extend(["--mode", str(self.config.mode)])

        if "platform" in overrides:
            cmd.extend(["--platform", str(overrides["platform"])])
        else:
            cmd.extend(["--platform", str(self.config.platform)])

        if overrides.get("verbose"):
            cmd.append("--verbose")
        if overrides.get("quiet"):
            cmd.append("--quiet")
        if overrides.get("yes"):
            cmd.append("--yes")

        cmd.append("run")
        if user != "root":
            cmd.extend(["--user", user])
        cmd.extend(["--timeout", str(timeout)])
        if not streaming:
            cmd.append("--no-streaming")

        cmd.append(command)
        return cmd

    def run_remote(
        self,
        command: str,
        *,
        user: str = "root",
        timeout: int = 60,
        check: bool = False,
    ) -> tuple[int, str, str]:
        """Execute a command on the remote server via SSH.

        Args:
            command: Command to execute on the remote host
            user: SSH user (default: root)
            timeout: Command timeout in seconds (default: 60)
            check: If True, raise error on non-zero exit code

        Returns:
            Tuple of (returncode, stdout, stderr)

        Raises:
            CmdError: If check=True and command fails
        """
        djb_cmd = self._build_djb_run_cmd(command, user=user, timeout=timeout, streaming=False)

        result = self.runner.run(djb_cmd, timeout=timeout + 30)

        if check and result.returncode != 0:
            raise CmdError(
                f"Remote command failed: {command}",
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                cmd=djb_cmd,
            )

        return result.returncode, result.stdout, result.stderr

    def run_remote_streaming(
        self,
        command: str,
        *,
        user: str = "root",
    ) -> int:
        """Execute a command on the remote server with streaming output.

        Args:
            command: Command to execute on the remote host
            user: SSH user (default: root)

        Returns:
            Exit code
        """
        djb_cmd = self._build_djb_run_cmd(command, user=user, streaming=True)
        result = self.runner.run(djb_cmd, show_output=True)
        return result.returncode

    def log(self, state: MachineStateABC, message: str) -> None:
        """Log a message with state context and indentation."""
        indent = "  " * self.depth
        self.logger.info(f"{indent}[{state.__class__.__name__}] {message}")

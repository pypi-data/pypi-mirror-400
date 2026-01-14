"""Centralized command runner for subprocess execution.

This module provides a unified interface for executing subprocess commands with
integrated error handling, logging, and verbose mode support. All subprocess
calls in djb should go through this module to ensure --verbose provides 100%
visibility into what commands are being executed.

Usage with CLI context (preferred for CLI commands):

    from djb.cli.context import djb_pass_context, CliContext

    @djb_pass_context
    def my_command(cli_ctx: CliContext):
        result = cli_ctx.runner.run(["git", "status"])

Usage for library code (verbose=False by default):

    from djb.core import CmdRunner

    runner = CmdRunner()
    result = runner.run(["git", "status"], cwd=project_root)
    if runner.check(["which", "sops"]):
        ...

Features:
    - Verbose mode: When --verbose is set, commands are printed and output streams
    - Inherited stdin: Subprocess inherits terminal for interactive commands (pinentry, etc.)
    - Input data: Use input= parameter to provide data to subprocess stdin
    - Shell mode: Use shell=True to run command strings through the shell
    - Timeout: Use timeout= parameter to limit command execution time
    - Process replacement: Use exec() to replace the current process (os.execvp)
    - Environment variables: Use env= parameter to set additional env vars
    - Sensitive arg masking: Use hide_args= to mask sensitive values in verbose output
"""

from __future__ import annotations

import os
import select
import shlex
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, NoReturn

from djb.core.exceptions import DjbError
from djb.core.logging import get_logger

import click

if TYPE_CHECKING:
    from typing import Any

logger = get_logger(__name__)

# Platform detection for PTY support
_IS_WINDOWS = sys.platform == "win32"

# Unix PTY support (Linux, macOS, WSL2)
# pty module is only available on Unix systems
_HAS_UNIX_PTY = False
pty: Any = None
if not _IS_WINDOWS:
    try:
        import pty

        _HAS_UNIX_PTY = True
    except ImportError:
        pass

# Windows ConPTY support via pywinpty
_HAS_WIN_PTY = False
WinPTY: Any = None
if _IS_WINDOWS:
    try:
        from winpty import PTY as WinPTY  # type: ignore[import-not-found]

        _HAS_WIN_PTY = True
    except ImportError:
        WinPTY = None

# select.poll() is not available on Windows
_HAS_POLL = hasattr(select, "poll")

# Buffer size for reading subprocess output
_READ_BUFFER_SIZE = 4096

# Poll timeout in milliseconds for subprocess I/O
_POLL_TIMEOUT_MS = 100


# --- Exceptions ---


class CmdError(DjbError):
    """Command execution failed."""

    def __init__(
        self,
        message: str,
        *,
        returncode: int | None = None,
        stdout: str = "",
        stderr: str = "",
        cmd: list[str] | str | None = None,
    ) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.cmd = cmd


class CmdTimeout(CmdError):
    """Command timed out."""

    def __init__(
        self,
        message: str,
        *,
        timeout: float,
        cmd: list[str] | str | None = None,
    ) -> None:
        super().__init__(message, cmd=cmd)
        self.timeout = timeout


# --- Result dataclass ---


@dataclass
class RunResult:
    """Result of a command execution."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        """Return True if command exited with code 0."""
        return self.returncode == 0

    def __bool__(self) -> bool:
        """Allow using RunResult in boolean context: `if result:`."""
        return self.returncode == 0


# --- Helper functions ---


def _mask_sensitive_args(cmd: list[str], hide_args: list[str]) -> list[str]:
    """Mask values of sensitive arguments for display.

    Handles both space-separated (--token secret) and equals-separated
    (--token=secret) argument formats.

    Args:
        cmd: Command and arguments list
        hide_args: Argument names whose values should be masked

    Returns:
        Command list with sensitive values replaced by "****"

    Example:
        >>> _mask_sensitive_args(["docker", "login", "--password", "secret"], ["--password"])
        ["docker", "login", "--password", "****"]
        >>> _mask_sensitive_args(["curl", "--header=Bearer token"], ["--header"])
        ["curl", "--header=****"]
    """
    if not hide_args:
        return cmd

    result = []
    hide_next = False
    for arg in cmd:
        if hide_next:
            result.append("****")
            hide_next = False
        elif arg in hide_args:
            result.append(arg)
            hide_next = True
        elif any(arg.startswith(f"{h}=") for h in hide_args):
            prefix = next(h for h in hide_args if arg.startswith(f"{h}="))
            result.append(f"{prefix}=****")
        else:
            result.append(arg)
    return result


def _get_env(cwd: Path | None, env: dict[str, str] | None) -> dict[str, str] | None:
    """Get environment with VIRTUAL_ENV cleared and custom env vars merged.

    When running commands in a different project directory (e.g., djb editable from host),
    the inherited VIRTUAL_ENV would point to the wrong venv and cause uv to emit:

        warning: `VIRTUAL_ENV=...` does not match the project environment path `.venv`
        and will be ignored; use `--active` to target the active environment instead

    Clearing VIRTUAL_ENV lets uv auto-detect the correct .venv for the target directory.
    """
    if cwd is None and env is None:
        return None
    result = os.environ.copy()
    if cwd is not None:
        result.pop("VIRTUAL_ENV", None)
    if env is not None:
        result.update(env)
    return result


def _format_cmd_for_display(cmd: list[str] | str, shell: bool) -> str:
    """Format command for display in logs."""
    if shell:
        return cmd if isinstance(cmd, str) else shlex.join(cmd)
    return shlex.join(cmd) if isinstance(cmd, list) else cmd


# --- Main class ---


class CmdRunner:
    """Centralized command runner for subprocess execution.

    The verbose flag determines whether commands are logged and output is streamed.

    Pattern:
    - CLI commands: Use cli_ctx.runner (cached CmdRunner with correct verbosity)
    - Tests/library: Use CmdRunner(verbose=False)

    Examples:
        # CLI mode - use context's runner
        @djb_pass_context
        def my_command(cli_ctx: CliContext):
            result = cli_ctx.runner.run(["git", "status"])

        # Test/library mode
        runner = CmdRunner(verbose=False)
        result = runner.run(["age-keygen"], timeout=5)

        # With stdin piping
        result = runner.run(["age-keygen", "-y"], input=private_key)

        # Shell mode
        result = runner.run("microk8s kubectl get pods", shell=True)

        # Process replacement (exec)
        runner.exec(["skaffold", "dev", "--port-forward"])
    """

    def __init__(self, verbose: bool = False) -> None:
        """Initialize CmdRunner.

        Args:
            verbose: If True, commands are printed and output is streamed
                to the terminal in real-time.
        """
        self._verbose = verbose

    def _is_verbose(self) -> bool:
        """Check if verbose mode is enabled."""
        return self._verbose

    def run(
        self,
        cmd: list[str] | str,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        input: str | None = None,
        shell: bool = False,
        timeout: float | None = None,
        label: str | None = None,
        done_msg: str | None = None,
        fail_msg: str | Exception | None = None,
        quiet: bool = False,
        hide_args: list[str] | None = None,
        show_output: bool = False,
        interactive: bool = False,
    ) -> RunResult:
        """Run a command with captured output.

        Output is always captured. When show_output=True (or CmdRunner verbose mode),
        output is also streamed to the terminal in real-time.

        Args:
            cmd: Command as list or string (string requires shell=True)
            cwd: Working directory
            env: Environment variables to add (merged with current env)
            input: String to pipe to stdin
            shell: Run command through shell (required for string commands)
            timeout: Command timeout in seconds (None = no timeout)
            label: Human-readable label (logged with logger.next)
            done_msg: Success message (logged with logger.done)
            fail_msg: Failure message (str) or exception to raise (Exception).
                      If a string: logged with logger.fail on failure.
                      If an exception: logged and raised on failure.
            quiet: Suppress all logging output
            hide_args: Argument names to mask in verbose output
            show_output: Show output to terminal (always on in verbose mode)
            interactive: Use PTY for commands needing terminal (GPG, editors).
                         stdout/stderr are combined in this mode.

        Returns:
            RunResult with returncode, stdout, stderr

        Raises:
            fail_msg: If fail_msg is an Exception and command fails
            CmdTimeout: If timeout expires
        """
        if label and not quiet:
            logger.next(label)

        # Log command (masked if sensitive args present)
        if isinstance(cmd, list):
            display_cmd = _mask_sensitive_args(cmd, hide_args or [])
            display_str = shlex.join(display_cmd)
        else:
            display_str = cmd  # Shell commands shown as-is (can't mask easily)

        verbose = self._is_verbose()
        if verbose:
            logger.info(f"$ {display_str}")
        else:
            logger.debug(f"Executing: {display_str}")

        merged_env = _get_env(cwd, env)

        # Show output in verbose mode, explicit show_output, or interactive mode
        should_show = verbose or show_output or interactive

        # Always use streaming - it handles input and timeout now
        if interactive:
            returncode, stdout, stderr = _run_with_pty(cmd, cwd=cwd, env=merged_env, shell=shell)
        else:
            returncode, stdout, stderr = _run_with_pipes(
                cmd,
                cwd=cwd,
                env=merged_env,
                shell=shell,
                input=input,
                timeout=timeout,
                show_output=should_show,
            )
        result = RunResult(returncode=returncode, stdout=stdout, stderr=stderr)

        if result.returncode != 0:
            # Handle fail_msg: can be string message or exception to raise
            if isinstance(fail_msg, Exception):
                # Exception instance: raise it
                # Skip logging for click.ClickException. Click formats on its own
                if not quiet and not isinstance(fail_msg, click.ClickException):
                    logger.fail(str(fail_msg))
                    if result.stderr and not should_show:
                        logger.info(f"  {result.stderr.strip()}")
                raise fail_msg
            elif fail_msg:
                # String: just log the message
                if not quiet:
                    logger.fail(fail_msg)
                    if result.stderr and not should_show:
                        logger.info(f"  {result.stderr.strip()}")
        elif done_msg and not quiet:
            logger.done(done_msg)

        return result

    def check(
        self,
        cmd: list[str] | str,
        *,
        cwd: Path | None = None,
        timeout: float | None = 10,
        shell: bool = False,
    ) -> bool:
        """Check if a command succeeds (exit code 0).

        Useful for checking tool availability.

        Args:
            cmd: Command to check
            cwd: Working directory
            timeout: Timeout in seconds (default 10s for availability checks)
            shell: Run command through shell

        Returns:
            True if command exits with code 0
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                shell=shell,
                timeout=timeout,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def exec(
        self,
        cmd: list[str],
        *,
        env: dict[str, str] | None = None,
    ) -> NoReturn:
        """Replace current process with command (os.execvp).

        This function never returns - the current process is replaced.

        Args:
            cmd: Command and arguments
            env: Environment variables (if provided, uses execvpe)

        Raises:
            CmdError: If exec fails (e.g., command not found)
        """
        if not cmd:
            raise CmdError("Cannot exec empty command", cmd=cmd)

        program = cmd[0]

        if self._is_verbose():
            logger.info(f"$ exec {shlex.join(cmd)}")

        try:
            if env is not None:
                merged_env = os.environ.copy()
                merged_env.update(env)
                os.execvpe(program, cmd, merged_env)
            else:
                os.execvp(program, cmd)
        except FileNotFoundError as e:
            raise CmdError(f"Command not found: {program}", cmd=cmd) from e
        except OSError as e:
            raise CmdError(f"Failed to exec {program}: {e}", cmd=cmd) from e

        # This line is never reached, but helps type checkers
        raise RuntimeError("exec should not return")  # pragma: no cover


# --- Streaming implementations ---


class _NullBuffer:
    """A buffer that discards all writes."""

    def write(self, data: bytes) -> int:
        return len(data)

    def flush(self) -> None:
        pass


# Singleton null buffer for suppressing output
_NULL_BUFFER = _NullBuffer()


def _run_with_pipes(
    cmd: list[str] | str,
    *,
    cwd: Path | None,
    env: dict[str, str] | None,
    shell: bool = False,
    input: str | None = None,
    timeout: float | None = None,
    show_output: bool = True,
) -> tuple[int, str, str]:
    """Run a command with pipes, optionally streaming output to terminal.

    Standard non-interactive mode: stdin receives optional input, stdout and stderr
    are captured separately while optionally being streamed to the terminal.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory
        env: Environment variables
        shell: Run command through shell
        input: String to write to stdin (then close)
        timeout: Timeout in seconds (None = no timeout)
        show_output: If True, stream output to terminal; if False, capture only

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        CmdTimeout: If timeout expires before command completes
    """
    # Use pipe for stdin if input provided, otherwise DEVNULL
    stdin_arg = subprocess.PIPE if input is not None else subprocess.DEVNULL

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdin=stdin_arg,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
    )
    assert process.stdout is not None
    assert process.stderr is not None

    # Write input to stdin if provided
    if input is not None and process.stdin is not None:
        try:
            process.stdin.write(input.encode())
            process.stdin.close()
        except OSError:
            pass  # Process may have exited

    start_time = time.monotonic() if timeout is not None else None

    # Choose output buffers: real terminal or null sink
    stdout_buf: BinaryIO = sys.stdout.buffer if show_output else _NULL_BUFFER  # type: ignore[assignment]
    stderr_buf: BinaryIO = sys.stderr.buffer if show_output else _NULL_BUFFER  # type: ignore[assignment]

    if _HAS_POLL:
        fds: list[tuple[int, BinaryIO]] = [
            (process.stdout.fileno(), stdout_buf),
            (process.stderr.fileno(), stderr_buf),
        ]
        chunks = _stream_with_fds_poll(fds, process, timeout=timeout, start_time=start_time)
        stdout_chunks, stderr_chunks = chunks[0], chunks[1]
    else:
        # Windows fallback using threads
        stdout_chunks, stderr_chunks = _stream_with_threads(
            process,
            timeout=timeout,
            start_time=start_time,
            stdout_buf=stdout_buf,
            stderr_buf=stderr_buf,
        )

    process.wait()
    stdout = b"".join(stdout_chunks).decode(errors="replace")
    stderr = b"".join(stderr_chunks).decode(errors="replace")
    return process.returncode, stdout, stderr


def _run_with_pty(
    cmd: list[str] | str,
    *,
    cwd: Path | None,
    env: dict[str, str] | None,
    shell: bool = False,
) -> tuple[int, str, str]:
    """Run a command with PTY for interactive terminal access.

    Dispatches to the appropriate platform-specific PTY implementation:
    - Windows: ConPTY via pywinpty
    - Unix/macOS/WSL2: pty module

    Args:
        cmd: Command and arguments to run
        cwd: Working directory
        env: Environment variables
        shell: Run command through shell

    Returns:
        Tuple of (return_code, combined_output, "")
        stderr is empty as PTY combines streams.

    Raises:
        CmdError: If no PTY support is available.
    """
    if _HAS_WIN_PTY:
        return _run_with_win_pty(cmd, cwd=cwd, env=env, shell=shell)
    elif _HAS_UNIX_PTY:
        return _run_with_unix_pty(cmd, cwd=cwd, env=env, shell=shell)
    else:
        raise CmdError(
            "Interactive mode requires PTY support. "
            "On Windows, install pywinpty: pip install pywinpty",
            cmd=cmd,
        )


def _run_with_unix_pty(
    cmd: list[str] | str,
    *,
    cwd: Path | None,
    env: dict[str, str] | None,
    shell: bool = False,
) -> tuple[int, str, str]:
    """Run a command with Unix PTY, streaming output to terminal.

    Creates a pseudo-terminal so the subprocess sees a real TTY (isatty() = True).
    This enables interactive prompts like GPG pinentry, editors, etc.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory
        env: Environment variables
        shell: Run command through shell

    Returns:
        Tuple of (return_code, combined_output, "")
        stderr is empty as PTY combines streams.
    """
    assert pty is not None  # Caller checks _HAS_UNIX_PTY

    master_fd, slave_fd = pty.openpty()

    try:
        has_tty = sys.stdin.isatty()
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdin=sys.stdin if has_tty else None,
            stdout=slave_fd,
            stderr=slave_fd,
            shell=shell,
        )
        os.close(slave_fd)  # Close slave in parent

        # Stream from PTY master
        fds: list[tuple[int, BinaryIO]] = [(master_fd, sys.stdout.buffer)]
        chunks = _stream_with_fds_poll(fds, process)

        process.wait()
        output = b"".join(chunks[0]).decode(errors="replace")
        return process.returncode, output, ""

    finally:
        try:
            os.close(master_fd)
        except OSError:
            pass


def _stream_with_fds_poll(
    fds: list[tuple[int, BinaryIO]],
    process: subprocess.Popen[bytes],
    timeout: float | None = None,
    start_time: float | None = None,
) -> list[list[bytes]]:
    """Stream from file descriptors to output buffers while capturing.

    Uses select.poll() to read from multiple file descriptors concurrently,
    writing to their corresponding output buffers and capturing the data.

    Args:
        fds: List of (input_fd, output_buffer) tuples.
             Each tuple specifies: fd to read from, buffer to write to.
        process: The subprocess to monitor for exit.
        timeout: Timeout in seconds (None = no timeout).
        start_time: Start time from time.monotonic() for timeout calculation.

    Returns:
        List of chunk lists, one per input fd in the same order.

    Raises:
        CmdTimeout: If timeout expires before process completes.
    """
    if not fds:
        return []

    poller = select.poll()
    # Map fd -> (output_buffer, chunks, index)
    fd_map: dict[int, tuple[BinaryIO, list[bytes], int]] = {}
    active_fds: set[int] = set()
    all_chunks: list[list[bytes]] = []

    for i, (fd, output_buffer) in enumerate(fds):
        chunks: list[bytes] = []
        all_chunks.append(chunks)
        poller.register(fd, select.POLLIN)
        fd_map[fd] = (output_buffer, chunks, i)
        active_fds.add(fd)

    while active_fds:
        # Check timeout
        if timeout is not None and start_time is not None:
            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                process.kill()
                process.wait()
                # process.args can be bytes on some platforms, normalize to expected type
                cmd_for_error: list[str] | str | None = None
                if isinstance(process.args, list):
                    cmd_for_error = [str(a) for a in process.args]
                elif isinstance(process.args, str):
                    cmd_for_error = process.args
                raise CmdTimeout(
                    f"Command timed out after {timeout} seconds",
                    timeout=timeout,
                    cmd=cmd_for_error,
                )

        events = poller.poll(_POLL_TIMEOUT_MS)

        for fd, event in events:
            if event & select.POLLIN:
                output_buffer, chunks, _ = fd_map[fd]
                try:
                    chunk = os.read(fd, _READ_BUFFER_SIZE)
                except OSError:
                    chunk = b""

                if chunk:
                    output_buffer.write(chunk)
                    output_buffer.flush()
                    chunks.append(chunk)
                else:
                    poller.unregister(fd)
                    active_fds.discard(fd)
            elif event & (select.POLLHUP | select.POLLERR):
                poller.unregister(fd)
                active_fds.discard(fd)

        # Process exited and no events - drain remaining data
        if process.poll() is not None and not events:
            for fd in list(active_fds):
                output_buffer, chunks, _ = fd_map[fd]
                try:
                    while True:
                        chunk = os.read(fd, _READ_BUFFER_SIZE)
                        if not chunk:
                            break
                        output_buffer.write(chunk)
                        output_buffer.flush()
                        chunks.append(chunk)
                except OSError:
                    pass
                poller.unregister(fd)
                active_fds.discard(fd)

    return all_chunks


def _stream_with_threads(
    process: subprocess.Popen[bytes],
    timeout: float | None = None,
    start_time: float | None = None,
    stdout_buf: BinaryIO | None = None,
    stderr_buf: BinaryIO | None = None,
) -> tuple[list[bytes], list[bytes]]:
    """Stream output using threads (Windows fallback).

    On Windows, select.poll() is not available and select.select() only works
    with sockets, not pipes. This implementation uses threads to read from
    stdout and stderr concurrently.

    Args:
        process: Subprocess with stdout and stderr pipes.
        timeout: Timeout in seconds (None = no timeout).
        start_time: Start time from time.monotonic() for timeout calculation.
        stdout_buf: Buffer to write stdout to (defaults to sys.stdout.buffer).
        stderr_buf: Buffer to write stderr to (defaults to sys.stderr.buffer).

    Returns:
        Tuple of (stdout_chunks, stderr_chunks) as lists of bytes.

    Raises:
        CmdTimeout: If timeout expires before process completes.
    """
    assert process.stdout is not None
    assert process.stderr is not None

    # Use provided buffers or defaults
    out_buf = stdout_buf if stdout_buf is not None else sys.stdout.buffer
    err_buf = stderr_buf if stderr_buf is not None else sys.stderr.buffer

    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    lock = threading.Lock()
    stop_event = threading.Event()

    def read_stream(
        stream: BinaryIO,
        chunks: list[bytes],
        output_buffer: BinaryIO,
    ) -> None:
        """Read from stream and write to output buffer."""
        while not stop_event.is_set():
            chunk = stream.read(_READ_BUFFER_SIZE)
            if not chunk:
                break
            with lock:
                output_buffer.write(chunk)
                output_buffer.flush()
                chunks.append(chunk)

    stdout_thread = threading.Thread(
        target=read_stream,
        args=(process.stdout, stdout_chunks, out_buf),
    )
    stderr_thread = threading.Thread(
        target=read_stream,
        args=(process.stderr, stderr_chunks, err_buf),
    )

    stdout_thread.start()
    stderr_thread.start()

    # Wait for process with timeout
    if timeout is not None and start_time is not None:
        while process.poll() is None:
            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                stop_event.set()
                process.kill()
                process.wait()
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
                # Build cmd for error
                cmd_for_error: list[str] | str | None = None
                if isinstance(process.args, list):
                    cmd_for_error = [str(a) for a in process.args]
                elif isinstance(process.args, str):
                    cmd_for_error = process.args
                raise CmdTimeout(
                    f"Command timed out after {timeout} seconds",
                    timeout=timeout,
                    cmd=cmd_for_error,
                )
            time.sleep(0.1)  # Small sleep to avoid busy-waiting
    else:
        process.wait()

    stdout_thread.join()
    stderr_thread.join()

    return stdout_chunks, stderr_chunks


def _run_with_win_pty(
    cmd: list[str] | str,
    *,
    cwd: Path | None,
    env: dict[str, str] | None,
    shell: bool = False,
) -> tuple[int, str, str]:
    """Run a command with Windows ConPTY, capturing output.

    Uses pywinpty to create a pseudo-terminal on Windows. The subprocess
    sees a real terminal (isatty() = True), enabling interactive prompts.

    Architecture::

        _run_with_win_pty(cmd)
            ├── WinPTY(cols, rows) -> ConPTY handle
            ├── pty.spawn(cmd) -> process in PTY
            ├── Thread: stdin -> pty.write() (user input)
            └── Main: pty.read() -> stdout + capture (streaming output)

    Args:
        cmd: Command and arguments to run
        cwd: Working directory (note: pywinpty doesn't support cwd directly)
        env: Environment variables
        shell: Run command through shell (ignored on Windows, commands run through shell anyway)

    Returns:
        Tuple of (return_code, captured_output, "")
        stderr is empty as PTY combines streams.
    """
    # shell parameter is ignored on Windows - pywinpty spawns through shell anyway
    del shell

    if not _HAS_WIN_PTY:
        raise CmdError("pywinpty not installed", cmd=cmd)

    # Get terminal size or use defaults
    try:
        size = os.get_terminal_size()
        cols, rows = size.columns, size.lines
    except OSError:
        cols, rows = 80, 25

    # Build command string for Windows
    if isinstance(cmd, str):
        cmd_str = cmd
    else:
        cmd_str = subprocess.list2cmdline(cmd)

    if cwd:
        # Prepend cd command since pywinpty doesn't support cwd
        cmd_str = f'cd /d "{cwd}" && ' + cmd_str

    # Create ConPTY
    win_pty = WinPTY(cols, rows)

    # Spawn process (pywinpty expects bytes on spawn)
    win_pty.spawn(cmd_str.encode())

    output_chunks: list[bytes] = []
    has_tty = sys.stdin.isatty()

    # Thread to forward stdin to PTY
    def forward_stdin() -> None:
        if not has_tty:
            return
        try:
            while win_pty.isalive():
                # Read from real stdin
                if sys.stdin.readable():
                    char = sys.stdin.read(1)
                    if char:
                        win_pty.write(char.encode())
        except (OSError, ValueError):
            pass

    stdin_thread = threading.Thread(target=forward_stdin, daemon=True)
    stdin_thread.start()

    # Read output and stream to terminal
    try:
        while win_pty.isalive():
            try:
                # pywinpty.read() returns bytes, may block briefly
                data = win_pty.read(4096, blocking=False)
                if data:
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
                    output_chunks.append(data)
            except (OSError, Exception):
                break

        # Drain any remaining output
        try:
            remaining = win_pty.read(4096, blocking=False)
            if remaining:
                sys.stdout.buffer.write(remaining)
                sys.stdout.buffer.flush()
                output_chunks.append(remaining)
        except (OSError, Exception):
            pass

    finally:
        # Get exit code before cleanup
        exitcode = win_pty.get_exitstatus() if hasattr(win_pty, "get_exitstatus") else 0
        del win_pty

    output = b"".join(output_chunks).decode(errors="replace")
    return exitcode, output, ""

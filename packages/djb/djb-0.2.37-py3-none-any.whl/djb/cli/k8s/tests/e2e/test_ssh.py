"""E2E tests for SSH client utility.

These tests require Docker to be running and use real SSH connections.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.cli.context import CliContext
from djb.core.cmd_runner import CmdRunner
from djb.ssh import SSHClient, SSHError


@pytest.fixture
def runner() -> CmdRunner:
    """CmdRunner for subprocess execution."""
    return CliContext().runner


pytestmark = pytest.mark.e2e_marker


class TestSSHClientE2E:
    """E2E tests for the SSH client utility."""

    def test_ssh_run_command(
        self,
        make_local_vps_container: dict,
        runner: CmdRunner,
    ) -> None:
        """Test running a command via SSH."""

        ssh = SSHClient(
            host=f"root@{make_local_vps_container['host']}",
            cmd_runner=runner,
            port=make_local_vps_container["port"],
            key_path=make_local_vps_container["ssh_key"],
        )

        returncode, stdout, stderr = ssh.run("echo hello")
        assert returncode == 0
        assert "hello" in stdout

    def test_ssh_run_command_with_check(
        self,
        make_local_vps_container: dict,
        runner: CmdRunner,
    ) -> None:
        """Test running a command with check=True."""
        ssh = SSHClient(
            host=f"root@{make_local_vps_container['host']}",
            cmd_runner=runner,
            port=make_local_vps_container["port"],
            key_path=make_local_vps_container["ssh_key"],
        )

        # Successful command
        returncode, stdout, _ = ssh.run("hostname", check=True)
        assert returncode == 0

        # Failing command should raise SSHError
        with pytest.raises(SSHError):
            ssh.run("exit 1", check=True)

    def test_ssh_copy_file(
        self,
        make_local_vps_container: dict,
        tmp_path: Path,
        runner: CmdRunner,
    ) -> None:
        """Test copying files via SCP."""
        ssh = SSHClient(
            host=f"root@{make_local_vps_container['host']}",
            cmd_runner=runner,
            port=make_local_vps_container["port"],
            key_path=make_local_vps_container["ssh_key"],
        )

        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Copy to remote
        ssh.copy_to(test_file, "/tmp/test.txt")

        # Verify file exists on remote
        returncode, stdout, _ = ssh.run("cat /tmp/test.txt")
        assert returncode == 0
        assert "test content" in stdout

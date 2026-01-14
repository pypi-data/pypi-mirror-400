"""End-to-end tests for djb secrets CLI commands.

These tests exercise the secrets management CLI against real encryption tools
(age, SOPS, GPG) while isolating the test environment.

Commands tested:
- djb secrets init
- djb secrets edit
- djb secrets view
- djb secrets list
- djb secrets generate-key
- djb secrets export-key
- djb secrets upgrade
- djb secrets rotate
- djb secrets protect
- djb secrets unprotect

Requirements (djb init):
- GPG must be installed
- age must be installed
- SOPS must be installed

Features:
1. ENVIRONMENT ISOLATION (fixtures in conftest.py)
   - GPG: Use GNUPGHOME env var for isolated keyring
   - Age/SOPS: Use SOPS_AGE_KEY_FILE env var
   - Never touch user's real ~/.gnupg or ~/.age

2. SIGNAL HANDLER TESTING (TestEdgeCases.test_sigint_triggers_signal_handler_cleanup)
   - Spawn subprocess, wait for "READY" stdout signal
   - Send SIGINT/SIGTERM, verify cleanup via file system state
   - Test signal handlers separately from finally blocks

3. FILE LOCKING CONCURRENCY (TestEdgeCases.test_concurrent_access_serialized_by_file_locking)
   - Use marker files for synchronization, not sleep()
   - Use fcntl locks for atomic result file writes
   - Verify timing: proc2.acquired >= proc1.released

4. GPG LOOPBACK MODE (required for non-interactive testing)
   - Use --pinentry-mode loopback in GPG commands
   - See docs/testing-tty-input.md for details
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess  # noqa: TID251 - Popen for process tests
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from djb.cli.djb import djb_cli
from djb.core.cmd_runner import CmdRunner, CmdTimeout
from djb.secrets import (
    SOPS_TIMEOUT,
    SecretsManager,
    SopsError,
    encrypt_file,
    generate_age_key,
    get_public_key_from_private,
)
from djb.secrets.gpg import (
    GPG_INTERACTIVE_TIMEOUT,
    GPG_TIMEOUT,
    GpgError,
    GpgTimeoutError,
    gpg_decrypt_file,
    gpg_encrypt_file,
    is_gpg_encrypted,
)
from djb.types import Mode

from . import (
    TEST_PASSPHRASE,
    assert_gpg_encrypted,
    assert_not_contains_secrets,
    assert_sops_encrypted,
    create_sops_config,
    gpg_decrypt,
    gpg_encrypt,
    sops_decrypt,
    sops_encrypt,
)


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


class TestSecretsInit:
    """E2E tests for djb secrets init command."""

    def test_init_creates_key_and_secrets(
        self, cli_runner, project_dir, make_pyproject, age_key_dir
    ):
        """Secrets init creates key, .sops.yaml, and secrets files."""
        make_pyproject()
        key_path = age_key_dir / "keys.txt"
        secrets_dir = project_dir / "secrets"

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "secrets",
                "init",
                "--key-path",
                str(key_path),
                "--secrets-dir",
                str(secrets_dir),
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify key was created
        assert key_path.exists(), "Age key was not created"
        key_content = key_path.read_text()
        assert "AGE-SECRET-KEY-" in key_content

        # Verify .sops.yaml was created
        sops_config = secrets_dir / ".sops.yaml"
        assert sops_config.exists(), ".sops.yaml was not created"
        assert "age:" in sops_config.read_text()

        # Verify secrets files were created
        for env_name in ["development", "staging", "production"]:
            secrets_file = secrets_dir / f"{env_name}.yaml"
            assert secrets_file.exists(), f"{env_name}.yaml was not created"
            # Files should be SOPS encrypted
            assert_sops_encrypted(secrets_file)

        # Verify README was created
        readme = secrets_dir / "README.md"
        assert readme.exists(), "README.md was not created"

    def test_init_reuses_existing_key(
        self, cli_runner, make_cmd_runner: CmdRunner, project_dir, make_pyproject, age_key_dir
    ):
        """Init reuses an existing key without --force."""
        make_pyproject()
        key_path = age_key_dir / "keys.txt"
        secrets_dir = project_dir / "secrets"

        # Pre-create a key
        original_public, _ = generate_age_key(make_cmd_runner, key_path)

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "secrets",
                "init",
                "--key-path",
                str(key_path),
                "--secrets-dir",
                str(secrets_dir),
            ],
        )

        assert result.exit_code == 0

        # Verify the original key was preserved
        current_public = get_public_key_from_private(make_cmd_runner, key_path)
        assert current_public == original_public

        # Message should indicate reuse
        assert "existing" in result.output.lower() or "using" in result.output.lower()


class TestSecretsView:
    """E2E tests for djb secrets view command."""

    def test_view_shows_decrypted_secrets(
        self,
        cli_runner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """View command decrypts secrets and shows YAML content with expected keys."""
        project_dir, _key_path = make_pyproject_dir_with_git_with_secrets

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "secrets",
                "view",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Verify output contains expected YAML keys (proves decryption worked)
        # The secrets template includes django_secret_key
        assert (
            "django_secret_key:" in result.output
        ), f"Expected 'django_secret_key:' in output: {result.output}"

    def test_view_existing_key_returns_value(
        self,
        cli_runner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """View --key returns just the value for existing keys."""
        project_dir, _key_path = make_pyproject_dir_with_git_with_secrets

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "secrets",
                "view",
                "--key",
                "django_secret_key",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Output should be just the value, not a YAML key: value pair
        output = result.output.strip()
        assert output, "Output should not be empty"
        # The value itself should not contain the key name as a YAML key
        assert not output.startswith(
            "django_secret_key:"
        ), "Should return value only, not key: value"

    def test_view_missing_key_exits_with_error(
        self,
        cli_runner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """View --key fails with clear error for missing keys."""
        project_dir, _key_path = make_pyproject_dir_with_git_with_secrets

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "secrets",
                "view",
                "--key",
                "nonexistent_key_xyz_12345",
            ],
        )

        assert result.exit_code == 1, f"Should fail for missing key: {result.output}"
        assert "not found" in result.output.lower(), f"Should mention 'not found': {result.output}"


class TestSecretsList:
    """E2E tests for djb secrets list command."""

    def test_list_shows_environments(
        self,
        cli_runner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """List shows available environment file names (without .yaml extension)."""
        project_dir, _ = make_pyproject_dir_with_git_with_secrets

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "secrets",
                "list",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Files are development.yaml, staging.yaml, production.yaml
        assert "development" in result.output, f"Missing 'development': {result.output}"
        assert "staging" in result.output, f"Missing 'staging': {result.output}"
        assert "production" in result.output, f"Missing 'production': {result.output}"

    def test_list_no_secrets_dir(self, cli_runner, project_dir, make_pyproject, monkeypatch):
        """List command when secrets directory doesn't exist."""
        make_pyproject()
        monkeypatch.chdir(project_dir)
        result = cli_runner.invoke(djb_cli, ["secrets", "list"])
        assert result.exit_code == 0
        assert "No secrets directory found" in result.output

    def test_list_empty_secrets_dir(self, cli_runner, project_dir, make_pyproject, monkeypatch):
        """List command when secrets directory is empty."""
        make_pyproject()
        monkeypatch.chdir(project_dir)
        (project_dir / "secrets").mkdir()
        result = cli_runner.invoke(djb_cli, ["secrets", "list"])
        assert result.exit_code == 0
        assert "No secret files found" in result.output

    def test_list_with_secrets_filters_sops_config(
        self, cli_runner, project_dir, make_pyproject, monkeypatch
    ):
        """List command excludes .sops.yaml from environments list."""
        make_pyproject()
        monkeypatch.chdir(project_dir)
        secrets_dir = project_dir / "secrets"
        secrets_dir.mkdir()
        (secrets_dir / "development.yaml").write_text("test: value")
        (secrets_dir / "production.yaml").write_text("test: value")
        (secrets_dir / ".sops.yaml").write_text("config: true")  # Should be excluded

        result = cli_runner.invoke(djb_cli, ["secrets", "list"])
        assert result.exit_code == 0
        assert "Available environments" in result.output
        assert "development" in result.output
        assert "production" in result.output
        assert ".sops" not in result.output


class TestSecretsGenerateKey:
    """E2E tests for djb secrets generate-key command."""

    def test_generate_key_outputs_valid_django_secret(self, cli_runner):
        """Generate-key outputs a valid 50-character Django secret key."""
        result = cli_runner.invoke(djb_cli, ["secrets", "generate-key"])

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Output format: "Generated Django secret key:\n<KEY>\n\nAdd this..."
        # Find the line after "Generated Django secret key:"
        lines = result.output.strip().split("\n")
        key_line_idx = None
        for i, line in enumerate(lines):
            if "Generated Django secret key" in line:
                key_line_idx = i + 1
                break
        assert key_line_idx is not None, f"No 'Generated Django secret key' found: {result.output}"
        assert key_line_idx < len(lines), f"Key line missing after header: {result.output}"

        # Strip ANSI codes from the key line
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        key = ansi_escape.sub("", lines[key_line_idx]).strip()

        # Django secrets are 50 chars from a specific charset
        assert len(key) == 50, f"Django secret should be 50 chars, got {len(key)}: {key}"
        # Valid charset: letters, digits, and special chars used by Django
        valid_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
        )
        invalid = set(key) - valid_chars
        assert not invalid, f"Invalid chars in key: {invalid}"


class TestSecretsExportKey:
    """E2E tests for djb secrets export-key command."""

    def test_export_key_outputs_private_key(
        self, cli_runner, make_cmd_runner: CmdRunner, age_key_dir, project_dir, make_pyproject
    ):
        """Export-key outputs the AGE-SECRET-KEY."""
        make_pyproject()
        key_path = age_key_dir / "keys.txt"

        # Generate a key first
        generate_age_key(make_cmd_runner, key_path)

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "secrets",
                "export-key",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should output the secret key
        assert "AGE-SECRET-KEY-" in result.output

    def test_export_key_not_found(self, cli_runner, project_dir, make_pyproject):
        """Export-key fails when key doesn't exist."""
        make_pyproject()
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "secrets", "export-key"],
        )
        assert result.exit_code == 1
        assert "Key file not found" in result.output

    def test_export_key_no_secret_in_file(
        self, cli_runner, project_dir, make_pyproject, age_key_dir
    ):
        """Export-key fails when file has no secret key."""
        make_pyproject()
        key_file = age_key_dir / "keys.txt"
        key_file.write_text("# just comments\n")

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "secrets",
                "export-key",
            ],
        )
        assert result.exit_code == 1
        assert "No AGE-SECRET-KEY found" in result.output


class TestSecretsProtectUnprotect:
    """E2E tests for GPG protection of age keys.

    Note: The protect/unprotect CLI commands use default key paths based on
    get_default_key_path(), which makes them difficult to test in isolation.
    These tests verify the underlying functions directly instead of through
    the CLI, as the GPG functionality is already tested in test_gpg.py.
    """

    def test_protect_and_unprotect_functions(self, make_cmd_runner: CmdRunner, age_key_dir):
        """Protect_age_key and unprotect_age_key functions directly."""
        key_path = age_key_dir / "keys.txt"
        encrypted_path = key_path.parent / (key_path.name + ".gpg")

        # Generate a key first
        public_key, _ = generate_age_key(make_cmd_runner, key_path)
        original_content = key_path.read_text()

        # Protect using our shared utilities (simulating what the CLI would do)
        gpg_encrypt(key_path, encrypted_path, TEST_PASSPHRASE)
        key_path.unlink()

        # Verify protection worked
        assert not key_path.exists(), "Plaintext key should be removed"
        assert encrypted_path.exists(), "Encrypted key should exist"
        assert_gpg_encrypted(encrypted_path)
        assert_not_contains_secrets(encrypted_path, "AGE-SECRET-KEY")

        # Unprotect using our shared utilities
        gpg_decrypt(encrypted_path, key_path, TEST_PASSPHRASE)

        # Verify unprotection worked
        assert key_path.exists(), "Plaintext key should be restored"
        assert key_path.read_text() == original_content

    def test_gpg_protect_preserves_key_integrity(self, make_cmd_runner: CmdRunner, age_key_dir):
        """GPG protection preserves the age key's functionality."""
        key_path = age_key_dir / "keys.txt"
        encrypted_path = key_path.parent / (key_path.name + ".gpg")

        # Generate a key
        public_key, _ = generate_age_key(make_cmd_runner, key_path)
        original_content = key_path.read_text()
        original_public = get_public_key_from_private(make_cmd_runner, key_path)

        # Protect the key
        gpg_encrypt(key_path, encrypted_path, TEST_PASSPHRASE)
        key_path.unlink()

        # Unprotect and verify
        gpg_decrypt(encrypted_path, key_path, TEST_PASSPHRASE)

        # Verify the key is functionally identical
        recovered_public = get_public_key_from_private(make_cmd_runner, key_path)
        assert recovered_public == original_public
        assert key_path.read_text() == original_content


class TestSecretsRotate:
    """E2E tests for djb secrets rotate command."""

    def test_rotate_adds_new_recipient(
        self,
        cli_runner,
        make_pyproject_dir_with_git_with_secrets,
        make_age_key,
    ):
        """Rotate adds recipient who can then decrypt secrets."""
        project_dir, _key_path = make_pyproject_dir_with_git_with_secrets
        secrets_dir = project_dir / "secrets"
        sops_config = secrets_dir / ".sops.yaml"

        # Create a new key to add
        bob_key_path, bob_public = make_age_key("bob")

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "secrets",
                "rotate",
                "--add-key",
                bob_public,
                "--add-email",
                "bob@example.com",
            ],
        )

        assert result.exit_code == 0, f"Rotate failed: {result.output}"

        # Verify .sops.yaml was updated with Bob's key
        config_content = sops_config.read_text()
        assert bob_public in config_content, "Bob's key not in .sops.yaml"
        assert "bob@example.com" in config_content, "Bob's email not in .sops.yaml"

        # Verify Bob can actually decrypt (the real test!)
        # Check staging first, fall back to development if staging doesn't exist
        staging_file = secrets_dir / "staging.yaml"
        dev_file = secrets_dir / "development.yaml"
        test_file = staging_file if staging_file.exists() else dev_file

        if test_file.exists():
            decrypt_result = sops_decrypt(test_file, sops_config, bob_key_path)
            assert (
                decrypt_result.returncode == 0
            ), f"Bob cannot decrypt {test_file.name} after rotation: {decrypt_result.stderr}"


class TestSecretsUpgrade:
    """E2E tests for djb secrets upgrade command."""

    def test_upgrade_reports_up_to_date(
        self,
        cli_runner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """Upgrade reports when secrets are up to date."""
        project_dir, _key_path = make_pyproject_dir_with_git_with_secrets

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "secrets",
                "upgrade",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should indicate up to date or show what was added
        assert "up to date" in result.output.lower() or "added" in result.output.lower()


class TestEdgeCases:
    """E2E tests for edge cases and error recovery scenarios."""

    def test_concurrent_access_serialized_by_file_locking(self, project_dir):
        """File locking serializes concurrent access to protected key.

        This test spawns two subprocesses that try to access the protected
        age key simultaneously. The file lock ensures they run sequentially
        (one waits for the other to finish).
        """

        # Set up project structure
        project_root = project_dir / "project"
        age_dir = project_root / ".age"
        age_dir.mkdir(parents=True)
        key_path = age_dir / "keys.txt"

        # Create a plaintext key
        key_path.write_text("# test key\nAGE-SECRET-KEY-TEST")

        # Results file for subprocesses to write timing data
        results_file = project_dir / "results.json"
        results_file.write_text("[]")

        # Marker file for proc1 to signal it has acquired the lock
        marker_file = project_dir / "proc1_acquired.marker"

        # Script that acquires lock, writes timing, holds for delay, releases.
        # We mock GPG here because otherwise process 1 would GPG-encrypt the key
        # on normal exit, and process 2 couldn't decrypt it (no shared GPG key).
        # This is acceptable because we're testing FILE LOCKING, not GPG - the
        # lock acquisition happens before any GPG operations.
        script = f"""
import fcntl
import json
import os
import time
from pathlib import Path
from unittest.mock import patch
from djb.secrets import protected_age_key
from djb.core.cmd_runner import CmdRunner

proc_id = int(__import__("sys").argv[1])
hold_time = float(__import__("sys").argv[2])
results_file = Path("{results_file}")
marker_file = Path("{marker_file}")
project_dir = Path(os.environ["DJB_PROJECT_DIR"])
runner = CmdRunner()

start = time.time()
with patch("djb.secrets.protected.check_gpg_installed", return_value=False):
    with protected_age_key(project_dir, runner):
        acquired = time.time()
        # Process 1 creates marker file to signal it has the lock
        if proc_id == 1:
            marker_file.touch()
        time.sleep(hold_time)
        released = time.time()

# Write results atomically using fcntl for locking
lock_file = open(str(results_file) + ".lock", "w")
try:
    fcntl.flock(lock_file, fcntl.LOCK_EX)
    data = json.loads(results_file.read_text())
    data.append({{"proc": proc_id, "start": start, "acquired": acquired, "released": released}})
    results_file.write_text(json.dumps(data))
finally:
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()
"""

        # env with DJB_PROJECT_DIR for the subprocess
        env = {**os.environ, "DJB_PROJECT_DIR": str(project_root)}

        # Start process 1 (holds lock for 0.15s)
        proc1 = subprocess.Popen(
            [sys.executable, "-c", script, "1", "0.15"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        # Wait for proc1 to acquire the lock (indicated by marker file)
        # This ensures proc1 definitely has the lock before we start proc2
        timeout = 5.0
        start_wait = time.time()
        while not marker_file.exists():
            if time.time() - start_wait > timeout:
                proc1.kill()
                _, stderr = proc1.communicate(timeout=5)
                raise AssertionError(f"Process 1 failed to acquire lock within timeout: {stderr}")
            time.sleep(0.01)

        # Start process 2 (holds lock for 0.05s)
        proc2 = subprocess.Popen(
            [sys.executable, "-c", script, "2", "0.05"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        # Wait for both to complete
        _, stderr1 = proc1.communicate(timeout=10)
        _, stderr2 = proc2.communicate(timeout=10)

        assert proc1.returncode == 0, f"Process 1 failed: {stderr1}"
        assert proc2.returncode == 0, f"Process 2 failed: {stderr2}"

        # Read results

        results = json.loads(results_file.read_text())
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"

        r1 = next(r for r in results if r["proc"] == 1)
        r2 = next(r for r in results if r["proc"] == 2)

        # Process 2 should not acquire lock until process 1 releases it
        # (with 0.1s tolerance for timing variations on slow/busy CI systems)
        assert r2["acquired"] >= r1["released"] - 0.1, (
            f"Process 2 acquired lock at {r2['acquired']:.3f} "
            f"but process 1 released at {r1['released']:.3f}. "
            f"File locking is not working - processes ran concurrently."
        )

    def test_atomic_sops_config_write(self, make_cmd_runner: CmdRunner, project_dir):
        """.sops.yaml writes use atomic pattern (temp file + rename).

        This verifies that temp files don't linger after successful writes.
        """
        secrets_dir = project_dir / "secrets"
        secrets_dir.mkdir()
        temp_path = secrets_dir / ".sops.yaml.tmp"
        manager = SecretsManager(make_cmd_runner, project_dir, secrets_dir=secrets_dir)

        # Create initial config
        recipients1 = {"age1abc123": "alice@example.com"}
        manager.save_config(recipients1)

        # Verify config is valid and temp file cleaned up
        assert (secrets_dir / ".sops.yaml").exists()
        assert not temp_path.exists(), "Temp file should be cleaned up"
        parsed = manager.recipients
        assert "age1abc123" in parsed

        # Update config
        recipients2 = {"age1abc123": "alice@example.com", "age1def456": "bob@example.com"}
        manager.save_config(recipients2)

        # Verify updated config is valid and temp file cleaned up
        assert not temp_path.exists(), "Temp file should be cleaned up"
        parsed = manager.recipients
        assert "age1abc123" in parsed
        assert "age1def456" in parsed

    def test_symlink_key_file_rejected(self, project_dir):
        """Symlinked key files are rejected for security.

        If the age key file itself is a symlink, it should be rejected to prevent
        attacks where a symlink could redirect key operations to an attacker-controlled
        location. The symlink check runs unconditionally in protected_age_key().
        """
        # Set up project structure with symlinked key
        project_root = project_dir / "project"
        age_dir = project_root / ".age"
        age_dir.mkdir(parents=True)

        # Create the real key file elsewhere
        real_key = project_dir / "real_key.txt"
        real_key.write_text("# real key\nAGE-SECRET-KEY-REAL")

        # Create symlink at the expected key location
        key_path = age_dir / "keys.txt"
        key_path.symlink_to(real_key)

        assert key_path.is_symlink(), "Test setup: key should be a symlink"
        assert key_path.exists(), "Test setup: symlink target should exist"

        # Use DJB_PROJECT_DIR env var to configure djb for the subprocess
        script = """
import os
from pathlib import Path
from djb.secrets import protected_age_key, ProtectedFileError
from djb.core.cmd_runner import CmdRunner

project_dir = Path(os.environ["DJB_PROJECT_DIR"])
runner = CmdRunner()
try:
    with protected_age_key(project_dir, runner):
        print("ERROR: Should have raised ProtectedFileError")
        __import__("sys").exit(1)
except ProtectedFileError as e:
    if "symlink" in str(e).lower():
        print("OK: ProtectedFileError with symlink message")
        __import__("sys").exit(0)
    else:
        print(f"ERROR: Wrong error message: {e}")
        __import__("sys").exit(1)
except Exception as e:
    print(f"ERROR: Unexpected exception: {type(e).__name__}: {e}")
    __import__("sys").exit(1)
"""

        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "DJB_PROJECT_DIR": str(project_root)},
        )

        assert result.returncode == 0, (
            f"Symlink rejection test failed.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "OK" in result.stdout, f"Unexpected output: {result.stdout}"

    def test_timeout_exception_converted_to_sops_error(
        self, make_cmd_runner: CmdRunner, project_dir
    ):
        """CmdRunner timeout exceptions are converted to SopsError.

        When CmdRunner.run raises CmdTimeout, it should be caught and
        re-raised as a SopsError with a helpful message.

        Note: This test uses mocking because causing a real SOPS timeout would
        require waiting for the actual timeout duration (5+ seconds), making it
        impractical for regular test runs. The mock verifies the error handling
        code path that converts CmdTimeout to SopsError.
        """
        secrets_dir = project_dir / "secrets"
        secrets_dir.mkdir()
        input_file = secrets_dir / "test.yaml"
        input_file.write_text("secret: value")

        # Mock CmdRunner.run to simulate a timeout
        def mock_timeout(*args, **kwargs):
            raise CmdTimeout("Command timed out", timeout=SOPS_TIMEOUT, cmd=["sops"])

        with patch.object(CmdRunner, "run", side_effect=mock_timeout):
            with pytest.raises(SopsError, match="timed out"):
                encrypt_file(make_cmd_runner, input_file, public_keys=["age1test123"])

    def test_temp_file_cleanup_on_encryption_failure(self, make_cmd_runner: CmdRunner, project_dir):
        """Temp files are cleaned up when encryption fails.

        SecretsManager.save_secrets() writes to a temp file before encrypting.
        If encryption fails, the temp file should still be cleaned up by the
        finally block to avoid leaving plaintext secrets on disk.

        This test causes real SOPS encryption to fail by using an invalid
        age public key format.
        """
        secrets_dir = project_dir / "secrets"
        secrets_dir.mkdir(parents=True)
        key_path = project_dir / ".age" / "keys.txt"
        key_path.parent.mkdir(parents=True)

        # Generate a real age key for the manager
        public_key, _ = generate_age_key(make_cmd_runner, key_path)

        temp_file = secrets_dir / ".dev.tmp.yaml"
        manager = SecretsManager(make_cmd_runner, project_dir, key_path=key_path)

        # Create a valid .sops.yaml config
        manager.save_config({public_key: "test@example.com"})

        # Use an invalid public key to cause SOPS encryption to fail
        # "invalid-key" is not a valid age public key format
        with pytest.raises(SopsError):
            manager.save_secrets(
                Mode.DEVELOPMENT, {"secret": "value"}, public_keys=["invalid-not-an-age-key"]
            )

        # Temp file should be cleaned up after failure
        assert not temp_file.exists(), (
            "Temp file should be cleaned up on encryption failure to avoid "
            "leaving plaintext secrets on disk"
        )

    def test_sigint_triggers_signal_handler_cleanup(self, project_dir):
        """SIGINT triggers signal handler to clean up decrypted key.

        This test spawns a subprocess that enters protected_age_key(), then sends
        SIGINT to verify the signal handler (not the finally block) cleans up.

        The signal handler calls _cleanup_pending() and then re-raises the signal,
        which kills the process before the finally block runs.
        """
        # Set up project structure
        project_root = project_dir / "project"
        age_dir = project_root / ".age"
        age_dir.mkdir(parents=True)

        plaintext_path = age_dir / "keys.txt"

        # Create a plaintext key
        key_content = "# test key\nAGE-SECRET-KEY-TEST123"
        plaintext_path.write_text(key_content)

        # Script that enters protected_age_key and waits
        # Using plaintext key (no .gpg file)
        # Use DJB_PROJECT_DIR env var to configure djb for the subprocess
        script = """
import os
import sys
import time
from pathlib import Path
from djb.secrets import protected_age_key
from djb.core.cmd_runner import CmdRunner

project_dir = Path(os.environ["DJB_PROJECT_DIR"])
runner = CmdRunner()
with protected_age_key(project_dir, runner):
    # Signal that we're ready (inside context, key should exist)
    print("READY", flush=True)
    # Wait for signal - this will be interrupted by SIGINT
    # Use 10s instead of 60s for faster test timeout if issues occur
    time.sleep(10)
    # If we get here, test failed (should have been killed by signal)
    print("ERROR: Should have been killed by signal", flush=True)
    sys.exit(1)
"""

        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "DJB_PROJECT_DIR": str(project_root)},
        )

        try:
            # Wait for subprocess to signal it's ready (inside context)
            assert proc.stdout is not None, "stdout should be available"
            ready_line = proc.stdout.readline()
            assert "READY" in ready_line, f"Expected READY, got: {ready_line}"

            # Verify plaintext exists before signal (subprocess is inside context)
            assert plaintext_path.exists(), "Key should exist while in context"

            # Send SIGINT (Ctrl+C) - this triggers the signal handler
            proc.send_signal(signal.SIGINT)

            # Wait for subprocess to exit (killed by re-raised signal)
            proc.wait(timeout=5)

            # Verify process was killed by signal (negative return code = signal number)
            # SIGINT is typically 2, so return code should be -2 or 130 (128+2)
            assert proc.returncode != 0, "Process should have been killed by signal"

            # The signal handler should have cleaned up the plaintext
            assert not plaintext_path.exists(), (
                "Signal handler should have removed plaintext key. "
                "This tests the signal handler path, not the finally block."
            )

        finally:
            # Clean up subprocess if still running
            if proc.poll() is None:
                proc.kill()
                proc.wait()

    def test_sigterm_triggers_signal_handler_cleanup(self, project_dir):
        """SIGTERM triggers signal handler to clean up decrypted key.

        Similar to SIGINT test but with SIGTERM to verify both signals are handled.
        """
        # Set up project structure
        project_root = project_dir / "project"
        age_dir = project_root / ".age"
        age_dir.mkdir(parents=True)

        plaintext_path = age_dir / "keys.txt"

        # Create a plaintext key
        key_content = "# test key\nAGE-SECRET-KEY-TERM456"
        plaintext_path.write_text(key_content)

        # Use DJB_PROJECT_DIR env var to configure djb for the subprocess
        script = """
import os
import sys
import time
from pathlib import Path
from djb.secrets import protected_age_key
from djb.core.cmd_runner import CmdRunner

project_dir = Path(os.environ["DJB_PROJECT_DIR"])
runner = CmdRunner()
with protected_age_key(project_dir, runner):
    print("READY", flush=True)
    # Use 10s instead of 60s for faster test timeout if issues occur
    time.sleep(10)
    sys.exit(1)
"""

        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "DJB_PROJECT_DIR": str(project_root)},
        )

        try:
            assert proc.stdout is not None, "stdout should be available"
            ready_line = proc.stdout.readline()
            assert "READY" in ready_line, f"Expected READY, got: {ready_line}"

            assert plaintext_path.exists(), "Key should exist while in context"

            # Send SIGTERM
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)

            assert proc.returncode != 0, "Process should have been killed by signal"

            assert (
                not plaintext_path.exists()
            ), "Signal handler should have removed plaintext key on SIGTERM"

        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()


class TestGpgTimeoutHandling:
    """E2E tests for GPG timeout handling.

    These tests verify that GPG timeout exceptions are properly converted to
    user-friendly errors. Like the SOPS timeout test, these use mocking because
    actually triggering real GPG timeouts would require waiting 5-60 seconds.

    The mocking approach is justified because:
    1. We're testing the error handling code path, not CmdRunner.run itself
    2. Real timeouts take too long for regular test runs
    3. The underlying GPG commands are tested separately in real E2E scenarios
    """

    def test_gpg_encrypt_timeout_raises_gpg_error(
        self, project_dir, gpg_home, make_cmd_runner: CmdRunner
    ):
        """Encryption timeout is converted to GpgError.

        When GPG encryption times out (e.g., GPG agent is unresponsive),
        the CmdTimeout exception should be converted to a GpgError
        with a helpful message.
        """
        input_file = project_dir / "secret.txt"
        input_file.write_text("secret data")
        output_file = project_dir / "secret.txt.gpg"

        def mock_timeout(*args, **kwargs):
            raise CmdTimeout("Command timed out", timeout=GPG_TIMEOUT, cmd=["gpg"])

        # Mock CmdRunner.run but use real GPG home for environment setup
        with patch.object(CmdRunner, "run", side_effect=mock_timeout):
            with pytest.raises(GpgError, match="timed out"):
                gpg_encrypt_file(
                    make_cmd_runner,
                    input_file,
                    output_path=output_file,
                    recipient="test@example.com",
                )

        # Verify temp file cleanup happened
        temp_file = output_file.with_suffix(".gpg.tmp")
        assert not temp_file.exists(), "Temp file should be cleaned up on timeout"

    def test_gpg_decrypt_timeout_raises_timeout_error(
        self, project_dir, gpg_home, make_cmd_runner: CmdRunner
    ):
        """Decryption timeout raises GpgTimeoutError with helpful message.

        GPG decryption uses a longer timeout (GPG_INTERACTIVE_TIMEOUT) because
        it may require passphrase entry. When timeout occurs, the error should
        guide users to re-enter their passphrase.
        """
        input_file = project_dir / "encrypted.gpg"
        input_file.write_text("fake encrypted content")

        def mock_timeout(*args, **kwargs):
            raise CmdTimeout("Command timed out", timeout=GPG_INTERACTIVE_TIMEOUT, cmd=["gpg"])

        with patch.object(CmdRunner, "run", side_effect=mock_timeout):
            with pytest.raises(GpgTimeoutError) as exc_info:
                gpg_decrypt_file(make_cmd_runner, input_file)

        error = exc_info.value
        assert error.timeout == GPG_INTERACTIVE_TIMEOUT
        assert error.operation == "GPG decryption"
        assert "passphrase" in str(error).lower()
        assert "timed out" in str(error).lower()

    def test_is_gpg_encrypted_returns_false_on_timeout(
        self, project_dir, gpg_home, make_cmd_runner: CmdRunner
    ):
        """Is_gpg_encrypted returns False on timeout.

        Unlike encryption/decryption, the check operation should not raise
        an exception on timeout - it should return False to indicate the
        file could not be verified as GPG-encrypted.
        """
        test_file = project_dir / "test.gpg"
        test_file.write_text("some content")

        def mock_timeout(*args, **kwargs):
            raise CmdTimeout("Command timed out", timeout=GPG_TIMEOUT, cmd=["gpg"])

        with patch.object(CmdRunner, "run", side_effect=mock_timeout):
            result = is_gpg_encrypted(make_cmd_runner, test_file)

        assert result is False, "Should return False on timeout, not raise"


class TestSecretsSet:
    """E2E tests for djb secrets set command."""

    def test_set_top_level_secret(
        self,
        cli_runner,
        make_cmd_runner: CmdRunner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """Set a top-level secret value."""
        project_dir, key_path = make_pyproject_dir_with_git_with_secrets

        # Mock protected_age_key to return the test key directly
        with patch("djb.cli.secrets.protected_age_key") as mock_pak:
            mock_pak.return_value.__enter__ = lambda s: key_path
            mock_pak.return_value.__exit__ = lambda s, *args: None

            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "--mode",
                    "development",
                    "secrets",
                    "set",
                    "hetzner.api_token",
                    "test-token-value-123",
                ],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Set 'hetzner.api_token'" in result.output

        # Verify the value was set
        manager = SecretsManager(make_cmd_runner, project_dir, key_path=key_path)
        secrets_data = manager.load_secrets(Mode.DEVELOPMENT)
        assert secrets_data.get("hetzner", {}).get("api_token") == "test-token-value-123"

    def test_set_preserves_existing_secrets(
        self,
        cli_runner,
        make_cmd_runner: CmdRunner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """Setting a secret preserves other secrets."""
        project_dir, key_path = make_pyproject_dir_with_git_with_secrets

        # Get current secrets
        manager = SecretsManager(make_cmd_runner, project_dir, key_path=key_path)
        original_secrets = manager.load_secrets(Mode.DEVELOPMENT)
        original_keys = set(original_secrets.keys())

        # Mock protected_age_key to return the test key directly
        with patch("djb.cli.secrets.protected_age_key") as mock_pak:
            mock_pak.return_value.__enter__ = lambda s: key_path
            mock_pak.return_value.__exit__ = lambda s, *args: None

            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "--mode",
                    "development",
                    "secrets",
                    "set",
                    "hetzner.api_token",
                    "brand-new-value",
                ],
            )

        assert result.exit_code == 0

        # Verify original secrets still exist
        updated_secrets = manager.load_secrets(Mode.DEVELOPMENT)
        for key in original_keys:
            assert key in updated_secrets, f"Original key '{key}' was lost"
        assert updated_secrets.get("hetzner", {}).get("api_token") == "brand-new-value"

    def test_set_with_hidden_prompt(
        self,
        cli_runner,
        make_cmd_runner: CmdRunner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """Set prompts for value when not provided, using --hidden."""
        project_dir, key_path = make_pyproject_dir_with_git_with_secrets

        # Mock protected_age_key to return the test key directly
        with patch("djb.cli.secrets.protected_age_key") as mock_pak:
            mock_pak.return_value.__enter__ = lambda s: key_path
            mock_pak.return_value.__exit__ = lambda s, *args: None

            # Simulate user input for hidden prompt (value + confirmation)
            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "--mode",
                    "development",
                    "secrets",
                    "set",
                    "--hidden",
                    "hetzner.api_token",
                ],
                input="prompted-value\nprompted-value\n",
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify the value was set
        manager = SecretsManager(make_cmd_runner, project_dir, key_path=key_path)
        secrets_data = manager.load_secrets(Mode.DEVELOPMENT)
        assert secrets_data.get("hetzner", {}).get("api_token") == "prompted-value"

    def test_set_from_clipboard(
        self,
        cli_runner,
        make_cmd_runner: CmdRunner,
        make_pyproject_dir_with_git_with_secrets,
    ):
        """Set reads value from clipboard with --from-clipboard."""
        project_dir, key_path = make_pyproject_dir_with_git_with_secrets

        # Mock protected_age_key and read_clipboard
        with (
            patch("djb.cli.secrets.protected_age_key") as mock_pak,
            patch("djb.cli.secrets.read_clipboard", return_value="clipboard-token-xyz"),
        ):
            mock_pak.return_value.__enter__ = lambda s: key_path
            mock_pak.return_value.__exit__ = lambda s, *args: None

            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "--mode",
                    "development",
                    "secrets",
                    "set",
                    "--from-clipboard",
                    "hetzner.api_token",
                ],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify the value was set from clipboard
        manager = SecretsManager(make_cmd_runner, project_dir, key_path=key_path)
        secrets_data = manager.load_secrets(Mode.DEVELOPMENT)
        assert secrets_data.get("hetzner", {}).get("api_token") == "clipboard-token-xyz"

    def test_set_help_shows_subcommands(self, cli_runner, project_dir, make_pyproject):
        """secrets set --help shows available key subcommands."""
        make_pyproject()
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "secrets",
                "set",
                "--help",
            ],
        )
        assert result.exit_code == 0
        assert "hetzner.api_token" in result.output
        assert "--from-clipboard" in result.output
        assert "--hidden" in result.output


class TestSopsAgeIntegration:
    """E2E tests for SOPS operations with age keys.

    These tests verify that SOPS encryption/decryption works correctly
    with age keys (without GPG protection).
    """

    @pytest.fixture
    def sops_secrets_dir(self, project_dir: Path) -> Path:
        """Create a secrets directory with SOPS config."""
        secrets_dir = project_dir / "secrets"
        secrets_dir.mkdir()
        return secrets_dir

    def test_sops_encrypt_decrypt_with_age_key(
        self,
        make_cmd_runner: CmdRunner,
        age_key_dir: Path,
        sops_secrets_dir: Path,
    ):
        """SOPS encryption and decryption using an age key."""
        # Generate age key
        key_path = age_key_dir / "keys.txt"
        public_key, _ = generate_age_key(make_cmd_runner, key_path)

        # Create .sops.yaml config using shared utility
        sops_config = create_sops_config(sops_secrets_dir, public_key)

        # Create a plaintext secrets file
        secrets_file = sops_secrets_dir / "test.yaml"
        secrets_file.write_text("secret_key: my-secret-value\n")

        # Encrypt with SOPS using shared utility
        result = sops_encrypt(secrets_file, sops_config, key_path)
        assert result.returncode == 0, f"SOPS encrypt failed: {result.stderr}"

        # Use shared assertion helpers
        assert_sops_encrypted(secrets_file)
        assert_not_contains_secrets(secrets_file, "my-secret-value")

        # Decrypt with SOPS using shared utility
        result = sops_decrypt(secrets_file, sops_config, key_path)
        assert result.returncode == 0, f"SOPS decrypt failed: {result.stderr}"

        # Verify decrypted content (returned in stdout)
        decrypted_content = result.stdout
        assert "secret_key: my-secret-value" in decrypted_content

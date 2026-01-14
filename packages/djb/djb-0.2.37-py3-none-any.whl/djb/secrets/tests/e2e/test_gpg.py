"""Unit tests for djb.secrets.gpg module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.e2e_marker

from djb.core.cmd_runner import CmdRunner, CmdTimeout
from djb.secrets import (
    GpgError,
    check_gpg_installed,
    ensure_loopback_pinentry,
    generate_gpg_key,
    get_default_gpg_email,
    get_gpg_home,
    get_gpg_key_id,
    gpg_decrypt_file,
    gpg_encrypt_file,
    has_gpg_secret_key,
    init_gpg_agent_config,
    is_gpg_encrypted,
    setup_gpg_tty,
)


class TestCheckGpgInstalled:
    """Tests for check_gpg_installed."""

    @pytest.mark.parametrize(
        "which_result,expected",
        [
            ("/usr/bin/gpg", True),
            (None, False),
        ],
        ids=["installed", "not_installed"],
    )
    def test_returns_based_on_which(self, which_result, expected):
        """Returns True/False based on shutil.which result."""
        with patch("shutil.which", return_value=which_result):
            assert check_gpg_installed() is expected


class TestSetupGpgTty:
    """Tests for setup_gpg_tty."""

    def test_sets_gpg_tty_from_os_ttyname(self, make_cmd_runner: CmdRunner):
        """GPG_TTY is set from os.ttyname() when available."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("djb.secrets.gpg.os.open", return_value=3):
                with patch("djb.secrets.gpg.os.ttyname", return_value="/dev/ttys001"):
                    with patch("djb.secrets.gpg.os.close"):
                        with patch.object(
                            make_cmd_runner,
                            "run",
                            return_value=Mock(returncode=0, stdout="", stderr=""),
                        ):
                            env = setup_gpg_tty(make_cmd_runner)
                            assert env["GPG_TTY"] == "/dev/ttys001"

    def test_falls_back_to_dev_tty_on_error(self, make_cmd_runner: CmdRunner):
        """Falls back to /dev/tty when os.ttyname fails."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("djb.secrets.gpg.os.open", side_effect=OSError("no tty")):
                with patch.object(
                    make_cmd_runner,
                    "run",
                    return_value=Mock(returncode=0, stdout="", stderr=""),
                ):
                    env = setup_gpg_tty(make_cmd_runner)
                    assert env["GPG_TTY"] == "/dev/tty"

    def test_preserves_existing_gpg_tty(self, make_cmd_runner: CmdRunner):
        """Preserves existing GPG_TTY if set."""
        with patch.dict("os.environ", {"GPG_TTY": "/dev/pts/0"}):
            with patch.object(
                make_cmd_runner, "run", return_value=Mock(returncode=0, stdout="", stderr="")
            ):
                env = setup_gpg_tty(make_cmd_runner)
                assert env["GPG_TTY"] == "/dev/pts/0"

    def test_falls_back_to_dev_tty_when_no_terminal(self, make_cmd_runner: CmdRunner):
        """Falls back to /dev/tty when there's no controlling terminal."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("djb.secrets.gpg.os.open", side_effect=OSError("no terminal")):
                with patch.object(
                    make_cmd_runner,
                    "run",
                    return_value=Mock(returncode=0, stdout="", stderr=""),
                ):
                    env = setup_gpg_tty(make_cmd_runner)
                    assert env["GPG_TTY"] == "/dev/tty"


class TestIsGpgEncrypted:
    """Tests for is_gpg_encrypted."""

    def test_returns_false_for_nonexistent_file(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """is_gpg_encrypted returns False when file doesn't exist."""
        assert is_gpg_encrypted(make_cmd_runner, tmp_path / "nonexistent.gpg") is False

    def test_returns_true_for_gpg_file(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """is_gpg_encrypted returns True when gpg --list-packets finds encryption markers."""
        test_file = tmp_path / "test.gpg"
        test_file.write_text("fake gpg content")

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout=":pubkey enc packet:\n", stderr=""),
        ):
            assert is_gpg_encrypted(make_cmd_runner, test_file) is True

    def test_returns_false_for_plain_file(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """is_gpg_encrypted returns False when gpg --list-packets fails."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("plain text")

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=1, stdout="", stderr=""),
        ):
            assert is_gpg_encrypted(make_cmd_runner, test_file) is False

    @pytest.mark.parametrize(
        "exception",
        [
            FileNotFoundError(),
            CmdTimeout("Command timed out", timeout=5, cmd=["gpg", "--list-packets"]),
        ],
        ids=["gpg_error", "timeout"],
    )
    def test_returns_false_on_exception(
        self, tmp_path: Path, exception, make_cmd_runner: CmdRunner
    ):
        """is_gpg_encrypted returns False when runner.run raises FileNotFoundError or CmdTimeout."""
        test_file = tmp_path / "test.gpg"
        test_file.write_text("content")

        with patch.object(make_cmd_runner, "run", side_effect=exception):
            assert is_gpg_encrypted(make_cmd_runner, test_file) is False


class TestGpgEncryptFile:
    """Tests for gpg_encrypt_file."""

    def test_raises_on_timeout(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """gpg_encrypt_file raises GpgError when encryption times out."""
        input_file = tmp_path / "secret.txt"
        input_file.write_text("secret data")
        output_file = tmp_path / "secret.txt.gpg"

        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=5, cmd=["gpg", "--encrypt"]),
        ):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with patch(
                    "djb.secrets.gpg.get_default_gpg_email",
                    return_value="test@example.com",
                ):
                    with pytest.raises(GpgError, match="timed out"):
                        gpg_encrypt_file(make_cmd_runner, input_file, output_path=output_file)

        # Verify temp file is cleaned up on timeout
        temp_file = output_file.with_suffix(".gpg.tmp")
        assert not temp_file.exists()

    def test_encrypts_file_successfully(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """gpg_encrypt_file encrypts a file with GPG."""
        input_file = tmp_path / "secret.txt"
        input_file.write_text("secret data")
        output_file = tmp_path / "secret.txt.gpg"

        with patch.object(
            make_cmd_runner, "run", return_value=Mock(returncode=0, stdout="", stderr="")
        ) as mock_run:
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with patch(
                    "djb.secrets.gpg.get_default_gpg_email",
                    return_value="test@example.com",
                ):
                    # Create the temp file that would be created by gpg
                    temp_file = output_file.with_suffix(".gpg.tmp")
                    temp_file.write_text("encrypted")

                    result = gpg_encrypt_file(make_cmd_runner, input_file, output_path=output_file)

                    assert result == output_file
                    mock_run.assert_called_once()
                    call_args = mock_run.call_args
                    assert "gpg" in call_args[0][0]
                    assert "--encrypt" in call_args[0][0]

    def test_raises_on_encryption_failure(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """gpg_encrypt_file raises GpgError on encryption failure."""
        input_file = tmp_path / "secret.txt"
        input_file.write_text("secret data")
        output_file = tmp_path / "secret.txt.gpg"

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=1, stdout="", stderr="encryption failed"),
        ):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with patch(
                    "djb.secrets.gpg.get_default_gpg_email",
                    return_value="test@example.com",
                ):
                    with pytest.raises(GpgError, match="encryption failed"):
                        gpg_encrypt_file(make_cmd_runner, input_file, output_path=output_file)

    def test_uses_armor_by_default(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """gpg_encrypt_file uses ASCII armor by default."""
        input_file = tmp_path / "secret.txt"
        input_file.write_text("secret data")
        output_file = tmp_path / "secret.txt.gpg"

        with patch.object(
            make_cmd_runner, "run", return_value=Mock(returncode=0, stdout="", stderr="")
        ) as mock_run:
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with patch(
                    "djb.secrets.gpg.get_default_gpg_email",
                    return_value="test@example.com",
                ):
                    temp_file = output_file.with_suffix(".gpg.tmp")
                    temp_file.write_text("encrypted")

                    gpg_encrypt_file(make_cmd_runner, input_file, output_path=output_file)

                    call_args = mock_run.call_args[0][0]
                    assert "--armor" in call_args


class TestGpgDecryptFile:
    """Tests for gpg_decrypt_file.

    These tests mock run since gpg_decrypt_file uses loopback
    pinentry mode which requires full terminal access (interactive=True).
    """

    def test_decrypts_file_successfully(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """gpg_decrypt_file decrypts file successfully with output path."""
        input_file = tmp_path / "secret.txt.gpg"
        input_file.write_text("encrypted data")
        output_file = tmp_path / "secret.txt"

        # Create output file that would be created by gpg
        output_file.write_text("decrypted")

        with patch("djb.secrets.gpg.ensure_loopback_pinentry"):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with patch.object(
                    make_cmd_runner, "run", return_value=Mock(returncode=0, stdout="", stderr="")
                ) as mock_run:
                    gpg_decrypt_file(make_cmd_runner, input_file, output_path=output_file)

                    mock_run.assert_called_once()
                    call_args = mock_run.call_args
                    cmd = call_args[0][0]
                    assert "gpg" in cmd
                    assert "--decrypt" in cmd
                    assert "--pinentry-mode" in cmd
                    assert "loopback" in cmd
                    assert call_args[1]["interactive"] is True

    def test_returns_content_without_output_path(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """gpg_decrypt_file returns decrypted content when no output path specified."""
        input_file = tmp_path / "secret.txt.gpg"
        input_file.write_text("encrypted data")

        with patch("djb.secrets.gpg.ensure_loopback_pinentry"):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with patch.object(
                    make_cmd_runner,
                    "run",
                    return_value=Mock(returncode=0, stdout="decrypted content", stderr=""),
                ):
                    result = gpg_decrypt_file(make_cmd_runner, input_file)
                    assert result == "decrypted content"

    def test_raises_on_decryption_failure(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """gpg_decrypt_file raises GpgError on decryption failure."""
        input_file = tmp_path / "secret.txt.gpg"
        input_file.write_text("encrypted data")

        with patch("djb.secrets.gpg.ensure_loopback_pinentry"):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with patch.object(
                    make_cmd_runner,
                    "run",
                    return_value=Mock(returncode=1, stdout="decryption failed", stderr=""),
                ):
                    with pytest.raises(GpgError, match="decryption failed"):
                        gpg_decrypt_file(make_cmd_runner, input_file)

    def test_raises_on_failure_with_output_path(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """gpg_decrypt_file raises GpgError when decryption fails with output path."""
        input_file = tmp_path / "secret.txt.gpg"
        input_file.write_text("encrypted data")
        output_file = tmp_path / "secret.txt"

        with patch("djb.secrets.gpg.ensure_loopback_pinentry"):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with patch.object(
                    make_cmd_runner, "run", return_value=Mock(returncode=1, stdout="", stderr="")
                ):
                    with pytest.raises(GpgError, match="GPG decryption failed"):
                        gpg_decrypt_file(make_cmd_runner, input_file, output_path=output_file)


class TestGetGpgKeyId:
    """Tests for get_gpg_key_id."""

    def test_returns_key_id_when_found(self, make_cmd_runner: CmdRunner):
        """get_gpg_key_id returns key ID when GPG key exists for email."""
        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(
                returncode=0,
                stdout="sec:u:4096:1:ABCDEF1234567890:1234567890::u:::scESC:::\n",
                stderr="",
            ),
        ):
            result = get_gpg_key_id(make_cmd_runner, "test@example.com")
            assert result == "ABCDEF1234567890"

    def test_returns_none_when_not_found(self, make_cmd_runner: CmdRunner):
        """get_gpg_key_id returns None when no key found for email."""
        # GPG returns 2 when no key found
        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=2, stdout="", stderr=""),
        ):
            result = get_gpg_key_id(make_cmd_runner, "unknown@example.com")
            assert result is None

    def test_returns_none_on_error(self, make_cmd_runner: CmdRunner):
        """get_gpg_key_id returns None when runner.run raises FileNotFoundError."""
        with patch.object(make_cmd_runner, "run", side_effect=FileNotFoundError):
            result = get_gpg_key_id(make_cmd_runner, "test@example.com")
            assert result is None

    def test_returns_none_on_timeout(self, make_cmd_runner: CmdRunner):
        """get_gpg_key_id returns None when runner.run raises CmdTimeout."""
        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=60, cmd=["gpg", "--list-secret-keys"]),
        ):
            result = get_gpg_key_id(make_cmd_runner, "test@example.com")
            assert result is None


class TestGetDefaultGpgEmail:
    """Tests for get_default_gpg_email."""

    def test_returns_email_when_key_exists(self, make_cmd_runner: CmdRunner):
        """get_default_gpg_email extracts email from GPG UID.

        GPG --with-colons output format for uid line (field 10 is the UID):
        uid:validity:::::::::userid:comment:...
        """
        # Field 10 (index 9) contains the UID
        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(
                returncode=0,
                stdout=(
                    "sec:u:4096:1:ABCD1234:1234567890::u:::scESC:::\n"
                    "uid:u::::1234567890::0123456789ABCDEF:0:Test User <test@example.com>:\n"
                ),
                stderr="",
            ),
        ):
            result = get_default_gpg_email(make_cmd_runner)
            assert result == "test@example.com"

    def test_returns_none_when_no_keys(self, make_cmd_runner: CmdRunner):
        """get_default_gpg_email returns None when no GPG keys exist."""
        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="", stderr=""),
        ):
            result = get_default_gpg_email(make_cmd_runner)
            assert result is None

    def test_returns_none_on_error(self, make_cmd_runner: CmdRunner):
        """get_default_gpg_email returns None when runner.run raises FileNotFoundError."""
        with patch.object(make_cmd_runner, "run", side_effect=FileNotFoundError):
            result = get_default_gpg_email(make_cmd_runner)
            assert result is None

    def test_returns_none_on_timeout(self, make_cmd_runner: CmdRunner):
        """get_default_gpg_email returns None when runner.run raises CmdTimeout."""
        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=5, cmd=["gpg", "--list-secret-keys"]),
        ):
            result = get_default_gpg_email(make_cmd_runner)
            assert result is None


class TestHasGpgSecretKey:
    """Tests for has_gpg_secret_key."""

    def test_returns_true_when_secret_key_exists(self, make_cmd_runner: CmdRunner):
        """has_gpg_secret_key returns True when at least one secret key exists."""
        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(
                returncode=0,
                stdout="sec:u:4096:1:ABCD1234:1234567890::u:::scESC:::\n",
                stderr="",
            ),
        ):
            assert has_gpg_secret_key(make_cmd_runner) is True

    def test_returns_false_when_no_secret_keys(self, make_cmd_runner: CmdRunner):
        """has_gpg_secret_key returns False when no secret keys exist."""
        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="", stderr=""),
        ):
            assert has_gpg_secret_key(make_cmd_runner) is False

    def test_returns_false_on_error(self, make_cmd_runner: CmdRunner):
        """has_gpg_secret_key returns False when runner.run raises FileNotFoundError."""
        with patch.object(make_cmd_runner, "run", side_effect=FileNotFoundError):
            assert has_gpg_secret_key(make_cmd_runner) is False

    def test_returns_false_on_timeout(self, make_cmd_runner: CmdRunner):
        """has_gpg_secret_key returns False when runner.run raises CmdTimeout."""
        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=5, cmd=["gpg", "--list-secret-keys"]),
        ):
            assert has_gpg_secret_key(make_cmd_runner) is False


class TestGetGpgHome:
    """Tests for get_gpg_home."""

    def test_returns_gnupghome_env_var(self):
        """get_gpg_home returns GNUPGHOME if set."""
        with patch.dict("os.environ", {"GNUPGHOME": "/custom/gnupg"}):
            result = get_gpg_home()
            assert result == Path("/custom/gnupg")

    def test_returns_default_when_no_env_var(self):
        """get_gpg_home returns ~/.gnupg when GNUPGHOME not set."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("os.environ.get", return_value=None):
                result = get_gpg_home()
                assert result == Path.home() / ".gnupg"


class TestInitGpgAgentConfig:
    """Tests for init_gpg_agent_config."""

    def test_creates_config_when_missing(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """init_gpg_agent_config creates gpg-agent.conf file when it doesn't exist in GNUPGHOME."""
        gnupg_home = tmp_path / ".gnupg"

        with patch("djb.secrets.gpg.get_gpg_home", return_value=gnupg_home):
            with patch.object(
                make_cmd_runner, "run", return_value=Mock(returncode=0, stdout="", stderr="")
            ):
                result = init_gpg_agent_config(make_cmd_runner)

                assert result is True
                config_path = gnupg_home / "gpg-agent.conf"
                assert config_path.exists()
                content = config_path.read_text()
                assert "default-cache-ttl 28800" in content

    def test_skips_when_config_exists(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """init_gpg_agent_config doesn't overwrite existing config."""
        gnupg_home = tmp_path / ".gnupg"
        gnupg_home.mkdir()
        config_path = gnupg_home / "gpg-agent.conf"
        config_path.write_text("# custom config\n")

        with patch("djb.secrets.gpg.get_gpg_home", return_value=gnupg_home):
            result = init_gpg_agent_config(make_cmd_runner)

            assert result is False
            assert config_path.read_text() == "# custom config\n"

    def test_succeeds_when_gpgconf_reload_times_out(
        self, tmp_path: Path, make_cmd_runner: CmdRunner
    ):
        """init_gpg_agent_config succeeds even if gpgconf reload times out."""
        gnupg_home = tmp_path / ".gnupg"

        with patch("djb.secrets.gpg.get_gpg_home", return_value=gnupg_home):
            with patch.object(
                make_cmd_runner,
                "run",
                side_effect=CmdTimeout("Timed out", timeout=5, cmd=["gpgconf", "--reload"]),
            ):
                # Should still return True (config was created)
                result = init_gpg_agent_config(make_cmd_runner)

                assert result is True
                config_path = gnupg_home / "gpg-agent.conf"
                assert config_path.exists()
                content = config_path.read_text()
                assert "default-cache-ttl 28800" in content


class TestEnsureLoopbackPinentry:
    """Tests for ensure_loopback_pinentry."""

    def test_creates_config_when_missing(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """ensure_loopback_pinentry creates gpg-agent.conf with loopback when no config exists."""
        gnupg_home = tmp_path / ".gnupg"

        with patch("djb.secrets.gpg.get_gpg_home", return_value=gnupg_home):
            with patch.object(
                make_cmd_runner, "run", return_value=Mock(returncode=0, stdout="", stderr="")
            ):
                result = ensure_loopback_pinentry(make_cmd_runner)

                assert result is True
                config_path = gnupg_home / "gpg-agent.conf"
                assert config_path.exists()
                content = config_path.read_text()
                assert "allow-loopback-pinentry" in content

    def test_appends_to_existing_config(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """ensure_loopback_pinentry appends loopback option to existing config without it."""
        gnupg_home = tmp_path / ".gnupg"
        gnupg_home.mkdir()
        config_path = gnupg_home / "gpg-agent.conf"
        config_path.write_text("default-cache-ttl 28800\n")

        with patch("djb.secrets.gpg.get_gpg_home", return_value=gnupg_home):
            with patch.object(
                make_cmd_runner, "run", return_value=Mock(returncode=0, stdout="", stderr="")
            ):
                result = ensure_loopback_pinentry(make_cmd_runner)

                assert result is True
                content = config_path.read_text()
                assert "default-cache-ttl 28800" in content
                assert "allow-loopback-pinentry" in content

    def test_skips_when_already_configured(self, tmp_path: Path, make_cmd_runner: CmdRunner):
        """ensure_loopback_pinentry does nothing when loopback is already configured."""
        gnupg_home = tmp_path / ".gnupg"
        gnupg_home.mkdir()
        config_path = gnupg_home / "gpg-agent.conf"
        original_content = "default-cache-ttl 28800\nallow-loopback-pinentry\n"
        config_path.write_text(original_content)

        with patch("djb.secrets.gpg.get_gpg_home", return_value=gnupg_home):
            result = ensure_loopback_pinentry(make_cmd_runner)

            assert result is False
            assert config_path.read_text() == original_content


class TestGenerateGpgKey:
    """Tests for generate_gpg_key."""

    def test_generates_key_successfully(self, make_cmd_runner: CmdRunner):
        """generate_gpg_key generates key successfully."""
        with patch.object(
            make_cmd_runner, "run", return_value=Mock(returncode=0, stdout="", stderr="")
        ):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                result = generate_gpg_key(make_cmd_runner, "Test User", "test@example.com")
                assert result is True

    def test_raises_on_failure(self, make_cmd_runner: CmdRunner):
        """generate_gpg_key raises GpgError on key generation failure."""
        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=1, stdout="", stderr="key generation failed"),
        ):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with pytest.raises(GpgError, match="Failed to generate GPG key"):
                    generate_gpg_key(make_cmd_runner, "Test User", "test@example.com")

    def test_raises_on_timeout(self, make_cmd_runner: CmdRunner):
        """generate_gpg_key raises GpgError on timeout."""
        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=120, cmd=["gpg", "--quick-generate-key"]),
        ):
            with patch("djb.secrets.gpg.setup_gpg_tty", return_value={"GPG_TTY": "/dev/tty"}):
                with pytest.raises(GpgError, match="timed out"):
                    generate_gpg_key(make_cmd_runner, "Test User", "test@example.com")

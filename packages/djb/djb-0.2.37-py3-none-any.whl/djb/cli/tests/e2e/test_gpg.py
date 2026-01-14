"""End-to-end tests for GPG encryption and age key operations.

These tests use real GPG and age commands without mocking.
They properly isolate the test environment to avoid polluting the user's
age keys (GPG symmetric encryption doesn't affect the keyring).

Test classes:
- TestGpgEncryption: Raw GPG encryption/decryption operations
- TestAgeKeyProtection: Age key generation and GPG protection

Key isolation techniques:
- Age keys: Generated in tmp_path, never touching user's ~/.age
- GPG symmetric encryption: Uses passphrase via stdin, doesn't affect keyring

Requirements:
- GPG must be installed (brew install gnupg)
- age must be installed (brew install age)

Note: SOPS integration tests are in test_secrets.py (TestSopsAgeIntegration).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.cli.tests.e2e.fixtures import TEST_PASSPHRASE
from djb.core.cmd_runner import CmdRunner
from djb.secrets import (
    generate_age_key,
    get_public_key_from_private,
    is_gpg_encrypted,
)

from . import (
    age_decrypt,
    age_encrypt,
    assert_gpg_encrypted,
    assert_not_contains_secrets,
    gpg_decrypt,
    gpg_encrypt,
)

# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture(autouse=True)
def _require_gpg(require_gpg):
    """Skip tests if GPG is not installed (uses fixture from conftest)."""
    pass


class TestGpgEncryption:
    """E2E tests for GPG encryption/decryption."""

    def test_encrypt_and_decrypt_file(self, project_dir: Path):
        """Encrypting and decrypting a file with GPG."""
        # Create a test file
        plaintext_file = project_dir / "secret.txt"
        plaintext_content = "This is a secret message!"
        plaintext_file.write_text(plaintext_content)

        encrypted_file = project_dir / "secret.txt.gpg"

        # Encrypt the file using shared utility
        result = gpg_encrypt(plaintext_file, encrypted_file, TEST_PASSPHRASE)
        assert result.returncode == 0, f"Encryption failed: {result.stderr}"
        assert encrypted_file.exists()

        # Use shared assertion helpers
        assert_gpg_encrypted(encrypted_file)
        assert_not_contains_secrets(encrypted_file, plaintext_content)

        # Remove original plaintext
        plaintext_file.unlink()

        # Decrypt and verify content using shared utility
        result = gpg_decrypt(encrypted_file, plaintext_file, TEST_PASSPHRASE)
        assert result.returncode == 0, f"Decryption failed: {result.stderr}"

        decrypted_content = plaintext_file.read_text()
        assert decrypted_content == plaintext_content

    def test_decryption_fails_with_wrong_passphrase(self, project_dir: Path):
        """Decryption fails with wrong passphrase."""
        # Create and encrypt a test file
        plaintext_file = project_dir / "secret.txt"
        plaintext_file.write_text("Secret data!")

        encrypted_file = project_dir / "secret.txt.gpg"
        result = gpg_encrypt(plaintext_file, encrypted_file, TEST_PASSPHRASE)
        assert result.returncode == 0

        # Try to decrypt with wrong passphrase
        plaintext_file.unlink()
        result = gpg_decrypt(encrypted_file, plaintext_file, "wrong-passphrase")
        # Should fail
        assert result.returncode != 0

    def test_is_gpg_encrypted_nonexistent_file(self, project_dir: Path, make_cmd_runner: CmdRunner):
        """Is_gpg_encrypted returns False for non-existent file."""
        assert is_gpg_encrypted(make_cmd_runner, project_dir / "nonexistent.gpg") is False


class TestAgeKeyProtection:
    """E2E tests for protecting age keys with GPG."""

    def test_protect_and_unprotect_age_key(
        self,
        make_cmd_runner: CmdRunner,
        age_key_dir: Path,
    ):
        """Full lifecycle: generate key, protect, use, unprotect."""
        # Generate an age key
        key_path = age_key_dir / "keys.txt"
        public_key, private_key = generate_age_key(make_cmd_runner, key_path)

        assert key_path.exists()
        assert public_key.startswith("age1")

        # Save original key content for verification
        original_key_content = key_path.read_text()

        # Protect the key using shared GPG utility
        encrypted_path = key_path.parent / (key_path.name + ".gpg")

        result = gpg_encrypt(key_path, encrypted_path, TEST_PASSPHRASE)
        assert result.returncode == 0, f"GPG encrypt failed: {result.stderr}"

        # Remove plaintext key
        key_path.unlink()

        # Verify state
        assert not key_path.exists()
        assert encrypted_path.exists()

        # Use shared assertion helpers
        assert_gpg_encrypted(encrypted_path)
        assert_not_contains_secrets(encrypted_path, "AGE-SECRET-KEY")

        # Decrypt the key using shared utility
        result = gpg_decrypt(encrypted_path, key_path, TEST_PASSPHRASE)
        assert result.returncode == 0, f"GPG decrypt failed: {result.stderr}"

        # Verify the decrypted key matches the original
        assert key_path.read_text() == original_key_content

        # Verify we can read the public key from the decrypted file
        recovered_public = get_public_key_from_private(make_cmd_runner, key_path)
        assert recovered_public == public_key

    def test_age_key_generation_and_usage(
        self, make_cmd_runner: CmdRunner, age_key_dir: Path, project_dir: Path
    ):
        """Generated age keys work for encryption/decryption."""
        # Generate age key
        key_path = age_key_dir / "keys.txt"
        public_key, _ = generate_age_key(make_cmd_runner, key_path)

        # Create a test file to encrypt
        plaintext = project_dir / "secret.txt"
        plaintext.write_text("Super secret data!")

        encrypted = project_dir / "secret.txt.age"

        # Encrypt with age using shared utility
        result = age_encrypt(plaintext, encrypted, public_key)
        assert result.returncode == 0, f"age encrypt failed: {result.stderr}"

        # Decrypt with age using shared utility
        decrypted = project_dir / "secret.decrypted.txt"
        result = age_decrypt(encrypted, decrypted, key_path)
        assert result.returncode == 0, f"age decrypt failed: {result.stderr}"

        assert decrypted.read_text() == "Super secret data!"

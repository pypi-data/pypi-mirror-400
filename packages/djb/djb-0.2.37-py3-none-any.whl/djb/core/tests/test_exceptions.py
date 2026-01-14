"""Tests for djb.core.exceptions module."""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.core.exceptions import (
    DeploymentError,
    DjbError,
    HerokuAuthError,
    HerokuPushError,
    ImproperlyConfigured,
    ProjectNotFound,
    SecretsDecryptionFailed,
    SecretsError,
    SecretsFileNotFound,
    SecretsKeyNotFound,
)


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_exception_hierarchy(self):
        """DjbError is the base class for all djb exceptions."""
        # DjbError is base for all djb exceptions
        assert issubclass(ImproperlyConfigured, DjbError)
        assert issubclass(ProjectNotFound, DjbError)
        assert issubclass(SecretsError, DjbError)
        assert issubclass(DeploymentError, DjbError)

        # SecretsError subclasses
        assert issubclass(SecretsKeyNotFound, SecretsError)
        assert issubclass(SecretsDecryptionFailed, SecretsError)
        assert issubclass(SecretsFileNotFound, SecretsError)

        # DeploymentError subclasses
        assert issubclass(HerokuAuthError, DeploymentError)
        assert issubclass(HerokuPushError, DeploymentError)

    def test_can_catch_all_djb_errors(self):
        """All djb errors can be caught with DjbError."""
        exceptions = [
            ImproperlyConfigured("test"),
            ProjectNotFound(),
            SecretsKeyNotFound("/path/to/key"),
            SecretsDecryptionFailed("dev"),
            SecretsFileNotFound("dev", "/secrets"),
            HerokuAuthError(),
            HerokuPushError("myapp"),
        ]

        for exc in exceptions:
            with pytest.raises(DjbError):
                raise exc


class TestDjbError:
    """Tests for DjbError base class."""

    def test_basic_message(self):
        """DjbError stores and returns the message."""
        exc = DjbError("Something went wrong")
        assert str(exc) == "Something went wrong"


class TestImproperlyConfigured:
    """Tests for ImproperlyConfigured exception."""

    def test_message(self):
        """ImproperlyConfigured stores and returns the message."""
        exc = ImproperlyConfigured("Missing required setting")
        assert "Missing required setting" in str(exc)


class TestProjectNotFound:
    """Tests for ProjectNotFound exception."""

    def test_default_message(self):
        """ProjectNotFound has helpful default message."""
        exc = ProjectNotFound()
        message = str(exc)

        assert "djb project" in message.lower()
        assert "pyproject.toml" in message
        assert "djb" in message
        assert "DJB_PROJECT_DIR" in message


class TestSecretsKeyNotFound:
    """Tests for SecretsKeyNotFound exception."""

    def test_exception_message_and_attributes(self):
        """SecretsKeyNotFound stores key_path and includes it in the message."""
        exc = SecretsKeyNotFound("/path/to/.age/keys.txt")
        message = str(exc)

        # Message includes path and fix instructions
        assert "/path/to/.age/keys.txt" in message
        assert "djb init" in message

        # Stores key_path attribute
        assert exc.key_path == Path("/path/to/.age/keys.txt")


class TestSecretsDecryptionFailed:
    """Tests for SecretsDecryptionFailed exception."""

    def test_exception_message_and_attributes(self):
        """SecretsDecryptionFailed stores environment and includes it in the message."""
        exc = SecretsDecryptionFailed("production")
        message = str(exc)

        # Message includes environment and hints
        assert "production" in message
        assert "wrong age key" in message.lower() or "wrong key" in message.lower()
        assert ".age/keys.txt" in message

        # Stores environment attribute
        assert exc.environment == "production"

    def test_message_includes_detail_when_provided(self):
        """SecretsDecryptionFailed message includes optional detail parameter."""
        exc = SecretsDecryptionFailed("dev", detail="Wrong key format")
        message = str(exc)

        assert "dev" in message
        assert "Wrong key format" in message


class TestSecretsFileNotFound:
    """Tests for SecretsFileNotFound exception."""

    def test_exception_message_and_attributes(self):
        """SecretsFileNotFound stores environment and secrets_dir in message and attributes."""
        exc = SecretsFileNotFound("production", "/app/secrets")
        message = str(exc)

        # Message includes path and helpful commands
        assert "production.yaml" in message
        assert "/app/secrets" in message
        assert "djb secrets list" in message
        assert "djb init" in message

        # Stores attributes
        assert exc.environment == "production"
        assert exc.secrets_dir == Path("/app/secrets")
        assert exc.expected_path == Path("/app/secrets/production.yaml")


class TestHerokuAuthError:
    """Tests for HerokuAuthError exception."""

    def test_default_message(self):
        """HerokuAuthError has helpful message."""
        exc = HerokuAuthError()
        message = str(exc)

        assert "heroku" in message.lower()
        assert "login" in message.lower()
        assert "heroku login" in message


class TestHerokuPushError:
    """Tests for HerokuPushError exception."""

    def test_exception_message_and_attributes(self):
        """HerokuPushError stores app name and includes it in the message."""
        exc = HerokuPushError("myapp")
        message = str(exc)

        # Message includes app name and hints
        assert "myapp" in message
        assert "heroku git:remote" in message
        assert "heroku logs" in message

        # Stores app attribute
        assert exc.app == "myapp"

    def test_message_includes_detail_when_provided(self):
        """HerokuPushError message includes optional detail parameter."""
        exc = HerokuPushError("myapp", detail="Build failed")
        message = str(exc)

        assert "myapp" in message
        assert "Build failed" in message

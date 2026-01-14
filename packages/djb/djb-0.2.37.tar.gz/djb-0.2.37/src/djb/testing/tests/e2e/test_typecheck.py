"""Tests for djb.testing.typecheck module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.e2e_marker

from djb.core.cmd_runner import CmdRunner
from djb.testing.typecheck import run_typecheck
from djb.testing.typecheck import test_typecheck as typecheck_test_func


class TestRunTypecheck:
    """Tests for run_typecheck function."""

    def test_success(self, tmp_path):
        """run_typecheck succeeds on passing typecheck."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        with patch.object(
            CmdRunner,
            "run",
            return_value=Mock(returncode=0, stdout="0 errors", stderr=""),
        ) as mock_run:
            # Should not raise
            run_typecheck(tmp_path)

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["pyright"]
            assert call_args[1]["cwd"] == tmp_path

    def test_failure_raises_assertion(self, tmp_path):
        """run_typecheck raises AssertionError on typecheck failure."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        with patch.object(
            CmdRunner,
            "run",
            return_value=Mock(returncode=1, stdout="error: Cannot find module 'foo'", stderr=""),
        ):
            with pytest.raises(AssertionError) as exc_info:
                run_typecheck(tmp_path)

            assert "Type checking failed" in str(exc_info.value)
            assert "Cannot find module" in str(exc_info.value)

    def test_includes_stderr_in_error(self, tmp_path):
        """run_typecheck includes stderr in error message."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        with patch.object(
            CmdRunner,
            "run",
            return_value=Mock(returncode=1, stdout="", stderr="pyright: command not found"),
        ):
            with pytest.raises(AssertionError) as exc_info:
                run_typecheck(tmp_path)

            assert "stderr" in str(exc_info.value)
            assert "pyright: command not found" in str(exc_info.value)

    def test_auto_finds_project_root(self, tmp_path, monkeypatch):
        """Run_typecheck finds project root when not provided."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        monkeypatch.chdir(tmp_path)

        with patch.object(
            CmdRunner,
            "run",
            return_value=Mock(returncode=0, stdout="", stderr=""),
        ) as mock_run:
            run_typecheck()  # No argument

            call_args = mock_run.call_args
            assert call_args[1]["cwd"] == tmp_path

    def test_accepts_string_path(self, tmp_path):
        """Run_typecheck accepts string path."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        with patch.object(
            CmdRunner,
            "run",
            return_value=Mock(returncode=0, stdout="", stderr=""),
        ) as mock_run:
            run_typecheck(str(tmp_path))  # String instead of Path

            call_args = mock_run.call_args
            assert call_args[1]["cwd"] == tmp_path


class TestTestTypecheck:
    """Tests for test_typecheck pytest function."""

    def test_is_importable(self):
        """Test_typecheck can be imported."""
        assert callable(typecheck_test_func)

    def test_runs_typecheck(self, tmp_path, monkeypatch):
        """Test_typecheck runs typecheck."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        monkeypatch.chdir(tmp_path)

        with patch.object(
            CmdRunner,
            "run",
            return_value=Mock(returncode=0, stdout="", stderr=""),
        ):
            # Should not raise
            typecheck_test_func()

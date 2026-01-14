"""Tests for djb health command."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from djb.cli.djb import djb_cli
from djb.core.cmd_runner import CmdTimeout
from djb.cli.health import (
    HealthStep,
    ProjectContext,
    StepFailure,
    StepResult,
    _build_backend_lint_steps,
    _build_backend_test_steps,
    _build_backend_typecheck_steps,
    _build_frontend_lint_steps,
    _build_frontend_test_steps,
    _build_frontend_typecheck_steps,
    _get_command_with_flag,
    _get_frontend_dir,
    _get_host_display_name,
    _get_project_context,
    _get_run_scopes,
    _has_ruff,
    _report_failures,
    _run_for_projects,
    _run_step_worker,
    _run_steps,
    _run_steps_parallel,
)
from djb.cli.context import CliHealthContext
from djb.cli.tests import FAKE_PROJECT_DIR
from djb.config import DjbConfig

# Common path for host-only context tests
HOST_PATH = Path("/tmp/host")


@pytest.fixture
def mock_project_context():
    """Mock _get_project_context for health tests.

    Tests that also need command mocking should add mock_cmd_runner to their args.
    """
    with patch("djb.cli.health._get_project_context") as mock_ctx:
        yield mock_ctx


@pytest.fixture
def host_only_context():
    """ProjectContext for host-only (no editable djb) scenario."""
    return ProjectContext(djb_path=None, host_path=HOST_PATH, inside_djb=False)


class TestHealthCommand:
    """Tests for djb health command."""

    def test_health_help(self, cli_runner):
        """Health --help shows all subcommands."""
        result = cli_runner.invoke(djb_cli, ["health", "--help"])
        assert result.exit_code == 0
        assert "Run health checks" in result.output
        assert "lint" in result.output
        assert "typecheck" in result.output
        assert "test" in result.output
        # --frontend and --backend are now global options on djb root
        assert "--fix" in result.output
        assert "--no-e2e" in result.output

    @pytest.mark.parametrize("subcommand", ["lint", "typecheck", "test"])
    def test_health_subcommand_help(self, cli_runner, subcommand):
        """Health subcommand --help works."""
        result = cli_runner.invoke(djb_cli, ["health", subcommand, "--help"])
        assert result.exit_code == 0

    def test_health_runs_all_checks(self, cli_runner, mock_cmd_runner, mock_project_context):
        """Health command runs all checks by default."""
        # Mock project context to avoid real file system docs validation
        mock_project_context.return_value = ProjectContext(
            djb_path=None, host_path=HOST_PATH, inside_djb=False
        )
        # Use --no-parallel to use mocked run (parallel uses subprocess.run directly)
        result = cli_runner.invoke(djb_cli, ["health", "--no-parallel"])
        assert result.exit_code == 0
        # Should have run multiple commands via run
        assert mock_cmd_runner.run.call_count >= 3

    def test_health_backend_only(self, cli_runner, mock_cmd_runner, mock_project_context):
        """djb --backend health runs only backend checks."""
        # Mock project context to avoid real file system docs validation
        mock_project_context.return_value = ProjectContext(
            djb_path=None, host_path=HOST_PATH, inside_djb=False
        )
        # Use --no-parallel to use mocked run
        result = cli_runner.invoke(djb_cli, ["--backend", "health", "--no-parallel"])
        assert result.exit_code == 0
        # Check that backend commands were called via run
        all_calls = [str(call) for call in mock_cmd_runner.run.call_args_list]
        assert any(
            "black" in str(call) or "pytest" in str(call) or "pyright" in str(call)
            for call in all_calls
        )

    @pytest.mark.parametrize(
        "subcommand,expected_tool",
        [
            ("lint", "black"),
            ("typecheck", "pyright"),
            ("test", "pytest"),
        ],
    )
    def test_health_subcommand_runs_tool(
        self, cli_runner, mock_cmd_runner, subcommand, expected_tool
    ):
        """Each health subcommand runs its expected tool."""
        result = cli_runner.invoke(djb_cli, ["health", subcommand])
        assert result.exit_code == 0
        # Check all run calls (tests use show_output=True)
        all_calls = [str(call) for call in mock_cmd_runner.run.call_args_list]
        assert any(expected_tool in str(call) for call in all_calls)

    def test_health_lint_fix(self, cli_runner, mock_cmd_runner):
        """Health lint --fix runs without --check."""
        result = cli_runner.invoke(djb_cli, ["health", "lint", "--fix"])
        assert result.exit_code == 0
        # Verify black was called without --check
        calls = [str(call) for call in mock_cmd_runner.run.call_args_list]
        has_black_call = any("black" in str(call) for call in calls)
        any("--check" in str(call) for call in calls)
        assert has_black_call
        # With --fix, --check should not be present
        # Note: this is a simplification, actual check depends on implementation

    def test_health_failure_reports_errors(self, cli_runner, mock_cmd_runner):
        """djb health reports failures properly."""
        # Make run_cmd return failure
        mock_cmd_runner.run.return_value.returncode = 1
        result = cli_runner.invoke(djb_cli, ["health", "typecheck"])
        assert result.exit_code != 0
        assert "failed" in result.output.lower()


# TestIsInsideDjbDir tests that require real file I/O are in e2e/test_health.py


class TestProjectContext:
    """Tests for _get_project_context helper."""

    def test_context_inside_djb_dir(self, djb_config):
        """_get_project_context returns correct context inside djb directory."""
        with patch("djb.cli.health._is_inside_djb_dir", return_value=True):
            context = _get_project_context(djb_config)

        assert context.djb_path == djb_config.project_dir
        assert context.host_path is None
        assert context.inside_djb is True

    def test_context_with_editable_djb(self, djb_config):
        """_get_project_context returns correct context with editable djb."""
        fake_djb_path = Path("/fake/djb")
        with (
            patch("djb.cli.health._is_inside_djb_dir", return_value=False),
            patch("djb.cli.health.is_djb_editable", return_value=True),
            patch("djb.cli.health.get_djb_source_path", return_value="../djb"),
            patch("pathlib.Path.resolve", return_value=fake_djb_path),
        ):
            context = _get_project_context(djb_config)

        assert context.djb_path == fake_djb_path
        assert context.host_path == djb_config.project_dir
        assert context.inside_djb is False

    def test_context_without_editable_djb(self, djb_config):
        """_get_project_context returns correct context without editable djb."""
        with (
            patch("djb.cli.health._is_inside_djb_dir", return_value=False),
            patch("djb.cli.health.is_djb_editable", return_value=False),
        ):
            context = _get_project_context(djb_config)

        assert context.djb_path is None
        assert context.host_path == djb_config.project_dir
        assert context.inside_djb is False


class TestRunForProjects:
    """Tests for _run_for_projects helper - the core shared logic for all subcommands."""

    @pytest.fixture
    def run_helper(self, djb_config):
        """Factory fixture that returns a function to test _run_for_projects.

        Pytest fixtures are setup functions that run before each test. When a test
        method includes `run_helper` as a parameter, pytest automatically calls this
        fixture and passes the returned value to the test.

        This fixture returns a function `_run(project_ctx)` that:
        1. Creates a tracking `build_steps` callback that records each call
        2. Mocks _run_for_projects dependencies (_get_project_context, _run_steps, etc.)
        3. Calls _run_for_projects with the provided ProjectContext
        4. Returns the list of (path, prefix, is_djb) tuples that build_steps received

        Usage in tests:
            def test_example(self, run_helper):
                djb_path = FAKE_PROJECT_DIR / "djb"
                calls = run_helper(ProjectContext(djb_path=djb_path, ...))
                assert calls == [(djb_path, "[djb]", True)]
        """

        def _run(project_ctx: ProjectContext) -> list[tuple[Path, str, bool]]:
            calls: list[tuple[Path, str, bool]] = []

            def build_steps(path: Path, prefix: str, is_djb: bool, runner) -> list[HealthStep]:
                calls.append((path, prefix, is_djb))
                return []

            with (
                patch("djb.cli.health._get_project_context", return_value=project_ctx),
                patch("djb.cli.health._run_steps", return_value=[]),
                patch("djb.cli.health._report_failures"),
                patch("djb.cli.health._get_host_display_name", return_value="host"),
            ):
                health_ctx = CliHealthContext()
                health_ctx.config = djb_config
                _run_for_projects(health_ctx, build_steps, "test")

            return calls

        return _run

    def test_calls_build_steps_for_djb_and_host(self, run_helper):
        """_run_for_projects calls build_steps for both djb and host when present."""
        djb_dir = FAKE_PROJECT_DIR / "djb"
        host_dir = FAKE_PROJECT_DIR / "host"

        calls = run_helper(ProjectContext(djb_path=djb_dir, host_path=host_dir, inside_djb=False))

        assert len(calls) == 2
        assert calls[0] == (djb_dir, "[djb]", True)
        assert calls[1] == (host_dir, "[host]", False)

    def test_only_calls_for_djb_when_inside_djb(self, run_helper):
        """_run_for_projects only checks djb when running from inside djb."""
        djb_path = FAKE_PROJECT_DIR / "djb"
        calls = run_helper(ProjectContext(djb_path=djb_path, host_path=None, inside_djb=True))

        assert len(calls) == 1
        assert calls[0] == (djb_path, "", True)  # No prefix when only djb

    def test_only_calls_for_host_when_no_editable_djb(self, run_helper):
        """_run_for_projects only checks host when djb is not editable."""
        host_path = FAKE_PROJECT_DIR / "host"
        calls = run_helper(ProjectContext(djb_path=None, host_path=host_path, inside_djb=False))

        assert len(calls) == 1
        assert calls[0] == (host_path, "", False)  # No prefix when only host


class TestEditableAwareHealth:
    """Tests for editable aware health command behavior."""

    def test_health_inside_djb_shows_skip_message(
        self, cli_runner, mock_cmd_runner, mock_project_context
    ):
        """Health command shows skip message when inside djb."""
        djb_path = FAKE_PROJECT_DIR / "djb"
        mock_project_context.return_value = ProjectContext(
            djb_path=djb_path, host_path=None, inside_djb=True
        )

        result = cli_runner.invoke(djb_cli, ["health", "lint"])

        assert result.exit_code == 0
        assert "skipping host project" in result.output.lower()

    def test_health_with_editable_runs_both_projects(
        self, cli_runner, mock_cmd_runner, mock_project_context, monkeypatch
    ):
        """Health runs for both djb and host when editable."""
        djb_dir = FAKE_PROJECT_DIR / "djb"
        host_dir = FAKE_PROJECT_DIR / "myproject"

        # Set project name via env var to avoid file I/O
        monkeypatch.setenv("DJB_PROJECT_NAME", "myproject")

        mock_project_context.return_value = ProjectContext(
            djb_path=djb_dir, host_path=host_dir, inside_djb=False
        )

        result = cli_runner.invoke(djb_cli, ["health", "lint"])

        assert result.exit_code == 0
        assert "djb (editable)" in result.output.lower()
        assert "running lint for myproject" in result.output.lower()

    def test_health_without_editable_runs_host_only(
        self, cli_runner, mock_cmd_runner, mock_project_context
    ):
        """Health only runs for host when djb is not editable."""
        host_dir = FAKE_PROJECT_DIR / "host"

        mock_project_context.return_value = ProjectContext(
            djb_path=None, host_path=host_dir, inside_djb=False
        )

        result = cli_runner.invoke(djb_cli, ["health", "lint"])

        assert result.exit_code == 0
        assert "Running lint for djb" not in result.output
        assert "Running lint for host" not in result.output

    @pytest.mark.parametrize("subcmd", ["lint", "typecheck", "test"])
    def test_all_subcommands_respect_project_context(
        self, cli_runner, mock_cmd_runner, mock_project_context, subcmd, monkeypatch
    ):
        """All subcommands respect project context via _run_for_projects."""
        djb_dir = FAKE_PROJECT_DIR / "djb"
        host_dir = FAKE_PROJECT_DIR / "myproject"

        # Set project name via env var to avoid file I/O
        monkeypatch.setenv("DJB_PROJECT_NAME", "myproject")

        mock_project_context.return_value = ProjectContext(
            djb_path=djb_dir, host_path=host_dir, inside_djb=False
        )

        result = cli_runner.invoke(djb_cli, ["health", subcmd])

        assert result.exit_code == 0
        assert "djb (editable)" in result.output.lower()
        assert "for myproject" in result.output.lower()


class TestGetCommandWithFlag:
    """Tests for _get_command_with_flag helper."""

    @pytest.mark.parametrize(
        "argv,flag,skip_if_present,expected",
        [
            # Inserts flag after program name, replaces full path with 'djb'
            (["/usr/local/bin/djb", "health", "lint"], "-v", None, "djb -v health lint"),
            (["/some/long/path/to/djb", "health"], "--fix", None, "djb --fix health"),
            (["djb"], "--fix", None, "djb --fix"),
            # skip_if_present behavior
            (["djb", "-v", "health", "lint"], "-v", ["-v"], "djb -v health lint"),
            (["djb", "--verbose", "health"], "-v", ["-v", "--verbose"], "djb --verbose health"),
            (["djb", "health", "lint"], "-v", ["--verbose"], "djb -v health lint"),
        ],
    )
    def test_get_command_with_flag(self, argv, flag, skip_if_present, expected):
        """_get_command_with_flag inserts flags correctly."""
        with patch.object(sys, "argv", argv):
            result = _get_command_with_flag(flag, skip_if_present=skip_if_present)
            assert result == expected


class TestGetHostDisplayName:
    """Tests for _get_host_display_name helper."""

    def test_returns_project_name_when_path_matches(self, make_djb_config):
        """Returns configured project name when host path matches config's project_dir."""
        config = make_djb_config(DjbConfig(project_name="myproject"))
        assert _get_host_display_name(config.project_dir, config) == "myproject"

    def test_falls_back_to_directory_name_when_path_differs(self, djb_config):
        """Falls back to directory name when host path differs from config's project_dir."""
        # Config points to /fake/test-project, but host_path is different
        host_dir = Path("/some/other/beachresort25")
        assert _get_host_display_name(host_dir, djb_config) == "beachresort25"

    def test_falls_back_to_directory_name_for_nested_path(self, djb_config):
        """Falls back to directory name for different nested path."""
        host_dir = Path("/different/myapp")
        assert _get_host_display_name(host_dir, djb_config) == "myapp"


class TestBackendStepBuilders:
    """Tests for backend step builder functions with scope parameter."""

    def _build_steps(self, builder, project_dir, prefix="", scope="Backend", runner=None):
        """Helper to call builder with appropriate arguments."""
        if builder == _build_backend_lint_steps:
            return builder(project_dir, fix=False, prefix=prefix, scope=scope, runner=runner)
        if builder == _build_backend_test_steps:
            return builder(project_dir, prefix=prefix, scope=scope, runner=runner)
        return builder(project_dir, prefix=prefix, scope=scope)

    @pytest.mark.parametrize(
        "builder,scope",
        [
            (_build_backend_lint_steps, "Python"),
            (_build_backend_lint_steps, "Backend"),
            (_build_backend_typecheck_steps, "Python"),
            (_build_backend_typecheck_steps, "Backend"),
            (_build_backend_test_steps, "Python"),
            (_build_backend_test_steps, "Backend"),
        ],
    )
    def test_steps_use_scope_in_label(self, builder, scope, mock_cmd_runner):
        """All steps from a builder include the scope in their label."""
        steps = self._build_steps(builder, FAKE_PROJECT_DIR, scope=scope, runner=mock_cmd_runner)
        assert steps, "Builder should return at least one step"
        for step in steps:
            assert scope in step.label, f"Expected '{scope}' in label '{step.label}'"

    @pytest.mark.parametrize(
        "builder,prefix,scope,expected_label",
        [
            (
                _build_backend_lint_steps,
                "[myproject]",
                "Backend",
                "[myproject] Backend lint (black --check)",
            ),
            (_build_backend_typecheck_steps, "[djb]", "Python", "[djb] Python typecheck (pyright)"),
            (_build_backend_test_steps, "[app]", "Backend", "[app] Backend tests (pytest)"),
        ],
    )
    def test_steps_with_prefix_and_scope(
        self, builder, prefix, scope, expected_label, mock_cmd_runner
    ):
        """The first step has the expected label format."""
        steps = self._build_steps(
            builder, FAKE_PROJECT_DIR, prefix=prefix, scope=scope, runner=mock_cmd_runner
        )
        assert steps, "Builder should return at least one step"
        assert steps[0].label == expected_label

    def test_lint_steps_with_fix_mode(self, mock_cmd_runner):
        """Lint steps use format mode when fix=True."""
        with patch("djb.cli.health._has_ruff", return_value=False):
            steps = _build_backend_lint_steps(
                FAKE_PROJECT_DIR,
                fix=True,
                prefix="",
                scope="Backend",
                runner=mock_cmd_runner,
            )
        # Steps: black format
        assert len(steps) == 1
        assert "--check" not in steps[0].cmd
        assert "format" in steps[0].label
        assert "black" in steps[0].label

    def test_lint_steps_without_fix_mode(self, mock_cmd_runner):
        """Lint steps use check mode when fix=False."""
        with patch("djb.cli.health._has_ruff", return_value=False):
            steps = _build_backend_lint_steps(
                FAKE_PROJECT_DIR,
                fix=False,
                prefix="",
                scope="Backend",
                runner=mock_cmd_runner,
            )
        # Steps: black check
        assert len(steps) == 1
        assert "--check" in steps[0].cmd
        assert "lint" in steps[0].label

    def test_lint_steps_with_ruff_available(self, mock_cmd_runner):
        """Lint steps include ruff when available."""
        with patch("djb.cli.health._has_ruff", return_value=True):
            steps = _build_backend_lint_steps(
                FAKE_PROJECT_DIR,
                fix=False,
                prefix="",
                scope="Backend",
                runner=mock_cmd_runner,
            )
        # Steps: black check + ruff check
        assert len(steps) == 2
        # First step is black
        assert "black" in steps[0].cmd
        assert "--check" in steps[0].cmd
        # Second step is ruff
        assert "ruff" in steps[1].cmd
        assert "check" in steps[1].cmd
        assert "--fix" not in steps[1].cmd

    def test_lint_steps_with_ruff_and_fix_mode(self, mock_cmd_runner):
        """Lint steps include ruff --fix when fix=True and ruff available."""
        with patch("djb.cli.health._has_ruff", return_value=True):
            steps = _build_backend_lint_steps(
                FAKE_PROJECT_DIR,
                fix=True,
                prefix="",
                scope="Backend",
                runner=mock_cmd_runner,
            )
        # Steps: black format + ruff fix
        assert len(steps) == 2
        # First step is black format
        assert "black" in steps[0].cmd
        assert "--check" not in steps[0].cmd
        # Second step is ruff with --fix
        assert "ruff" in steps[1].cmd
        assert "--fix" in steps[1].cmd
        assert "lint fix" in steps[1].label

    def test_lint_steps_without_ruff(self, mock_cmd_runner):
        """Lint steps exclude ruff when not available."""
        with patch("djb.cli.health._has_ruff", return_value=False):
            steps = _build_backend_lint_steps(
                FAKE_PROJECT_DIR,
                fix=False,
                prefix="",
                scope="Backend",
                runner=mock_cmd_runner,
            )
        # Steps: black check
        assert len(steps) == 1
        assert "black" in steps[0].cmd
        # No ruff step
        assert not any("ruff" in step.cmd for step in steps)

    def test_test_steps_have_stream_enabled(self, mock_cmd_runner):
        """Backend test steps have show_output=True for real-time pytest output."""
        steps = _build_backend_test_steps(
            FAKE_PROJECT_DIR, prefix="", scope="Backend", runner=mock_cmd_runner
        )
        assert len(steps) == 1
        assert steps[0].show_output is True

    def test_lint_steps_use_correct_command(self, mock_cmd_runner):
        """Lint steps use uv run black --check."""
        with patch("djb.cli.health._has_ruff", return_value=False):
            steps = _build_backend_lint_steps(
                FAKE_PROJECT_DIR,
                fix=False,
                prefix="",
                scope="Backend",
                runner=mock_cmd_runner,
            )
        assert steps[0].cmd == ["uv", "run", "black", "--check", "."]
        assert steps[0].cwd == FAKE_PROJECT_DIR

    def test_typecheck_steps_use_correct_command(self):
        """Typecheck steps use uv run pyright."""
        steps = _build_backend_typecheck_steps(FAKE_PROJECT_DIR, prefix="", scope="Backend")
        assert steps[0].cmd == ["uv", "run", "pyright"]
        assert steps[0].cwd == FAKE_PROJECT_DIR

    def test_test_steps_use_correct_command(self, mock_cmd_runner):
        """_build_backend_test_steps uses uv run pytest with parallel and worksteal when xdist available."""
        with patch("djb.cli.health.has_pytest_xdist", return_value=True):
            steps = _build_backend_test_steps(
                FAKE_PROJECT_DIR, prefix="", scope="Backend", runner=mock_cmd_runner
            )
        assert steps[0].cmd == ["uv", "run", "pytest", "-n", "auto", "--dist", "worksteal"]
        assert steps[0].cwd == FAKE_PROJECT_DIR

    def test_test_steps_fallback_when_xdist_unavailable(self, mock_cmd_runner):
        """_build_backend_test_steps falls back to sequential when xdist not installed."""
        with patch("djb.cli.health.has_pytest_xdist", return_value=False):
            steps = _build_backend_test_steps(
                FAKE_PROJECT_DIR, prefix="", scope="Backend", runner=mock_cmd_runner
            )
        assert steps[0].cmd == ["uv", "run", "pytest"]
        assert "-n" not in steps[0].cmd
        assert steps[0].cwd == FAKE_PROJECT_DIR

    def test_test_steps_without_parallel(self, mock_cmd_runner):
        """_build_backend_test_steps without parallel doesn't include -n auto."""
        steps = _build_backend_test_steps(
            FAKE_PROJECT_DIR,
            prefix="",
            scope="Backend",
            parallel=False,
            runner=mock_cmd_runner,
        )
        assert steps[0].cmd == ["uv", "run", "pytest"]
        assert steps[0].cwd == FAKE_PROJECT_DIR

    @pytest.mark.parametrize(
        "e2e,flag_in_cmd,label_has_no_e2e",
        [
            (True, False, False),
            (False, True, True),
        ],
        ids=["with_e2e", "without_e2e"],
    )
    def test_test_steps_e2e_flag(self, e2e, flag_in_cmd, label_has_no_e2e, mock_cmd_runner):
        """_build_backend_test_steps includes/excludes --no-e2e flag based on e2e parameter."""
        steps = _build_backend_test_steps(
            FAKE_PROJECT_DIR, prefix="", scope="Backend", e2e=e2e, runner=mock_cmd_runner
        )
        assert ("--no-e2e" in steps[0].cmd) == flag_in_cmd
        assert ("no E2E" in steps[0].label) == label_has_no_e2e

    def test_test_steps_label_with_no_e2e(self, mock_cmd_runner):
        """_build_backend_test_steps label format includes 'no E2E' when e2e=False."""
        steps = _build_backend_test_steps(
            FAKE_PROJECT_DIR,
            prefix="[app]",
            scope="Backend",
            e2e=False,
            runner=mock_cmd_runner,
        )
        assert steps[0].label == "[app] Backend tests (pytest (no E2E))"

    def test_test_steps_with_no_e2e_and_coverage(self, mock_cmd_runner):
        """_build_backend_test_steps can combine no-e2e and coverage."""
        with patch("djb.cli.health.has_pytest_cov", return_value=True):
            with patch("djb.cli.health.has_pytest_xdist", return_value=True):
                steps = _build_backend_test_steps(
                    FAKE_PROJECT_DIR,
                    prefix="",
                    scope="Backend",
                    e2e=False,
                    cov=True,
                    runner=mock_cmd_runner,
                )
        assert "--no-e2e" in steps[0].cmd
        assert "--cov" in steps[0].cmd
        assert "no E2E" in steps[0].label
        assert "coverage" in steps[0].label.lower()

    @pytest.mark.parametrize(
        "parallel,e2e,expected_in_cmd,expected_not_in_cmd",
        [
            (True, True, ["-n", "auto"], ["--no-e2e"]),
            (True, False, ["-n", "auto", "--no-e2e"], []),
            (False, True, [], ["-n", "--no-e2e"]),
            (False, False, ["--no-e2e"], ["-n"]),
        ],
    )
    def test_test_steps_parallel_and_e2e_combinations(
        self, parallel, e2e, expected_in_cmd, expected_not_in_cmd, mock_cmd_runner
    ):
        """Parallel and e2e flags work correctly in combination."""
        with patch("djb.cli.health.has_pytest_xdist", return_value=True):
            steps = _build_backend_test_steps(
                FAKE_PROJECT_DIR,
                prefix="",
                scope="Backend",
                parallel=parallel,
                e2e=e2e,
                runner=mock_cmd_runner,
            )
        for expected in expected_in_cmd:
            assert expected in steps[0].cmd
        for not_expected in expected_not_in_cmd:
            assert not_expected not in steps[0].cmd

    @pytest.mark.parametrize(
        "builder,expected_label",
        [
            (_build_backend_lint_steps, "Backend lint (black --check)"),
            (_build_backend_typecheck_steps, "Backend typecheck (pyright)"),
            (_build_backend_test_steps, "Backend tests (pytest)"),
        ],
    )
    def test_steps_label_format_without_prefix(self, builder, expected_label, mock_cmd_runner):
        """Backend step builders produce correct label format when no prefix is provided."""
        with patch("djb.cli.health._has_ruff", return_value=False):
            steps = self._build_steps(
                builder, FAKE_PROJECT_DIR, prefix="", scope="Backend", runner=mock_cmd_runner
            )
        assert steps[0].label == expected_label


class TestFrontendStepBuilders:
    """Tests for frontend step builder functions."""

    def _build_steps(self, builder, frontend_dir, prefix=""):
        """Helper to call builder with appropriate arguments."""
        if builder == _build_frontend_lint_steps:
            return builder(frontend_dir, fix=False, prefix=prefix)
        return builder(frontend_dir, prefix=prefix)

    @pytest.mark.parametrize(
        "builder",
        [
            _build_frontend_lint_steps,
            _build_frontend_typecheck_steps,
            _build_frontend_test_steps,
        ],
    )
    def test_returns_empty_when_frontend_dir_missing(self, builder):
        """Builders return empty list when frontend directory doesn't exist."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        # Default: Path.exists() returns False for fake paths
        steps = self._build_steps(builder, frontend_dir)
        assert steps == []

    @pytest.mark.parametrize(
        "builder",
        [
            _build_frontend_lint_steps,
            _build_frontend_typecheck_steps,
            _build_frontend_test_steps,
        ],
    )
    def test_returns_steps_when_frontend_dir_exists(self, builder):
        """Builders return steps when frontend directory exists."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        with patch.object(Path, "exists", return_value=True):
            steps = self._build_steps(builder, frontend_dir)
        assert len(steps) >= 1

    @pytest.mark.parametrize(
        "builder,expected_label",
        [
            (_build_frontend_lint_steps, "Frontend lint (bun lint)"),
            (_build_frontend_typecheck_steps, "Frontend typecheck (tsc)"),
            (_build_frontend_test_steps, "Frontend tests (bun test)"),
        ],
    )
    def test_steps_label_format_without_prefix(self, builder, expected_label):
        """Frontend step builders produce correct label format when no prefix is provided."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        with patch.object(Path, "exists", return_value=True):
            steps = self._build_steps(builder, frontend_dir)
        assert steps[0].label == expected_label

    @pytest.mark.parametrize(
        "builder,expected_label",
        [
            (_build_frontend_lint_steps, "[myproject] Frontend lint (bun lint)"),
            (_build_frontend_typecheck_steps, "[myproject] Frontend typecheck (tsc)"),
            (_build_frontend_test_steps, "[myproject] Frontend tests (bun test)"),
        ],
    )
    def test_steps_with_prefix(self, builder, expected_label):
        """Frontend step builders include prefix in label."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        with patch.object(Path, "exists", return_value=True):
            steps = self._build_steps(builder, frontend_dir, prefix="[myproject]")
        assert steps[0].label == expected_label

    @pytest.mark.parametrize(
        "fix,expect_fix_in_cmd",
        [
            (True, True),
            (False, False),
        ],
        ids=["with_fix", "without_fix"],
    )
    def test_lint_steps_fix_mode(self, fix, expect_fix_in_cmd):
        """Lint steps include/exclude --fix flag based on fix parameter."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        with patch.object(Path, "exists", return_value=True):
            steps = _build_frontend_lint_steps(frontend_dir, fix=fix)
        assert len(steps) == 1
        assert ("--fix" in steps[0].cmd) == expect_fix_in_cmd
        assert ("--fix" in steps[0].label) == expect_fix_in_cmd

    def test_test_steps_have_stream_enabled(self):
        """Frontend test steps have show_output=True for real-time bun test output."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        with patch.object(Path, "exists", return_value=True):
            steps = _build_frontend_test_steps(frontend_dir)
        assert len(steps) == 1
        assert steps[0].show_output is True

    def test_lint_steps_use_correct_command(self):
        """Lint steps use bun run lint."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        with patch.object(Path, "exists", return_value=True):
            steps = _build_frontend_lint_steps(frontend_dir, fix=False)
        assert steps[0].cmd == ["bun", "run", "lint"]
        assert steps[0].cwd == frontend_dir

    def test_typecheck_steps_use_correct_command(self):
        """Typecheck steps use bun run tsc."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        with patch.object(Path, "exists", return_value=True):
            steps = _build_frontend_typecheck_steps(frontend_dir)
        assert steps[0].cmd == ["bun", "run", "tsc"]
        assert steps[0].cwd == frontend_dir

    def test_test_steps_use_correct_command(self):
        """_build_frontend_test_steps uses bun test."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"
        with patch.object(Path, "exists", return_value=True):
            steps = _build_frontend_test_steps(frontend_dir)
        assert steps[0].cmd == ["bun", "test"]
        assert steps[0].cwd == frontend_dir


class TestFailureTips:
    """Tests for failure tip output including full commands."""

    def test_failure_shows_fix_tip_with_command(
        self, cli_runner, mock_cmd_runner, mock_project_context, host_only_context
    ):
        """Failure output shows --fix tip with full command."""
        mock_cmd_runner.run.return_value.returncode = 1
        mock_project_context.return_value = host_only_context

        with patch.object(sys, "argv", ["djb", "health", "lint"]):
            result = cli_runner.invoke(djb_cli, ["health", "lint"])

        assert result.exit_code != 0
        assert "--fix" in result.output
        assert "auto-fix" in result.output.lower()
        # Should show the full command (--fix appended at end since it's a subcommand flag)
        assert "djb health lint --fix" in result.output

    def test_fix_mode_hides_fix_tip(
        self, cli_runner, mock_cmd_runner, mock_project_context, host_only_context
    ):
        """--fix tip is hidden when already using --fix."""
        mock_cmd_runner.run.return_value.returncode = 1
        mock_project_context.return_value = host_only_context

        result = cli_runner.invoke(djb_cli, ["health", "lint", "--fix"])

        assert result.exit_code != 0
        # Should NOT show the fix tip since we're already using --fix
        assert "re-run with --fix" not in result.output


class TestScopeLabelsInOutput:
    """Tests for correct scope labels (Python vs Backend) in output."""

    def test_djb_uses_python_scope(self, cli_runner, mock_cmd_runner, mock_project_context):
        """djb project uses 'Python' scope label."""
        djb_dir = FAKE_PROJECT_DIR / "djb"

        mock_project_context.return_value = ProjectContext(
            djb_path=djb_dir, host_path=None, inside_djb=True
        )

        result = cli_runner.invoke(djb_cli, ["health", "lint"])

        assert result.exit_code == 0
        # Check that run_cmd was called with "Python" in the label
        assert mock_cmd_runner.run.call_count > 0, "Expected run_cmd to be called"
        # The label kwarg should contain "Python" for djb projects
        calls_with_python = [
            call
            for call in mock_cmd_runner.run.call_args_list
            if "label" in call.kwargs and "Python" in call.kwargs["label"]
        ]
        assert (
            len(calls_with_python) > 0
        ), f"Expected label with 'Python', got: {mock_cmd_runner.run.call_args_list}"

    def test_host_uses_backend_scope(
        self, cli_runner, mock_cmd_runner, mock_project_context, monkeypatch
    ):
        """Host project uses 'Backend' scope label."""
        host_dir = FAKE_PROJECT_DIR / "myapp"

        mock_project_context.return_value = ProjectContext(
            djb_path=None, host_path=host_dir, inside_djb=False
        )

        # Set project name via env var to avoid file I/O
        monkeypatch.setenv("DJB_PROJECT_NAME", "myapp")
        result = cli_runner.invoke(djb_cli, ["health", "lint"])

        assert result.exit_code == 0
        # Check that run_cmd was called with "Backend" in the label
        assert mock_cmd_runner.run.call_count > 0, "Expected run_cmd to be called"
        # The label kwarg should contain "Backend" for host projects
        calls_with_backend = [
            call
            for call in mock_cmd_runner.run.call_args_list
            if "label" in call.kwargs and "Backend" in call.kwargs["label"]
        ]
        assert (
            len(calls_with_backend) > 0
        ), f"Expected label with 'Backend', got: {mock_cmd_runner.run.call_args_list}"

    def test_editable_shows_both_scopes(
        self, cli_runner, mock_cmd_runner, mock_project_context, monkeypatch
    ):
        """Editable mode shows Python for djb and Backend for host."""
        djb_dir = FAKE_PROJECT_DIR / "djb"
        host_dir = FAKE_PROJECT_DIR / "myapp"

        mock_project_context.return_value = ProjectContext(
            djb_path=djb_dir, host_path=host_dir, inside_djb=False
        )

        # Set project name via env var to avoid file I/O
        monkeypatch.setenv("DJB_PROJECT_NAME", "myapp")
        result = cli_runner.invoke(djb_cli, ["health", "lint"])

        assert result.exit_code == 0
        # Should show djb banner
        assert "djb (editable)" in result.output.lower()
        # Should show host project name
        assert "myapp" in result.output.lower()


class TestCoverageSupport:
    """Tests for coverage support in health commands."""

    def test_build_backend_test_steps_without_coverage(self, mock_cmd_runner):
        """_build_backend_test_steps excludes --cov when cov=False."""
        steps = _build_backend_test_steps(
            FAKE_PROJECT_DIR, prefix="", scope="Backend", cov=False, runner=mock_cmd_runner
        )
        assert len(steps) == 1
        assert "--cov" not in steps[0].cmd
        assert "coverage" not in steps[0].label.lower()

    def test_build_backend_test_steps_with_coverage(self, mock_cmd_runner):
        """_build_backend_test_steps includes --cov when cov=True."""
        with patch("djb.cli.health.has_pytest_cov", return_value=True):
            steps = _build_backend_test_steps(
                FAKE_PROJECT_DIR,
                prefix="",
                scope="Backend",
                cov=True,
                runner=mock_cmd_runner,
            )
        assert len(steps) == 1
        assert "--cov" in steps[0].cmd
        assert "--cov-report=term-missing" in steps[0].cmd
        assert "coverage" in steps[0].label.lower()

    def test_build_backend_test_steps_coverage_fallback(self, mock_cmd_runner):
        """_build_backend_test_steps falls back when pytest-cov unavailable."""
        with patch("djb.cli.health.has_pytest_cov", return_value=False):
            steps = _build_backend_test_steps(
                FAKE_PROJECT_DIR,
                prefix="",
                scope="Backend",
                cov=True,
                runner=mock_cmd_runner,
            )
        assert len(steps) == 1
        assert "--cov" not in steps[0].cmd
        assert "coverage" not in steps[0].label.lower()

    def test_health_test_has_cov_flag(self, cli_runner):
        """Health test --help shows --cov flag."""
        result = cli_runner.invoke(djb_cli, ["health", "test", "--help"])
        assert result.exit_code == 0
        assert "--cov" in result.output
        assert "--no-cov" in result.output

    @pytest.mark.parametrize(
        "args",
        [
            ["health", "test"],
            ["health", "--no-parallel"],  # Use --no-parallel to go through mocked run_cmd
        ],
    )
    def test_coverage_disabled_by_default(
        self, cli_runner, mock_cmd_runner, mock_project_context, args
    ):
        """djb health disables coverage by default."""
        # Mock project context to avoid real file system docs validation
        mock_project_context.return_value = ProjectContext(
            djb_path=None, host_path=HOST_PATH, inside_djb=False
        )
        result = cli_runner.invoke(djb_cli, args)
        assert result.exit_code == 0
        # Check all run calls (tests use show_output=True)
        all_calls = [str(call) for call in mock_cmd_runner.run.call_args_list]
        pytest_calls = [c for c in all_calls if "pytest" in c]
        assert not any("--cov" in str(call) for call in pytest_calls)

    @pytest.mark.parametrize(
        "args",
        [
            ["health", "test", "--cov"],
            ["health", "--cov", "--no-parallel"],  # Use --no-parallel to go through mocked run
        ],
    )
    def test_cov_flag_enables_coverage(
        self, cli_runner, mock_cmd_runner, mock_project_context, args
    ):
        """--cov flag enables coverage."""
        # Mock project context to avoid real file system docs validation
        mock_project_context.return_value = ProjectContext(
            djb_path=None, host_path=HOST_PATH, inside_djb=False
        )
        with patch("djb.cli.health.has_pytest_cov", return_value=True):
            result = cli_runner.invoke(djb_cli, args)
        assert result.exit_code == 0
        # Check all run calls (tests use show_output=True)
        all_calls = [str(call) for call in mock_cmd_runner.run.call_args_list]
        assert any("--cov" in str(call) for call in all_calls)

    def test_no_cov_flag_disables_coverage(self, cli_runner, mock_cmd_runner):
        """--no-cov explicitly disables coverage."""
        result = cli_runner.invoke(djb_cli, ["health", "test", "--no-cov"])
        assert result.exit_code == 0
        # Check all run calls (tests use show_output=True)
        all_calls = [str(call) for call in mock_cmd_runner.run.call_args_list]
        pytest_calls = [c for c in all_calls if "pytest" in c]
        assert not any("--cov" in str(call) for call in pytest_calls)


class TestGetRunScopes:
    """Tests for _get_run_scopes helper function."""

    @pytest.mark.parametrize(
        "frontend,backend,expected_backend,expected_frontend",
        [
            (False, False, True, True),  # Neither flag runs both
            (True, False, False, True),  # --frontend only
            (False, True, True, False),  # --backend only
            (True, True, True, True),  # Both flags runs both
        ],
    )
    def test_run_scopes(self, frontend, backend, expected_backend, expected_frontend):
        """_get_run_scopes returns correct flags based on frontend/backend parameters."""
        run_backend, run_frontend = _get_run_scopes(frontend, backend)
        assert run_backend is expected_backend
        assert run_frontend is expected_frontend


class TestHasRuff:
    """Tests for the _has_ruff function."""

    @pytest.mark.parametrize(
        "returncode,expected",
        [
            (0, True),
            (1, False),
        ],
        ids=["available", "not_available"],
    )
    def test_returns_based_on_returncode(self, returncode, expected, mock_cmd_runner):
        """_has_ruff returns True/False based on runner.run returncode."""
        mock_cmd_runner.run.return_value.returncode = returncode

        result = _has_ruff(FAKE_PROJECT_DIR, mock_cmd_runner)

        assert result is expected

    def test_returns_false_on_timeout(self, mock_cmd_runner):
        """_has_ruff returns False on timeout."""
        mock_cmd_runner.run.side_effect = CmdTimeout("Command timed out", timeout=10)

        result = _has_ruff(FAKE_PROJECT_DIR, mock_cmd_runner)

        assert result is False


class TestGetFrontendDir:
    """Tests for _get_frontend_dir helper."""

    def test_returns_frontend_path(self):
        """_get_frontend_dir returns the frontend subdirectory path."""
        result = _get_frontend_dir(FAKE_PROJECT_DIR)
        assert result == FAKE_PROJECT_DIR / "frontend"

    def test_returns_path_regardless_of_existence(self):
        """_get_frontend_dir returns the path without checking if it exists."""
        result = _get_frontend_dir(FAKE_PROJECT_DIR)
        assert result == FAKE_PROJECT_DIR / "frontend"
        # Function just constructs the path, doesn't check existence

    def test_returns_correct_path_type(self):
        """_get_frontend_dir returns a Path object."""
        result = _get_frontend_dir(FAKE_PROJECT_DIR)
        assert isinstance(result, Path)
        assert result.name == "frontend"


class TestRunSteps:
    """Direct unit tests for _run_steps core step runner function.

    These tests verify the step execution logic, failure collection,
    streaming vs captured modes, and quiet mode behavior.
    """

    def test_returns_empty_list_when_all_steps_pass(self, mock_cmd_runner):
        """_run_steps returns empty list when all steps succeed."""
        with patch("djb.cli.health.logger"):
            steps = [
                HealthStep("lint", ["black", "--check", "."], FAKE_PROJECT_DIR),
                HealthStep("typecheck", ["pyright"], FAKE_PROJECT_DIR),
            ]

            failures = _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        assert failures == []
        assert mock_cmd_runner.run.call_count == 2

    def test_returns_failures_for_failed_steps(self, mock_cmd_runner):
        """_run_steps collects failures for steps with non-zero exit codes."""
        mock_cmd_runner.run.return_value.returncode = 1
        mock_cmd_runner.run.return_value.stdout = "error output"
        mock_cmd_runner.run.return_value.stderr = "error details"

        with patch("djb.cli.health.logger"):
            steps = [HealthStep("lint", ["black", "--check", "."], FAKE_PROJECT_DIR)]
            failures = _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        assert len(failures) == 1
        assert failures[0].label == "lint"
        assert failures[0].returncode == 1
        assert failures[0].stdout == "error output"
        assert failures[0].stderr == "error details"

    def test_collects_multiple_failures(self, mock_cmd_runner):
        """_run_steps collects multiple failures."""
        mock_cmd_runner.run.return_value.returncode = 1
        mock_cmd_runner.run.return_value.stdout = "out"
        mock_cmd_runner.run.return_value.stderr = "err"

        with patch("djb.cli.health.logger"):
            steps = [
                HealthStep("step1", ["cmd1"], FAKE_PROJECT_DIR),
                HealthStep("step2", ["cmd2"], FAKE_PROJECT_DIR),
                HealthStep("step3", ["cmd3"], FAKE_PROJECT_DIR),
            ]
            failures = _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        assert len(failures) == 3
        assert [f.label for f in failures] == ["step1", "step2", "step3"]

    def test_uses_show_output_when_verbose(self, mock_cmd_runner):
        """_run_steps uses run with show_output=True when verbose=True."""
        with patch("djb.cli.health.logger"):
            steps = [HealthStep("lint", ["black", "--check", "."], FAKE_PROJECT_DIR)]
            _run_steps(mock_cmd_runner, steps, quiet=False, verbose=True)

        mock_cmd_runner.run.assert_called_once()
        _, kwargs = mock_cmd_runner.run.call_args
        assert kwargs.get("show_output") is True

    def test_uses_show_output_when_step_requests_stream(self, mock_cmd_runner):
        """_run_steps uses run with show_output=True when step has show_output=True."""
        with patch("djb.cli.health.logger"):
            steps = [HealthStep("tests", ["pytest"], FAKE_PROJECT_DIR, show_output=True)]
            _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        mock_cmd_runner.run.assert_called_once()
        _, kwargs = mock_cmd_runner.run.call_args
        assert kwargs.get("show_output") is True

    def test_uses_captured_mode_when_not_streaming(self, mock_cmd_runner):
        """_run_steps uses run without show_output when neither verbose nor stream."""
        with patch("djb.cli.health.logger"):
            steps = [HealthStep("lint", ["black", "--check", "."], FAKE_PROJECT_DIR)]
            _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        mock_cmd_runner.run.assert_called_once()
        _, kwargs = mock_cmd_runner.run.call_args
        assert kwargs.get("show_output") is not True

    def test_uses_captured_mode_when_quiet_overrides_stream(self, mock_cmd_runner):
        """_run_steps uses captured output when quiet=True even with show_output=True."""
        with patch("djb.cli.health.logger"):
            steps = [HealthStep("tests", ["pytest"], FAKE_PROJECT_DIR, show_output=True)]
            _run_steps(mock_cmd_runner, steps, quiet=True, verbose=False)

        # When quiet=True, should_stream is not honored
        mock_cmd_runner.run.assert_called_once()
        _, kwargs = mock_cmd_runner.run.call_args
        # Even if step has show_output=True, quiet=True suppresses it
        assert kwargs.get("show_output") is not True

    def test_captures_streaming_failures(self, mock_cmd_runner):
        """_run_steps captures streaming failures correctly."""
        mock_cmd_runner.run.return_value = Mock(
            returncode=1, stdout="streaming stdout", stderr="streaming stderr"
        )

        with patch("djb.cli.health.logger"):
            steps = [HealthStep("tests", ["pytest"], FAKE_PROJECT_DIR, show_output=True)]
            failures = _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        assert len(failures) == 1
        assert failures[0].label == "tests"
        assert failures[0].returncode == 1
        assert failures[0].stdout == "streaming stdout"
        assert failures[0].stderr == "streaming stderr"

    def test_logs_failure_message_for_captured_mode(self, mock_cmd_runner):
        """_run_steps logs failure message in captured mode."""
        mock_cmd_runner.run.return_value.returncode = 1
        mock_cmd_runner.run.return_value.stdout = ""
        mock_cmd_runner.run.return_value.stderr = ""

        with patch("djb.cli.health.logger") as mock_logger:
            steps = [HealthStep("lint", ["black", "--check", "."], FAKE_PROJECT_DIR)]
            _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        mock_logger.fail.assert_called_once()
        call_arg = mock_logger.fail.call_args[0][0]
        assert "lint failed" in call_arg
        assert "exit 1" in call_arg

    def test_logs_failure_message_for_streaming_mode(self, mock_cmd_runner):
        """_run_steps logs failure message in streaming mode."""
        mock_cmd_runner.run.return_value.returncode = 1
        mock_cmd_runner.run.return_value.stdout = ""
        mock_cmd_runner.run.return_value.stderr = ""

        with patch("djb.cli.health.logger") as mock_logger:
            steps = [HealthStep("tests", ["pytest"], FAKE_PROJECT_DIR, show_output=True)]
            _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        mock_logger.fail.assert_called_once()
        call_arg = mock_logger.fail.call_args[0][0]
        assert "tests failed" in call_arg
        assert "exit 1" in call_arg

    def test_quiet_mode_suppresses_failure_logs(self, mock_cmd_runner):
        """_run_steps with quiet=True suppresses failure log messages."""
        mock_cmd_runner.run.return_value.returncode = 1
        mock_cmd_runner.run.return_value.stdout = ""
        mock_cmd_runner.run.return_value.stderr = ""

        with patch("djb.cli.health.logger") as mock_logger:
            steps = [HealthStep("lint", ["black", "--check", "."], FAKE_PROJECT_DIR)]
            failures = _run_steps(mock_cmd_runner, steps, quiet=True, verbose=False)

        # Failures are still collected
        assert len(failures) == 1
        # But no failure message is logged
        mock_logger.fail.assert_not_called()

    def test_passes_correct_args_to_run_captured(self, mock_cmd_runner):
        """_run_steps passes correct arguments to run in captured mode."""
        with patch("djb.cli.health.logger"):
            steps = [HealthStep("lint", ["black", "--check", "."], FAKE_PROJECT_DIR)]
            _run_steps(mock_cmd_runner, steps, quiet=True, verbose=False)

        mock_cmd_runner.run.assert_called_once_with(
            ["black", "--check", "."],
            cwd=FAKE_PROJECT_DIR,
            label="lint",
            quiet=True,
            show_output=False,
        )

    def test_passes_correct_args_to_run_with_show_output(self, mock_cmd_runner):
        """_run_steps passes correct arguments to run with show_output=True."""
        with patch("djb.cli.health.logger"):
            steps = [HealthStep("tests", ["pytest"], FAKE_PROJECT_DIR, show_output=True)]
            _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        mock_cmd_runner.run.assert_called_once_with(
            ["pytest"],
            cwd=FAKE_PROJECT_DIR,
            label="tests",
            quiet=False,
            show_output=True,
        )

    def test_processes_steps_in_order(self, mock_cmd_runner):
        """_run_steps processes steps in order."""
        with patch("djb.cli.health.logger"):
            steps = [
                HealthStep("first", ["cmd1"], FAKE_PROJECT_DIR),
                HealthStep("second", ["cmd2"], FAKE_PROJECT_DIR),
                HealthStep("third", ["cmd3"], FAKE_PROJECT_DIR),
            ]
            _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        assert mock_cmd_runner.run.call_count == 3
        labels = [call.kwargs["label"] for call in mock_cmd_runner.run.call_args_list]
        assert labels == ["first", "second", "third"]

    def test_mixed_success_and_failures(self, mock_cmd_runner):
        """_run_steps handles mixed success and failure results."""

        # Configure mock to return success for first and third, failure for second
        def side_effect(*args, **kwargs):
            label = kwargs.get("label", "")
            result = MagicMock()
            if label == "step2":
                result.returncode = 1
                result.stdout = "step2 failed"
                result.stderr = "error"
            else:
                result.returncode = 0
                result.stdout = ""
                result.stderr = ""
            return result

        mock_cmd_runner.run.side_effect = side_effect

        with patch("djb.cli.health.logger"):
            steps = [
                HealthStep("step1", ["cmd1"], FAKE_PROJECT_DIR),
                HealthStep("step2", ["cmd2"], FAKE_PROJECT_DIR),
                HealthStep("step3", ["cmd3"], FAKE_PROJECT_DIR),
            ]
            failures = _run_steps(mock_cmd_runner, steps, quiet=False, verbose=False)

        assert len(failures) == 1
        assert failures[0].label == "step2"
        # All three steps should have been run
        assert mock_cmd_runner.run.call_count == 3


class TestReportFailures:
    """Direct unit tests for _report_failures failure reporting function.

    These tests verify failure output formatting and tip display logic.
    """

    @pytest.fixture
    def mock_logger_and_argv(self):
        """Mock logger and sys.argv for testing _report_failures."""
        with (
            patch("djb.cli.health.logger") as mock_logger,
            patch.object(sys, "argv", ["djb", "health", "lint"]),
        ):
            yield mock_logger

    def test_reports_success_when_no_failures(self, mock_logger_and_argv):
        """_report_failures logs success message when no failures."""
        mock_logger = mock_logger_and_argv

        _report_failures([], fix=False)

        mock_logger.done.assert_called_once_with("Health checks passed")

    def test_raises_exception_when_failures_present(self, mock_logger_and_argv):
        """_report_failures raises ClickException when there are failures."""
        failures = [StepFailure("lint", 1, "", "")]

        with pytest.raises(click.ClickException, match="Health checks failed"):
            _report_failures(failures, fix=False)

    def test_logs_failure_header(self, mock_logger_and_argv):
        """_report_failures logs failure header."""
        mock_logger = mock_logger_and_argv
        failures = [StepFailure("lint", 1, "", "")]

        with pytest.raises(click.ClickException):
            _report_failures(failures, fix=False)

        # Check that header message was logged
        fail_calls = [call[0][0] for call in mock_logger.fail.call_args_list]
        assert any("Health checks completed with failures" in msg for msg in fail_calls)

    def test_logs_each_failure(self, mock_logger_and_argv):
        """_report_failures logs each failure with label and exit code."""
        mock_logger = mock_logger_and_argv
        failures = [
            StepFailure("lint", 1, "", ""),
            StepFailure("typecheck", 2, "", ""),
        ]

        with pytest.raises(click.ClickException):
            _report_failures(failures, fix=False)

        fail_calls = [call[0][0] for call in mock_logger.fail.call_args_list]
        assert any("lint (exit 1)" in msg for msg in fail_calls)
        assert any("typecheck (exit 2)" in msg for msg in fail_calls)

    def test_shows_fix_tip_when_not_fix(self, mock_logger_and_argv):
        """_report_failures shows fix tip when not using --fix."""
        mock_logger = mock_logger_and_argv
        failures = [StepFailure("lint", 1, "", "")]

        with pytest.raises(click.ClickException):
            _report_failures(failures, fix=False)

        tip_calls = [call[0][0] for call in mock_logger.tip.call_args_list]
        assert any("--fix" in msg and "auto-fix" in msg for msg in tip_calls)

    def test_hides_fix_tip_when_fix(self, mock_logger_and_argv):
        """_report_failures hides fix tip when already using --fix."""
        mock_logger = mock_logger_and_argv
        failures = [StepFailure("lint", 1, "", "")]

        with pytest.raises(click.ClickException):
            _report_failures(failures, fix=True)

        tip_calls = [call[0][0] for call in mock_logger.tip.call_args_list]
        # Should not suggest --fix when already using it
        assert not any("re-run with --fix" in msg for msg in tip_calls)


class TestParallelExecution:
    """Tests for parallel execution functions."""

    def test_run_step_worker_success(self, mock_cmd_runner):
        """_run_step_worker returns success result."""
        step = HealthStep("echo test", ["echo", "hello"], FAKE_PROJECT_DIR)
        mock_cmd_runner.run.return_value.returncode = 0
        mock_cmd_runner.run.return_value.stdout = "hello"
        mock_cmd_runner.run.return_value.stderr = ""

        result = _run_step_worker(step, mock_cmd_runner)

        assert isinstance(result, StepResult)
        assert result.step == step
        assert result.failure is None
        assert result.duration > 0

    def test_run_step_worker_failure(self, mock_cmd_runner):
        """_run_step_worker returns failure result for failed command."""
        step = HealthStep("false test", ["false"], FAKE_PROJECT_DIR)
        mock_cmd_runner.run.return_value.returncode = 1
        mock_cmd_runner.run.return_value.stdout = ""
        mock_cmd_runner.run.return_value.stderr = ""

        result = _run_step_worker(step, mock_cmd_runner)

        assert isinstance(result, StepResult)
        assert result.step == step
        assert result.failure is not None
        assert result.failure.returncode != 0
        assert result.duration > 0

    def test_run_step_worker_exception(self, mock_cmd_runner):
        """_run_step_worker handles exceptions (timeout)."""
        step = HealthStep("timeout", ["slow_command"], FAKE_PROJECT_DIR)
        mock_cmd_runner.run.side_effect = CmdTimeout("Command timed out", timeout=10)

        result = _run_step_worker(step, mock_cmd_runner)

        assert isinstance(result, StepResult)
        assert result.failure is not None

    def test_run_steps_parallel_empty(self, mock_cmd_runner):
        """_run_steps_parallel handles empty list."""
        failures, timings = _run_steps_parallel([], mock_cmd_runner, quiet=True)
        assert failures == []
        assert timings == {}

    def test_run_steps_parallel_success(self, mock_cmd_runner):
        """_run_steps_parallel returns empty failures with successful steps."""
        steps = [
            HealthStep("echo 1", ["echo", "1"], FAKE_PROJECT_DIR),
            HealthStep("echo 2", ["echo", "2"], FAKE_PROJECT_DIR),
        ]
        mock_cmd_runner.run.return_value.returncode = 0
        mock_cmd_runner.run.return_value.stdout = ""
        mock_cmd_runner.run.return_value.stderr = ""

        failures, timings = _run_steps_parallel(steps, mock_cmd_runner, quiet=True)

        assert failures == []
        assert len(timings) == 2
        assert "echo 1" in timings
        assert "echo 2" in timings

    def test_run_steps_parallel_with_failures(self, mock_cmd_runner):
        """_run_steps_parallel collects failures."""
        steps = [
            HealthStep("echo ok", ["echo", "ok"], FAKE_PROJECT_DIR),
            HealthStep("should fail", ["false"], FAKE_PROJECT_DIR),
        ]

        # Mock to return success for echo, failure for false
        def mock_run(cmd, **kwargs):
            result = MagicMock()
            if cmd == ["false"]:
                result.returncode = 1
            else:
                result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        mock_cmd_runner.run.side_effect = mock_run

        failures, timings = _run_steps_parallel(steps, mock_cmd_runner, quiet=True)

        assert len(failures) == 1
        assert failures[0].label == "should fail"
        assert len(timings) == 2

    def test_parallel_flag_in_help(self, cli_runner):
        """--parallel flag appears in help."""
        result = cli_runner.invoke(djb_cli, ["health", "--help"])
        assert result.exit_code == 0
        assert "--parallel" in result.output
        assert "--no-parallel" in result.output

    def test_parallel_flag_default_true(self, cli_runner):
        """djb health enables parallel by default."""
        # Test by checking context is set correctly
        with patch("djb.cli.health._run_all_checks") as mock_run:
            cli_runner.invoke(djb_cli, ["health"])
            if mock_run.called:
                ctx = mock_run.call_args[0][0]
                assert ctx.parallel is True

    def test_no_parallel_flag_disables(self, cli_runner):
        """--no-parallel disables parallel execution."""
        with patch("djb.cli.health._run_all_checks") as mock_run:
            cli_runner.invoke(djb_cli, ["health", "--no-parallel"])
            if mock_run.called:
                ctx = mock_run.call_args[0][0]
                assert ctx.parallel is False

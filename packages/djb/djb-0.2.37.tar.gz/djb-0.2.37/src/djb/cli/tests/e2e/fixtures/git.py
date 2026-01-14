"""Git repository fixtures for E2E tests.

These fixtures create isolated git repositories for testing.
All fixtures follow the make_* naming convention for factory fixtures.
"""

from __future__ import annotations

import subprocess  # noqa: TID251 - invokes git directly to set up test repos
from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def make_project_with_git_repo(project_dir: Path) -> Callable[..., Path]:
    """Factory to initialize a git repo with configurable options.

    Creates a git repo with configurable user identity, path, and initial commit.

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.

    Args (to the returned callable):
        repo_path: Directory to initialize. If None, creates project_dir/repo.
        user_email: Git user email for commits.
        user_name: Git user name for commits.
        with_initial_commit: If True, stages all files and commits. Creates a
            README if the directory is empty (so there's something to commit).

    Example:
        def test_something(make_project_with_git_repo):
            # Default: creates project_dir/repo with initial commit
            repo = make_project_with_git_repo()

            # Custom path, no initial commit (just git init + config)
            make_project_with_git_repo(repo_path=my_dir, with_initial_commit=False)
    """

    def _make_git_repo(
        *,
        repo_path: Path | None = None,
        user_email: str = "e2e-test@example.com",
        user_name: str = "E2E Test",
        with_initial_commit: bool = True,
    ) -> Path:
        if repo_path is None:
            repo_dir = project_dir / "repo"
            repo_dir.mkdir()
        else:
            repo_dir = repo_path

        subprocess.run(["git", "init", str(repo_dir)], capture_output=True, check=True)
        subprocess.run(
            ["git", "-C", str(repo_dir), "config", "user.email", user_email],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo_dir), "config", "user.name", user_name],
            capture_output=True,
            check=True,
        )

        if with_initial_commit:
            # Commit whatever files exist; create README if empty
            if not any(repo_dir.iterdir()):
                readme = repo_dir / "README.md"
                readme.write_text("# Test Repository\n")
            subprocess.run(["git", "-C", str(repo_dir), "add", "."], capture_output=True)
            subprocess.run(
                ["git", "-C", str(repo_dir), "commit", "-m", "Initial commit"],
                capture_output=True,
            )

        return repo_dir

    return _make_git_repo


@pytest.fixture
def make_project_with_git_repo_with_commits(
    make_project_with_git_repo: Callable[..., Path],
) -> Callable[..., Path]:
    """Factory to create a git repo with multiple commits for revert testing.

    Builds on make_project_with_git_repo and adds additional commits.

    Example:
        def test_revert(make_project_with_git_repo_with_commits):
            repo = make_project_with_git_repo_with_commits(num_commits=5)
    """

    def _make_git_repo_with_commits(
        *,
        user_email: str = "e2e-test@example.com",
        user_name: str = "E2E Test",
        num_commits: int = 3,
    ) -> Path:
        repo_dir = make_project_with_git_repo(user_email=user_email, user_name=user_name)

        # Add more commits
        for i in range(num_commits):
            file_path = repo_dir / f"file{i}.txt"
            file_path.write_text(f"Content {i}\n")
            subprocess.run(["git", "-C", str(repo_dir), "add", "."], capture_output=True)
            subprocess.run(
                ["git", "-C", str(repo_dir), "commit", "-m", f"Add file{i}"],
                capture_output=True,
            )

        return repo_dir

    return _make_git_repo_with_commits


@pytest.fixture
def make_pyproject_toml_with_git_repo(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Callable[..., Path]:
    """Factory to create a Python project with pyproject.toml and git repo.

    Creates pyproject.toml directly in project_dir (not a subdirectory).
    Builds on make_project_with_git_repo for git initialization.

    Example:
        def test_something(make_pyproject_toml_with_git_repo):
            project = make_pyproject_toml_with_git_repo(name="myproject")
    """

    def _make_project(
        *,
        name: str = "testproject",
        user_email: str = "e2e-test@example.com",
        user_name: str = "E2E Test",
    ) -> Path:
        # Create pyproject.toml
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(f'[project]\nname = "{name}"\ndependencies = []\n')

        # Initialize git and commit
        make_project_with_git_repo(
            repo_path=project_dir,
            user_email=user_email,
            user_name=user_name,
            with_initial_commit=True,
        )

        return project_dir

    return _make_project


@pytest.fixture
def make_project_with_editable_djb_repo(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Callable[..., Path]:
    """Factory to create a project with editable djb and git repo.

    Creates a nested project directory with:
    - Initialized git repo with configurable identity
    - djb/ subdirectory (editable source) with pyproject.toml
    - pyproject.toml with editable djb reference in [tool.uv.sources]
    - .djb/local.toml with user config
    - uv.lock with editable djb reference
    - Initial commit

    Builds on make_project_with_git_repo for git initialization.
    This is the E2E sibling of mock_project_with_editable_djb_repo (for unit tests).

    Example:
        def test_editable(make_project_with_editable_djb_repo):
            project = make_project_with_editable_djb_repo(
                project_name="myproject",
                user_email="test@example.com",
                user_name="Test User"
            )
    """

    def _make_project(
        *,
        project_name: str = "myproject",
        user_email: str = "e2e-test@example.com",
        user_name: str = "E2E Test",
    ) -> Path:
        editable_project = project_dir / project_name
        editable_project.mkdir()

        # Create djb subdirectory (editable source)
        djb_dir = editable_project / "djb"
        djb_dir.mkdir()
        (djb_dir / "pyproject.toml").write_text('[project]\nname = "djb"\n')

        # Create pyproject.toml with editable djb
        (editable_project / "pyproject.toml").write_text(
            f"""
[project]
name = "{project_name}"
dependencies = []

[tool.uv.sources]
djb = {{ path = "./djb", editable = true }}
"""
        )

        # Create .djb/local.toml with required config
        djb_config_dir = editable_project / ".djb"
        djb_config_dir.mkdir()
        (djb_config_dir / "local.toml").write_text(
            f'name = "{user_name}"\nemail = "{user_email}"\n'
        )

        # Create uv.lock to be stashed
        (editable_project / "uv.lock").write_text(
            '[[package]]\nname = "djb"\nsource = { editable = "djb" }\n'
        )

        # Initialize git and commit all content
        make_project_with_git_repo(
            repo_path=editable_project,
            user_email=user_email,
            user_name=user_name,
            with_initial_commit=True,
        )

        return editable_project

    return _make_project

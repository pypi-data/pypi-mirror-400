"""djb init project - Update .gitignore and Django settings."""

from __future__ import annotations

import re
from pathlib import Path

import click

from djb.cli.context import djb_pass_context
from djb.cli.init.shared import InitContext
from djb.core.logging import get_logger

logger = get_logger(__name__)

# Entries that djb adds to .gitignore
DJB_GITIGNORE_ENTRIES = [
    ("# djb local config (user-specific, not committed)", ".djb/local.toml"),
    ("# djb generated test indexes", "**/pytest_index.toml"),
]


def find_settings_file(project_root: Path) -> Path | None:
    """Find the Django settings.py file in the project.

    Searches for settings.py in subdirectories of project_root that look like
    Django project directories (contain __init__.py).

    Returns:
        Path to settings.py if found, None otherwise.
    """
    # Look for directories containing settings.py
    for item in project_root.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            settings_path = item / "settings.py"
            init_path = item / "__init__.py"
            # Must have both settings.py and __init__.py to be a Django project
            if settings_path.exists() and init_path.exists():
                return settings_path
    return None


def add_djb_to_installed_apps(project_root: Path) -> bool:
    """Add 'djb' to Django's INSTALLED_APPS if not already present.

    Finds the settings.py file and modifies INSTALLED_APPS to include 'djb'.
    Inserts djb after the last django.* app for proper ordering.

    Returns:
        True if djb was added, False if already present or settings not found.
    """
    logger.next("Configuring Django settings")
    settings_path = find_settings_file(project_root)
    if not settings_path:
        logger.skip("No Django settings.py found")
        return False

    content = settings_path.read_text()

    # Check if djb is already in INSTALLED_APPS
    # Match various formats: "djb", 'djb', with or without trailing comma
    if re.search(r'["\']djb["\']', content):
        logger.info("djb already in INSTALLED_APPS")
        return False

    # Find INSTALLED_APPS list and insert djb
    # Match the pattern: INSTALLED_APPS = [
    pattern = r"(INSTALLED_APPS\s*=\s*\[)"

    match = re.search(pattern, content)
    if not match:
        logger.warning("Could not find INSTALLED_APPS in settings.py")
        return False

    # Find a good insertion point - after the last django.* entry
    # or at the end of the list if no django entries
    lines = content.split("\n")
    installed_apps_start = None
    last_django_line = None
    bracket_depth = 0
    in_installed_apps = False

    for i, line in enumerate(lines):
        if "INSTALLED_APPS" in line and "=" in line:
            installed_apps_start = i
            in_installed_apps = True

        if in_installed_apps:
            bracket_depth += line.count("[") - line.count("]")
            # Match django.* apps (django.contrib.*, django_components, etc.)
            if re.search(r'["\']django[._]', line):
                last_django_line = i
            if bracket_depth == 0 and installed_apps_start is not None and i > installed_apps_start:
                break

    if last_django_line is not None:
        # Insert after the last django.* line
        insert_line = last_django_line
        # Detect indentation from the previous line
        indent_match = re.match(r"^(\s*)", lines[insert_line])
        indent = indent_match.group(1) if indent_match else "    "
        lines.insert(insert_line + 1, f'{indent}"djb",')
    elif installed_apps_start is not None:
        # No django entries, insert after the opening bracket
        indent = "    "
        lines.insert(installed_apps_start + 1, f'{indent}"djb",')
    else:
        logger.warning("Could not determine where to insert djb in INSTALLED_APPS")
        return False

    # Write the modified content
    settings_path.write_text("\n".join(lines))
    logger.done(f"Added djb to INSTALLED_APPS in {settings_path.name}")
    return True


def update_gitignore_for_project_config(project_root: Path) -> bool:
    """Update .gitignore to ensure djb entries are ignored.

    Adds djb-specific entries if not already present.

    Returns:
        True if .gitignore was updated, False otherwise.
    """
    gitignore_path = project_root / ".gitignore"
    if not gitignore_path.exists():
        return False

    content = gitignore_path.read_text()
    updated = False

    for comment, pattern in DJB_GITIGNORE_ENTRIES:
        if pattern in content:
            continue
        # Add the entry
        entry = f"\n{comment}\n{pattern}\n"
        content = content.rstrip() + entry
        updated = True

    if updated:
        gitignore_path.write_text(content)

    return updated


@click.command("project")
@djb_pass_context(InitContext)
@click.pass_context
def project(ctx: click.Context, init_ctx: InitContext) -> None:
    """Update .gitignore and Django settings.

    Adds djb-specific entries to .gitignore and adds djb to INSTALLED_APPS.
    """
    project_dir = init_ctx.config.project_dir
    gitignore_updated = init_ctx.gitignore_updated

    # Update .gitignore
    gitignore_was_updated = update_gitignore_for_project_config(project_dir)
    if gitignore_was_updated:
        logger.done("Updated .gitignore with djb entries")
        gitignore_updated = True

    # Add djb to Django INSTALLED_APPS
    add_djb_to_installed_apps(project_dir)

    # Store results in context for other subcommands
    init_ctx.gitignore_updated = gitignore_updated

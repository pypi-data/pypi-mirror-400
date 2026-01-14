"""Documentation path validation for markdown file references."""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple


class PathError(NamedTuple):
    """A documentation path that doesn't exist."""

    path: str
    line_number: int
    source_file: str


def _is_command_or_example(text: str) -> bool:
    """Check if text looks like a shell command or example rather than a file path."""
    # Skip if contains shell operators or multiple commands
    if "&&" in text or "||" in text or " | " in text or ";" in text:
        return True

    # Skip if contains spaces (likely a command with arguments)
    if " " in text:
        return True

    # Skip if starts with common command prefixes
    first_part = text.split("/")[0]
    if first_part in ("uv", "cd", "git", "bun", "npm", "pytest", "python", "pip"):
        return True

    return False


def _is_glob_pattern(text: str) -> bool:
    """Check if text contains glob pattern or placeholder characters."""
    # Glob patterns: *, ?, [...]
    # Placeholders: <...> (commonly used in docs for variable parts)
    return "*" in text or "?" in text or "[" in text or "<" in text


def _is_valid_path_reference(text: str) -> bool:
    """Check if text looks like an actual file/directory path reference.

    Validates that the path looks like a real file reference:
    - Has a file extension for common source files, OR
    - Contains directory patterns like /src/ or /tests/, OR
    - Is a directory path (ends with /)
    """
    # Skip glob patterns - they're examples, not specific files
    if _is_glob_pattern(text):
        return False

    # Skip hidden files/directories (often config examples like .djb/config.yaml)
    # Also skip paths containing hidden files (e.g., secrets/.sops.yaml)
    if text.startswith(".") or "/." in text:
        return False

    # Check for common file extensions
    if text.endswith(
        (".py", ".ts", ".js", ".tsx", ".jsx", ".md", ".toml", ".json", ".yaml", ".yml")
    ):
        return True

    # Check for directory patterns (likely real paths)
    if "/src/" in text or "/tests/" in text or "/lib/" in text:
        return True

    # Skip generic directory references like "e2e/" - too likely to be examples
    # Only accept directory paths if they have multiple path components
    if text.endswith("/"):
        # e2e/ -> only 1 component, skip
        # beachresort25/landing/e2e/ -> 3 components, accept
        components = [c for c in text.rstrip("/").split("/") if c]
        if len(components) < 2:
            return False
        return True

    return False


def extract_paths_from_markdown(content: str) -> list[tuple[str, int]]:
    """Extract file paths from markdown content.

    Extracts paths from:
    1. Markdown links: [text](relative/path)
    2. Inline code paths: `relative/path` that look like file paths

    Returns list of (path, line_number) tuples.
    """
    paths: list[tuple[str, int]] = []
    lines = content.split("\n")

    # Pattern for markdown links: [text](path)
    # Excludes URLs (http://, https://, #anchors, mailto:)
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    # Pattern for inline code that looks like file paths
    # Must contain / and end with common extensions or be a known pattern
    code_pattern = re.compile(r"`([^`]+)`")

    for line_num, line in enumerate(lines, start=1):
        # Extract from markdown links
        for match in link_pattern.finditer(line):
            path = match.group(2)
            # Skip URLs, anchors, and mailto links
            if path.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # Skip glob patterns
            if _is_glob_pattern(path):
                continue
            paths.append((path, line_num))

        # Extract from inline code
        for match in code_pattern.finditer(line):
            candidate = match.group(1)
            # Must look like a file path (contains /)
            if "/" not in candidate:
                continue

            # Skip URLs
            if candidate.startswith(("http://", "https://")):
                continue

            # Skip commands and examples
            if _is_command_or_example(candidate):
                continue

            # Must look like an actual path reference
            if not _is_valid_path_reference(candidate):
                continue

            # Strip line number suffix (e.g., "file.py:42" or "file.py:42-57")
            if ":" in candidate:
                base_path = candidate.split(":")[0]
                # Only strip if what follows the colon looks like line numbers
                suffix = candidate.split(":", 1)[1]
                if suffix and suffix[0].isdigit():
                    candidate = base_path

            paths.append((candidate, line_num))

    return paths


def extract_paths_from_toml(content: str) -> list[tuple[str, int]]:
    """Extract file paths from TOML files arrays.

    Handles paths like:
    - "beachresort25/cli/ai/agents/runner.py:222-241"
    - "beachresort25/cli/ai/review.py:136-207"

    Returns list of (path, line_number) tuples.
    The path returned is the file path before the colon (line numbers stripped).
    """
    paths: list[tuple[str, int]] = []
    lines = content.split("\n")

    # Pattern for files array: files = ["path:line", "path:line-line"]
    # Match quoted strings that look like file paths with line numbers
    file_ref_pattern = re.compile(r'"([^"]+\.[a-zA-Z]+):(\d+(?:-\d+)?)"')

    for line_num, line in enumerate(lines, start=1):
        for match in file_ref_pattern.finditer(line):
            path = match.group(1)  # Just the file path, without :line suffix
            paths.append((path, line_num))

    return paths


def validate_paths(
    project_root: Path,
    markdown_path: Path,
) -> list[PathError]:
    """Validate all path references in a markdown file exist.

    Args:
        project_root: Root directory to resolve project-relative paths
        markdown_path: Path to markdown file to validate

    For paths starting with '../', resolution is relative to the markdown file's
    directory. For other paths, resolution is relative to project_root.

    Returns:
        List of PathError for paths that don't exist
    """
    errors: list[PathError] = []

    if not markdown_path.exists():
        return errors  # File doesn't exist, nothing to validate

    content = markdown_path.read_text()
    paths = extract_paths_from_markdown(content)

    # Track unique paths to avoid duplicate errors
    seen: set[str] = set()

    for path, line_num in paths:
        if path in seen:
            continue
        seen.add(path)

        # Handle relative paths:
        # - "../" paths: resolved relative to markdown file's directory
        # - "./" paths: resolved relative to markdown file's directory
        # - Bare filenames (no /): resolved relative to markdown file's directory
        # - Paths with "/" but not starting with "../" or "./": resolved relative to project_root
        if path.startswith("../") or path.startswith("./") or "/" not in path:
            full_path = (markdown_path.parent / path).resolve()
            # Skip if path resolves outside project root (external references)
            try:
                full_path.relative_to(project_root)
            except ValueError:
                continue  # External reference, skip validation
        else:
            full_path = project_root / path

        if not full_path.exists():
            errors.append(PathError(path, line_num, str(markdown_path)))

    return errors


def validate_toml_paths(
    project_root: Path,
    toml_path: Path,
) -> list[PathError]:
    """Validate all path references in a TOML file exist.

    Args:
        project_root: Root directory to resolve relative paths against
        toml_path: Path to TOML file to validate

    Returns:
        List of PathError for paths that don't exist
    """
    errors: list[PathError] = []

    if not toml_path.exists():
        return errors

    content = toml_path.read_text()
    paths = extract_paths_from_toml(content)

    # Track unique paths to avoid duplicate errors
    seen: set[str] = set()

    for path, line_num in paths:
        if path in seen:
            continue
        seen.add(path)

        full_path = project_root / path
        if not full_path.exists():
            errors.append(PathError(path, line_num, str(toml_path)))

    return errors

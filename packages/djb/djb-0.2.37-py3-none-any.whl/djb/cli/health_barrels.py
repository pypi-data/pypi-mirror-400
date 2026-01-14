"""Barrel export validation for markdown documentation.

This module provides functionality to keep barrel export listings in markdown files
synchronized with the actual exports defined in the source files.

Barrel listings follow this format:
    **Label** [`path/to/file.py`]: `export1`, `export2`, ...

The module can:
- Detect barrel listings in markdown files
- Extract actual exports from Python (`__all__`) and TypeScript (`export { }`) files
- Compare documented exports with actual exports
- Auto-fix markdown files to match actual exports
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from djb.core.logging import get_logger

logger = get_logger(__name__)


# Pattern to match barrel listings in markdown:
# **Label** [`path/to/file`]: `export1`, `export2`, ...
#
# Groups:
# 1. Label (e.g., "Components")
# 2. File path (e.g., "frontend/src/lib/components/index.ts")
# 3. Exports string (e.g., "`export1`, `export2`, ...")
BARREL_PATTERN = re.compile(
    r"\*\*([^*]+)\*\*\s*\[`([^`]+)`\]:\s*(.+?)(?=\n\n|\n\*\*|\Z)",
    re.DOTALL,
)

# Pattern to extract individual export names from backtick-quoted list
EXPORT_NAME_PATTERN = re.compile(r"`([^`]+)`")


@dataclass
class BarrelListing:
    """A barrel export listing found in a markdown file."""

    label: str
    file_path: str
    exports: list[str]
    line_number: int
    match_start: int
    match_end: int


@dataclass
class BarrelDiscrepancy:
    """Discrepancy between documented and actual exports."""

    label: str
    file_path: str
    missing: list[str]  # In source but not in docs
    extra: list[str]  # In docs but not in source
    documented: list[str]
    actual: list[str]


def find_barrel_listings(content: str) -> list[BarrelListing]:
    """Find all barrel listings in markdown content.

    Args:
        content: Markdown file content

    Returns:
        List of BarrelListing objects found in the content
    """
    listings = []

    for match in BARREL_PATTERN.finditer(content):
        label = match.group(1).strip()
        file_path = match.group(2).strip()
        exports_str = match.group(3).strip()

        # Extract individual export names
        exports = EXPORT_NAME_PATTERN.findall(exports_str)

        # Calculate line number from position
        line_number = content[: match.start()].count("\n") + 1

        listings.append(
            BarrelListing(
                label=label,
                file_path=file_path,
                exports=exports,
                line_number=line_number,
                match_start=match.start(),
                match_end=match.end(),
            )
        )

    return listings


def extract_python_exports(path: Path) -> list[str]:
    """Extract exports from a Python barrel file by parsing __all__.

    Args:
        path: Path to Python file

    Returns:
        List of export names from __all__, or empty list if not found
    """
    if not path.exists():
        return []

    try:
        source = path.read_text()
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        exports = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                exports.append(elt.value)
                        return exports

    return []


def extract_typescript_exports(path: Path) -> list[str]:
    """Extract exports from a TypeScript barrel file.

    Parses export statements like:
        export { Foo, Bar } from './module'
        export type { FooType } from './types'

    Args:
        path: Path to TypeScript file

    Returns:
        List of export names, or empty list if file not found
    """
    if not path.exists():
        return []

    try:
        source = path.read_text()
    except OSError:
        return []

    exports = []

    # Match: export { name1, name2 } from '...'
    # Match: export type { Type1, Type2 } from '...'
    pattern = r"export\s+(?:type\s+)?{\s*([^}]+)\s*}"
    for match in re.finditer(pattern, source):
        names = match.group(1)
        for name in names.split(","):
            name = name.strip()
            # Skip empty names and comments
            if not name or name.startswith("//"):
                continue
            # Handle "Foo as Bar" renames - use the exported name (Bar)
            if " as " in name:
                name = name.split(" as ")[1].strip()
            exports.append(name)

    return exports


def extract_exports(path: Path) -> list[str]:
    """Extract exports from a barrel file based on its extension.

    Args:
        path: Path to barrel file (.py or .ts)

    Returns:
        List of export names
    """
    suffix = path.suffix.lower()
    if suffix == ".py":
        return extract_python_exports(path)
    elif suffix in (".ts", ".tsx"):
        return extract_typescript_exports(path)
    else:
        return []


def format_exports_line(label: str, file_path: str, exports: list[str]) -> str:
    """Format a barrel listing line.

    Args:
        label: Label for the barrel (e.g., "Components")
        file_path: Path to the barrel file
        exports: List of export names

    Returns:
        Formatted markdown line
    """
    exports_str = ", ".join(f"`{name}`" for name in exports)
    return f"**{label}** [`{file_path}`]: {exports_str}"


def check_barrel(project_root: Path, listing: BarrelListing) -> BarrelDiscrepancy | None:
    """Check if a barrel listing matches actual exports.

    Args:
        project_root: Project root directory
        listing: The barrel listing to check

    Returns:
        BarrelDiscrepancy if there are differences, None if in sync
    """
    barrel_path = project_root / listing.file_path
    actual = extract_exports(barrel_path)

    if not actual:
        # File not found or no exports - report all documented as extra
        if listing.exports:
            return BarrelDiscrepancy(
                label=listing.label,
                file_path=listing.file_path,
                missing=[],
                extra=listing.exports,
                documented=listing.exports,
                actual=[],
            )
        return None

    documented_set = set(listing.exports)
    actual_set = set(actual)

    missing = sorted(actual_set - documented_set)
    extra = sorted(documented_set - actual_set)

    if missing or extra:
        return BarrelDiscrepancy(
            label=listing.label,
            file_path=listing.file_path,
            missing=missing,
            extra=extra,
            documented=listing.exports,
            actual=actual,
        )

    return None


def check_barrels_in_file(
    project_root: Path, md_path: Path
) -> tuple[list[BarrelListing], list[BarrelDiscrepancy]]:
    """Check all barrel listings in a markdown file.

    Args:
        project_root: Project root directory
        md_path: Path to markdown file

    Returns:
        Tuple of (all listings, discrepancies)
    """
    try:
        content = md_path.read_text()
    except OSError:
        return [], []

    listings = find_barrel_listings(content)
    discrepancies = []

    for listing in listings:
        discrepancy = check_barrel(project_root, listing)
        if discrepancy:
            discrepancies.append(discrepancy)

    return listings, discrepancies


def fix_barrels_in_file(project_root: Path, md_path: Path) -> int:
    """Fix barrel listings in a markdown file to match actual exports.

    Args:
        project_root: Project root directory
        md_path: Path to markdown file

    Returns:
        Number of listings fixed
    """
    try:
        content = md_path.read_text()
    except OSError:
        return 0

    listings = find_barrel_listings(content)
    if not listings:
        return 0

    # Process listings in reverse order to preserve offsets
    fixed_count = 0
    for listing in reversed(listings):
        barrel_path = project_root / listing.file_path
        actual = extract_exports(barrel_path)

        if not actual:
            continue

        # Check if there's a difference
        if set(listing.exports) != set(actual):
            # Generate new line
            new_line = format_exports_line(listing.label, listing.file_path, actual)

            # Replace in content
            content = content[: listing.match_start] + new_line + content[listing.match_end :]
            fixed_count += 1

    if fixed_count > 0:
        md_path.write_text(content)

    return fixed_count


def find_markdown_files(project_root: Path) -> list[Path]:
    """Find markdown files that may contain barrel listings.

    Args:
        project_root: Project root directory

    Returns:
        List of markdown file paths
    """
    markdown_files: list[Path] = []
    seen_targets: set[Path] = set()

    # Root-level markdown files
    for md_file in project_root.glob("*.md"):
        target = md_file.resolve()
        if target in seen_targets:
            continue
        seen_targets.add(target)
        markdown_files.append(md_file)

    # Nested docs directory
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        for md_file in docs_dir.rglob("*.md"):
            # Skip plan files - they may contain speculative paths
            parts = md_file.parts
            if "plans" in parts:
                continue
            target = md_file.resolve()
            if target in seen_targets:
                continue
            seen_targets.add(target)
            markdown_files.append(md_file)

    return sorted(markdown_files)


def check_all_barrels(
    project_root: Path,
) -> dict[Path, tuple[list[BarrelListing], list[BarrelDiscrepancy]]]:
    """Check all barrel listings in a project.

    Args:
        project_root: Project root directory

    Returns:
        Dict mapping markdown file paths to (listings, discrepancies) tuples
    """
    results: dict[Path, tuple[list[BarrelListing], list[BarrelDiscrepancy]]] = {}

    for md_path in find_markdown_files(project_root):
        listings, discrepancies = check_barrels_in_file(project_root, md_path)
        if listings:  # Only include files that have barrel listings
            results[md_path] = (listings, discrepancies)

    return results


def fix_all_barrels(project_root: Path) -> dict[Path, int]:
    """Fix all barrel listings in a project.

    Args:
        project_root: Project root directory

    Returns:
        Dict mapping markdown file paths to number of listings fixed
    """
    results: dict[Path, int] = {}

    for md_path in find_markdown_files(project_root):
        fixed = fix_barrels_in_file(project_root, md_path)
        if fixed > 0:
            results[md_path] = fixed

    return results

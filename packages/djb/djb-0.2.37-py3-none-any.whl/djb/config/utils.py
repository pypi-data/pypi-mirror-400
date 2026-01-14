"""Utility functions for configuration module."""

from __future__ import annotations

from collections import deque


def topological_sort(dependencies: dict[str, list[str]]) -> list[str]:
    """Topological sort via Kahn's algorithm.

    Returns nodes in resolution order (dependencies before dependents).

    Args:
        dependencies: Dict mapping node names to their list of dependencies.
            Example: {"a": [], "b": ["a"], "c": ["a", "b"]}
            Means: a has no deps, b depends on a, c depends on a and b.

    Returns:
        List of node names in resolution order.

    Raises:
        ValueError: If there are circular dependencies or unknown nodes.
    """
    # Build in-degree count and dependents adjacency list
    in_degree: dict[str, int] = {name: 0 for name in dependencies}
    dependents: dict[str, list[str]] = {name: [] for name in dependencies}

    for name, deps in dependencies.items():
        for dep in deps:
            if dep not in dependencies:
                raise ValueError(f"Node '{name}' depends on unknown node: '{dep}'")
            dependents[dep].append(name)
            in_degree[name] += 1

    # Start with nodes that have no dependencies
    queue = deque(name for name, degree in in_degree.items() if degree == 0)
    result: list[str] = []

    while queue:
        name = queue.popleft()
        result.append(name)
        for dependent in dependents[name]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(result) != len(dependencies):
        # Find and report the cycle
        remaining = set(dependencies) - set(result)
        cycle = _find_cycle(remaining, dependencies)
        raise ValueError(
            f"Circular dependency detected - cannot resolve order:\n"
            f"  {' -> '.join(cycle)}\n"
            f"Break the cycle by removing one of these dependencies."
        )

    return result


def _find_cycle(nodes: set[str], dependencies: dict[str, list[str]]) -> list[str]:
    """Find a cycle among the given nodes for error reporting.

    Args:
        nodes: Set of node names that couldn't be resolved.
        dependencies: Dict mapping node names to their dependencies.

    Returns:
        List of node names forming a cycle.
    """
    visited: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> list[str] | None:
        if node in path:
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        if node in visited:
            return None
        visited.add(node)
        path.append(node)
        for dep in dependencies[node]:
            if dep in nodes:
                result = dfs(dep)
                if result:
                    return result
        path.pop()
        return None

    for node in nodes:
        cycle = dfs(node)
        if cycle:
            return cycle
    return list(nodes)  # Fallback

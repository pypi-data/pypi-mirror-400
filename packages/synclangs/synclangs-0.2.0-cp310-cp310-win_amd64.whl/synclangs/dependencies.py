"""Dependency graph utilities for SyncLangs modules."""

from __future__ import annotations

import posixpath
from collections.abc import Iterable

from synclangs.parser.ast import Module


def resolve_import_path(module_path: str, import_path: str) -> str:
    """Resolve an import path to a normalized module path."""
    base_dir = posixpath.dirname(module_path)
    return posixpath.normpath(posixpath.join(base_dir, import_path))


def build_dependency_graph(modules: dict[str, Module]) -> dict[str, set[str]]:
    """Build a dependency graph from modules to their imports."""
    graph: dict[str, set[str]] = {path: set() for path in modules}
    for module in modules.values():
        for import_stmt in module.imports:
            target = resolve_import_path(module.path, import_stmt.path)
            if target in modules:
                graph[module.path].add(target)
    return graph


def build_reverse_graph(
    graph: dict[str, Iterable[str]],
) -> dict[str, set[str]]:
    """Build a reverse dependency graph."""
    reverse: dict[str, set[str]] = {node: set() for node in graph}
    for node, deps in graph.items():
        for dep in deps:
            reverse.setdefault(dep, set()).add(node)
    return reverse


def collect_dependents(
    reverse_graph: dict[str, Iterable[str]],
    start: str,
) -> set[str]:
    """Collect all dependents of a module in the reverse graph."""
    dependents: set[str] = set()
    queue = [start]
    while queue:
        current = queue.pop(0)
        for child in reverse_graph.get(current, []):
            if child not in dependents:
                dependents.add(child)
                queue.append(child)
    return dependents


def detect_cycles(graph: dict[str, Iterable[str]]) -> list[list[str]]:
    """Detect cycles in a dependency graph."""
    visited: set[str] = set()
    stack: list[str] = []
    in_stack: set[str] = set()
    cycles: list[list[str]] = []
    seen_cycles: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        if node in in_stack:
            cycle = _extract_cycle(stack, node)
            normalized = _normalize_cycle(cycle)
            if normalized not in seen_cycles:
                seen_cycles.add(normalized)
                cycles.append(cycle + [node])
            return
        if node in visited:
            return
        visited.add(node)
        stack.append(node)
        in_stack.add(node)
        for dep in graph.get(node, []):
            visit(dep)
        stack.pop()
        in_stack.remove(node)

    for node in graph:
        visit(node)
    return cycles


def _extract_cycle(stack: list[str], node: str) -> list[str]:
    """Extract a cycle path from the current DFS stack."""
    if node not in stack:
        return [node]
    idx = stack.index(node)
    return stack[idx:].copy()


def _normalize_cycle(cycle: list[str]) -> tuple[str, ...]:
    """Normalize cycle ordering for deduplication."""
    if not cycle:
        return tuple()
    min_index = min(range(len(cycle)), key=lambda i: cycle[i])
    rotated = cycle[min_index:] + cycle[:min_index]
    return tuple(rotated)

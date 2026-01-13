"""Semantic validation for SyncLangs modules."""

from __future__ import annotations

import difflib
from collections.abc import Iterable

from synclangs.dependencies import (
    build_dependency_graph,
    detect_cycles,
    resolve_import_path,
)
from synclangs.errors import (
    SY002,
    SY003,
    SY004,
    SY005,
    SY006,
    SY007,
    SY008,
    SY020,
    SyncLangsError,
)
from synclangs.parser.ast import (
    ConstDef,
    EnumDef,
    Field,
    ListTypeExpr,
    MapTypeExpr,
    Module,
    NullableTypeExpr,
    PrimitiveTypeExpr,
    SourceLocation,
    TypeExpr,
    TypeRef,
)


def validate_modules(modules: dict[str, Module]) -> list[SyncLangsError]:
    """Validate modules for unresolved imports and type references.

    Args:
        modules: Mapping of module path to parsed module.

    Returns:
        A list of formatted error messages. Empty if valid.
    """
    errors: list[SyncLangsError] = []
    definitions = {
        path: (
            {type_def.name for type_def in module.types}
            | {enum_def.name for enum_def in module.enums}
        )
        for path, module in modules.items()
    }

    for module in modules.values():
        _validate_duplicate_types(module, errors)
        _validate_duplicate_enums(module, errors)
        _validate_duplicate_constants(module, errors)
        _validate_enum_variants(module, errors)
        _validate_name_conflicts(module, errors)
        _validate_constant_types(module, errors)
        import_map, missing_imports = _validate_imports(
            module, modules, definitions, errors
        )
        available = (
            definitions.get(module.path, set())
            | set(import_map.keys())
            | missing_imports
        )
        for field in _iter_fields(module):
            for ref in _collect_type_refs(field.type_expr):
                if ref.name not in available:
                    hint = _suggest_type(ref.name, available)
                    message = f"Type '{ref.name}' not found."
                    if hint:
                        message = f"{message} {hint}"
                    errors.append(
                        SyncLangsError(
                            code=SY002,
                            message=message,
                            file_path=module.path,
                            line=_location_line(ref.location),
                            column=_location_column(ref.location),
                            line_text=_line_text(module, ref.location),
                            span=_location_span(ref.location, ref.name),
                            hint="Import the type or define it in this file.",
                        )
                    )

    graph = build_dependency_graph(modules)
    for cycle in detect_cycles(graph):
        if not cycle:
            continue
        chain = " -> ".join(cycle)
        errors.append(
            SyncLangsError(
                code=SY003,
                message=f"Circular import detected: {chain}",
                file_path=cycle[0],
                hint="Break the cycle by removing one of the imports.",
            )
        )

    return errors


def _validate_imports(
    module: Module,
    modules: dict[str, Module],
    definitions: dict[str, set[str]],
    errors: list[SyncLangsError],
) -> tuple[dict[str, str], set[str]]:
    """Validate import statements and return imported type map."""
    import_map: dict[str, str] = {}
    missing_imports: set[str] = set()
    for import_stmt in module.imports:
        target_path = resolve_import_path(module.path, import_stmt.path)
        if target_path not in modules:
            errors.append(
                SyncLangsError(
                    code=SY020,
                    message=f"Import '{import_stmt.path}' could not be resolved.",
                    file_path=module.path,
                    line=_location_line(import_stmt.location),
                    column=_location_column(import_stmt.location),
                    line_text=_line_text(module, import_stmt.location),
                    span=_location_span(import_stmt.location, import_stmt.path),
                    hint="Check the import path or create the referenced file.",
                )
            )
            continue
        available = definitions.get(target_path, set())
        for name in import_stmt.names:
            if name not in available:
                hint = _suggest_type(name, available)
                message = (
                    f"Type '{name}' is not exported by '{import_stmt.path}'."
                )
                if hint:
                    message = f"{message} {hint}"
                errors.append(
                    SyncLangsError(
                        code=SY002,
                        message=message,
                        file_path=module.path,
                        line=_location_line(import_stmt.location),
                        column=_location_column(import_stmt.location),
                        line_text=_line_text(module, import_stmt.location),
                        span=_location_span(
                            import_stmt.location, import_stmt.path
                        ),
                        hint="Check the imported module or update the import list.",
                    )
                )
                missing_imports.add(name)
                continue
            import_map[name] = target_path
    return import_map, missing_imports


def _validate_duplicate_types(module: Module, errors: list[SyncLangsError]) -> None:
    """Validate duplicate type definitions in a module."""
    seen: dict[str, SourceLocation | None] = {}
    for type_def in module.types:
        if type_def.name in seen:
            errors.append(
                SyncLangsError(
                    code=SY004,
                    message=f"Duplicate type definition '{type_def.name}'.",
                    file_path=module.path,
                    line=_location_line(type_def.location),
                    column=_location_column(type_def.location),
                    line_text=_line_text(module, type_def.location),
                    span=_location_span(type_def.location, type_def.name),
                    hint="Remove or rename the duplicate type.",
                )
            )
        else:
            seen[type_def.name] = type_def.location


def _validate_duplicate_enums(
    module: Module, errors: list[SyncLangsError]
) -> None:
    """Validate duplicate enum definitions in a module."""
    seen: dict[str, SourceLocation | None] = {}
    for enum_def in module.enums:
        if enum_def.name in seen:
            errors.append(
                SyncLangsError(
                    code=SY004,
                    message=f"Duplicate enum definition '{enum_def.name}'.",
                    file_path=module.path,
                    line=_location_line(enum_def.location),
                    column=_location_column(enum_def.location),
                    line_text=_line_text(module, enum_def.location),
                    span=_location_span(enum_def.location, enum_def.name),
                    hint="Remove or rename the duplicate enum.",
                )
            )
        else:
            seen[enum_def.name] = enum_def.location


def _validate_duplicate_constants(
    module: Module, errors: list[SyncLangsError]
) -> None:
    """Validate duplicate constant definitions in a module."""
    seen: dict[str, SourceLocation | None] = {}
    for const_def in module.constants:
        if const_def.name in seen:
            errors.append(
                SyncLangsError(
                    code=SY007,
                    message=f"Duplicate constant definition '{const_def.name}'.",
                    file_path=module.path,
                    line=_location_line(const_def.location),
                    column=_location_column(const_def.location),
                    line_text=_line_text(module, const_def.location),
                    span=_location_span(const_def.location, const_def.name),
                    hint="Remove or rename the duplicate constant.",
                )
            )
        else:
            seen[const_def.name] = const_def.location


def _validate_enum_variants(
    module: Module, errors: list[SyncLangsError]
) -> None:
    """Validate that enum variants are unique within each enum."""
    for enum_def in module.enums:
        seen: dict[str, SourceLocation | None] = {}
        for variant in enum_def.variants:
            if variant.name in seen:
                errors.append(
                    SyncLangsError(
                        code=SY005,
                        message=(
                            f"Duplicate variant '{variant.name}' "
                            f"in enum '{enum_def.name}'."
                        ),
                        file_path=module.path,
                        line=_location_line(variant.location),
                        column=_location_column(variant.location),
                        line_text=_line_text(module, variant.location),
                        span=_location_span(variant.location, variant.name),
                        hint="Remove or rename the duplicate variant.",
                    )
                )
            else:
                seen[variant.name] = variant.location


def _validate_name_conflicts(
    module: Module, errors: list[SyncLangsError]
) -> None:
    """Validate that types, enums, and constants have unique names."""
    names: dict[str, tuple[str, SourceLocation | None]] = {}
    for type_def in module.types:
        if type_def.name in names:
            kind, _ = names[type_def.name]
            errors.append(
                SyncLangsError(
                    code=SY006,
                    message=(
                        f"Type '{type_def.name}' conflicts with "
                        f"existing {kind} of the same name."
                    ),
                    file_path=module.path,
                    line=_location_line(type_def.location),
                    column=_location_column(type_def.location),
                    line_text=_line_text(module, type_def.location),
                    span=_location_span(type_def.location, type_def.name),
                    hint="Rename one of the conflicting definitions.",
                )
            )
        else:
            names[type_def.name] = ("type", type_def.location)
    for enum_def in module.enums:
        if enum_def.name in names:
            kind, _ = names[enum_def.name]
            errors.append(
                SyncLangsError(
                    code=SY006,
                    message=(
                        f"Enum '{enum_def.name}' conflicts with "
                        f"existing {kind} of the same name."
                    ),
                    file_path=module.path,
                    line=_location_line(enum_def.location),
                    column=_location_column(enum_def.location),
                    line_text=_line_text(module, enum_def.location),
                    span=_location_span(enum_def.location, enum_def.name),
                    hint="Rename one of the conflicting definitions.",
                )
            )
        else:
            names[enum_def.name] = ("enum", enum_def.location)
    for const_def in module.constants:
        if const_def.name in names:
            kind, _ = names[const_def.name]
            errors.append(
                SyncLangsError(
                    code=SY006,
                    message=(
                        f"Constant '{const_def.name}' conflicts with "
                        f"existing {kind} of the same name."
                    ),
                    file_path=module.path,
                    line=_location_line(const_def.location),
                    column=_location_column(const_def.location),
                    line_text=_line_text(module, const_def.location),
                    span=_location_span(const_def.location, const_def.name),
                    hint="Rename one of the conflicting definitions.",
                )
            )
        else:
            names[const_def.name] = ("constant", const_def.location)


def _validate_constant_types(
    module: Module, errors: list[SyncLangsError]
) -> None:
    """Validate that constants use primitive types only."""
    for const_def in module.constants:
        if not isinstance(const_def.type_expr, PrimitiveTypeExpr):
            errors.append(
                SyncLangsError(
                    code=SY008,
                    message=(
                        f"Constant '{const_def.name}' must have a primitive type."
                    ),
                    file_path=module.path,
                    line=_location_line(const_def.location),
                    column=_location_column(const_def.location),
                    line_text=_line_text(module, const_def.location),
                    span=_location_span(const_def.location, const_def.name),
                    hint="Use string, int, float, or bool for constant types.",
                )
            )


def _iter_fields(module: Module) -> Iterable[Field]:
    """Yield all fields within a module."""
    for type_def in module.types:
        for field in type_def.fields:
            yield field


def _collect_type_refs(type_expr: TypeExpr) -> list[TypeRef]:
    """Collect all type references within a type expression."""
    if isinstance(type_expr, TypeRef):
        return [type_expr]
    if isinstance(type_expr, ListTypeExpr):
        return _collect_type_refs(type_expr.element_type)
    if isinstance(type_expr, MapTypeExpr):
        return _collect_type_refs(type_expr.key_type) + _collect_type_refs(
            type_expr.value_type
        )
    if isinstance(type_expr, NullableTypeExpr):
        return _collect_type_refs(type_expr.inner_type)
    if isinstance(type_expr, PrimitiveTypeExpr):
        return []
    return []


def _suggest_type(name: str, candidates: Iterable[str]) -> str | None:
    """Return a suggestion for a missing type name."""
    matches = difflib.get_close_matches(name, list(candidates), n=1)
    if matches:
        return f"Did you mean '{matches[0]}'?"
    if candidates:
        return "Available types: " + ", ".join(sorted(candidates))
    return None


def _line_text(module: Module, location: SourceLocation | None) -> str | None:
    """Return the source line for a location."""
    if location is None or module.source is None:
        return None
    lines = module.source.splitlines()
    if location.line <= 0 or location.line > len(lines):
        return None
    return lines[location.line - 1]


def _location_line(location: SourceLocation | None) -> int | None:
    return location.line if location else None


def _location_column(location: SourceLocation | None) -> int | None:
    return location.column if location else None


def _location_span(location: SourceLocation | None, fallback: str) -> int | None:
    if location is None:
        return None
    if location.end_column is not None:
        return max(location.end_column - location.column, 1)
    return max(len(fallback), 1)

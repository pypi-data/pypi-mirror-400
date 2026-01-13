"""Abstract syntax tree nodes for the SyncLangs DSL."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias


class PrimitiveType(Enum):
    """Supported primitive types in the SyncLangs DSL."""

    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    ANY = "any"


@dataclass(frozen=True)
class SourceLocation:
    """Source location for a parsed token."""

    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None


@dataclass(frozen=True)
class PrimitiveTypeExpr:
    """Primitive type expression (e.g., string, int)."""

    primitive: PrimitiveType


@dataclass(frozen=True)
class ListTypeExpr:
    """List type expression (e.g., list<string>)."""

    element_type: "TypeExpr"


@dataclass(frozen=True)
class MapTypeExpr:
    """Map type expression (e.g., map<string, int>)."""

    key_type: "TypeExpr"
    value_type: "TypeExpr"


@dataclass(frozen=True)
class NullableTypeExpr:
    """Nullable type expression (e.g., string?)."""

    inner_type: "TypeExpr"


@dataclass(frozen=True)
class TypeRef:
    """Reference to a named type within the same module."""

    name: str
    location: SourceLocation | None = None


TypeExpr: TypeAlias = (
    PrimitiveTypeExpr | ListTypeExpr | MapTypeExpr | NullableTypeExpr | TypeRef
)


@dataclass(frozen=True)
class Field:
    """Field definition within a type."""

    name: str
    type_expr: TypeExpr
    doc_comment: str | None = None
    location: SourceLocation | None = None


@dataclass(frozen=True)
class TypeDef:
    """Type definition consisting of named fields."""

    name: str
    fields: list[Field]
    extends: str | None = None
    implements: list[str] | None = None
    doc_comment: str | None = None
    location: SourceLocation | None = None


@dataclass(frozen=True)
class Import:
    """Import statement for referenced types."""

    names: list[str]
    path: str
    location: SourceLocation | None = None


@dataclass(frozen=True)
class EnumVariant:
    """A single variant within an enum definition."""

    name: str
    doc_comment: str | None = None
    location: SourceLocation | None = None


@dataclass(frozen=True)
class EnumDef:
    """Enum definition with named variants."""

    name: str
    variants: list[EnumVariant]
    doc_comment: str | None = None
    location: SourceLocation | None = None


@dataclass(frozen=True)
class ConstValue:
    """A constant literal value."""

    value: str | int | float | bool
    raw: str  # Original string representation


@dataclass(frozen=True)
class ConstDef:
    """Constant definition with name, type, and value."""

    name: str
    type_expr: TypeExpr
    value: ConstValue
    doc_comment: str | None = None
    location: SourceLocation | None = None


@dataclass(frozen=True)
class FunctionParam:
    """A parameter in a function signature."""

    name: str
    type_expr: TypeExpr
    default_value: ConstValue | None = None
    location: SourceLocation | None = None


@dataclass(frozen=True)
class VoidType:
    """Represents a void return type."""

    pass


# Return type can be a TypeExpr or VoidType
ReturnType = TypeExpr | VoidType


@dataclass(frozen=True)
class FunctionDef:
    """Function signature definition."""

    name: str
    params: list[FunctionParam]
    return_type: ReturnType
    is_async: bool = False
    doc_comment: str | None = None
    location: SourceLocation | None = None


@dataclass(frozen=True)
class InterfaceDef:
    """Interface definition with fields and function signatures."""

    name: str
    fields: list[Field]
    functions: list[FunctionDef]
    doc_comment: str | None = None
    location: SourceLocation | None = None


@dataclass(frozen=True)
class Module:
    """A module representing a single .syln file."""

    path: str
    imports: list[Import]
    types: list[TypeDef]
    enums: list[EnumDef] = None  # type: ignore[assignment]
    constants: list[ConstDef] = None  # type: ignore[assignment]
    functions: list[FunctionDef] = None  # type: ignore[assignment]
    interfaces: list[InterfaceDef] = None  # type: ignore[assignment]
    source: str | None = None

    def __post_init__(self) -> None:
        """Initialize default values for optional fields."""
        if self.enums is None:
            object.__setattr__(self, "enums", [])
        if self.constants is None:
            object.__setattr__(self, "constants", [])
        if self.functions is None:
            object.__setattr__(self, "functions", [])
        if self.interfaces is None:
            object.__setattr__(self, "interfaces", [])

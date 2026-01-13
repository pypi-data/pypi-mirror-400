"""Lark parse tree to AST transformer."""

from __future__ import annotations

from typing import Any

from lark import Token, Transformer, v_args

from synclangs.parser.ast import (
    ConstDef,
    ConstValue,
    EnumDef,
    EnumVariant,
    Field,
    FunctionDef,
    FunctionParam,
    Import,
    InterfaceDef,
    ListTypeExpr,
    MapTypeExpr,
    Module,
    NullableTypeExpr,
    PrimitiveType,
    PrimitiveTypeExpr,
    SourceLocation,
    TypeDef,
    TypeExpr,
    TypeRef,
    VoidType,
)


@v_args(inline=True)
class TreeToAstTransformer(Transformer):
    """Transform a Lark parse tree into SyncLangs AST nodes."""

    def __init__(self, path: str = "<string>", source: str | None = None) -> None:
        super().__init__()
        self._path = path
        self._source = source

    def start(self, *items: Any) -> Module:
        """Create a module from imports, types, enums, constants, functions, and interfaces."""
        imports: list[Import] = []
        types: list[TypeDef] = []
        enums: list[EnumDef] = []
        constants: list[ConstDef] = []
        functions: list[FunctionDef] = []
        interfaces: list[InterfaceDef] = []
        for item in items:
            if isinstance(item, Import):
                imports.append(item)
            elif isinstance(item, TypeDef):
                types.append(item)
            elif isinstance(item, EnumDef):
                enums.append(item)
            elif isinstance(item, ConstDef):
                constants.append(item)
            elif isinstance(item, FunctionDef):
                functions.append(item)
            elif isinstance(item, InterfaceDef):
                interfaces.append(item)
        return Module(
            path=self._path,
            imports=imports,
            types=types,
            enums=enums,
            constants=constants,
            functions=functions,
            interfaces=interfaces,
            source=self._source,
        )

    def type_def(self, *args: Any) -> TypeDef:
        """Create a type definition with its fields, extends, and implements."""
        doc_comment: str | None = None
        extends: str | None = None
        implements: list[str] | None = None

        args_list = list(args)

        # Check for doc comment first
        if args_list and isinstance(args_list[0], str) and not isinstance(args_list[0], Token):
            doc_comment = args_list.pop(0)

        # Name is the next token
        name = args_list.pop(0)

        # Process remaining items
        fields: list[Field] = []
        for item in args_list:
            if isinstance(item, Field):
                fields.append(item)
            elif isinstance(item, str) and not isinstance(item, Token):
                # This could be extends or implements result
                # extends is a single string, implements is a list
                pass
            elif isinstance(item, tuple) and len(item) == 2:
                key, value = item
                if key == "extends":
                    extends = value
                elif key == "implements":
                    implements = value

        return TypeDef(
            name=str(name),
            fields=fields,
            extends=extends,
            implements=implements,
            doc_comment=doc_comment,
            location=_location_from_token(name),
        )

    def extends_clause(self, name: Any) -> tuple[str, str]:
        """Extract the base type name from extends clause."""
        return ("extends", str(name))

    def implements_clause(self, first: Any, *rest: Any) -> tuple[str, list[str]]:
        """Extract interface names from implements clause."""
        return ("implements", [str(first)] + [str(n) for n in rest])

    def enum_def(self, *args: Any) -> EnumDef:
        """Create an enum definition with its variants."""
        doc_comment: str | None = None
        if args and isinstance(args[0], Token):
            name = args[0]
            variants = [v for v in args[1:] if isinstance(v, EnumVariant)]
        else:
            doc_comment = str(args[0])
            name = args[1]
            variants = [v for v in args[2:] if isinstance(v, EnumVariant)]
        return EnumDef(
            name=str(name),
            variants=variants,
            doc_comment=doc_comment,
            location=_location_from_token(name),
        )

    def enum_variant(self, *args: Any) -> EnumVariant:
        """Create a single enum variant."""
        doc_comment: str | None = None
        if args and isinstance(args[0], Token):
            name = args[0]
        else:
            doc_comment = str(args[0])
            name = args[1]
        return EnumVariant(
            name=str(name),
            doc_comment=doc_comment,
            location=_location_from_token(name),
        )

    def const_def(self, *args: Any) -> ConstDef:
        """Create a constant definition."""
        doc_comment: str | None = None
        if args and isinstance(args[0], Token):
            name = args[0]
            type_expr = args[1]
            value = args[2]
        else:
            doc_comment = str(args[0])
            name = args[1]
            type_expr = args[2]
            value = args[3]
        return ConstDef(
            name=str(name),
            type_expr=type_expr,
            value=value,
            doc_comment=doc_comment,
            location=_location_from_token(name),
        )

    def number_value(self, token: Any) -> ConstValue:
        """Parse a numeric constant value."""
        raw = str(token)
        if "." in raw:
            return ConstValue(value=float(raw), raw=raw)
        return ConstValue(value=int(raw), raw=raw)

    def string_value(self, token: Any) -> ConstValue:
        """Parse a string constant value."""
        raw = str(token)
        return ConstValue(value=_strip_quotes(raw), raw=raw)

    def true_value(self) -> ConstValue:
        """Parse a true boolean constant."""
        return ConstValue(value=True, raw="true")

    def false_value(self) -> ConstValue:
        """Parse a false boolean constant."""
        return ConstValue(value=False, raw="false")

    def import_names(self, first: Any, *rest: Any) -> list[str]:
        """Return a list of imported type names."""
        return [str(first), *[str(item) for item in rest]]

    def import_stmt(self, names: list[str], path: Any) -> Import:
        """Create an import statement."""
        return Import(
            names=names,
            path=_strip_quotes(str(path)),
            location=_location_from_token(path),
        )

    def field(self, *args: Any) -> Field:
        """Create a field definition."""
        doc_comment: str | None = None
        if args and isinstance(args[0], Token):
            name = args[0]
            type_expr = args[1]
        else:
            doc_comment = str(args[0])
            name = args[1]
            type_expr = args[2]
        return Field(
            name=str(name),
            type_expr=type_expr,
            doc_comment=doc_comment,
            location=_location_from_token(name),
        )

    def doc_comment(self, *lines: Any) -> str:
        """Normalize doc comments into a single string."""
        cleaned: list[str] = []
        for line in lines:
            text = str(line)
            if text.startswith("##"):
                text = text[2:]
            cleaned.append(text.strip())
        return "\n".join(cleaned).strip()

    def type_expr(self, value: TypeExpr | Any) -> TypeExpr:
        """Normalize primitive or reference types into AST nodes."""
        if isinstance(value, (PrimitiveTypeExpr, TypeRef)):
            return value
        return value

    def base_type(self, value: TypeExpr) -> TypeExpr:
        """Return the base type expression."""
        return value

    def generic_type(self, value: TypeExpr) -> TypeExpr:
        """Return the generic type expression."""
        return value

    def type_ref(self, name: Any) -> TypeRef:
        """Create a reference to another type."""
        return TypeRef(str(name), location=_location_from_token(name))

    def list_type(self, element_type: TypeExpr) -> ListTypeExpr:
        """Return a list type expression."""
        return ListTypeExpr(element_type=element_type)

    def map_type(self, key_type: TypeExpr, value_type: TypeExpr) -> MapTypeExpr:
        """Return a map type expression."""
        return MapTypeExpr(key_type=key_type, value_type=value_type)

    def nullable_type(self, inner_type: TypeExpr) -> NullableTypeExpr:
        """Return a nullable type expression."""
        return NullableTypeExpr(inner_type=inner_type)

    def string_type(self) -> PrimitiveTypeExpr:
        """Return a string primitive type expression."""
        return PrimitiveTypeExpr(PrimitiveType.STRING)

    def int_type(self) -> PrimitiveTypeExpr:
        """Return an int primitive type expression."""
        return PrimitiveTypeExpr(PrimitiveType.INT)

    def float_type(self) -> PrimitiveTypeExpr:
        """Return a float primitive type expression."""
        return PrimitiveTypeExpr(PrimitiveType.FLOAT)

    def bool_type(self) -> PrimitiveTypeExpr:
        """Return a bool primitive type expression."""
        return PrimitiveTypeExpr(PrimitiveType.BOOL)

    def any_type(self) -> PrimitiveTypeExpr:
        """Return an any primitive type expression."""
        return PrimitiveTypeExpr(PrimitiveType.ANY)

    def void_type(self) -> VoidType:
        """Return a void type for functions with no return value."""
        return VoidType()

    def return_type(self, value: Any) -> TypeExpr | VoidType:
        """Return the return type expression."""
        return value

    def async_modifier(self) -> bool:
        """Return True to indicate an async function."""
        return True

    def fn_param(self, *args: Any) -> FunctionParam:
        """Create a function parameter."""
        name = args[0]
        type_expr = args[1]
        default_value = args[2] if len(args) > 2 else None
        return FunctionParam(
            name=str(name),
            type_expr=type_expr,
            default_value=default_value,
            location=_location_from_token(name),
        )

    def default_value(self, value: ConstValue) -> ConstValue:
        """Return the default value for a parameter."""
        return value

    def fn_params(self, first: FunctionParam, *rest: Any) -> list[FunctionParam]:
        """Collect function parameters into a list."""
        return [first] + [p for p in rest if isinstance(p, FunctionParam)]

    def fn_def(self, *args: Any) -> FunctionDef:
        """Create a standalone function definition."""
        return self._parse_function_def(args)

    def fn_signature(self, *args: Any) -> FunctionDef:
        """Create a function signature (for interfaces)."""
        return self._parse_function_def(args)

    def _parse_function_def(self, args: tuple[Any, ...]) -> FunctionDef:
        """Parse function definition arguments."""
        doc_comment: str | None = None
        is_async: bool = False
        params: list[FunctionParam] = []

        args_list = list(args)

        # Check for doc comment first
        if args_list and isinstance(args_list[0], str) and not isinstance(args_list[0], Token):
            doc_comment = args_list.pop(0)

        # Check for async modifier
        if args_list and args_list[0] is True:
            is_async = True
            args_list.pop(0)

        # Name is the next token
        name = args_list.pop(0)

        # Process remaining items
        return_type: TypeExpr | VoidType = VoidType()
        for item in args_list:
            if isinstance(item, list):
                params = item
            elif isinstance(item, FunctionParam):
                # Single param without list wrapper
                params = [item]
            elif isinstance(item, (VoidType, PrimitiveTypeExpr, ListTypeExpr,
                                   MapTypeExpr, NullableTypeExpr, TypeRef)):
                return_type = item

        return FunctionDef(
            name=str(name),
            params=params,
            return_type=return_type,
            is_async=is_async,
            doc_comment=doc_comment,
            location=_location_from_token(name),
        )

    def interface_member(self, value: Any) -> Field | FunctionDef:
        """Return an interface member (field or function signature)."""
        return value

    def interface_def(self, *args: Any) -> InterfaceDef:
        """Create an interface definition."""
        doc_comment: str | None = None

        args_list = list(args)

        # Check for doc comment first
        if args_list and isinstance(args_list[0], str) and not isinstance(args_list[0], Token):
            doc_comment = args_list.pop(0)

        # Name is the next token
        name = args_list.pop(0)

        # Separate fields and functions from members
        fields: list[Field] = []
        functions: list[FunctionDef] = []
        for item in args_list:
            if isinstance(item, Field):
                fields.append(item)
            elif isinstance(item, FunctionDef):
                functions.append(item)

        return InterfaceDef(
            name=str(name),
            fields=fields,
            functions=functions,
            doc_comment=doc_comment,
            location=_location_from_token(name),
        )


def _strip_quotes(value: str) -> str:
    """Strip matching quotes from a string token."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("\"", "'"):
        return value[1:-1]
    return value


def _location_from_token(token: Any) -> SourceLocation | None:
    """Build a source location from a Lark token."""
    if not isinstance(token, Token):
        return None
    end_line = getattr(token, "end_line", None)
    end_column = getattr(token, "end_column", None)
    if end_line is None:
        end_line = token.line
    if end_column is None:
        end_column = token.column + len(str(token))
    return SourceLocation(
        line=token.line,
        column=token.column,
        end_line=end_line,
        end_column=end_column,
    )

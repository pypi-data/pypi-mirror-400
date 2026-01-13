"""Parser entry points for SyncLangs DSL."""

from __future__ import annotations

from pathlib import Path

from lark import Lark

from synclangs.parser.ast import Module
from synclangs.parser.transformer import TreeToAstTransformer


def _load_grammar() -> str:
    """Load the Lark grammar from disk."""
    grammar_path = Path(__file__).with_name("grammar.lark")
    return grammar_path.read_text(encoding="utf-8")


_PARSER = Lark(_load_grammar(), start="start", parser="lalr")


def parse(source: str, path: str | None = None) -> Module:
    """Parse a SyncLangs schema string into a Module AST.

    Args:
        source: The schema contents to parse.
        path: Optional path for the source file.

    Returns:
        A Module AST representing the schema.
    """
    tree = _PARSER.parse(source)
    transformer = TreeToAstTransformer(path or "<string>", source=source)
    return transformer.transform(tree)

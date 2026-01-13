"""Base interfaces for code generators."""

from __future__ import annotations

from abc import ABC, abstractmethod

from synclangs.parser.ast import Module


class CodeGenerator(ABC):
    """Abstract base class for language-specific generators."""

    @abstractmethod
    def generate(self, module: Module) -> str:
        """Generate source code for a parsed module."""
        raise NotImplementedError

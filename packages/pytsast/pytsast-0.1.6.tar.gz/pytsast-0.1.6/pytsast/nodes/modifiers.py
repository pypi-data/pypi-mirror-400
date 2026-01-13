"""
Modifier AST nodes - export, const, async, public, private, etc.
"""

from __future__ import annotations

from typing import ClassVar

from pytsast.nodes.keywords import Keyword
from pytsast.core.syntax_kind import SyntaxKind


class Modifier(Keyword):
    """
    Base class for keyword modifiers.

    All modifier keywords (export, public, readonly, etc.) should
    inherit from this class.
    """

    factory_name: ClassVar[str] = "createToken"


# ============================================================================
# Specific Modifiers (for convenience)
# ============================================================================


class ExportKeyword(Modifier):
    """Represents the 'export' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.ExportKeyword,)


class DefaultKeyword(Modifier):
    """Represents the 'default' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.DefaultKeyword,)


class DeclareKeyword(Modifier):
    """Represents the 'declare' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.DeclareKeyword,)


class ConstKeyword(Modifier):
    """Represents the 'const' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.ConstKeyword,)


class AbstractKeyword(Modifier):
    """Represents the 'abstract' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.AbstractKeyword,)


class AsyncKeyword(Modifier):
    """Represents the 'async' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.AsyncKeyword,)


class PublicKeyword(Modifier):
    """Represents the 'public' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.PublicKeyword,)


class PrivateKeyword(Modifier):
    """Represents the 'private' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.PrivateKeyword,)


class ProtectedKeyword(Modifier):
    """Represents the 'protected' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.ProtectedKeyword,)


class ReadonlyKeyword(Modifier):
    """Represents the 'readonly' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.ReadonlyKeyword,)


class StaticKeyword(Modifier):
    """Represents the 'static' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.StaticKeyword,)


class OverrideKeyword(Modifier):
    """Represents the 'override' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.OverrideKeyword,)


class AccessorKeyword(Modifier):
    """Represents the 'accessor' keyword."""

    def _get_ordered_args(self):
        return (SyntaxKind.AccessorKeyword,)


class InKeyword(Modifier):
    """Represents the 'in' keyword (for type parameters)."""

    def _get_ordered_args(self):
        return (SyntaxKind.InKeyword,)


class OutKeyword(Modifier):
    """Represents the 'out' keyword (for type parameters)."""

    def _get_ordered_args(self):
        return (SyntaxKind.OutKeyword,)

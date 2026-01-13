"""
Keyword type AST nodes - void, never, any, boolean, number, string, etc.
"""

from __future__ import annotations

from typing import ClassVar

from pytsast.core.base import Node
from pytsast.core.syntax_kind import SyntaxKind


class Keyword(Node):
    """
    Base class for keyword type nodes.

    All keyword type nodes (void, any, boolean, etc.) should
    inherit from this class.
    """

    factory_name: ClassVar[str] = "createKeywordTypeNode"


class VoidKeyword(Keyword):
    """Represents the 'void' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.VoidKeyword,)


class NeverKeyword(Keyword):
    """Represents the 'never' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.NeverKeyword,)


class AnyKeyword(Keyword):
    """Represents the 'any' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.AnyKeyword,)


class BooleanKeyword(Keyword):
    """Represents the 'boolean' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.BooleanKeyword,)


class NumberKeyword(Keyword):
    """Represents the 'number' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.NumberKeyword,)


class StringKeyword(Keyword):
    """Represents the 'string' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.StringKeyword,)


class SymbolKeyword(Keyword):
    """Represents the 'symbol' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.SymbolKeyword,)


class BigIntKeyword(Keyword):
    """Represents the 'bigint' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.BigIntKeyword,)


class ObjectKeyword(Keyword):
    """Represents the 'object' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.ObjectKeyword,)


class UnknownKeyword(Keyword):
    """Represents the 'unknown' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.UnknownKeyword,)


class UndefinedKeyword(Keyword):
    """Represents the 'undefined' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.UndefinedKeyword,)


class NullKeyword(Keyword):
    """Represents the 'null' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.NullKeyword,)


class ThisKeyword(Keyword):
    """
    Represents the 'this' keyword.

    TypeScript: ts.factory.createToken(SyntaxKind.ThisKeyword)
    """

    factory_name = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.ThisKeyword,)


class SuperKeyword(Keyword):
    """
    Represents the 'super' keyword.

    TypeScript: ts.factory.createToken(SyntaxKind.SuperKeyword)
    """

    factory_name = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.SuperKeyword,)


class IntrinsicKeyword(Keyword):
    """Represents the 'intrinsic' keyword type."""

    def _get_ordered_args(self):
        return (SyntaxKind.IntrinsicKeyword,)


class AssertsKeyword(Keyword):
    """
    Represents the 'asserts' keyword.

    TypeScript: ts.factory.createToken(SyntaxKind.AssertsKeyword)
    """

    factory_name = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.AssertsKeyword,)


class AwaitKeywordType(Keyword):
    """
    Represents the 'await' keyword type.

    TypeScript: ts.factory.createToken(SyntaxKind.AwaitKeyword)
    """

    factory_name = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.AwaitKeyword,)

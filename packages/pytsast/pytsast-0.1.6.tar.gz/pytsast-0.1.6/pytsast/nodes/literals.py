"""
Literal AST nodes - String, Number, Boolean, etc.
"""

from __future__ import annotations

from typing import ClassVar

from pytsast.core.base import Node
from pytsast.core.types import Undefined, undefined


class StringLiteral(Node):
    """
    Represents a string literal.

    TypeScript: ts.factory.createStringLiteral(text, isSingleQuote?)
    """

    factory_name: ClassVar[str] = "createStringLiteral"

    text: str
    is_single_quote: bool = False


class NumericLiteral(Node):
    """
    Represents a numeric literal.

    TypeScript: ts.factory.createNumericLiteral(value, numericLiteralFlags?)
    """

    factory_name: ClassVar[str] = "createNumericLiteral"

    value: str | int | float


class BigIntLiteral(Node):
    """
    Represents a BigInt literal (e.g., 100n).

    TypeScript: ts.factory.createBigIntLiteral(value)
    """

    factory_name: ClassVar[str] = "createBigIntLiteral"

    value: str


class RegularExpressionLiteral(Node):
    """
    Represents a regular expression literal.

    TypeScript: ts.factory.createRegularExpressionLiteral(text)
    """

    factory_name: ClassVar[str] = "createRegularExpressionLiteral"

    text: str


class NoSubstitutionTemplateLiteral(Node):
    """
    Represents a template literal without substitutions.

    TypeScript: ts.factory.createNoSubstitutionTemplateLiteral(text, rawText?)
    """

    factory_name: ClassVar[str] = "createNoSubstitutionTemplateLiteral"

    text: str
    raw_text: str | Undefined = undefined


class TrueLiteral(Node):
    """
    Represents the 'true' literal.

    TypeScript: ts.factory.createTrue()
    """

    factory_name: ClassVar[str] = "createTrue"

    def _get_ordered_args(self):
        return ()


class FalseLiteral(Node):
    """
    Represents the 'false' literal.

    TypeScript: ts.factory.createFalse()
    """

    factory_name: ClassVar[str] = "createFalse"

    def _get_ordered_args(self):
        return ()


class NullLiteral(Node):
    """
    Represents the 'null' literal.

    TypeScript: ts.factory.createNull()
    """

    factory_name: ClassVar[str] = "createNull"

    def _get_ordered_args(self):
        return ()

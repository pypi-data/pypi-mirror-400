"""
Token AST nodes - Punctuation tokens like ?, ..., :, =>, *, etc.
"""

from __future__ import annotations

from typing import ClassVar

from pytsast.core.base import Node
from pytsast.core.syntax_kind import SyntaxKind


class Token(Node):
    """
    Base class for token nodes.

    TypeScript: ts.factory.createToken(kind)
    """

    factory_name: ClassVar[str] = "createToken"

    kind: int

    def _get_ordered_args(self):
        return (self.kind,)


class QuestionToken(Node):
    """
    Represents the '?' token.

    TypeScript: ts.factory.createToken(SyntaxKind.QuestionToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.QuestionToken,)


class ExclamationToken(Node):
    """
    Represents the '!' token.

    TypeScript: ts.factory.createToken(SyntaxKind.ExclamationToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.ExclamationToken,)


class DotDotDotToken(Node):
    """
    Represents the '...' token.

    TypeScript: ts.factory.createToken(SyntaxKind.DotDotDotToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.DotDotDotToken,)


class ColonToken(Node):
    """
    Represents the ':' token.

    TypeScript: ts.factory.createToken(SyntaxKind.ColonToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.ColonToken,)


class EqualsGreaterThanToken(Node):
    """
    Represents the '=>' token.

    TypeScript: ts.factory.createToken(SyntaxKind.EqualsGreaterThanToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.EqualsGreaterThanToken,)


class AsteriskToken(Node):
    """
    Represents the '*' token.

    TypeScript: ts.factory.createToken(SyntaxKind.AsteriskToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.AsteriskToken,)


class EqualsToken(Node):
    """
    Represents the '=' token.

    TypeScript: ts.factory.createToken(SyntaxKind.EqualsToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.EqualsToken,)


class PlusToken(Node):
    """
    Represents the '+' token.

    TypeScript: ts.factory.createToken(SyntaxKind.PlusToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.PlusToken,)


class MinusToken(Node):
    """
    Represents the '-' token.

    TypeScript: ts.factory.createToken(SyntaxKind.MinusToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.MinusToken,)


class CommaToken(Node):
    """
    Represents the ',' token.

    TypeScript: ts.factory.createToken(SyntaxKind.CommaToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.CommaToken,)


class SemicolonToken(Node):
    """
    Represents the ';' token.

    TypeScript: ts.factory.createToken(SyntaxKind.SemicolonToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.SemicolonToken,)


class OpenBraceToken(Node):
    """
    Represents the '{' token.

    TypeScript: ts.factory.createToken(SyntaxKind.OpenBraceToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.OpenBraceToken,)


class CloseBraceToken(Node):
    """
    Represents the '}' token.

    TypeScript: ts.factory.createToken(SyntaxKind.CloseBraceToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.CloseBraceToken,)


class OpenParenToken(Node):
    """
    Represents the '(' token.

    TypeScript: ts.factory.createToken(SyntaxKind.OpenParenToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.OpenParenToken,)


class CloseParenToken(Node):
    """
    Represents the ')' token.

    TypeScript: ts.factory.createToken(SyntaxKind.CloseParenToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.CloseParenToken,)


class OpenBracketToken(Node):
    """
    Represents the '[' token.

    TypeScript: ts.factory.createToken(SyntaxKind.OpenBracketToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.OpenBracketToken,)


class CloseBracketToken(Node):
    """
    Represents the ']' token.

    TypeScript: ts.factory.createToken(SyntaxKind.CloseBracketToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.CloseBracketToken,)


class DotToken(Node):
    """
    Represents the '.' token.

    TypeScript: ts.factory.createToken(SyntaxKind.DotToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.DotToken,)


class LessThanToken(Node):
    """
    Represents the '<' token.

    TypeScript: ts.factory.createToken(SyntaxKind.LessThanToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.LessThanToken,)


class GreaterThanToken(Node):
    """
    Represents the '>' token.

    TypeScript: ts.factory.createToken(SyntaxKind.GreaterThanToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.GreaterThanToken,)


class AtToken(Node):
    """
    Represents the '@' token.

    TypeScript: ts.factory.createToken(SyntaxKind.AtToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.AtToken,)


class BarToken(Node):
    """
    Represents the '|' token.

    TypeScript: ts.factory.createToken(SyntaxKind.BarToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.BarToken,)


class AmpersandToken(Node):
    """
    Represents the '&' token.

    TypeScript: ts.factory.createToken(SyntaxKind.AmpersandToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.AmpersandToken,)


class CaretToken(Node):
    """
    Represents the '^' token.

    TypeScript: ts.factory.createToken(SyntaxKind.CaretToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.CaretToken,)


class TildeToken(Node):
    """
    Represents the '~' token.

    TypeScript: ts.factory.createToken(SyntaxKind.TildeToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.TildeToken,)


class QuestionQuestionToken(Node):
    """
    Represents the '??' token.

    TypeScript: ts.factory.createToken(SyntaxKind.QuestionQuestionToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.QuestionQuestionToken,)


class BarBarToken(Node):
    """
    Represents the '||' token.

    TypeScript: ts.factory.createToken(SyntaxKind.BarBarToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.BarBarToken,)


class AmpersandAmpersandToken(Node):
    """
    Represents the '&&' token.

    TypeScript: ts.factory.createToken(SyntaxKind.AmpersandAmpersandToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.AmpersandAmpersandToken,)


class PlusPlusToken(Node):
    """
    Represents the '++' token.

    TypeScript: ts.factory.createToken(SyntaxKind.PlusPlusToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.PlusPlusToken,)


class MinusMinusToken(Node):
    """
    Represents the '--' token.

    TypeScript: ts.factory.createToken(SyntaxKind.MinusMinusToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.MinusMinusToken,)


class QuestionDotToken(Node):
    """
    Represents the '?.' token (optional chaining).

    TypeScript: ts.factory.createToken(SyntaxKind.QuestionDotToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.QuestionDotToken,)


class AmpersandAmpersandEqualsToken(Node):
    """
    Represents the '&&=' token.

    TypeScript: ts.factory.createToken(
        SyntaxKind.AmpersandAmpersandEqualsToken
    )
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.AmpersandAmpersandEqualsToken,)


class BarBarEqualsToken(Node):
    """
    Represents the '||=' token.

    TypeScript: ts.factory.createToken(SyntaxKind.BarBarEqualsToken)
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.BarBarEqualsToken,)


class QuestionQuestionEqualsToken(Node):
    """
    Represents the '??=' token.

    TypeScript: ts.factory.createToken(
        SyntaxKind.QuestionQuestionEqualsToken
    )
    """

    factory_name: ClassVar[str] = "createToken"

    def _get_ordered_args(self):
        return (SyntaxKind.QuestionQuestionEqualsToken,)

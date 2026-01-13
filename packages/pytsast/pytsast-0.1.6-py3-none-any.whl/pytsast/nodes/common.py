"""
Common AST nodes - Identifiers and qualified names.
"""

from __future__ import annotations

from typing import ClassVar

from pytsast.core.base import Node


class Identifier(Node):
    """
    Represents an identifier (variable name, function name, etc.).

    TypeScript: ts.factory.createIdentifier(text)
    """

    factory_name: ClassVar[str] = "createIdentifier"

    text: str


class PrivateIdentifier(Node):
    """
    Represents a private identifier (#name).

    TypeScript: ts.factory.createPrivateIdentifier(text)
    """

    factory_name: ClassVar[str] = "createPrivateIdentifier"

    text: str


class QualifiedName(Node):
    """
    Represents a qualified name (e.g., Namespace.Type).

    TypeScript: ts.factory.createQualifiedName(left, right)
    """

    factory_name: ClassVar[str] = "createQualifiedName"

    left: "Identifier | QualifiedName"
    right: Identifier

"""
Core module - Base types and serialization infrastructure.
"""

from pytsast.core.base import Node, NodeList
from pytsast.core.types import (
    LiteralValue,
    Undefined,
    undefined,
    SerializedLiteral,
    SerializedNumber,
    SerializedFactory,
    SerializedUndefined,
    SerializedNode,
)
from pytsast.core.serializer import Serializer
from pytsast.core.syntax_kind import SyntaxKind, NodeFlags

__all__ = [
    "Node",
    "NodeList",
    "LiteralValue",
    "Undefined",
    "undefined",
    "SerializedFactory",
    "SerializedLiteral",
    "SerializedNode",
    "SerializedNumber",
    "SerializedUndefined",
    "Serializer",
    "SyntaxKind",
    "NodeFlags",
]

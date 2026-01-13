"""
pytsast - Python TypeScript AST Generator

Create TypeScript AST nodes from Python and serialize to JSON
for processing by the TypeScript compiler API.
"""

from pytsast.core.base import Node
from pytsast.core.serializer import Serializer
from pytsast.core.syntax_kind import SyntaxKind
from pytsast import factory
from pytsast.cli import generate_typescript, generate_typescript_inline

__all__ = [
    "Node",
    "Serializer",
    "factory",
    "SyntaxKind",
    "generate_typescript",
    "generate_typescript_inline",
]

__version__ = "0.1.6"

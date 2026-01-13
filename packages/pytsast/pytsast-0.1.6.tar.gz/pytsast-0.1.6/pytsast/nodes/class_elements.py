"""
Class element AST nodes - Properties, Methods, Constructors, Accessors.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Sequence

from pytsast.core.base import Node
from pytsast.core.types import Undefined, undefined
from pytsast.nodes.misc import Decorator
from pytsast.nodes.modifiers import Modifier

if TYPE_CHECKING:
    from pytsast.nodes.common import Identifier, PrivateIdentifier
    from pytsast.nodes.expressions import Expression
    from pytsast.nodes.statements import Block
    from pytsast.nodes.type_nodes import TypeNode
    from pytsast.nodes.misc import Parameter, TypeParameter


class PropertyDeclaration(Node):
    """
    Represents a class property declaration.

    TypeScript: ts.factory.createPropertyDeclaration(
        modifiers?, name, questionOrExclamationToken?, type?, initializer?
    )
    """

    factory_name: ClassVar[str] = "createPropertyDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | PrivateIdentifier | str | Node"
    question_or_exclamation_token: Node | Undefined = undefined
    type: "TypeNode | Undefined" = undefined
    initializer: "Expression | Undefined" = undefined


class MethodDeclaration(Node):
    """
    Represents a class method declaration.

    TypeScript: ts.factory.createMethodDeclaration(
        modifiers?, asteriskToken?, name, questionToken?, typeParameters?,
        parameters, type?, body?
    )
    """

    factory_name: ClassVar[str] = "createMethodDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    asterisk_token: Node | Undefined = undefined
    name: "Identifier | PrivateIdentifier | str | Node"
    question_token: Node | Undefined = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined
    body: "Block | Undefined" = undefined


class Constructor(Node):
    """
    Represents a constructor declaration.

    TypeScript: ts.factory.createConstructorDeclaration(modifiers?, parameters,
    body?)
    """

    factory_name: ClassVar[str] = "createConstructorDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    parameters: Sequence["Parameter"]
    body: "Block | Undefined" = undefined


class GetAccessor(Node):
    """
    Represents a get accessor: get name() { }.

    TypeScript: ts.factory.createGetAccessorDeclaration(modifiers?, name,
      parameters, type?, body?)
    """

    factory_name: ClassVar[str] = "createGetAccessorDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | PrivateIdentifier | str | Node"
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined
    body: "Block | Undefined" = undefined


class SetAccessor(Node):
    """
    Represents a set accessor: set name(value) { }.

    TypeScript: ts.factory.createSetAccessorDeclaration(modifiers?, name,
      parameters, body?)
    """

    factory_name: ClassVar[str] = "createSetAccessorDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | PrivateIdentifier | str | Node"
    parameters: Sequence["Parameter"]
    body: "Block | Undefined" = undefined


class IndexSignature(Node):
    """
    Represents an index signature: [key: string]: Type.

    TypeScript: ts.factory.createIndexSignature(modifiers?, parameters, type)
    """

    factory_name: ClassVar[str] = "createIndexSignature"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: "TypeNode"


class ClassStaticBlockDeclaration(Node):
    """
    Represents a static block: static { }.

    TypeScript: ts.factory.createClassStaticBlockDeclaration(body)
    """

    factory_name: ClassVar[str] = "createClassStaticBlockDeclaration"

    body: "Block"

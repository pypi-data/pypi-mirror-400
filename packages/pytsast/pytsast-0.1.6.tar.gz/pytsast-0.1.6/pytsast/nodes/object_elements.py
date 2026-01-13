"""
Object literal element AST nodes - Property assignments, spreads, etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Sequence

from pytsast.core.base import Node
from pytsast.core.types import Undefined, undefined
from pytsast.nodes.misc import Decorator

if TYPE_CHECKING:
    from pytsast.nodes.common import Identifier
    from pytsast.nodes.expressions import Expression
    from pytsast.nodes.statements import Block
    from pytsast.nodes.type_nodes import TypeNode
    from pytsast.nodes.modifiers import Modifier
    from pytsast.nodes.misc import Parameter, TypeParameter


class PropertyAssignment(Node):
    """
    Represents a property assignment: key: value.

    TypeScript: ts.factory.createPropertyAssignment(name, initializer)
    """

    factory_name: ClassVar[str] = "createPropertyAssignment"

    name: "Identifier | str | Node"
    initializer: "Expression"


class ShorthandPropertyAssignment(Node):
    """
    Represents a shorthand property assignment: { x } (same as { x: x }).

    TypeScript: ts.factory.createShorthandPropertyAssignment(name,
    objectAssignmentInitializer?)
    """

    factory_name: ClassVar[str] = "createShorthandPropertyAssignment"

    name: "Identifier | str"
    object_assignment_initializer: "Expression | Undefined" = undefined


class SpreadAssignment(Node):
    """
    Represents a spread assignment: ...obj.

    TypeScript: ts.factory.createSpreadAssignment(expression)
    """

    factory_name: ClassVar[str] = "createSpreadAssignment"

    expression: "Expression"


class MethodDeclarationShort(Node):
    """
    Represents a method declaration in an object literal: method() { }.

    TypeScript: ts.factory.createMethodDeclaration(
        modifiers?, asteriskToken?, name, questionToken?, typeParameters?,
        parameters, type?, body?
    )
    """

    factory_name: ClassVar[str] = "createMethodDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    asterisk_token: Node | Undefined = undefined
    name: "Identifier | str | Node"
    question_token: Node | Undefined = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined
    body: "Block | Undefined" = undefined


class GetAccessorShort(Node):
    """
    Represents a get accessor in an object literal: get name() { }.

    TypeScript: ts.factory.createGetAccessorDeclaration(modifiers?, name,
    parameters, type?, body?)
    """

    factory_name: ClassVar[str] = "createGetAccessorDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | str | Node"
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined
    body: "Block | Undefined" = undefined


class SetAccessorShort(Node):
    """
    Represents a set accessor in an object literal: set name(value) { }.

    TypeScript: ts.factory.createSetAccessorDeclaration(modifiers?, name,
      parameters, body?)
    """

    factory_name: ClassVar[str] = "createSetAccessorDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | str | Node"
    parameters: Sequence["Parameter"]
    body: "Block | Undefined" = undefined

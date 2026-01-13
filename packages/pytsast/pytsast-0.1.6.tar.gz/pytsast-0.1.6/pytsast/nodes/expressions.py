"""
Expression AST nodes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Sequence

from pytsast.core.base import Node
from pytsast.core.types import Undefined, undefined
from pytsast.nodes.misc import Decorator
from pytsast.nodes.modifiers import Modifier

if TYPE_CHECKING:
    from pytsast.nodes.common import Identifier, PrivateIdentifier
    from pytsast.nodes.type_nodes import TypeNode
    from pytsast.nodes.misc import (
        TemplateSpan,
        TemplateHead,
        Parameter,
        TypeParameter,
    )
    from pytsast.nodes.statements import Block


# Type alias for any expression
Expression = Node


class ArrayLiteralExpression(Node):
    """
    Represents an array literal expression: [a, b, c].

    TypeScript: ts.factory.createArrayLiteralExpression(elements?, multiLine?)
    """

    factory_name: ClassVar[str] = "createArrayLiteralExpression"

    elements: Sequence[Expression] | Undefined = undefined
    multi_line: bool = False


class ObjectLiteralExpression(Node):
    """
    Represents an object literal expression: { a: 1, b: 2 }.

    TypeScript: ts.factory.createObjectLiteralExpression(properties?,
      multiLine?)
    """

    factory_name: ClassVar[str] = "createObjectLiteralExpression"

    properties: Sequence[Node] | Undefined = undefined
    multi_line: bool = False


class PropertyAccessExpression(Node):
    """
    Represents property access: obj.property.

    TypeScript: ts.factory.createPropertyAccessExpression(expression, name)
    """

    factory_name: ClassVar[str] = "createPropertyAccessExpression"

    expression: Expression
    name: "Identifier | PrivateIdentifier | str"


class ElementAccessExpression(Node):
    """
    Represents element access: obj[index].

    TypeScript: ts.factory.createElementAccessExpression(expression, index)
    """

    factory_name: ClassVar[str] = "createElementAccessExpression"

    expression: Expression
    index: Expression


class CallExpression(Node):
    """
    Represents a function call: func(args).

    TypeScript: ts.factory.createCallExpression(expression, typeArguments?,
      argumentsArray?)
    """

    factory_name: ClassVar[str] = "createCallExpression"

    expression: Expression
    type_arguments: Sequence["TypeNode"] | Undefined = undefined
    arguments: Sequence[Expression] | Undefined = undefined


class NewExpression(Node):
    """
    Represents a new expression: new Class(args).

    TypeScript: ts.factory.createNewExpression(expression, typeArguments?,
      argumentsArray?)
    """

    factory_name: ClassVar[str] = "createNewExpression"

    expression: Expression
    type_arguments: Sequence["TypeNode"] | Undefined = undefined
    arguments: Sequence[Expression] | Undefined = undefined


class TaggedTemplateExpression(Node):
    """
    Represents a tagged template expression: tag`template`.

    TypeScript: ts.factory.createTaggedTemplateExpression(tag, typeArguments?,
      template)
    """

    factory_name: ClassVar[str] = "createTaggedTemplateExpression"

    tag: Expression
    type_arguments: Sequence["TypeNode"] | Undefined = undefined
    template: Node  # TemplateLiteral


class TypeAssertionExpression(Node):
    """
    Represents a type assertion: <Type>expression.

    TypeScript: ts.factory.createTypeAssertion(type, expression)
    """

    factory_name: ClassVar[str] = "createTypeAssertion"

    type: "TypeNode"
    expression: Expression


class ParenthesizedExpression(Node):
    """
    Represents a parenthesized expression: (expression).

    TypeScript: ts.factory.createParenthesizedExpression(expression)
    """

    factory_name: ClassVar[str] = "createParenthesizedExpression"

    expression: Expression


class FunctionExpression(Node):
    """
    Represents a function expression: function(params) { body }.

    TypeScript: ts.factory.createFunctionExpression(
        modifiers?, asteriskToken?, name?, typeParameters?, parameters?, type?,
          body
    )
    """

    factory_name: ClassVar[str] = "createFunctionExpression"

    modifiers: Sequence[Modifier] | Undefined = undefined
    asterisk_token: Node | Undefined = undefined
    name: "Identifier | str | Undefined" = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"] | Undefined = undefined
    type: "TypeNode | Undefined" = undefined
    body: "Block | Undefined" = undefined


class ArrowFunction(Node):
    """
    Represents an arrow function: (params) => body.

    TypeScript: ts.factory.createArrowFunction(
        modifiers?, typeParameters?, parameters, type?,
          equalsGreaterThanToken?, body
    )
    """

    factory_name: ClassVar[str] = "createArrowFunction"

    modifiers: Sequence[Modifier] | Undefined = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined
    equals_greater_than_token: Node | Undefined = undefined
    body: "Block | Expression"


class DeleteExpression(Node):
    """
    Represents a delete expression: delete obj.prop.

    TypeScript: ts.factory.createDeleteExpression(expression)
    """

    factory_name: ClassVar[str] = "createDeleteExpression"

    expression: Expression


class TypeOfExpression(Node):
    """
    Represents a typeof expression: typeof x.

    TypeScript: ts.factory.createTypeOfExpression(expression)
    """

    factory_name: ClassVar[str] = "createTypeOfExpression"

    expression: Expression


class VoidExpression(Node):
    """
    Represents a void expression: void expression.

    TypeScript: ts.factory.createVoidExpression(expression)
    """

    factory_name: ClassVar[str] = "createVoidExpression"

    expression: Expression


class AwaitExpression(Node):
    """
    Represents an await expression: await promise.

    TypeScript: ts.factory.createAwaitExpression(expression)
    """

    factory_name: ClassVar[str] = "createAwaitExpression"

    expression: Expression


class PrefixUnaryExpression(Node):
    """
    Represents a prefix unary expression: ++x, !x, etc.

    TypeScript: ts.factory.createPrefixUnaryExpression(operator, operand)
    """

    factory_name: ClassVar[str] = "createPrefixUnaryExpression"

    operator: int  # SyntaxKind
    operand: Expression


class PostfixUnaryExpression(Node):
    """
    Represents a postfix unary expression: x++, x--.

    TypeScript: ts.factory.createPostfixUnaryExpression(operand, operator)
    """

    factory_name: ClassVar[str] = "createPostfixUnaryExpression"

    operand: Expression
    operator: int  # SyntaxKind


class BinaryExpression(Node):
    """
    Represents a binary expression: a + b, a && b, etc.

    TypeScript: ts.factory.createBinaryExpression(left, operator, right)
    """

    factory_name: ClassVar[str] = "createBinaryExpression"

    left: Expression
    operator: int | Node  # SyntaxKind or Token
    right: Expression


class ConditionalExpression(Node):
    """
    Represents a conditional expression: condition ? whenTrue : whenFalse.

    TypeScript: ts.factory.createConditionalExpression(
        condition, questionToken?, whenTrue, colonToken?, whenFalse
    )
    """

    factory_name: ClassVar[str] = "createConditionalExpression"

    condition: Expression
    question_token: Node | Undefined = undefined
    when_true: Expression
    colon_token: Node | Undefined = undefined
    when_false: Expression


class TemplateExpression(Node):
    """
    Represents a template expression: `hello ${name}`.

    TypeScript: ts.factory.createTemplateExpression(head, templateSpans)
    """

    factory_name: ClassVar[str] = "createTemplateExpression"

    head: "TemplateHead"
    template_spans: Sequence["TemplateSpan"]


class YieldExpression(Node):
    """
    Represents a yield expression: yield value or yield* iterable.

    TypeScript: ts.factory.createYieldExpression(asteriskToken?, expression?)
    """

    factory_name: ClassVar[str] = "createYieldExpression"

    asterisk_token: Node | Undefined = undefined
    expression: Expression | Undefined = undefined


class SpreadElement(Node):
    """
    Represents a spread element: ...array.

    TypeScript: ts.factory.createSpreadElement(expression)
    """

    factory_name: ClassVar[str] = "createSpreadElement"

    expression: Expression


class ClassExpression(Node):
    """
    Represents a class expression: class { }.

    TypeScript: ts.factory.createClassExpression(
        modifiers?, name?, typeParameters?, heritageClauses?, members
    )
    """

    factory_name: ClassVar[str] = "createClassExpression"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | str | Undefined" = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    heritage_clauses: Sequence[Node] | Undefined = undefined
    members: Sequence[Node]


class OmittedExpression(Node):
    """
    Represents an omitted expression in an array: [a, , b].

    TypeScript: ts.factory.createOmittedExpression()
    """

    factory_name: ClassVar[str] = "createOmittedExpression"

    def _get_ordered_args(self):
        return ()


class AsExpression(Node):
    """
    Represents an 'as' expression: expression as Type.

    TypeScript: ts.factory.createAsExpression(expression, type)
    """

    factory_name: ClassVar[str] = "createAsExpression"

    expression: Expression
    type: "TypeNode"


class NonNullExpression(Node):
    """
    Represents a non-null assertion: expression!.

    TypeScript: ts.factory.createNonNullExpression(expression)
    """

    factory_name: ClassVar[str] = "createNonNullExpression"

    expression: Expression


class SatisfiesExpression(Node):
    """
    Represents a 'satisfies' expression: expression satisfies Type.

    TypeScript: ts.factory.createSatisfiesExpression(expression, type)
    """

    factory_name: ClassVar[str] = "createSatisfiesExpression"

    expression: Expression
    type: "TypeNode"


class ThisExpression(Node):
    """
    Represents the 'this' expression.

    TypeScript: ts.factory.createThis()
    """

    factory_name: ClassVar[str] = "createThis"

    def _get_ordered_args(self):
        return ()


class SuperExpression(Node):
    """
    Represents the 'super' expression.

    TypeScript: ts.factory.createSuper()
    """

    factory_name: ClassVar[str] = "createSuper"

    def _get_ordered_args(self):
        return ()


class MetaProperty(Node):
    """
    Represents a meta property: import.meta or new.target.

    TypeScript: ts.factory.createMetaProperty(keywordToken, name)
    """

    factory_name: ClassVar[str] = "createMetaProperty"

    keyword_token: int  # SyntaxKind (ImportKeyword or NewKeyword)
    name: "Identifier"


class CommaListExpression(Node):
    """
    Represents a comma-separated list of expressions.

    TypeScript: ts.factory.createCommaListExpression(elements)
    """

    factory_name: ClassVar[str] = "createCommaListExpression"

    elements: Sequence[Expression]


class PartiallyEmittedExpression(Node):
    """
    Represents a partially emitted expression (internal use).

    TypeScript: ts.factory.createPartiallyEmittedExpression(
        expression, original?
    )
    """

    factory_name: ClassVar[str] = "createPartiallyEmittedExpression"

    expression: Expression
    original: Node | Undefined = undefined

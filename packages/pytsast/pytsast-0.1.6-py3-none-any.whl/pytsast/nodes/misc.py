"""
Miscellaneous AST nodes - Templates, Heritage, Catch, Decorators, Parameters,
etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Sequence, Union

from pytsast.core.base import Node
from pytsast.core.types import Undefined, undefined
from pytsast.nodes.modifiers import Modifier

if TYPE_CHECKING:
    from pytsast.nodes.common import Identifier
    from pytsast.nodes.expressions import Expression
    from pytsast.nodes.statements import Block
    from pytsast.nodes.type_nodes import TypeNode


# ============================================================================
# Template Parts
# ============================================================================


class TemplateHead(Node):
    """
    Represents the head of a template expression.

    TypeScript: ts.factory.createTemplateHead(text, rawText?, templateFlags?)
    """

    factory_name: ClassVar[str] = "createTemplateHead"

    text: str
    raw_text: str | Undefined = undefined
    template_flags: int = 0


class TemplateMiddle(Node):
    """
    Represents a middle part of a template expression.

    TypeScript: ts.factory.createTemplateMiddle(text, rawText?, templateFlags?)
    """

    factory_name: ClassVar[str] = "createTemplateMiddle"

    text: str
    raw_text: str | Undefined = undefined
    template_flags: int = 0


class TemplateTail(Node):
    """
    Represents the tail of a template expression.

    TypeScript: ts.factory.createTemplateTail(text, rawText?, templateFlags?)
    """

    factory_name: ClassVar[str] = "createTemplateTail"

    text: str
    raw_text: str | Undefined = undefined
    template_flags: int = 0


class TemplateSpan(Node):
    """
    Represents a span in a template expression.

    TypeScript: ts.factory.createTemplateSpan(expression, literal)
    """

    factory_name: ClassVar[str] = "createTemplateSpan"

    expression: "Expression"
    literal: TemplateMiddle | TemplateTail


# ============================================================================
# Heritage and Clauses
# ============================================================================


class HeritageClause(Node):
    """
    Represents a heritage clause: extends/implements.

    TypeScript: ts.factory.createHeritageClause(token, types)
    """

    factory_name: ClassVar[str] = "createHeritageClause"

    token: int  # SyntaxKind (ExtendsKeyword or ImplementsKeyword)
    types: Sequence[Node]  # ExpressionWithTypeArguments


class CatchClause(Node):
    """
    Represents a catch clause: catch (e) { }.

    TypeScript: ts.factory.createCatchClause(variableDeclaration?, block)
    """

    factory_name: ClassVar[str] = "createCatchClause"

    variable_declaration: Node | str | Undefined = (
        undefined  # VariableDeclaration or BindingName
    )
    block: "Block"


class CaseClause(Node):
    """
    Represents a case clause: case x: statements.

    TypeScript: ts.factory.createCaseClause(expression, statements)
    """

    factory_name: ClassVar[str] = "createCaseClause"

    expression: "Expression"
    statements: Sequence[Node]


class DefaultClause(Node):
    """
    Represents a default clause: default: statements.

    TypeScript: ts.factory.createDefaultClause(statements)
    """

    factory_name: ClassVar[str] = "createDefaultClause"

    statements: Sequence[Node]


class CaseBlock(Node):
    """
    Represents a case block: { case clauses }.

    TypeScript: ts.factory.createCaseBlock(clauses)
    """

    factory_name: ClassVar[str] = "createCaseBlock"

    clauses: Sequence[CaseClause | DefaultClause]


# ============================================================================
# Decorators and Parameters
# ============================================================================


class Decorator(Node):
    """
    Represents a decorator: @decorator.

    TypeScript: ts.factory.createDecorator(expression)
    """

    factory_name: ClassVar[str] = "createDecorator"

    expression: "Expression"


class Parameter(Node):
    """
    Represents a parameter: name: Type = default.

    TypeScript: ts.factory.createParameterDeclaration(
        modifiers?, dotDotDotToken?, name, questionToken?, type?, initializer?
    )
    """

    factory_name: ClassVar[str] = "createParameterDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    dot_dot_dot_token: Node | Undefined = undefined
    name: "Identifier | Node | str"  # BindingName
    question_token: Node | Undefined = undefined
    type: "TypeNode | Undefined" = undefined
    initializer: "Expression | Undefined" = undefined


class TypeParameter(Node):
    """
    Represents a type parameter: T extends Constraint = Default.

    TypeScript: ts.factory.createTypeParameterDeclaration(modifiers?, name,
    constraint?, defaultType?)
    """

    factory_name: ClassVar[str] = "createTypeParameterDeclaration"

    modifiers: Sequence[Modifier] | Undefined = undefined
    name: "Identifier | str"
    constraint: "TypeNode | Undefined" = undefined
    default_type: "TypeNode | Undefined" = undefined


class ExpressionWithTypeArguments(Node):
    """
    Represents an expression with type arguments for extends/implements.

    TypeScript: ts.factory.createExpressionWithTypeArguments(
        expression, typeArguments?
    )
    """

    factory_name: ClassVar[str] = "createExpressionWithTypeArguments"

    expression: "Expression"
    type_arguments: Sequence["TypeNode"] | Undefined = undefined


class ComputedPropertyName(Node):
    """
    Represents a computed property name: [expression].

    TypeScript: ts.factory.createComputedPropertyName(expression)
    """

    factory_name: ClassVar[str] = "createComputedPropertyName"

    expression: "Expression"


class PropertySignature(Node):
    """
    Represents a property signature: name?: Type.

    TypeScript: ts.factory.createPropertySignature(
        modifiers?, name, questionToken?, type?
    )
    """

    factory_name: ClassVar[str] = "createPropertySignature"

    modifiers: Sequence[Modifier] | Undefined = undefined
    name: "Identifier | str | Node"  # PropertyName
    question_token: Node | Undefined = undefined
    type: "TypeNode | Undefined" = undefined


class MethodSignature(Node):
    """
    Represents a method signature: name(params): Type.

    TypeScript: ts.factory.createMethodSignature(
        modifiers?, name, questionToken?, typeParameters?, parameters, type?
    )
    """

    factory_name: ClassVar[str] = "createMethodSignature"

    modifiers: Sequence[Modifier] | Undefined = undefined
    name: "Identifier | str | Node"  # PropertyName
    question_token: Node | Undefined = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined


class CallSignatureDeclaration(Node):
    """
    Represents a call signature: (params): Type.

    TypeScript: ts.factory.createCallSignature(
        typeParameters?, parameters, type?
    )
    """

    factory_name: ClassVar[str] = "createCallSignature"

    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined


class ConstructSignatureDeclaration(Node):
    """
    Represents a construct signature: new (params): Type.

    TypeScript: ts.factory.createConstructSignature(
        typeParameters?, parameters, type?
    )
    """

    factory_name: ClassVar[str] = "createConstructSignature"

    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined


class SemicolonClassElement(Node):
    """
    Represents a semicolon in a class body.

    TypeScript: ts.factory.createSemicolonClassElement()
    """

    factory_name: ClassVar[str] = "createSemicolonClassElement"

    def _get_ordered_args(self):
        return ()


class ImportAttribute(Node):
    """
    Represents an import attribute: key: value.

    TypeScript: ts.factory.createImportAttribute(name, value)
    """

    factory_name: ClassVar[str] = "createImportAttribute"

    name: "Identifier | str"
    value: "Expression"


class ImportAttributes(Node):
    """
    Represents import attributes: with { key: value }.

    TypeScript: ts.factory.createImportAttributes(elements, multiLine?)
    """

    factory_name: ClassVar[str] = "createImportAttributes"

    elements: Sequence[ImportAttribute]
    multi_line: bool = False


class JsxAttribute(Node):
    """
    Represents a JSX attribute: name={value} or name="value".

    TypeScript: ts.factory.createJsxAttribute(name, initializer?)
    """

    factory_name: ClassVar[str] = "createJsxAttribute"

    name: Union["Identifier", "JsxNamespacedName"]
    initializer: Node | Undefined = undefined


class JsxSpreadAttribute(Node):
    """
    Represents a JSX spread attribute: {...expression}.

    TypeScript: ts.factory.createJsxSpreadAttribute(expression)
    """

    factory_name: ClassVar[str] = "createJsxSpreadAttribute"

    expression: "Expression"


class JsxElement(Node):
    """
    Represents a JSX element: <tag>children</tag>.

    TypeScript: ts.factory.createJsxElement(openingElement, children,
      closingElement)
    """

    factory_name: ClassVar[str] = "createJsxElement"

    opening_element: Node  # JsxOpeningElement
    children: Sequence[Node]  # JsxChild[]
    closing_element: Node  # JsxClosingElement


class JsxSelfClosingElement(Node):
    """
    Represents a self-closing JSX element: <tag />.

    TypeScript: ts.factory.createJsxSelfClosingElement(
        tagName, typeArguments?, attributes
    )
    """

    factory_name: ClassVar[str] = "createJsxSelfClosingElement"

    tag_name: Node  # JsxTagNameExpression
    type_arguments: Sequence["TypeNode"] | Undefined = undefined
    attributes: Node  # JsxAttributes


class JsxOpeningElement(Node):
    """
    Represents a JSX opening element: <tag>.

    TypeScript: ts.factory.createJsxOpeningElement(
        tagName, typeArguments?, attributes
    )
    """

    factory_name: ClassVar[str] = "createJsxOpeningElement"

    tag_name: Node  # JsxTagNameExpression
    type_arguments: Sequence["TypeNode"] | Undefined = undefined
    attributes: Node  # JsxAttributes


class JsxClosingElement(Node):
    """
    Represents a JSX closing element: </tag>.

    TypeScript: ts.factory.createJsxClosingElement(tagName)
    """

    factory_name: ClassVar[str] = "createJsxClosingElement"

    tag_name: Node  # JsxTagNameExpression


class JsxFragment(Node):
    """
    Represents a JSX fragment: <>children</>.

    TypeScript: ts.factory.createJsxFragment(
        openingFragment, children, closingFragment
    )
    """

    factory_name: ClassVar[str] = "createJsxFragment"

    opening_fragment: Node  # JsxOpeningFragment
    children: Sequence[Node]  # JsxChild[]
    closing_fragment: Node  # JsxClosingFragment


class JsxOpeningFragment(Node):
    """
    Represents a JSX opening fragment: <>.

    TypeScript: ts.factory.createJsxOpeningFragment()
    """

    factory_name: ClassVar[str] = "createJsxOpeningFragment"

    def _get_ordered_args(self):
        return ()


class JsxClosingFragment(Node):
    """
    Represents a JSX closing fragment: </>.

    TypeScript: ts.factory.createJsxJsxClosingFragment()
    """

    factory_name: ClassVar[str] = "createJsxJsxClosingFragment"

    def _get_ordered_args(self):
        return ()


class JsxText(Node):
    """
    Represents JSX text content.

    TypeScript: ts.factory.createJsxText(text, containsOnlyTriviaWhiteSpaces?)
    """

    factory_name: ClassVar[str] = "createJsxText"

    text: str
    contains_only_trivia_white_spaces: bool = False


class JsxExpression(Node):
    """
    Represents a JSX expression: {expression}.

    TypeScript: ts.factory.createJsxExpression(dotDotDotToken?, expression?)
    """

    factory_name: ClassVar[str] = "createJsxExpression"

    dot_dot_dot_token: Node | Undefined = undefined
    expression: "Expression | Undefined" = undefined


class JsxAttributes(Node):
    """
    Represents JSX attributes.

    TypeScript: ts.factory.createJsxAttributes(properties)
    """

    factory_name: ClassVar[str] = "createJsxAttributes"

    properties: Sequence[Node]  # JsxAttributeLike[]


class JsxNamespacedName(Node):
    """
    Represents a namespaced JSX name: namespace:name.

    TypeScript: ts.factory.createJsxNamespacedName(namespace, name)
    """

    factory_name: ClassVar[str] = "createJsxNamespacedName"

    namespace: "Identifier"
    name: "Identifier"

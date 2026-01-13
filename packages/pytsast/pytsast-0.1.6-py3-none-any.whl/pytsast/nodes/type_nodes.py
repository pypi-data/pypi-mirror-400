"""
Type node AST nodes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Sequence

from pytsast.core.base import Node
from pytsast.core.types import Undefined, undefined
from pytsast.nodes.modifiers import Modifier

if TYPE_CHECKING:
    from pytsast.nodes.common import Identifier, QualifiedName
    from pytsast.nodes.misc import Parameter, TypeParameter

# Type alias for any type node
TypeNode = Node


class TypeReference(Node):
    """
    Represents a type reference: TypeName<Args>.

    TypeScript: ts.factory.createTypeReferenceNode(typeName, typeArguments?)
    """

    factory_name: ClassVar[str] = "createTypeReferenceNode"

    type_name: "Identifier | QualifiedName | str"
    type_arguments: Sequence[TypeNode] | Undefined = undefined


class FunctionType(Node):
    """
    Represents a function type: (params) => ReturnType.

    TypeScript: ts.factory.createFunctionTypeNode(typeParameters?, parameters,
      type)
    """

    factory_name: ClassVar[str] = "createFunctionTypeNode"

    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: TypeNode


class ConstructorType(Node):
    """
    Represents a constructor type: new (params) => Type.

    TypeScript: ts.factory.createConstructorTypeNode(modifiers?,
      typeParameters?, parameters, type)
    """

    factory_name: ClassVar[str] = "createConstructorTypeNode"

    modifiers: Sequence[Modifier] | Undefined = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: TypeNode


class TypeQuery(Node):
    """
    Represents a typeof type query: typeof x.

    TypeScript: ts.factory.createTypeQueryNode(exprName, typeArguments?)
    """

    factory_name: ClassVar[str] = "createTypeQueryNode"

    expr_name: "Identifier | QualifiedName"
    type_arguments: Sequence[TypeNode] | Undefined = undefined


class TypeLiteral(Node):
    """
    Represents a type literal: { prop: Type }.

    TypeScript: ts.factory.createTypeLiteralNode(members?)
    """

    factory_name: ClassVar[str] = "createTypeLiteralNode"

    members: Sequence[Node] | Undefined = undefined


class ArrayType(Node):
    """
    Represents an array type: Type[].

    TypeScript: ts.factory.createArrayTypeNode(elementType)
    """

    factory_name: ClassVar[str] = "createArrayTypeNode"

    element_type: TypeNode


class TupleType(Node):
    """
    Represents a tuple type: [A, B, C].

    TypeScript: ts.factory.createTupleTypeNode(elements)
    """

    factory_name: ClassVar[str] = "createTupleTypeNode"

    elements: Sequence[TypeNode]


class OptionalType(Node):
    """
    Represents an optional type: Type?.

    TypeScript: ts.factory.createOptionalTypeNode(type)
    """

    factory_name: ClassVar[str] = "createOptionalTypeNode"

    type: TypeNode


class RestType(Node):
    """
    Represents a rest type: ...Type.

    TypeScript: ts.factory.createRestTypeNode(type)
    """

    factory_name: ClassVar[str] = "createRestTypeNode"

    type: TypeNode


class UnionType(Node):
    """
    Represents a union type: A | B | C.

    TypeScript: ts.factory.createUnionTypeNode(types)
    """

    factory_name: ClassVar[str] = "createUnionTypeNode"

    types: Sequence[TypeNode]


class IntersectionType(Node):
    """
    Represents an intersection type: A & B & C.

    TypeScript: ts.factory.createIntersectionTypeNode(types)
    """

    factory_name: ClassVar[str] = "createIntersectionTypeNode"

    types: Sequence[TypeNode]


class ConditionalType(Node):
    """
    Represents a conditional type: T extends U ? X : Y.

    TypeScript: ts.factory.createConditionalTypeNode(checkType, extendsType,
    trueType, falseType)
    """

    factory_name: ClassVar[str] = "createConditionalTypeNode"

    check_type: TypeNode
    extends_type: TypeNode
    true_type: TypeNode
    false_type: TypeNode


class InferType(Node):
    """
    Represents an infer type: infer T.

    TypeScript: ts.factory.createInferTypeNode(typeParameter)
    """

    factory_name: ClassVar[str] = "createInferTypeNode"

    type_parameter: "TypeParameter"


class ParenthesizedType(Node):
    """
    Represents a parenthesized type: (Type).

    TypeScript: ts.factory.createParenthesizedType(type)
    """

    factory_name: ClassVar[str] = "createParenthesizedType"

    type: TypeNode


class ThisType(Node):
    """
    Represents the 'this' type.

    TypeScript: ts.factory.createThisTypeNode()
    """

    factory_name: ClassVar[str] = "createThisTypeNode"

    def _get_ordered_args(self):
        return ()


class TypeOperator(Node):
    """
    Represents a type operator: keyof T, readonly T, unique symbol.

    TypeScript: ts.factory.createTypeOperatorNode(operator, type)
    """

    factory_name: ClassVar[str] = "createTypeOperatorNode"

    operator: int  # SyntaxKind
    type: TypeNode


class IndexedAccessType(Node):
    """
    Represents an indexed access type: T[K].

    TypeScript: ts.factory.createIndexedAccessTypeNode(objectType, indexType)
    """

    factory_name: ClassVar[str] = "createIndexedAccessTypeNode"

    object_type: TypeNode
    index_type: TypeNode


class MappedType(Node):
    """
    Represents a mapped type: { [K in T]: U }.

    TypeScript: ts.factory.createMappedTypeNode(
        readonlyToken?, typeParameter, nameType?, questionToken?, type?,
          members?
    )
    """

    factory_name: ClassVar[str] = "createMappedTypeNode"

    readonly_token: Node | Undefined = undefined
    type_parameter: "TypeParameter"
    name_type: TypeNode | Undefined = undefined
    question_token: Node | Undefined = undefined
    type: TypeNode | Undefined = undefined
    members: Sequence[Node] | Undefined = undefined


class LiteralType(Node):
    """
    Represents a literal type: 'a' | 1 | true.

    TypeScript: ts.factory.createLiteralTypeNode(literal)
    """

    factory_name: ClassVar[str] = "createLiteralTypeNode"

    literal: Node


class TemplateLiteralType(Node):
    """
    Represents a template literal type: `prefix${T}suffix`.

    TypeScript: ts.factory.createTemplateLiteralType(head, templateSpans)
    """

    factory_name: ClassVar[str] = "createTemplateLiteralType"

    head: Node  # TemplateHead
    template_spans: Sequence[Node]  # TemplateLiteralTypeSpan


class ImportType(Node):
    """
    Represents an import type: import('module').Type.

    TypeScript: ts.factory.createImportTypeNode(argument, attributes?,
      qualifier?, typeArguments?, isTypeOf?)
    """

    factory_name: ClassVar[str] = "createImportTypeNode"

    argument: TypeNode
    attributes: Node | Undefined = undefined
    qualifier: "Identifier | QualifiedName | Undefined" = undefined
    type_arguments: Sequence[TypeNode] | Undefined = undefined
    is_type_of: bool = False


class NamedTupleMember(Node):
    """
    Represents a named tuple member: name: Type or name?: Type.

    TypeScript: ts.factory.createNamedTupleMember(
        dotDotDotToken?, name, questionToken?, type
    )
    """

    factory_name: ClassVar[str] = "createNamedTupleMember"

    dot_dot_dot_token: Node | Undefined = undefined
    name: "Identifier"
    question_token: Node | Undefined = undefined
    type: TypeNode


class TemplateLiteralTypeSpan(Node):
    """
    Represents a span in a template literal type: ${Type}text.

    TypeScript: ts.factory.createTemplateLiteralTypeSpan(type, literal)
    """

    factory_name: ClassVar[str] = "createTemplateLiteralTypeSpan"

    type: TypeNode
    literal: Node  # TemplateMiddle | TemplateTail


class TypePredicateNode(Node):
    """
    Represents a type predicate: param is Type.

    TypeScript: ts.factory.createTypePredicateNode(
        assertsModifier?, parameterName, type?
    )
    """

    factory_name: ClassVar[str] = "createTypePredicateNode"

    asserts_modifier: Node | Undefined = undefined
    parameter_name: "Identifier | Node | str"  # Identifier or ThisTypeNode
    type: TypeNode | Undefined = undefined

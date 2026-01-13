"""
Factory functions for creating TypeScript AST nodes.

This module mirrors the TypeScript factory API (ts.factory.*) for
a familiar and consistent experience.

Usage:
    from pytsast import factory as ts

    import_decl = ts.createImportDeclaration(
        Undefined,
        ts.createImportClause(
            False,
            ts.createIdentifier("zod"),
            ts.createNamedImports([
                ts.createImportSpecifier(
                    False, Undefined, ts.createIdentifier("output")
                )
            ])
        ),
        ts.createStringLiteral("zod"),
        Undefined
    )
"""

# flake8: noqa: disable F401

from __future__ import annotations

from typing import Literal, Sequence, TypeAlias, Union

from pytsast.core.base import Node

# Import all nodes from the main nodes module (which rebuilds models)
from pytsast.core.types import Undefined, undefined

# Type aliases (defined after imports to use proper types)
from pytsast.nodes import (
    # Common
    Identifier,
    PrivateIdentifier,
    QualifiedName,
    # Literals
    BigIntLiteral,
    FalseLiteral,
    NoSubstitutionTemplateLiteral,
    NullLiteral,
    NumericLiteral,
    RegularExpressionLiteral,
    StringLiteral,
    TrueLiteral,
    # Expressions
    ArrayLiteralExpression,
    ArrowFunction,
    AsExpression,
    AwaitExpression,
    BinaryExpression,
    CallExpression,
    ClassExpression,
    CommaListExpression,
    ConditionalExpression,
    DeleteExpression,
    ElementAccessExpression,
    FunctionExpression,
    MetaProperty,
    NewExpression,
    NonNullExpression,
    ObjectLiteralExpression,
    OmittedExpression,
    ParenthesizedExpression,
    PartiallyEmittedExpression,
    PostfixUnaryExpression,
    PrefixUnaryExpression,
    PropertyAccessExpression,
    SatisfiesExpression,
    SpreadElement,
    SuperExpression,
    TaggedTemplateExpression,
    TemplateExpression,
    ThisExpression,
    TypeAssertionExpression,
    TypeOfExpression,
    VoidExpression,
    YieldExpression,
    # Statements
    Block,
    BreakStatement,
    ContinueStatement,
    DebuggerStatement,
    DoStatement,
    EmptyStatement,
    ExpressionStatement,
    ForInStatement,
    ForOfStatement,
    ForStatement,
    IfStatement,
    LabeledStatement,
    ReturnStatement,
    SwitchStatement,
    ThrowStatement,
    TryStatement,
    VariableStatement,
    WhileStatement,
    WithStatement,
    # Declarations
    ClassDeclaration,
    EnumDeclaration,
    EnumMember,
    ExportAssignment,
    ExportDeclaration,
    ExportSpecifier,
    ExternalModuleReference,
    FunctionDeclaration,
    ImportClause,
    ImportDeclaration,
    ImportEqualsDeclaration,
    ImportSpecifier,
    InterfaceDeclaration,
    ModuleDeclaration,
    NamedExports,
    NamedImports,
    NamespaceExport,
    NamespaceExportDeclaration,
    NamespaceImport,
    TypeAliasDeclaration,
    VariableDeclaration,
    VariableDeclarationList,
    # Type nodes
    ArrayType,
    ConditionalType,
    ConstructorType,
    FunctionType,
    ImportType,
    IndexedAccessType,
    InferType,
    IntersectionType,
    LiteralType,
    MappedType,
    NamedTupleMember,
    OptionalType,
    ParenthesizedType,
    RestType,
    TemplateLiteralType,
    TemplateLiteralTypeSpan,
    ThisType,
    TupleType,
    TypeLiteral,
    TypeOperator,
    TypePredicateNode,
    TypeQuery,
    TypeReference,
    UnionType,
    # Class elements
    ClassStaticBlockDeclaration,
    Constructor,
    GetAccessor,
    IndexSignature,
    MethodDeclaration,
    PropertyDeclaration,
    SetAccessor,
    # Object elements
    PropertyAssignment,
    ShorthandPropertyAssignment,
    SpreadAssignment,
    # Bindings
    ArrayBindingPattern,
    BindingElement,
    ObjectBindingPattern,
    # Misc
    CallSignatureDeclaration,
    CaseBlock,
    CaseClause,
    CatchClause,
    ComputedPropertyName,
    ConstructSignatureDeclaration,
    Decorator,
    DefaultClause,
    ExpressionWithTypeArguments,
    HeritageClause,
    ImportAttribute,
    ImportAttributes,
    JsxAttribute,
    JsxAttributes,
    JsxClosingElement,
    JsxClosingFragment,
    JsxElement,
    JsxExpression,
    JsxFragment,
    JsxNamespacedName,
    JsxOpeningElement,
    JsxOpeningFragment,
    JsxSelfClosingElement,
    JsxSpreadAttribute,
    JsxText,
    MethodSignature,
    Parameter,
    PropertySignature,
    SemicolonClassElement,
    TemplateHead,
    TemplateMiddle,
    TemplateSpan,
    TemplateTail,
    TypeParameter,
    # Modifiers
    AbstractKeyword,
    AccessorKeyword,
    AsyncKeyword,
    ConstKeyword,
    DeclareKeyword,
    DefaultKeyword,
    ExportKeyword,
    InKeyword,
    Modifier,
    OutKeyword,
    OverrideKeyword,
    PrivateKeyword,
    ProtectedKeyword,
    PublicKeyword,
    ReadonlyKeyword,
    StaticKeyword,
    # Keywords
    AnyKeyword,
    AssertsKeyword,
    AwaitKeywordType,
    BigIntKeyword,
    BooleanKeyword,
    IntrinsicKeyword,
    NeverKeyword,
    NullKeyword,
    NumberKeyword,
    ObjectKeyword,
    StringKeyword,
    SuperKeyword,
    SymbolKeyword,
    ThisKeyword,
    UndefinedKeyword,
    UnknownKeyword,
    VoidKeyword,
    # Tokens
    AsteriskToken,
    ColonToken,
    DotDotDotToken,
    EqualsGreaterThanToken,
    EqualsToken,
    ExclamationToken,
    MinusToken,
    PlusToken,
    QuestionToken,
    Token,
)

from pytsast.core.syntax_kind import SyntaxKind

# =============================================================================
# Type Aliases - Following TypeScript's union types for strict typing
# =============================================================================
# These aliases match TypeScript's AST type unions for proper type safety

# Expression types (for use in function signatures)
Expression: TypeAlias = Node

# Type nodes (for use in type annotations)
TypeNode: TypeAlias = Node

# PropertyName: Identifier | StringLiteral | NumericLiteral
#   | ComputedPropertyName | PrivateIdentifier | BigIntLiteral
PropertyName: TypeAlias = Union[
    Identifier,
    StringLiteral,
    NumericLiteral,
    ComputedPropertyName,
    PrivateIdentifier,
    BigIntLiteral,
    NoSubstitutionTemplateLiteral,
    str,
]

# BindingName: Identifier | BindingPattern
BindingName: TypeAlias = Union[
    Identifier, ObjectBindingPattern, ArrayBindingPattern, str
]

# EntityName: Identifier | QualifiedName
EntityName: TypeAlias = Union[Identifier, QualifiedName]

# ModuleName: Identifier | StringLiteral
ModuleName: TypeAlias = Union[Identifier, StringLiteral, str]

# ModifierLike: Modifier | Decorator
ModifierLike: TypeAlias = Union[Modifier, Decorator]

# ClassElement types for class members
ClassElement: TypeAlias = Union[
    PropertyDeclaration,
    MethodDeclaration,
    Constructor,
    GetAccessor,
    SetAccessor,
    IndexSignature,
    ClassStaticBlockDeclaration,
    SemicolonClassElement,
]

# TypeElement types for interface/type literal members
TypeElement: TypeAlias = Union[
    PropertySignature,
    MethodSignature,
    CallSignatureDeclaration,
    ConstructSignatureDeclaration,
    IndexSignature,
]

# ObjectLiteralElementLike for object literals
ObjectLiteralElementLike: TypeAlias = Union[
    PropertyAssignment, ShorthandPropertyAssignment, SpreadAssignment
]

# Statement types
Statement: TypeAlias = Node

# JsxChild types
JsxChild: TypeAlias = Union[
    JsxText, JsxExpression, JsxElement, JsxSelfClosingElement, JsxFragment
]

# JsxTagNameExpression
JsxTagNameExpression: TypeAlias = Union[
    Identifier, JsxNamespacedName, PropertyAccessExpression
]

# JsxAttributeLike
JsxAttributeLike: TypeAlias = Union[JsxAttribute, JsxSpreadAttribute]

# JsxAttributeValue
JsxAttributeValue: TypeAlias = Union[
    StringLiteral, JsxExpression, JsxElement, JsxFragment
]

# TemplateLiteral
TemplateLiteral: TypeAlias = Union[
    NoSubstitutionTemplateLiteral, TemplateExpression
]

# ConciseBody for arrow functions
ConciseBody: TypeAlias = Union[Block, Expression]

# ModuleBody
ModuleBody: TypeAlias = Node  # ModuleBlock or ModuleDeclaration

# ForInitializer
ForInitializer: TypeAlias = Union[VariableDeclarationList, Node]

# NamedExportBindings
NamedExportBindings: TypeAlias = Union[NamedExports, NamespaceExport]

# NamedImportBindings
NamedImportBindings: TypeAlias = Union[NamedImports, NamespaceImport]

# ModuleReference
ModuleReference: TypeAlias = Union[EntityName, ExternalModuleReference]

# MemberName: Identifier | PrivateIdentifier
MemberName: TypeAlias = Union[Identifier, PrivateIdentifier]

# ArrayBindingElement
ArrayBindingElement: TypeAlias = Union[BindingElement, OmittedExpression]

# LiteralTypeLiteral - the 'literal' property of LiteralTypeNode
# TypeScript: NullLiteral | BooleanLiteral | LiteralExpression |
# PrefixUnaryExpression
# Where LiteralExpression includes StringLiteral, NumericLiteral, etc.
LiteralTypeLiteral: TypeAlias = Union[
    NullLiteral,
    TrueLiteral,
    FalseLiteral,
    StringLiteral,
    NumericLiteral,
    BigIntLiteral,
    RegularExpressionLiteral,
    NoSubstitutionTemplateLiteral,
    PrefixUnaryExpression,
]


# ============================================================================
# Common
# ============================================================================


def createIdentifier(text: str) -> Identifier:
    """Create an identifier node."""
    return Identifier(text=text)


def createPrivateIdentifier(text: str) -> PrivateIdentifier:
    """Create a private identifier node (#name)."""
    return PrivateIdentifier(text=text)


def createQualifiedName(
    left: Identifier | QualifiedName,
    right: Identifier,
) -> QualifiedName:
    """Create a qualified name (Namespace.Name)."""
    return QualifiedName(left=left, right=right)


# ============================================================================
# Literals
# ============================================================================


def createStringLiteral(
    text: str, is_single_quote: bool = False
) -> StringLiteral:
    """Create a string literal node."""
    return StringLiteral(text=text, is_single_quote=is_single_quote)


def createNumericLiteral(value: str | int | float) -> NumericLiteral:
    """Create a numeric literal node."""
    return NumericLiteral(value=value)


def createBigIntLiteral(value: str) -> BigIntLiteral:
    """Create a BigInt literal node."""
    return BigIntLiteral(value=value)


def createRegularExpressionLiteral(text: str) -> RegularExpressionLiteral:
    """Create a regular expression literal node."""
    return RegularExpressionLiteral(text=text)


def createNoSubstitutionTemplateLiteral(
    text: str,
    raw_text: str | Undefined = undefined,
) -> NoSubstitutionTemplateLiteral:
    """Create a template literal without substitutions."""
    return NoSubstitutionTemplateLiteral(text=text, raw_text=raw_text)


def createTrue() -> TrueLiteral:
    """Create a 'true' literal."""
    return TrueLiteral()


def createFalse() -> FalseLiteral:
    """Create a 'false' literal."""
    return FalseLiteral()


def createNull() -> NullLiteral:
    """Create a 'null' literal."""
    return NullLiteral()


# ============================================================================
# Expressions
# ============================================================================


def createArrayLiteralExpression(
    elements: Sequence[Expression] | Undefined = undefined,
    multi_line: bool = False,
) -> ArrayLiteralExpression:
    """Create an array literal expression."""
    return ArrayLiteralExpression(elements=elements, multi_line=multi_line)


def createObjectLiteralExpression(
    properties: Sequence[ObjectLiteralElementLike] | Undefined = undefined,
    multi_line: bool = False,
) -> ObjectLiteralExpression:
    """Create an object literal expression."""
    return ObjectLiteralExpression(
        properties=properties, multi_line=multi_line
    )


def createPropertyAccessExpression(
    expression: Expression,
    name: MemberName | str,
) -> PropertyAccessExpression:
    """Create a property access expression (obj.property)."""
    return PropertyAccessExpression(expression=expression, name=name)


def createElementAccessExpression(
    expression: Expression,
    index: Expression,
) -> ElementAccessExpression:
    """Create an element access expression (obj[index])."""
    return ElementAccessExpression(expression=expression, index=index)


def createCallExpression(
    expression: Expression,
    type_arguments: Sequence[TypeNode] | Undefined = undefined,
    arguments: Sequence[Expression] | Undefined = undefined,
) -> CallExpression:
    """Create a call expression (func(args))."""
    return CallExpression(
        expression=expression,
        type_arguments=type_arguments,
        arguments=arguments,
    )


def createNewExpression(
    expression: Expression,
    type_arguments: Sequence[TypeNode] | Undefined = undefined,
    arguments: Sequence[Expression] | Undefined = undefined,
) -> NewExpression:
    """Create a new expression (new Class(args))."""
    return NewExpression(
        expression=expression,
        type_arguments=type_arguments,
        arguments=arguments,
    )


def createParenthesizedExpression(
    expression: Expression,
) -> ParenthesizedExpression:
    """Create a parenthesized expression ((expr))."""
    return ParenthesizedExpression(expression=expression)


def createArrowFunction(
    modifiers: Sequence[Modifier] | Undefined,
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode | Undefined,
    equals_greater_than_token: EqualsGreaterThanToken | Undefined,
    body: ConciseBody,
) -> ArrowFunction:
    """Create an arrow function ((params) => body)."""
    return ArrowFunction(
        modifiers=modifiers,
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
        equals_greater_than_token=equals_greater_than_token,
        body=body,
    )


def createFunctionExpression(
    modifiers: Sequence[Modifier] | Undefined,
    asterisk_token: AsteriskToken | Undefined,
    name: Identifier | str | Undefined,
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter] | Undefined,
    type: TypeNode | Undefined,
    body: Block,
) -> FunctionExpression:
    """Create a function expression."""
    return FunctionExpression(
        modifiers=modifiers,
        asterisk_token=asterisk_token,
        name=name,
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
        body=body,
    )


def createBinaryExpression(
    left: Expression,
    operator: int | Node,
    right: Expression,
) -> BinaryExpression:
    """Create a binary expression (a + b)."""
    return BinaryExpression(left=left, operator=operator, right=right)


def createConditionalExpression(
    condition: Expression,
    question_token: QuestionToken | Undefined,
    when_true: Expression,
    colon_token: ColonToken | Undefined,
    when_false: Expression,
) -> ConditionalExpression:
    """Create a conditional expression (cond ? a : b)."""
    return ConditionalExpression(
        condition=condition,
        question_token=question_token,
        when_true=when_true,
        colon_token=colon_token,
        when_false=when_false,
    )


def createAwaitExpression(expression: Expression) -> AwaitExpression:
    """Create an await expression."""
    return AwaitExpression(expression=expression)


def createSpreadElement(expression: Expression) -> SpreadElement:
    """Create a spread element (...array)."""
    return SpreadElement(expression=expression)


def createAsExpression(expression: Expression, type: TypeNode) -> AsExpression:
    """Create an 'as' expression (expr as Type)."""
    return AsExpression(expression=expression, type=type)


def createNonNullExpression(expression: Expression) -> NonNullExpression:
    """Create a non-null assertion (expr!)."""
    return NonNullExpression(expression=expression)


def createOmittedExpression() -> OmittedExpression:
    """Create an omitted expression (for array holes)."""
    return OmittedExpression()


# ============================================================================
# Statements
# ============================================================================


def createBlock(
    statements: Sequence[Statement],
    multi_line: bool = True,
) -> Block:
    """Create a block statement ({ statements })."""
    return Block(statements=statements, multi_line=multi_line)


def createEmptyStatement() -> EmptyStatement:
    """Create an empty statement (;)."""
    return EmptyStatement()


def createVariableStatement(
    modifiers: Sequence[ModifierLike] | Undefined,
    declaration_list: VariableDeclarationList,
) -> VariableStatement:
    """Create a variable statement (const x = 1;)."""
    return VariableStatement(
        modifiers=modifiers, declaration_list=declaration_list
    )


def createExpressionStatement(expression: Expression) -> ExpressionStatement:
    """Create an expression statement (expr;)."""
    return ExpressionStatement(expression=expression)


def createIfStatement(
    expression: Expression,
    then_statement: Statement,
    else_statement: Statement | Undefined = undefined,
) -> IfStatement:
    """Create an if statement."""
    return IfStatement(
        expression=expression,
        then_statement=then_statement,
        else_statement=else_statement,
    )


def createReturnStatement(
    expression: Expression | Undefined = undefined,
) -> ReturnStatement:
    """Create a return statement."""
    return ReturnStatement(expression=expression)


def createThrowStatement(expression: Expression) -> ThrowStatement:
    """Create a throw statement."""
    return ThrowStatement(expression=expression)


def createTryStatement(
    try_block: Block,
    catch_clause: CatchClause | Undefined = undefined,
    finally_block: Block | Undefined = undefined,
) -> TryStatement:
    """Create a try statement."""
    return TryStatement(
        try_block=try_block,
        catch_clause=catch_clause,
        finally_block=finally_block,
    )


def createDebuggerStatement() -> DebuggerStatement:
    """Create a debugger statement."""
    return DebuggerStatement()


# ============================================================================
# Declarations
# ============================================================================


def createVariableDeclaration(
    name: BindingName,
    exclamation_token: ExclamationToken | Undefined = undefined,
    type: TypeNode | Undefined = undefined,
    initializer: Expression | Undefined = undefined,
) -> VariableDeclaration:
    """Create a variable declaration."""
    return VariableDeclaration(
        name=name,
        exclamation_token=exclamation_token,
        type=type,
        initializer=initializer,
    )


def createVariableDeclarationList(
    declarations: Sequence[VariableDeclaration],
    flags: int = 0,
) -> VariableDeclarationList:
    """Create a variable declaration list.

    Flags: 0 = var, 1 = let, 2 = const
    """
    return VariableDeclarationList(declarations=declarations, flags=flags)


def createFunctionDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    asterisk_token: AsteriskToken | Undefined,
    name: Identifier | str | Undefined,
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode | Undefined,
    body: Block | Undefined,
) -> FunctionDeclaration:
    """Create a function declaration."""
    return FunctionDeclaration(
        modifiers=modifiers,
        asterisk_token=asterisk_token,
        name=name,
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
        body=body,
    )


def createClassDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    name: Identifier | str | Undefined,
    type_parameters: Sequence[TypeParameter] | Undefined,
    heritage_clauses: Sequence[HeritageClause] | Undefined,
    members: Sequence[ClassElement],
) -> ClassDeclaration:
    """Create a class declaration."""
    return ClassDeclaration(
        modifiers=modifiers,
        name=name,
        type_parameters=type_parameters,
        heritage_clauses=heritage_clauses,
        members=members,
    )


def createInterfaceDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    name: Identifier | str,
    type_parameters: Sequence[TypeParameter] | Undefined,
    heritage_clauses: Sequence[HeritageClause] | Undefined,
    members: Sequence[TypeElement],
) -> InterfaceDeclaration:
    """Create an interface declaration."""
    return InterfaceDeclaration(
        modifiers=modifiers,
        name=name,
        type_parameters=type_parameters,
        heritage_clauses=heritage_clauses,
        members=members,
    )


def createTypeAliasDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    name: Identifier | str,
    type_parameters: Sequence[TypeParameter] | Undefined,
    type: TypeNode,
) -> TypeAliasDeclaration:
    """Create a type alias declaration."""
    return TypeAliasDeclaration(
        modifiers=modifiers,
        name=name,
        type_parameters=type_parameters,
        type=type,
    )


# ============================================================================
# Import/Export
# ============================================================================


def createImportDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    import_clause: ImportClause | Undefined,
    module_specifier: Expression,
    attributes: ImportAttributes | Undefined = undefined,
) -> ImportDeclaration:
    """Create an import declaration."""
    return ImportDeclaration(
        modifiers=modifiers,
        import_clause=import_clause,
        module_specifier=module_specifier,
        attributes=attributes,
    )


def createImportClause(
    is_type_only: bool,
    name: Identifier | Undefined,
    named_bindings: NamedImportBindings | Undefined,
) -> ImportClause:
    """Create an import clause."""
    return ImportClause(
        is_type_only=is_type_only,
        name=name,
        named_bindings=named_bindings,
    )


def createNamespaceImport(name: Identifier) -> NamespaceImport:
    """Create a namespace import (* as name)."""
    return NamespaceImport(name=name)


def createNamedImports(elements: Sequence[ImportSpecifier]) -> NamedImports:
    """Create named imports ({ a, b })."""
    return NamedImports(elements=elements)


def createImportSpecifier(
    is_type_only: bool,
    property_name: Identifier | Undefined,
    name: Identifier,
) -> ImportSpecifier:
    """Create an import specifier."""
    return ImportSpecifier(
        is_type_only=is_type_only,
        property_name=property_name,
        name=name,
    )


def createExportAssignment(
    modifiers: Sequence[ModifierLike] | Undefined,
    is_export_equals: bool,
    expression: Expression,
) -> ExportAssignment:
    """Create an export assignment (export default or export =)."""
    return ExportAssignment(
        modifiers=modifiers,
        is_export_equals=is_export_equals,
        expression=expression,
    )


def createExportDefault(expression: Expression) -> ExportAssignment:
    """Create an export default statement.

    Shorthand for createExportAssignment(undefined, False, expression).
    """
    return ExportAssignment(
        modifiers=undefined,
        is_export_equals=False,
        expression=expression,
    )


def createExportDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    is_type_only: bool,
    export_clause: NamedExportBindings | Undefined,
    module_specifier: Expression | Undefined = undefined,
    attributes: ImportAttributes | Undefined = undefined,
) -> ExportDeclaration:
    """Create an export declaration."""
    return ExportDeclaration(
        modifiers=modifiers,
        is_type_only=is_type_only,
        export_clause=export_clause,
        module_specifier=module_specifier,
        attributes=attributes,
    )


def createNamedExports(elements: Sequence[ExportSpecifier]) -> NamedExports:
    """Create named exports ({ a, b })."""
    return NamedExports(elements=elements)


def createExportSpecifier(
    is_type_only: bool,
    property_name: Identifier | str | Undefined,
    name: Identifier | str,
) -> ExportSpecifier:
    """Create an export specifier."""
    return ExportSpecifier(
        is_type_only=is_type_only,
        property_name=property_name,
        name=name,
    )


# ============================================================================
# Type Nodes
# ============================================================================


def createTypeReferenceNode(
    type_name: EntityName | str,
    type_arguments: Sequence[TypeNode] | Undefined = undefined,
) -> TypeReference:
    """Create a type reference node."""
    return TypeReference(type_name=type_name, type_arguments=type_arguments)


def createArrayTypeNode(element_type: TypeNode) -> ArrayType:
    """Create an array type node (Type[])."""
    return ArrayType(element_type=element_type)


def createTupleTypeNode(
    elements: Sequence[TypeNode | NamedTupleMember],
) -> TupleType:
    """Create a tuple type node ([A, B])."""
    return TupleType(elements=elements)


def createUnionTypeNode(types: Sequence[TypeNode]) -> UnionType:
    """Create a union type node (A | B)."""
    return UnionType(types=types)


def createIntersectionTypeNode(types: Sequence[TypeNode]) -> IntersectionType:
    """Create an intersection type node (A & B)."""
    return IntersectionType(types=types)


def createTypeLiteralNode(
    members: Sequence[TypeElement] | Undefined = undefined,
) -> TypeLiteral:
    """Create a type literal node."""
    return TypeLiteral(members=members)


def createLiteralTypeNode(
    literal: LiteralTypeLiteral,
) -> LiteralType:
    """Create a literal type node ('a' | 1)."""
    return LiteralType(literal=literal)


def createFunctionTypeNode(
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode,
) -> FunctionType:
    """Create a function type node."""
    return FunctionType(
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
    )


def createTypeQueryNode(
    expr_name: Identifier | QualifiedName,
    type_arguments: Sequence[TypeNode] | Undefined = undefined,
) -> TypeQuery:
    """Create a typeof type query (typeof x)."""
    return TypeQuery(
        expr_name=expr_name,
        type_arguments=type_arguments,
    )


# Keyword type shortcuts
def createVoidKeyword() -> VoidKeyword:
    return VoidKeyword()


def createNeverKeyword() -> NeverKeyword:
    return NeverKeyword()


def createAnyKeyword() -> AnyKeyword:
    return AnyKeyword()


def createBooleanKeyword() -> BooleanKeyword:
    return BooleanKeyword()


def createNumberKeyword() -> NumberKeyword:
    return NumberKeyword()


def createStringKeyword() -> StringKeyword:
    return StringKeyword()


# ============================================================================
# Class Elements
# ============================================================================


def createPropertyDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    name: PropertyName,
    question_or_exclamation_token: (
        QuestionToken | ExclamationToken | Undefined
    ),
    type: TypeNode | Undefined,
    initializer: Expression | Undefined,
) -> PropertyDeclaration:
    """Create a property declaration."""
    return PropertyDeclaration(
        modifiers=modifiers,
        name=name,
        question_or_exclamation_token=question_or_exclamation_token,
        type=type,
        initializer=initializer,
    )


def createMethodDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    asterisk_token: AsteriskToken | Undefined,
    name: PropertyName,
    question_token: QuestionToken | Undefined,
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode | Undefined,
    body: Block | Undefined,
) -> MethodDeclaration:
    """Create a method declaration."""
    return MethodDeclaration(
        modifiers=modifiers,
        asterisk_token=asterisk_token,
        name=name,
        question_token=question_token,
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
        body=body,
    )


def createConstructorDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    parameters: Sequence[Parameter],
    body: Block | Undefined,
) -> Constructor:
    """Create a constructor declaration."""
    return Constructor(modifiers=modifiers, parameters=parameters, body=body)


# ============================================================================
# Object Elements
# ============================================================================


def createPropertyAssignment(
    name: PropertyName,
    initializer: Expression,
) -> PropertyAssignment:
    """Create a property assignment (key: value)."""
    return PropertyAssignment(name=name, initializer=initializer)


def createShorthandPropertyAssignment(
    name: Identifier | str,
    object_assignment_initializer: Expression | Undefined = undefined,
) -> ShorthandPropertyAssignment:
    """Create a shorthand property assignment ({ x })."""
    return ShorthandPropertyAssignment(
        name=name,
        object_assignment_initializer=object_assignment_initializer,
    )


def createSpreadAssignment(expression: Expression) -> SpreadAssignment:
    """Create a spread assignment (...obj)."""
    return SpreadAssignment(expression=expression)


# ============================================================================
# Bindings
# ============================================================================


def createObjectBindingPattern(
    elements: Sequence[BindingElement],
) -> ObjectBindingPattern:
    """Create an object binding pattern ({ a, b })."""
    return ObjectBindingPattern(elements=elements)


def createArrayBindingPattern(
    elements: Sequence[ArrayBindingElement],
) -> ArrayBindingPattern:
    """Create an array binding pattern ([a, b])."""
    return ArrayBindingPattern(elements=elements)


def createBindingElement(
    dot_dot_dot_token: DotDotDotToken | Undefined,
    property_name: PropertyName | Undefined,
    name: BindingName,
    initializer: Expression | Undefined = undefined,
) -> BindingElement:
    """Create a binding element."""
    return BindingElement(
        dot_dot_dot_token=dot_dot_dot_token,
        property_name=property_name,
        name=name,
        initializer=initializer,
    )


# ============================================================================
# Misc
# ============================================================================


def createParameterDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    dot_dot_dot_token: DotDotDotToken | Undefined,
    name: BindingName,
    question_token: QuestionToken | Undefined = undefined,
    type: TypeNode | Undefined = undefined,
    initializer: Expression | Undefined = undefined,
) -> Parameter:
    """Create a parameter declaration."""
    return Parameter(
        modifiers=modifiers,
        dot_dot_dot_token=dot_dot_dot_token,
        name=name,
        question_token=question_token,
        type=type,
        initializer=initializer,
    )


def createTypeParameterDeclaration(
    modifiers: Sequence[Modifier] | Undefined,
    name: Identifier | str,
    constraint: TypeNode | Undefined = undefined,
    default_type: TypeNode | Undefined = undefined,
) -> TypeParameter:
    """Create a type parameter declaration."""
    return TypeParameter(
        modifiers=modifiers,
        name=name,
        constraint=constraint,
        default_type=default_type,
    )


def createDecorator(expression: Expression) -> Decorator:
    """Create a decorator (@decorator)."""
    return Decorator(expression=expression)


def createHeritageClause(
    token: int,
    types: Sequence[ExpressionWithTypeArguments],
) -> HeritageClause:
    """Create a heritage clause (extends/implements)."""
    return HeritageClause(token=token, types=types)


def createExpressionWithTypeArguments(
    expression: Expression,
    type_arguments: Sequence[TypeNode] | Undefined = undefined,
) -> ExpressionWithTypeArguments:
    """Create an expression with type arguments for extends/implements."""
    return ExpressionWithTypeArguments(
        expression=expression,
        type_arguments=type_arguments,
    )


def createCatchClause(
    variable_declaration: VariableDeclaration | BindingName | Undefined,
    block: Block,
) -> CatchClause:
    """Create a catch clause."""
    return CatchClause(variable_declaration=variable_declaration, block=block)


def createCaseClause(
    expression: Expression,
    statements: Sequence[Statement],
) -> CaseClause:
    """Create a case clause."""
    return CaseClause(expression=expression, statements=statements)


def createDefaultClause(statements: Sequence[Statement]) -> DefaultClause:
    """Create a default clause."""
    return DefaultClause(statements=statements)


def createCaseBlock(
    clauses: Sequence[CaseClause | DefaultClause],
) -> CaseBlock:
    """Create a case block."""
    return CaseBlock(clauses=clauses)


def createTemplateHead(
    text: str,
    raw_text: str | Undefined = undefined,
    template_flags: int = 0,
) -> TemplateHead:
    """Create a template head."""
    return TemplateHead(
        text=text, raw_text=raw_text, template_flags=template_flags
    )


def createTemplateMiddle(
    text: str,
    raw_text: str | Undefined = undefined,
    template_flags: int = 0,
) -> TemplateMiddle:
    """Create a template middle."""
    return TemplateMiddle(
        text=text, raw_text=raw_text, template_flags=template_flags
    )


def createTemplateTail(
    text: str,
    raw_text: str | Undefined = undefined,
    template_flags: int = 0,
) -> TemplateTail:
    """Create a template tail."""
    return TemplateTail(
        text=text, raw_text=raw_text, template_flags=template_flags
    )


def createTemplateSpan(
    expression: Expression,
    literal: TemplateMiddle | TemplateTail,
) -> TemplateSpan:
    """Create a template span."""
    return TemplateSpan(expression=expression, literal=literal)


def createTemplateExpression(
    head: TemplateHead,
    template_spans: Sequence[TemplateSpan],
) -> TemplateExpression:
    """Create a template expression."""
    return TemplateExpression(head=head, template_spans=template_spans)


# ============================================================================
# Modifiers
# ============================================================================


ModifierSyntaxKinds: TypeAlias = Literal[
    SyntaxKind.AbstractKeyword,
    SyntaxKind.AsyncKeyword,
    SyntaxKind.ConstKeyword,
    SyntaxKind.DeclareKeyword,
    SyntaxKind.DefaultKeyword,
    SyntaxKind.ExportKeyword,
    SyntaxKind.OverrideKeyword,
    SyntaxKind.PrivateKeyword,
    SyntaxKind.ProtectedKeyword,
    SyntaxKind.PublicKeyword,
    SyntaxKind.ReadonlyKeyword,
    SyntaxKind.StaticKeyword,
]


def createModifier(kind: ModifierSyntaxKinds) -> Modifier:
    """Create a generic modifier by SyntaxKind."""
    match kind:
        case SyntaxKind.AbstractKeyword:
            return AbstractKeyword()
        case SyntaxKind.AsyncKeyword:
            return AsyncKeyword()
        case SyntaxKind.ConstKeyword:
            return ConstKeyword()
        case SyntaxKind.DeclareKeyword:
            return DeclareKeyword()
        case SyntaxKind.DefaultKeyword:
            return DefaultKeyword()
        case SyntaxKind.ExportKeyword:
            return ExportKeyword()
        case SyntaxKind.OverrideKeyword:
            return OverrideKeyword()
        case SyntaxKind.PrivateKeyword:
            return PrivateKeyword()
        case SyntaxKind.ProtectedKeyword:
            return ProtectedKeyword()
        case SyntaxKind.PublicKeyword:
            return PublicKeyword()
        case SyntaxKind.ReadonlyKeyword:
            return ReadonlyKeyword()
        case SyntaxKind.StaticKeyword:
            return StaticKeyword()
        case _:
            raise ValueError(f"Unsupported modifier kind: {kind}")


def createExportKeyword() -> ExportKeyword:
    """Create an 'export' keyword."""
    return ExportKeyword()


def createConstKeyword() -> ConstKeyword:
    """Create a 'const' keyword."""
    return ConstKeyword()


def createAsyncKeyword() -> AsyncKeyword:
    """Create an 'async' keyword."""
    return AsyncKeyword()


def createPublicKeyword() -> PublicKeyword:
    """Create a 'public' keyword."""
    return PublicKeyword()


def createPrivateKeyword() -> PrivateKeyword:
    """Create a 'private' keyword."""
    return PrivateKeyword()


def createProtectedKeyword() -> ProtectedKeyword:
    """Create a 'protected' keyword."""
    return ProtectedKeyword()


def createReadonlyKeyword() -> ReadonlyKeyword:
    """Create a 'readonly' keyword."""
    return ReadonlyKeyword()


def createStaticKeyword() -> StaticKeyword:
    """Create a 'static' keyword."""
    return StaticKeyword()


# ============================================================================
# Additional Statements
# ============================================================================


def createDoStatement(
    statement: Statement,
    expression: Expression,
) -> DoStatement:
    """Create a do-while statement."""
    return DoStatement(statement=statement, expression=expression)


def createWhileStatement(
    expression: Expression,
    statement: Statement,
) -> WhileStatement:
    """Create a while statement."""
    return WhileStatement(expression=expression, statement=statement)


def createForStatement(
    initializer: ForInitializer | Undefined,
    condition: Expression | Undefined,
    incrementor: Expression | Undefined,
    statement: Statement,
) -> ForStatement:
    """Create a for statement."""
    return ForStatement(
        initializer=initializer,
        condition=condition,
        incrementor=incrementor,
        statement=statement,
    )


def createForInStatement(
    initializer: ForInitializer,
    expression: Expression,
    statement: Statement,
) -> ForInStatement:
    """Create a for-in statement."""
    return ForInStatement(
        initializer=initializer,
        expression=expression,
        statement=statement,
    )


def createForOfStatement(
    await_modifier: AwaitKeywordType | Undefined,
    initializer: ForInitializer,
    expression: Expression,
    statement: Statement,
) -> ForOfStatement:
    """Create a for-of statement."""
    return ForOfStatement(
        await_modifier=await_modifier,
        initializer=initializer,
        expression=expression,
        statement=statement,
    )


def createContinueStatement(
    label: Identifier | str | Undefined = undefined,
) -> ContinueStatement:
    """Create a continue statement."""
    return ContinueStatement(label=label)


def createBreakStatement(
    label: Identifier | str | Undefined = undefined,
) -> BreakStatement:
    """Create a break statement."""
    return BreakStatement(label=label)


def createWithStatement(
    expression: Expression,
    statement: Statement,
) -> WithStatement:
    """Create a with statement."""
    return WithStatement(expression=expression, statement=statement)


def createSwitchStatement(
    expression: Expression,
    case_block: CaseBlock,
) -> SwitchStatement:
    """Create a switch statement."""
    return SwitchStatement(expression=expression, case_block=case_block)


def createLabeledStatement(
    label: Identifier | str,
    statement: Statement,
) -> LabeledStatement:
    """Create a labeled statement."""
    return LabeledStatement(label=label, statement=statement)


# ============================================================================
# Additional Declarations
# ============================================================================


def createEnumDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    name: Identifier | str,
    members: Sequence[EnumMember],
) -> EnumDeclaration:
    """Create an enum declaration."""
    return EnumDeclaration(modifiers=modifiers, name=name, members=members)


def createModuleDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    name: ModuleName,
    body: ModuleBody | Undefined = undefined,
    flags: int = 0,
) -> ModuleDeclaration:
    """Create a module/namespace declaration."""
    return ModuleDeclaration(
        modifiers=modifiers,
        name=name,
        body=body,
        flags=flags,
    )


# ============================================================================
# Additional Class Elements
# ============================================================================


def createGetAccessorDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    name: PropertyName,
    parameters: Sequence[Parameter],
    type: TypeNode | Undefined = undefined,
    body: Block | Undefined = undefined,
) -> GetAccessor:
    """Create a get accessor declaration."""
    return GetAccessor(
        modifiers=modifiers,
        name=name,
        parameters=parameters,
        type=type,
        body=body,
    )


def createSetAccessorDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    name: PropertyName,
    parameters: Sequence[Parameter],
    body: Block | Undefined = undefined,
) -> SetAccessor:
    """Create a set accessor declaration."""
    return SetAccessor(
        modifiers=modifiers,
        name=name,
        parameters=parameters,
        body=body,
    )


def createIndexSignature(
    modifiers: Sequence[ModifierLike] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode,
) -> IndexSignature:
    """Create an index signature."""
    return IndexSignature(
        modifiers=modifiers,
        parameters=parameters,
        type=type,
    )


def createClassStaticBlockDeclaration(
    body: Block,
) -> ClassStaticBlockDeclaration:
    """Create a static block declaration."""
    return ClassStaticBlockDeclaration(body=body)


# ============================================================================
# Additional Expressions
# ============================================================================


def createTaggedTemplateExpression(
    tag: Expression,
    type_arguments: Sequence[TypeNode] | Undefined,
    template: TemplateLiteral,
) -> TaggedTemplateExpression:
    """Create a tagged template expression (tag`template`)."""
    return TaggedTemplateExpression(
        tag=tag,
        type_arguments=type_arguments,
        template=template,
    )


def createTypeAssertion(
    type: TypeNode,
    expression: Expression,
) -> TypeAssertionExpression:
    """Create a type assertion (<Type>expression)."""
    return TypeAssertionExpression(type=type, expression=expression)


def createDeleteExpression(expression: Expression) -> DeleteExpression:
    """Create a delete expression."""
    return DeleteExpression(expression=expression)


def createTypeOfExpression(expression: Expression) -> TypeOfExpression:
    """Create a typeof expression."""
    return TypeOfExpression(expression=expression)


def createVoidExpression(expression: Expression) -> VoidExpression:
    """Create a void expression."""
    return VoidExpression(expression=expression)


def createPrefixUnaryExpression(
    operator: int,
    operand: Expression,
) -> PrefixUnaryExpression:
    """Create a prefix unary expression (++x, !x, etc)."""
    return PrefixUnaryExpression(operator=operator, operand=operand)


def createPostfixUnaryExpression(
    operand: Expression,
    operator: int,
) -> PostfixUnaryExpression:
    """Create a postfix unary expression (x++, x--)."""
    return PostfixUnaryExpression(operand=operand, operator=operator)


def createYieldExpression(
    asterisk_token: Node | Undefined = undefined,
    expression: Expression | Undefined = undefined,
) -> YieldExpression:
    """Create a yield expression."""
    return YieldExpression(
        asterisk_token=asterisk_token,
        expression=expression,
    )


def createClassExpression(
    modifiers: Sequence[Modifier] | Undefined,
    name: Identifier | str | Undefined,
    type_parameters: Sequence[TypeParameter] | Undefined,
    heritage_clauses: Sequence[HeritageClause] | Undefined,
    members: Sequence[ClassElement],
) -> ClassExpression:
    """Create a class expression."""
    return ClassExpression(
        modifiers=modifiers,
        name=name,
        type_parameters=type_parameters,
        heritage_clauses=heritage_clauses,
        members=members,
    )


def createSatisfiesExpression(
    expression: Expression,
    type: TypeNode,
) -> SatisfiesExpression:
    """Create a satisfies expression (expr satisfies Type)."""
    return SatisfiesExpression(expression=expression, type=type)


# ============================================================================
# Additional Expressions
# ============================================================================


def createThis() -> ThisExpression:
    """Create a 'this' expression."""
    return ThisExpression()


def createSuper() -> SuperExpression:
    """Create a 'super' expression."""
    return SuperExpression()


def createMetaProperty(
    keyword_token: int,
    name: Identifier,
) -> MetaProperty:
    """Create a meta property (import.meta or new.target)."""
    return MetaProperty(keyword_token=keyword_token, name=name)


def createCommaListExpression(
    elements: Sequence[Expression],
) -> CommaListExpression:
    """Create a comma-separated list of expressions."""
    return CommaListExpression(elements=elements)


def createPartiallyEmittedExpression(
    expression: Expression,
    original: Node | Undefined = undefined,
) -> PartiallyEmittedExpression:
    """Create a partially emitted expression."""
    return PartiallyEmittedExpression(expression=expression, original=original)


# ============================================================================
# Additional Declarations
# ============================================================================


def createEnumMember(
    name: PropertyName,
    initializer: Expression | Undefined = undefined,
) -> EnumMember:
    """Create an enum member."""
    return EnumMember(name=name, initializer=initializer)


def createNamespaceExportDeclaration(
    name: Identifier | str,
) -> NamespaceExportDeclaration:
    """Create a namespace export declaration (export as namespace Name)."""
    return NamespaceExportDeclaration(name=name)


def createNamespaceExport(name: Identifier) -> NamespaceExport:
    """Create a namespace export (* as name)."""
    return NamespaceExport(name=name)


def createImportEqualsDeclaration(
    modifiers: Sequence[ModifierLike] | Undefined,
    is_type_only: bool,
    name: Identifier,
    module_reference: ModuleReference,
) -> ImportEqualsDeclaration:
    """Create an import equals declaration."""
    return ImportEqualsDeclaration(
        modifiers=modifiers,
        is_type_only=is_type_only,
        name=name,
        module_reference=module_reference,
    )


def createExternalModuleReference(
    expression: Expression,
) -> ExternalModuleReference:
    """Create an external module reference (require('module'))."""
    return ExternalModuleReference(expression=expression)


# ============================================================================
# Additional Type Nodes
# ============================================================================


def createConstructorTypeNode(
    modifiers: Sequence[Modifier] | Undefined,
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode,
) -> ConstructorType:
    """Create a constructor type node."""
    return ConstructorType(
        modifiers=modifiers,
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
    )


def createOptionalTypeNode(type: TypeNode) -> OptionalType:
    """Create an optional type node (Type?)."""
    return OptionalType(type=type)


def createRestTypeNode(type: TypeNode) -> RestType:
    """Create a rest type node (...Type)."""
    return RestType(type=type)


def createConditionalTypeNode(
    check_type: TypeNode,
    extends_type: TypeNode,
    true_type: TypeNode,
    false_type: TypeNode,
) -> ConditionalType:
    """Create a conditional type node (T extends U ? X : Y)."""
    return ConditionalType(
        check_type=check_type,
        extends_type=extends_type,
        true_type=true_type,
        false_type=false_type,
    )


def createInferTypeNode(type_parameter: TypeParameter) -> InferType:
    """Create an infer type node (infer T)."""
    return InferType(type_parameter=type_parameter)


def createParenthesizedType(type: TypeNode) -> ParenthesizedType:
    """Create a parenthesized type node ((Type))."""
    return ParenthesizedType(type=type)


def createThisTypeNode() -> ThisType:
    """Create a 'this' type node."""
    return ThisType()


def createTypeOperatorNode(operator: int, type: TypeNode) -> TypeOperator:
    """Create a type operator node (keyof T, readonly T, unique symbol)."""
    return TypeOperator(operator=operator, type=type)


def createIndexedAccessTypeNode(
    object_type: TypeNode,
    index_type: TypeNode,
) -> IndexedAccessType:
    """Create an indexed access type node (T[K])."""
    return IndexedAccessType(object_type=object_type, index_type=index_type)


def createMappedTypeNode(
    readonly_token: ReadonlyKeyword | PlusToken | MinusToken | Undefined,
    type_parameter: TypeParameter,
    name_type: TypeNode | Undefined,
    question_token: QuestionToken | PlusToken | MinusToken | Undefined,
    type: TypeNode | Undefined,
    members: Sequence[TypeElement] | Undefined = undefined,
) -> MappedType:
    """Create a mapped type node ({ [K in T]: U })."""
    return MappedType(
        readonly_token=readonly_token,
        type_parameter=type_parameter,
        name_type=name_type,
        question_token=question_token,
        type=type,
        members=members,
    )


def createTemplateLiteralType(
    head: TemplateHead,
    template_spans: Sequence[TemplateLiteralTypeSpan],
) -> TemplateLiteralType:
    """Create a template literal type (`prefix${T}suffix`)."""
    return TemplateLiteralType(head=head, template_spans=template_spans)


def createImportTypeNode(
    argument: TypeNode,
    attributes: ImportAttributes | Undefined = undefined,
    qualifier: EntityName | Undefined = undefined,
    type_arguments: Sequence[TypeNode] | Undefined = undefined,
    is_type_of: bool = False,
) -> ImportType:
    """Create an import type node (import('module').Type)."""
    return ImportType(
        argument=argument,
        attributes=attributes,
        qualifier=qualifier,
        type_arguments=type_arguments,
        is_type_of=is_type_of,
    )


def createNamedTupleMember(
    dot_dot_dot_token: DotDotDotToken | Undefined,
    name: Identifier,
    question_token: QuestionToken | Undefined,
    type: TypeNode,
) -> NamedTupleMember:
    """Create a named tuple member (name: Type)."""
    return NamedTupleMember(
        dot_dot_dot_token=dot_dot_dot_token,
        name=name,
        question_token=question_token,
        type=type,
    )


def createTemplateLiteralTypeSpan(
    type: TypeNode,
    literal: TemplateMiddle | TemplateTail,
) -> TemplateLiteralTypeSpan:
    """Create a template literal type span."""
    return TemplateLiteralTypeSpan(type=type, literal=literal)


def createTypePredicateNode(
    asserts_modifier: AssertsKeyword | Undefined,
    parameter_name: Identifier | ThisType | str,
    type: TypeNode | Undefined = undefined,
) -> TypePredicateNode:
    """Create a type predicate node (param is Type)."""
    return TypePredicateNode(
        asserts_modifier=asserts_modifier,
        parameter_name=parameter_name,
        type=type,
    )


# ============================================================================
# Additional Misc Nodes
# ============================================================================


def createComputedPropertyName(
    expression: Expression,
) -> ComputedPropertyName:
    """Create a computed property name ([expression])."""
    return ComputedPropertyName(expression=expression)


def createPropertySignature(
    modifiers: Sequence[Modifier] | Undefined,
    name: PropertyName,
    question_token: QuestionToken | Undefined = undefined,
    type: TypeNode | Undefined = undefined,
) -> PropertySignature:
    """Create a property signature (name?: Type)."""
    return PropertySignature(
        modifiers=modifiers,
        name=name,
        question_token=question_token,
        type=type,
    )


def createMethodSignature(
    modifiers: Sequence[Modifier] | Undefined,
    name: PropertyName,
    question_token: QuestionToken | Undefined,
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode | Undefined = undefined,
) -> MethodSignature:
    """Create a method signature (name(params): Type)."""
    return MethodSignature(
        modifiers=modifiers,
        name=name,
        question_token=question_token,
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
    )


def createCallSignature(
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode | Undefined = undefined,
) -> CallSignatureDeclaration:
    """Create a call signature ((params): Type)."""
    return CallSignatureDeclaration(
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
    )


def createConstructSignature(
    type_parameters: Sequence[TypeParameter] | Undefined,
    parameters: Sequence[Parameter],
    type: TypeNode | Undefined = undefined,
) -> ConstructSignatureDeclaration:
    """Create a construct signature (new (params): Type)."""
    return ConstructSignatureDeclaration(
        type_parameters=type_parameters,
        parameters=parameters,
        type=type,
    )


def createSemicolonClassElement() -> SemicolonClassElement:
    """Create a semicolon class element."""
    return SemicolonClassElement()


def createImportAttribute(
    name: Identifier | str,
    value: Expression,
) -> ImportAttribute:
    """Create an import attribute (key: value)."""
    return ImportAttribute(name=name, value=value)


def createImportAttributes(
    elements: Sequence[ImportAttribute],
    multi_line: bool = False,
) -> ImportAttributes:
    """Create import attributes (with { key: value })."""
    return ImportAttributes(elements=elements, multi_line=multi_line)


# ============================================================================
# Additional Keywords
# ============================================================================


def createSymbolKeyword() -> SymbolKeyword:
    """Create a 'symbol' keyword type."""
    return SymbolKeyword()


def createBigIntKeyword() -> BigIntKeyword:
    """Create a 'bigint' keyword type."""
    return BigIntKeyword()


def createObjectKeyword() -> ObjectKeyword:
    """Create an 'object' keyword type."""
    return ObjectKeyword()


def createUnknownKeyword() -> UnknownKeyword:
    """Create an 'unknown' keyword type."""
    return UnknownKeyword()


def createUndefinedKeyword() -> UndefinedKeyword:
    """Create an 'undefined' keyword type."""
    return UndefinedKeyword()


def createNullKeyword() -> NullKeyword:
    """Create a 'null' keyword type."""
    return NullKeyword()


def createIntrinsicKeyword() -> IntrinsicKeyword:
    """Create an 'intrinsic' keyword type."""
    return IntrinsicKeyword()


# ============================================================================
# Additional Modifiers
# ============================================================================


def createAbstractKeyword() -> AbstractKeyword:
    """Create an 'abstract' keyword."""
    return AbstractKeyword()


def createDeclareKeyword() -> DeclareKeyword:
    """Create a 'declare' keyword."""
    return DeclareKeyword()


def createDefaultKeyword() -> DefaultKeyword:
    """Create a 'default' keyword."""
    return DefaultKeyword()


def createOverrideKeyword() -> OverrideKeyword:
    """Create an 'override' keyword."""
    return OverrideKeyword()


def createAccessorKeyword() -> AccessorKeyword:
    """Create an 'accessor' keyword."""
    return AccessorKeyword()


def createInModifier() -> InKeyword:
    """Create an 'in' keyword (for type parameters)."""
    return InKeyword()


def createOutModifier() -> OutKeyword:
    """Create an 'out' keyword (for type parameters)."""
    return OutKeyword()


# ============================================================================
# Tokens
# ============================================================================


def createToken(kind: int) -> Token:
    """Create a token with the given SyntaxKind."""
    return Token(kind=kind)


def createQuestionToken() -> QuestionToken:
    """Create a '?' token."""
    return QuestionToken()


def createExclamationToken() -> ExclamationToken:
    """Create a '!' token."""
    return ExclamationToken()


def createDotDotDotToken() -> DotDotDotToken:
    """Create a '...' token."""
    return DotDotDotToken()


def createColonToken() -> ColonToken:
    """Create a ':' token."""
    return ColonToken()


def createEqualsGreaterThanToken() -> EqualsGreaterThanToken:
    """Create a '=>' token."""
    return EqualsGreaterThanToken()


def createAsteriskToken() -> AsteriskToken:
    """Create a '*' token."""
    return AsteriskToken()


def createEqualsToken() -> EqualsToken:
    """Create a '=' token."""
    return EqualsToken()


def createPlusToken() -> PlusToken:
    """Create a '+' token."""
    return PlusToken()


def createMinusToken() -> MinusToken:
    """Create a '-' token."""
    return MinusToken()


# ============================================================================
# JSX Nodes
# ============================================================================


def createJsxElement(
    opening_element: JsxOpeningElement,
    children: Sequence[JsxChild],
    closing_element: JsxClosingElement,
) -> JsxElement:
    """Create a JSX element (<tag>children</tag>)."""
    return JsxElement(
        opening_element=opening_element,
        children=children,
        closing_element=closing_element,
    )


def createJsxSelfClosingElement(
    tag_name: JsxTagNameExpression,
    type_arguments: Sequence[TypeNode] | Undefined,
    attributes: JsxAttributes,
) -> JsxSelfClosingElement:
    """Create a self-closing JSX element (<tag />)."""
    return JsxSelfClosingElement(
        tag_name=tag_name,
        type_arguments=type_arguments,
        attributes=attributes,
    )


def createJsxOpeningElement(
    tag_name: JsxTagNameExpression,
    type_arguments: Sequence[TypeNode] | Undefined,
    attributes: JsxAttributes,
) -> JsxOpeningElement:
    """Create a JSX opening element (<tag>)."""
    return JsxOpeningElement(
        tag_name=tag_name,
        type_arguments=type_arguments,
        attributes=attributes,
    )


def createJsxClosingElement(
    tag_name: JsxTagNameExpression,
) -> JsxClosingElement:
    """Create a JSX closing element (</tag>)."""
    return JsxClosingElement(tag_name=tag_name)


def createJsxFragment(
    opening_fragment: JsxOpeningFragment,
    children: Sequence[JsxChild],
    closing_fragment: JsxClosingFragment,
) -> JsxFragment:
    """Create a JSX fragment (<>children</>)."""
    return JsxFragment(
        opening_fragment=opening_fragment,
        children=children,
        closing_fragment=closing_fragment,
    )


def createJsxOpeningFragment() -> JsxOpeningFragment:
    """Create a JSX opening fragment (<>)."""
    return JsxOpeningFragment()


def createJsxClosingFragment() -> JsxClosingFragment:
    """Create a JSX closing fragment (</>)."""
    return JsxClosingFragment()


def createJsxText(
    text: str,
    contains_only_trivia_white_spaces: bool = False,
) -> JsxText:
    """Create JSX text content."""
    return JsxText(
        text=text,
        contains_only_trivia_white_spaces=contains_only_trivia_white_spaces,
    )


def createJsxExpression(
    dot_dot_dot_token: DotDotDotToken | Undefined = undefined,
    expression: Expression | Undefined = undefined,
) -> JsxExpression:
    """Create a JSX expression ({expression})."""
    return JsxExpression(
        dot_dot_dot_token=dot_dot_dot_token,
        expression=expression,
    )


def createJsxAttribute(
    name: Identifier | JsxNamespacedName,
    initializer: JsxAttributeValue | Undefined = undefined,
) -> JsxAttribute:
    """Create a JSX attribute (name={value})."""
    return JsxAttribute(name=name, initializer=initializer)


def createJsxSpreadAttribute(expression: Expression) -> JsxSpreadAttribute:
    """Create a JSX spread attribute ({...expression})."""
    return JsxSpreadAttribute(expression=expression)


def createJsxAttributes(
    properties: Sequence[JsxAttributeLike],
) -> JsxAttributes:
    """Create JSX attributes."""
    return JsxAttributes(properties=properties)


def createJsxNamespacedName(
    namespace: Identifier,
    name: Identifier,
) -> JsxNamespacedName:
    """Create a namespaced JSX name (namespace:name)."""
    return JsxNamespacedName(namespace=namespace, name=name)

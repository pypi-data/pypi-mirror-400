"""
TypeScript AST Nodes module.

This module exports all AST node types organized by category.
"""

from pytsast.core.base import Node


# Base types
from pytsast.nodes.common import (
    Identifier,
    PrivateIdentifier,
    QualifiedName,
)

# Literals
from pytsast.nodes.literals import (
    StringLiteral,
    NumericLiteral,
    BigIntLiteral,
    RegularExpressionLiteral,
    NoSubstitutionTemplateLiteral,
    TrueLiteral,
    FalseLiteral,
    NullLiteral,
)

# Expressions
from pytsast.nodes.expressions import (
    ArrayLiteralExpression,
    ObjectLiteralExpression,
    PropertyAccessExpression,
    ElementAccessExpression,
    CallExpression,
    NewExpression,
    TaggedTemplateExpression,
    TypeAssertionExpression,
    ParenthesizedExpression,
    FunctionExpression,
    ArrowFunction,
    DeleteExpression,
    TypeOfExpression,
    VoidExpression,
    AwaitExpression,
    PrefixUnaryExpression,
    PostfixUnaryExpression,
    BinaryExpression,
    ConditionalExpression,
    TemplateExpression,
    YieldExpression,
    SpreadElement,
    ClassExpression,
    OmittedExpression,
    AsExpression,
    NonNullExpression,
    SatisfiesExpression,
    ThisExpression,
    SuperExpression,
    MetaProperty,
    CommaListExpression,
    PartiallyEmittedExpression,
)

# Statements
from pytsast.nodes.statements import (
    Block,
    EmptyStatement,
    VariableStatement,
    ExpressionStatement,
    IfStatement,
    DoStatement,
    WhileStatement,
    ForStatement,
    ForInStatement,
    ForOfStatement,
    ContinueStatement,
    BreakStatement,
    ReturnStatement,
    WithStatement,
    SwitchStatement,
    LabeledStatement,
    ThrowStatement,
    TryStatement,
    DebuggerStatement,
)

# Declarations
from pytsast.nodes.declarations import (
    VariableDeclaration,
    VariableDeclarationList,
    FunctionDeclaration,
    ClassDeclaration,
    InterfaceDeclaration,
    TypeAliasDeclaration,
    EnumDeclaration,
    ModuleDeclaration,
    ImportDeclaration,
    ImportClause,
    NamespaceImport,
    NamedImports,
    ImportSpecifier,
    ExportAssignment,
    ExportDeclaration,
    NamedExports,
    ExportSpecifier,
    EnumMember,
    NamespaceExportDeclaration,
    NamespaceExport,
    ImportEqualsDeclaration,
    ExternalModuleReference,
)

# Type nodes
from pytsast.nodes.type_nodes import (
    TypeReference,
    FunctionType,
    ConstructorType,
    TypeQuery,
    TypeLiteral,
    ArrayType,
    TupleType,
    OptionalType,
    RestType,
    UnionType,
    IntersectionType,
    ConditionalType,
    InferType,
    ParenthesizedType,
    ThisType,
    TypeOperator,
    IndexedAccessType,
    MappedType,
    LiteralType,
    TemplateLiteralType,
    ImportType,
    NamedTupleMember,
    TemplateLiteralTypeSpan,
    TypePredicateNode,
)

# Class elements
from pytsast.nodes.class_elements import (
    PropertyDeclaration,
    MethodDeclaration,
    Constructor,
    GetAccessor,
    SetAccessor,
    IndexSignature,
    ClassStaticBlockDeclaration,
)

# Object literal elements
from pytsast.nodes.object_elements import (
    PropertyAssignment,
    ShorthandPropertyAssignment,
    SpreadAssignment,
    MethodDeclarationShort,
    GetAccessorShort,
    SetAccessorShort,
)

# Binding patterns
from pytsast.nodes.bindings import (
    ObjectBindingPattern,
    ArrayBindingPattern,
    BindingElement,
)

# Misc
from pytsast.nodes.misc import (
    TemplateSpan,
    TemplateTail,
    TemplateMiddle,
    TemplateHead,
    HeritageClause,
    CatchClause,
    Decorator,
    Parameter,
    TypeParameter,
    CaseClause,
    DefaultClause,
    CaseBlock,
    ExpressionWithTypeArguments,
    ComputedPropertyName,
    PropertySignature,
    MethodSignature,
    CallSignatureDeclaration,
    ConstructSignatureDeclaration,
    SemicolonClassElement,
    ImportAttribute,
    ImportAttributes,
    JsxAttribute,
    JsxSpreadAttribute,
    JsxElement,
    JsxSelfClosingElement,
    JsxOpeningElement,
    JsxClosingElement,
    JsxFragment,
    JsxOpeningFragment,
    JsxClosingFragment,
    JsxText,
    JsxExpression,
    JsxAttributes,
    JsxNamespacedName,
)

# Modifiers
from pytsast.nodes.modifiers import (
    Modifier,
    ExportKeyword,
    DefaultKeyword,
    DeclareKeyword,
    ConstKeyword,
    AbstractKeyword,
    AsyncKeyword,
    PublicKeyword,
    PrivateKeyword,
    ProtectedKeyword,
    ReadonlyKeyword,
    StaticKeyword,
    OverrideKeyword,
    AccessorKeyword,
    InKeyword,
    OutKeyword,
)

# Keywords
from pytsast.nodes.keywords import (
    VoidKeyword,
    NeverKeyword,
    AnyKeyword,
    BooleanKeyword,
    NumberKeyword,
    StringKeyword,
    SymbolKeyword,
    BigIntKeyword,
    ObjectKeyword,
    UnknownKeyword,
    UndefinedKeyword,
    NullKeyword,
    ThisKeyword,
    SuperKeyword,
    IntrinsicKeyword,
    AssertsKeyword,
    AwaitKeywordType,
)

# Tokens
from pytsast.nodes.tokens import (
    Token,
    QuestionToken,
    ExclamationToken,
    DotDotDotToken,
    ColonToken,
    EqualsGreaterThanToken,
    AsteriskToken,
    EqualsToken,
    PlusToken,
    MinusToken,
    CommaToken,
    SemicolonToken,
    OpenBraceToken,
    CloseBraceToken,
    OpenParenToken,
    CloseParenToken,
    OpenBracketToken,
    CloseBracketToken,
    DotToken,
    LessThanToken,
    GreaterThanToken,
    AtToken,
    BarToken,
    AmpersandToken,
    CaretToken,
    TildeToken,
    QuestionQuestionToken,
    BarBarToken,
    AmpersandAmpersandToken,
    PlusPlusToken,
    MinusMinusToken,
    QuestionDotToken,
    AmpersandAmpersandEqualsToken,
    BarBarEqualsToken,
    QuestionQuestionEqualsToken,
)


# Type aliases (defined early for forward references)
Expression = Node
TypeNode = Node

__all__ = [
    # Type aliases
    "Node",
    "Expression",
    "TypeNode",
    # Common
    "Identifier",
    "PrivateIdentifier",
    "QualifiedName",
    # Literals
    "StringLiteral",
    "NumericLiteral",
    "BigIntLiteral",
    "RegularExpressionLiteral",
    "NoSubstitutionTemplateLiteral",
    "TrueLiteral",
    "FalseLiteral",
    "NullLiteral",
    # Expressions
    "ArrayLiteralExpression",
    "ObjectLiteralExpression",
    "PropertyAccessExpression",
    "ElementAccessExpression",
    "CallExpression",
    "NewExpression",
    "TaggedTemplateExpression",
    "TypeAssertionExpression",
    "ParenthesizedExpression",
    "FunctionExpression",
    "ArrowFunction",
    "DeleteExpression",
    "TypeOfExpression",
    "VoidExpression",
    "AwaitExpression",
    "PrefixUnaryExpression",
    "PostfixUnaryExpression",
    "BinaryExpression",
    "ConditionalExpression",
    "TemplateExpression",
    "YieldExpression",
    "SpreadElement",
    "ClassExpression",
    "OmittedExpression",
    "AsExpression",
    "NonNullExpression",
    "SatisfiesExpression",
    # Statements
    "Block",
    "EmptyStatement",
    "VariableStatement",
    "ExpressionStatement",
    "IfStatement",
    "DoStatement",
    "WhileStatement",
    "ForStatement",
    "ForInStatement",
    "ForOfStatement",
    "ContinueStatement",
    "BreakStatement",
    "ReturnStatement",
    "WithStatement",
    "SwitchStatement",
    "LabeledStatement",
    "ThrowStatement",
    "TryStatement",
    "DebuggerStatement",
    # Declarations
    "VariableDeclaration",
    "VariableDeclarationList",
    "FunctionDeclaration",
    "ClassDeclaration",
    "InterfaceDeclaration",
    "TypeAliasDeclaration",
    "EnumDeclaration",
    "ModuleDeclaration",
    "ImportDeclaration",
    "ImportClause",
    "NamespaceImport",
    "NamedImports",
    "ImportSpecifier",
    "ExportAssignment",
    "ExportDeclaration",
    "NamedExports",
    "ExportSpecifier",
    # Type nodes
    "TypeReference",
    "FunctionType",
    "ConstructorType",
    "TypeQuery",
    "TypeLiteral",
    "ArrayType",
    "TupleType",
    "OptionalType",
    "RestType",
    "UnionType",
    "IntersectionType",
    "ConditionalType",
    "InferType",
    "ParenthesizedType",
    "ThisType",
    "TypeOperator",
    "IndexedAccessType",
    "MappedType",
    "LiteralType",
    "TemplateLiteralType",
    "ImportType",
    # Class elements
    "PropertyDeclaration",
    "MethodDeclaration",
    "Constructor",
    "GetAccessor",
    "SetAccessor",
    "IndexSignature",
    "ClassStaticBlockDeclaration",
    # Object elements
    "PropertyAssignment",
    "ShorthandPropertyAssignment",
    "SpreadAssignment",
    "MethodDeclarationShort",
    "GetAccessorShort",
    "SetAccessorShort",
    # Bindings
    "ObjectBindingPattern",
    "ArrayBindingPattern",
    "BindingElement",
    # Misc
    "TemplateSpan",
    "TemplateTail",
    "TemplateMiddle",
    "TemplateHead",
    "HeritageClause",
    "CatchClause",
    "Decorator",
    "Parameter",
    "TypeParameter",
    "CaseClause",
    "DefaultClause",
    "CaseBlock",
    "ExpressionWithTypeArguments",
    # Modifiers
    "Modifier",
    "ExportKeyword",
    "DefaultKeyword",
    "DeclareKeyword",
    "ConstKeyword",
    "AbstractKeyword",
    "AsyncKeyword",
    "PublicKeyword",
    "PrivateKeyword",
    "ProtectedKeyword",
    "ReadonlyKeyword",
    "StaticKeyword",
    "OverrideKeyword",
    # Keywords
    "VoidKeyword",
    "NeverKeyword",
    "AnyKeyword",
    "BooleanKeyword",
    "NumberKeyword",
    "StringKeyword",
    "SymbolKeyword",
    "BigIntKeyword",
    "ObjectKeyword",
    "UnknownKeyword",
    "UndefinedKeyword",
    "NullKeyword",
    "ThisKeyword",
    "SuperKeyword",
    "IntrinsicKeyword",
    "AssertsKeyword",
    "AwaitKeywordType",
    # Additional Expressions
    "ThisExpression",
    "SuperExpression",
    "MetaProperty",
    "CommaListExpression",
    "PartiallyEmittedExpression",
    # Additional Declarations
    "EnumMember",
    "NamespaceExportDeclaration",
    "NamespaceExport",
    "ImportEqualsDeclaration",
    "ExternalModuleReference",
    # Additional Type Nodes
    "NamedTupleMember",
    "TemplateLiteralTypeSpan",
    "TypePredicateNode",
    # Additional Misc
    "ComputedPropertyName",
    "PropertySignature",
    "MethodSignature",
    "CallSignatureDeclaration",
    "ConstructSignatureDeclaration",
    "SemicolonClassElement",
    "ImportAttribute",
    "ImportAttributes",
    "JsxAttribute",
    "JsxSpreadAttribute",
    "JsxElement",
    "JsxSelfClosingElement",
    "JsxOpeningElement",
    "JsxClosingElement",
    "JsxFragment",
    "JsxOpeningFragment",
    "JsxClosingFragment",
    "JsxText",
    "JsxExpression",
    "JsxAttributes",
    "JsxNamespacedName",
    # Additional Modifiers
    "AccessorKeyword",
    "InKeyword",
    "OutKeyword",
    # Tokens
    "Token",
    "QuestionToken",
    "ExclamationToken",
    "DotDotDotToken",
    "ColonToken",
    "EqualsGreaterThanToken",
    "AsteriskToken",
    "EqualsToken",
    "PlusToken",
    "MinusToken",
    "CommaToken",
    "SemicolonToken",
    "OpenBraceToken",
    "CloseBraceToken",
    "OpenParenToken",
    "CloseParenToken",
    "OpenBracketToken",
    "CloseBracketToken",
    "DotToken",
    "LessThanToken",
    "GreaterThanToken",
    "AtToken",
    "BarToken",
    "AmpersandToken",
    "CaretToken",
    "TildeToken",
    "QuestionQuestionToken",
    "BarBarToken",
    "AmpersandAmpersandToken",
    "PlusPlusToken",
    "MinusMinusToken",
    "QuestionDotToken",
    "AmpersandAmpersandEqualsToken",
    "BarBarEqualsToken",
    "QuestionQuestionEqualsToken",
]


# Rebuild all models to resolve forward references
def _rebuild_models():
    """Rebuild all Pydantic models to resolve forward references."""
    import sys
    from pytsast.core.base import Node

    current_module = sys.modules[__name__]

    # Build a namespace with all types for forward reference resolution
    local_ns = {}
    for name in __all__:
        cls = getattr(current_module, name, None)
        if cls is not None:
            local_ns[name] = cls

    # Add Node to namespace
    local_ns["Node"] = Node

    for name in __all__:
        cls = getattr(current_module, name, None)
        if cls is not None and hasattr(cls, "model_rebuild"):
            try:
                cls.model_rebuild(_types_namespace=local_ns)
            except Exception:
                pass  # Some classes may not need rebuilding


_rebuild_models()

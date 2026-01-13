"""
TypeScript SyntaxKind enum for pytsast.

These values must match the TypeScript compiler's SyntaxKind enum.
Values are from TypeScript 5.x compiler API.
"""

from enum import IntEnum


class SyntaxKind(IntEnum):
    """TypeScript SyntaxKind values for tokens and keywords."""

    # Keywords - Modifiers
    ConstKeyword = 87
    DefaultKeyword = 90
    ExportKeyword = 95
    ExtendsKeyword = 96
    FalseKeyword = 97
    NullKeyword = 106
    TrueKeyword = 112
    VoidKeyword = 116
    ImplementsKeyword = 119
    PrivateKeyword = 123
    ProtectedKeyword = 124
    PublicKeyword = 125
    StaticKeyword = 126
    AbstractKeyword = 128
    AnyKeyword = 133
    AsyncKeyword = 134
    BooleanKeyword = 136
    DeclareKeyword = 138
    NeverKeyword = 146
    ReadonlyKeyword = 148
    NumberKeyword = 150
    ObjectKeyword = 151
    StringKeyword = 154
    SymbolKeyword = 155
    UndefinedKeyword = 157
    UnknownKeyword = 159
    BigIntKeyword = 163
    OverrideKeyword = 164

    # Additional keywords
    IntrinsicKeyword = 141
    ThisKeyword = 110
    SuperKeyword = 108
    AccessorKeyword = 129
    InKeyword = 103
    OutKeyword = 147

    # Tokens
    QuestionToken = 58
    ExclamationToken = 54
    DotDotDotToken = 26
    ColonToken = 59
    EqualsGreaterThanToken = 39
    AsteriskToken = 42
    EqualsToken = 64
    PlusToken = 40
    MinusToken = 41
    CommaToken = 28
    SemicolonToken = 27
    OpenBraceToken = 19
    CloseBraceToken = 20
    OpenParenToken = 21
    CloseParenToken = 22
    OpenBracketToken = 23
    CloseBracketToken = 24
    DotToken = 25
    LessThanToken = 30
    GreaterThanToken = 32
    AtToken = 60
    BarToken = 52
    AmpersandToken = 51
    CaretToken = 53
    TildeToken = 55
    QuestionQuestionToken = 61
    BarBarToken = 57
    AmpersandAmpersandToken = 56
    PlusPlusToken = 46
    MinusMinusToken = 47
    LessThanLessThanToken = 48
    GreaterThanGreaterThanToken = 49
    GreaterThanGreaterThanGreaterThanToken = 50

    # Additional compound assignment tokens
    QuestionDotToken = 29
    AmpersandAmpersandEqualsToken = 77
    BarBarEqualsToken = 76
    QuestionQuestionEqualsToken = 78

    # Additional keywords
    AssertsKeyword = 131
    AwaitKeyword = 135
    KeyOfKeyword = 143
    UniqueKeyword = 158


class NodeFlags(IntEnum):
    """TypeScript NodeFlags values for node flags."""

    NONE = 0
    Let = 1
    Const = 2
    Using = 4
    AwaitUsing = 6
    NestedNamespace = 8
    Synthesized = 16
    Namespace = 32
    OptionalChain = 64
    ExportContext = 128
    ContainsThis = 256
    HasImplicitReturn = 512
    HasExplicitReturn = 1024
    GlobalAugmentation = 2048
    HasAsyncFunctions = 4096

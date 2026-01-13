"""
Declaration AST nodes - Variables, Functions, Classes, Imports, Exports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Sequence

from pytsast.core.base import Node
from pytsast.core.types import Undefined, undefined
from pytsast.nodes.misc import Decorator
from pytsast.nodes.modifiers import Modifier

if TYPE_CHECKING:
    from pytsast.nodes.common import Identifier
    from pytsast.nodes.expressions import Expression
    from pytsast.nodes.statements import Block
    from pytsast.nodes.type_nodes import TypeNode
    from pytsast.nodes.misc import Parameter, TypeParameter, HeritageClause


class VariableDeclaration(Node):
    """
    Represents a variable declaration: x = 1.

    TypeScript: ts.factory.createVariableDeclaration(name, exclamationToken?,
      type?, initializer?)
    """

    factory_name: ClassVar[str] = "createVariableDeclaration"

    name: "Identifier | Node | str"  # BindingName
    exclamation_token: Node | Undefined = undefined
    type: "TypeNode | Undefined" = undefined
    initializer: "Expression | Undefined" = undefined


class VariableDeclarationList(Node):
    """
    Represents a variable declaration list: const x = 1, y = 2.

    TypeScript: ts.factory.createVariableDeclarationList(declarations, flags?)
    """

    factory_name: ClassVar[str] = "createVariableDeclarationList"

    declarations: Sequence[VariableDeclaration]
    flags: int = 0  # NodeFlags (Const = 2, Let = 1, Undefined = 0 for var)


class FunctionDeclaration(Node):
    """
    Represents a function declaration: function name() { }.

    TypeScript: ts.factory.createFunctionDeclaration(
        modifiers?, asteriskToken?, name?, typeParameters?, parameters, type?,
         body?
    )
    """

    factory_name: ClassVar[str] = "createFunctionDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    asterisk_token: Node | Undefined = undefined
    name: "Identifier | str | Undefined" = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    parameters: Sequence["Parameter"]
    type: "TypeNode | Undefined" = undefined
    body: "Block | Undefined" = undefined


class ClassDeclaration(Node):
    """
    Represents a class declaration: class Name { }.

    TypeScript: ts.factory.createClassDeclaration(
        modifiers?, name?, typeParameters?, heritageClauses?, members
    )
    """

    factory_name: ClassVar[str] = "createClassDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | str | Undefined" = undefined
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    heritage_clauses: Sequence["HeritageClause"] | Undefined = undefined
    members: Sequence[Node]


class InterfaceDeclaration(Node):
    """
    Represents an interface declaration: interface Name { }.

    TypeScript: ts.factory.createInterfaceDeclaration(
        modifiers?, name, typeParameters?, heritageClauses?, members
    )
    """

    factory_name: ClassVar[str] = "createInterfaceDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | str"
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    heritage_clauses: Sequence["HeritageClause"] | Undefined = undefined
    members: Sequence[Node]


class TypeAliasDeclaration(Node):
    """
    Represents a type alias declaration: type Name = Type.

    TypeScript: ts.factory.createTypeAliasDeclaration(modifiers?, name,
    typeParameters?, type)
    """

    factory_name: ClassVar[str] = "createTypeAliasDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | str"
    type_parameters: Sequence["TypeParameter"] | Undefined = undefined
    type: "TypeNode"


class EnumDeclaration(Node):
    """
    Represents an enum declaration: enum Name { }.

    TypeScript: ts.factory.createEnumDeclaration(modifiers?, name, members)
    """

    factory_name: ClassVar[str] = "createEnumDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | str"
    members: Sequence[Node]  # EnumMember


class ModuleDeclaration(Node):
    """
    Represents a module/namespace declaration.

    TypeScript: ts.factory.createModuleDeclaration(modifiers?, name, body?,
    flags?)
    """

    factory_name: ClassVar[str] = "createModuleDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    name: "Identifier | Node | str"  # ModuleName
    body: Node | Undefined = undefined  # ModuleBody
    flags: int = 0


# ============================================================================
# Import/Export Declarations
# ============================================================================


class ImportDeclaration(Node):
    """
    Represents an import declaration: import { x } from 'module'.

    TypeScript: ts.factory.createImportDeclaration(
        modifiers?, importClause?, moduleSpecifier, attributes?
    )
    """

    factory_name: ClassVar[str] = "createImportDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    import_clause: "ImportClause | Undefined" = undefined
    module_specifier: "Expression"
    attributes: Node | Undefined = undefined  # ImportAttributes


class ImportClause(Node):
    """
    Represents an import clause: default, { named }.

    TypeScript: ts.factory.createImportClause(isTypeOnly, name?,
      namedBindings?)
    """

    factory_name: ClassVar[str] = "createImportClause"

    is_type_only: bool = False
    name: "Identifier | Undefined" = undefined
    named_bindings: "NamespaceImport | NamedImports | Undefined" = undefined


class NamespaceImport(Node):
    """
    Represents a namespace import: * as name.

    TypeScript: ts.factory.createNamespaceImport(name)
    """

    factory_name: ClassVar[str] = "createNamespaceImport"

    name: "Identifier"


class NamedImports(Node):
    """
    Represents named imports: { a, b, c }.

    TypeScript: ts.factory.createNamedImports(elements)
    """

    factory_name: ClassVar[str] = "createNamedImports"

    elements: Sequence["ImportSpecifier"]


class ImportSpecifier(Node):
    """
    Represents an import specifier: a or a as b.

    TypeScript: ts.factory.createImportSpecifier(isTypeOnly, propertyName?,
      name)
    """

    factory_name: ClassVar[str] = "createImportSpecifier"

    is_type_only: bool = False
    property_name: "Identifier | Undefined" = undefined
    name: "Identifier"


class ExportAssignment(Node):
    """
    Represents an export assignment: export default x or export = x.

    TypeScript: ts.factory.createExportAssignment(modifiers?, isExportEquals?,
    expression)
    """

    factory_name: ClassVar[str] = "createExportAssignment"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    is_export_equals: bool = False
    expression: "Expression"


class ExportDeclaration(Node):
    """
    Represents an export declaration: export { x } from 'module'.

    TypeScript: ts.factory.createExportDeclaration(
        modifiers?, isTypeOnly, exportClause?, moduleSpecifier?, attributes?
    )
    """

    factory_name: ClassVar[str] = "createExportDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    is_type_only: bool = False
    export_clause: "NamedExports | Node | Undefined" = undefined
    module_specifier: "Expression | Undefined" = undefined
    attributes: Node | Undefined = undefined


class NamedExports(Node):
    """
    Represents named exports: { a, b, c }.

    TypeScript: ts.factory.createNamedExports(elements)
    """

    factory_name: ClassVar[str] = "createNamedExports"

    elements: Sequence["ExportSpecifier"]


class ExportSpecifier(Node):
    """
    Represents an export specifier: a or a as b.

    TypeScript: ts.factory.createExportSpecifier(isTypeOnly, propertyName?,
    name)
    """

    factory_name: ClassVar[str] = "createExportSpecifier"

    is_type_only: bool = False
    property_name: "Identifier | Node | str | Undefined" = undefined
    name: "Identifier | str"


class EnumMember(Node):
    """
    Represents an enum member: Name = value.

    TypeScript: ts.factory.createEnumMember(name, initializer?)
    """

    factory_name: ClassVar[str] = "createEnumMember"

    name: "Identifier | str | Node"  # PropertyName
    initializer: "Expression | Undefined" = undefined


class NamespaceExportDeclaration(Node):
    """
    Represents a namespace export declaration: export as namespace Name.

    TypeScript: ts.factory.createNamespaceExportDeclaration(name)
    """

    factory_name: ClassVar[str] = "createNamespaceExportDeclaration"

    name: "Identifier | str"


class NamespaceExport(Node):
    """
    Represents a namespace export: * as name.

    TypeScript: ts.factory.createNamespaceExport(name)
    """

    factory_name: ClassVar[str] = "createNamespaceExport"

    name: "Identifier"


class ImportEqualsDeclaration(Node):
    """
    Represents an import equals declaration: import x = require('module').

    TypeScript: ts.factory.createImportEqualsDeclaration(
        modifiers?, isTypeOnly, name, moduleReference
    )
    """

    factory_name: ClassVar[str] = "createImportEqualsDeclaration"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    is_type_only: bool = False
    name: "Identifier"
    module_reference: Node  # ModuleReference


class ExternalModuleReference(Node):
    """
    Represents an external module reference: require('module').

    TypeScript: ts.factory.createExternalModuleReference(expression)
    """

    factory_name: ClassVar[str] = "createExternalModuleReference"

    expression: "Expression"

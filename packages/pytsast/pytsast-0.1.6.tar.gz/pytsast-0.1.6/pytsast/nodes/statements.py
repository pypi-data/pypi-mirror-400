"""
Statement AST nodes.
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
    from pytsast.nodes.declarations import VariableDeclarationList
    from pytsast.nodes.misc import CaseBlock, CatchClause


class Block(Node):
    """
    Represents a block statement: { statements }.

    TypeScript: ts.factory.createBlock(statements, multiLine?)
    """

    factory_name: ClassVar[str] = "createBlock"

    statements: Sequence[Node]
    multi_line: bool = True


class EmptyStatement(Node):
    """
    Represents an empty statement: ;

    TypeScript: ts.factory.createEmptyStatement()
    """

    factory_name: ClassVar[str] = "createEmptyStatement"

    def _get_ordered_args(self):
        return ()


class VariableStatement(Node):
    """
    Represents a variable statement: const x = 1;

    TypeScript: ts.factory.createVariableStatement(modifiers?, declarationList)
    """

    factory_name: ClassVar[str] = "createVariableStatement"

    modifiers: Sequence[Modifier | Decorator] | Undefined = undefined
    declaration_list: "VariableDeclarationList"


class ExpressionStatement(Node):
    """
    Represents an expression statement: expression;

    TypeScript: ts.factory.createExpressionStatement(expression)
    """

    factory_name: ClassVar[str] = "createExpressionStatement"

    expression: "Expression"


class IfStatement(Node):
    """
    Represents an if statement: if (condition) then else.

    TypeScript: ts.factory.createIfStatement(expression, thenStatement,
      elseStatement?)
    """

    factory_name: ClassVar[str] = "createIfStatement"

    expression: "Expression"
    then_statement: Node  # Statement
    else_statement: Node | Undefined = undefined


class DoStatement(Node):
    """
    Represents a do-while statement: do { } while (condition);

    TypeScript: ts.factory.createDoStatement(statement, expression)
    """

    factory_name: ClassVar[str] = "createDoStatement"

    statement: Node
    expression: "Expression"


class WhileStatement(Node):
    """
    Represents a while statement: while (condition) { }.

    TypeScript: ts.factory.createWhileStatement(expression, statement)
    """

    factory_name: ClassVar[str] = "createWhileStatement"

    expression: "Expression"
    statement: Node


class ForStatement(Node):
    """
    Represents a for statement: for (init; condition; increment) { }.

    TypeScript: ts.factory.createForStatement(initializer?, condition?,
    incrementor?, statement)
    """

    factory_name: ClassVar[str] = "createForStatement"

    initializer: "VariableDeclarationList | Expression | Undefined" = (
        undefined  # noqa: E501
    )
    condition: "Expression | Undefined" = undefined
    incrementor: "Expression | Undefined" = undefined
    statement: Node


class ForInStatement(Node):
    """
    Represents a for-in statement: for (x in obj) { }.

    TypeScript: ts.factory.createForInStatement(initializer, expression,
      statement)
    """

    factory_name: ClassVar[str] = "createForInStatement"

    initializer: "VariableDeclarationList | Expression"
    expression: "Expression"
    statement: Node


class ForOfStatement(Node):
    """
    Represents a for-of statement: for (x of iterable) { }.

    TypeScript: ts.factory.createForOfStatement(awaitModifier?, initializer,
      expression, statement)
    """

    factory_name: ClassVar[str] = "createForOfStatement"

    await_modifier: Node | Undefined = undefined
    initializer: "VariableDeclarationList | Expression"
    expression: "Expression"
    statement: Node


class ContinueStatement(Node):
    """
    Represents a continue statement: continue; or continue label;

    TypeScript: ts.factory.createContinueStatement(label?)
    """

    factory_name: ClassVar[str] = "createContinueStatement"

    label: "Identifier | str | Undefined" = undefined


class BreakStatement(Node):
    """
    Represents a break statement: break; or break label;

    TypeScript: ts.factory.createBreakStatement(label?)
    """

    factory_name: ClassVar[str] = "createBreakStatement"

    label: "Identifier | str | Undefined" = undefined


class ReturnStatement(Node):
    """
    Represents a return statement: return expression;

    TypeScript: ts.factory.createReturnStatement(expression?)
    """

    factory_name: ClassVar[str] = "createReturnStatement"

    expression: "Expression | Undefined" = undefined


class WithStatement(Node):
    """
    Represents a with statement: with (expression) { }.

    TypeScript: ts.factory.createWithStatement(expression, statement)
    """

    factory_name: ClassVar[str] = "createWithStatement"

    expression: "Expression"
    statement: Node


class SwitchStatement(Node):
    """
    Represents a switch statement: switch (expression) { cases }.

    TypeScript: ts.factory.createSwitchStatement(expression, caseBlock)
    """

    factory_name: ClassVar[str] = "createSwitchStatement"

    expression: "Expression"
    case_block: "CaseBlock"


class LabeledStatement(Node):
    """
    Represents a labeled statement: label: statement.

    TypeScript: ts.factory.createLabeledStatement(label, statement)
    """

    factory_name: ClassVar[str] = "createLabeledStatement"

    label: "Identifier | str"
    statement: Node


class ThrowStatement(Node):
    """
    Represents a throw statement: throw expression;

    TypeScript: ts.factory.createThrowStatement(expression)
    """

    factory_name: ClassVar[str] = "createThrowStatement"

    expression: "Expression"


class TryStatement(Node):
    """
    Represents a try statement: try { } catch { } finally { }.

    TypeScript: ts.factory.createTryStatement(tryBlock, catchClause?,
      finallyBlock?)
    """

    factory_name: ClassVar[str] = "createTryStatement"

    try_block: Block
    catch_clause: "CatchClause | Undefined" = undefined
    finally_block: Block | Undefined = undefined


class DebuggerStatement(Node):
    """
    Represents a debugger statement: debugger;

    TypeScript: ts.factory.createDebuggerStatement()
    """

    factory_name: ClassVar[str] = "createDebuggerStatement"

    def _get_ordered_args(self):
        return ()

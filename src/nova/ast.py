from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SourceSpan:
    filename: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int


class Node:
    span: SourceSpan


class Expression(Node):
    pass


class Statement(Node):
    pass


# =========================
# Expressions
# =========================

@dataclass
class Literal(Expression):
    value: Any
    span: SourceSpan


@dataclass
class Identifier(Expression):
    name: str
    span: SourceSpan


@dataclass
class Unary(Expression):
    operator: Any
    operand: Expression
    span: SourceSpan


@dataclass
class Binary(Expression):
    left: Expression
    operator: Any
    right: Expression
    span: SourceSpan


@dataclass
class Assignment(Expression):
    name: str
    value: Expression
    span: SourceSpan


@dataclass
class Call(Expression):
    callee: Expression
    arguments: list[Expression]
    span: SourceSpan


@dataclass
class Index(Expression):
    collection: Expression
    index: Expression
    span: SourceSpan


@dataclass
class ArrayLiteral(Expression):
    elements: list[Expression]
    span: SourceSpan


@dataclass
class FunctionExpression(Expression):
    parameters: list[str]
    body: Block
    span: SourceSpan


# =========================
# Statements
# =========================

@dataclass
class ExpressionStatement(Statement):
    expression: Expression
    span: SourceSpan


@dataclass
class LetStatement(Statement):
    name: str
    initializer: Expression | None
    span: SourceSpan


@dataclass
class Block(Statement):
    statements: list[Statement]
    span: SourceSpan


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: Block
    else_branch: Statement | None
    span: SourceSpan


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: Block
    span: SourceSpan


@dataclass
class FunctionDeclaration(Statement):
    name: str
    parameters: list[str]
    body: Block
    span: SourceSpan


@dataclass
class ReturnStatement(Statement):
    value: Expression | None
    span: SourceSpan


@dataclass
class Program(Node):
    declarations: list[Statement]
    span: SourceSpan

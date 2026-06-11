from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Define la estructura basica del AST usado por el compilador.
# Cada clase representa una pieza del programa: variables, expresiones, bloques y funciones.


class Node:
    pass


@dataclass
class Program(Node):
    statements: list[Node]


@dataclass
class Block(Node):
    statements: list[Node]


@dataclass
class VarDecl(Node):
    name: str
    expr: Node


@dataclass
class Assignment(Node):
    name: str
    expr: Node


@dataclass
class PrintStmt(Node):
    args: list[Node]


@dataclass
class IfStmt(Node):
    condition: Node
    then_block: Block
    elifs: list[tuple[Node, Block]]
    else_block: Block | None


@dataclass
class WhileStmt(Node):
    condition: Node
    body: Block


@dataclass
class ForStmt(Node):
    var_name: str
    iterable: Node
    body: Block


@dataclass
class FunctionDecl(Node):
    name: str
    params: list[str]
    body: Block


@dataclass
class ReturnStmt(Node):
    expr: Node


@dataclass
class ExprStmt(Node):
    expr: Node


@dataclass
class BinaryOp(Node):
    left: Node
    op: str
    right: Node


@dataclass
class UnaryOp(Node):
    op: str
    expr: Node


@dataclass
class Literal(Node):
    value: Any


@dataclass
class Variable(Node):
    name: str


@dataclass
class FunctionCall(Node):
    name: str
    args: list[Node]


@dataclass
class InputCall(Node):
    prompt_args: list[Node]


@dataclass
class ListLiteral(Node):
    items: list[Node]

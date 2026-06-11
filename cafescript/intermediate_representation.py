from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ast_nodes import (
    Assignment,
    BinaryOp,
    Block,
    ExprStmt,
    ForStmt,
    FunctionCall,
    FunctionDecl,
    IfStmt,
    InputCall,
    ListLiteral,
    Literal,
    PrintStmt,
    Program,
    ReturnStmt,
    UnaryOp,
    VarDecl,
    Variable,
    WhileStmt,
)


@dataclass
class IRInstruction:
    op: str
    args: tuple[Any, ...]

    def __str__(self) -> str:
        op = self.op
        a = self.args
        if op == "label":
            return f"{a[0]}:"
        if op == "assign":
            return f"{a[0]} = {a[1]}"
        if op == "const":
            return f"{a[0]} = {a[1]!r}"
        if op == "binop":
            return f"{a[0]} = {a[1]} {a[2]} {a[3]}"
        if op == "unary":
            return f"{a[0]} = {a[1]} {a[2]}"
        if op == "jump":
            return f"JUMP {a[0]}"
        if op == "jump_if_false":
            return f"JUMP_IF_FALSE {a[0]} {a[1]}"
        if op == "print":
            return "PRINT " + ", ".join(map(str, a[0]))
        if op == "input":
            return f"{a[0]} = INPUT {list(a[1])}"
        if op == "call":
            return f"{a[0]} = CALL {a[1]}({', '.join(map(str, a[2]))})"
        if op == "function":
            return f"FUNCTION {a[0]}({', '.join(a[1])})"
        if op == "end_function":
            return f"END_FUNCTION {a[0]}"
        if op == "return":
            return f"RETURN {a[0]}"
        if op == "iter_start":
            return f"{a[0]} = ITER_START {a[1]}"
        if op == "iter_next":
            return f"{a[0]} = ITER_NEXT {a[1]} -> {a[2]}"
        if op == "list":
            return f"{a[0]} = LIST {list(a[1])}"
        return f"{op.upper()} {a}"


class IRGenerator:
    def __init__(self) -> None:
        self.instructions: list[IRInstruction] = []
        self.temp_count = 0
        self.label_count = 0

    def generate(self, program: Program) -> list[IRInstruction]:
        self.instructions = []
        for statement in program.statements:
            self._gen_statement(statement)
        return self.instructions

    def _temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def _label(self, prefix: str) -> str:
        self.label_count += 1
        return f"{prefix}_{self.label_count}"

    def _emit(self, op: str, *args: Any) -> None:
        self.instructions.append(IRInstruction(op, args))

    def _gen_statement(self, node: object) -> None:
        if isinstance(node, VarDecl):
            value = self._gen_expr(node.expr)
            self._emit("assign", node.name, value)
        elif isinstance(node, Assignment):
            value = self._gen_expr(node.expr)
            self._emit("assign", node.name, value)
        elif isinstance(node, PrintStmt):
            values = [self._gen_expr(arg) for arg in node.args]
            self._emit("print", tuple(values))
        elif isinstance(node, IfStmt):
            self._gen_if(node)
        elif isinstance(node, WhileStmt):
            self._gen_while(node)
        elif isinstance(node, ForStmt):
            self._gen_for(node)
        elif isinstance(node, FunctionDecl):
            self._emit("function", node.name, tuple(node.params))
            self._gen_block(node.body)
            self._emit("return", None)
            self._emit("end_function", node.name)
        elif isinstance(node, ReturnStmt):
            self._emit("return", self._gen_expr(node.expr))
        elif isinstance(node, ExprStmt):
            self._gen_expr(node.expr)
        else:
            raise TypeError(f"Statement IR no soportado: {type(node).__name__}")

    def _gen_block(self, block: Block) -> None:
        for statement in block.statements:
            self._gen_statement(statement)

    def _gen_if(self, node: IfStmt) -> None:
        end_label = self._label("if_end")
        next_label = self._label("if_next")
        condition = self._gen_expr(node.condition)
        self._emit("jump_if_false", condition, next_label)
        self._gen_block(node.then_block)
        self._emit("jump", end_label)
        self._emit("label", next_label)

        for condition_node, block in node.elifs:
            next_label = self._label("if_next")
            condition = self._gen_expr(condition_node)
            self._emit("jump_if_false", condition, next_label)
            self._gen_block(block)
            self._emit("jump", end_label)
            self._emit("label", next_label)

        if node.else_block:
            self._gen_block(node.else_block)
        self._emit("label", end_label)

    def _gen_while(self, node: WhileStmt) -> None:
        start_label = self._label("while_start")
        end_label = self._label("while_end")
        self._emit("label", start_label)
        condition = self._gen_expr(node.condition)
        self._emit("jump_if_false", condition, end_label)
        self._gen_block(node.body)
        self._emit("jump", start_label)
        self._emit("label", end_label)

    def _gen_for(self, node: ForStmt) -> None:
        iterator = self._temp()
        has_next = self._temp()
        start_label = self._label("for_start")
        end_label = self._label("for_end")
        iterable = self._gen_expr(node.iterable)
        self._emit("iter_start", iterator, iterable)
        self._emit("label", start_label)
        self._emit("iter_next", has_next, iterator, node.var_name)
        self._emit("jump_if_false", has_next, end_label)
        self._gen_block(node.body)
        self._emit("jump", start_label)
        self._emit("label", end_label)

    def _gen_expr(self, node: object) -> str:
        if isinstance(node, Literal):
            temp = self._temp()
            self._emit("const", temp, node.value)
            return temp
        if isinstance(node, Variable):
            return node.name
        if isinstance(node, ListLiteral):
            items = tuple(self._gen_expr(item) for item in node.items)
            temp = self._temp()
            self._emit("list", temp, items)
            return temp
        if isinstance(node, BinaryOp):
            left = self._gen_expr(node.left)
            right = self._gen_expr(node.right)
            temp = self._temp()
            self._emit("binop", temp, left, node.op, right)
            return temp
        if isinstance(node, UnaryOp):
            value = self._gen_expr(node.expr)
            temp = self._temp()
            self._emit("unary", temp, node.op, value)
            return temp
        if isinstance(node, FunctionCall):
            args = tuple(self._gen_expr(arg) for arg in node.args)
            temp = self._temp()
            self._emit("call", temp, node.name, args)
            return temp
        if isinstance(node, InputCall):
            args = tuple(self._gen_expr(arg) for arg in node.prompt_args)
            temp = self._temp()
            self._emit("input", temp, args)
            return temp
        raise TypeError(f"Expresion IR no soportada: {type(node).__name__}")

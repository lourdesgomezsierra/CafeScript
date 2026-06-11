from __future__ import annotations

import json
from dataclasses import dataclass, field
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
class CodeInstruction:
    op: str
    args: tuple[Any, ...] = ()
    body: list["CodeInstruction"] = field(default_factory=list)
    elif_blocks: list[tuple[Any, str, list["CodeInstruction"]]] = field(default_factory=list)
    else_body: list["CodeInstruction"] = field(default_factory=list)


class CodeGenerator:
    def generate(self, program: Program) -> list[CodeInstruction]:
        return self._generate_statements(program.statements)

    def format_code(self, instructions: list[CodeInstruction]) -> str:
        return "\n".join(self._format_instruction(instruction, 0) for instruction in instructions)

    def _generate_statements(self, statements: list[object]) -> list[CodeInstruction]:
        return [self._generate_statement(statement) for statement in statements]

    def _generate_statement(self, node: object) -> CodeInstruction:
        if isinstance(node, VarDecl):
            return CodeInstruction("DECLARE", (node.name, node.expr, self._expr_to_code(node.expr)))
        if isinstance(node, Assignment):
            return CodeInstruction("SET", (node.name, node.expr, self._expr_to_code(node.expr)))
        if isinstance(node, PrintStmt):
            return CodeInstruction("PRINT", (tuple(node.args), tuple(self._expr_to_code(arg) for arg in node.args)))
        if isinstance(node, IfStmt):
            return CodeInstruction(
                "IF",
                (node.condition, self._expr_to_code(node.condition)),
                body=self._generate_block(node.then_block),
                elif_blocks=[
                    (condition, self._expr_to_code(condition), self._generate_block(block))
                    for condition, block in node.elifs
                ],
                else_body=self._generate_block(node.else_block) if node.else_block else [],
            )
        if isinstance(node, WhileStmt):
            return CodeInstruction(
                "WHILE",
                (node.condition, self._expr_to_code(node.condition)),
                body=self._generate_block(node.body),
            )
        if isinstance(node, ForStmt):
            return CodeInstruction(
                "FOR",
                (node.var_name, node.iterable, self._expr_to_code(node.iterable)),
                body=self._generate_block(node.body),
            )
        if isinstance(node, FunctionDecl):
            return CodeInstruction(
                "FUNCTION",
                (node.name, tuple(node.params)),
                body=self._generate_block(node.body),
            )
        if isinstance(node, ReturnStmt):
            return CodeInstruction("RETURN", (node.expr, self._expr_to_code(node.expr)))
        if isinstance(node, ExprStmt):
            return CodeInstruction("EXPR", (node.expr, self._expr_to_code(node.expr)))
        raise TypeError(f"Sentencia no soportada para generacion de codigo: {type(node).__name__}")

    def _generate_block(self, block: Block | None) -> list[CodeInstruction]:
        if block is None:
            return []
        return self._generate_statements(block.statements)

    def _format_instruction(self, instruction: CodeInstruction, indent: int) -> str:
        pad = "    " * indent
        op = instruction.op
        args = instruction.args
        if op == "DECLARE":
            return f"{pad}DECLARE {args[0]} {args[2]}"
        if op == "SET":
            return f"{pad}SET {args[0]} {args[2]}"
        if op == "PRINT":
            return f"{pad}PRINT {' '.join(args[1])}"
        if op == "RETURN":
            return f"{pad}RETURN {args[1]}"
        if op == "EXPR":
            return f"{pad}EXPR {args[1]}"
        if op == "FUNCTION":
            lines = [f"{pad}FUNCTION {args[0]}({', '.join(args[1])})"]
            lines.extend(self._format_instruction(item, indent + 1) for item in instruction.body)
            lines.append(f"{pad}END_FUNCTION")
            return "\n".join(lines)
        if op == "IF":
            lines = [f"{pad}IF {args[1]}"]
            lines.extend(self._format_instruction(item, indent + 1) for item in instruction.body)
            for _condition, condition_code, body in instruction.elif_blocks:
                lines.append(f"{pad}ELIF {condition_code}")
                lines.extend(self._format_instruction(item, indent + 1) for item in body)
            if instruction.else_body:
                lines.append(f"{pad}ELSE")
                lines.extend(self._format_instruction(item, indent + 1) for item in instruction.else_body)
            lines.append(f"{pad}END_IF")
            return "\n".join(lines)
        if op == "WHILE":
            lines = [f"{pad}WHILE {args[1]}"]
            lines.extend(self._format_instruction(item, indent + 1) for item in instruction.body)
            lines.append(f"{pad}END_WHILE")
            return "\n".join(lines)
        if op == "FOR":
            lines = [f"{pad}FOR {args[0]} IN {args[2]}"]
            lines.extend(self._format_instruction(item, indent + 1) for item in instruction.body)
            lines.append(f"{pad}END_FOR")
            return "\n".join(lines)
        raise TypeError(f"Instruccion no soportada: {op}")

    def _expr_to_code(self, node: object) -> str:
        if isinstance(node, Literal):
            if isinstance(node.value, str):
                return json.dumps(node.value, ensure_ascii=False)
            if isinstance(node.value, bool):
                return "Disponible" if node.value else "Agotado"
            return str(node.value)
        if isinstance(node, Variable):
            return node.name
        if isinstance(node, BinaryOp):
            return f"{self._expr_to_code(node.left)} {node.op} {self._expr_to_code(node.right)}"
        if isinstance(node, UnaryOp):
            return f"{node.op} {self._expr_to_code(node.expr)}"
        if isinstance(node, FunctionCall):
            args = ", ".join(self._expr_to_code(arg) for arg in node.args)
            return f"{node.name}({args})"
        if isinstance(node, InputCall):
            args = ", ".join(self._expr_to_code(arg) for arg in node.prompt_args)
            return f"TomarPedido({args})"
        if isinstance(node, ListLiteral):
            return "[" + ", ".join(self._expr_to_code(item) for item in node.items) + "]"
        raise TypeError(f"Expresion no soportada para generacion de codigo: {type(node).__name__}")

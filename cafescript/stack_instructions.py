from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from intermediate_representation import IRInstruction


@dataclass
class Instruction:
    op: str
    args: tuple[Any, ...] = ()

    def __str__(self) -> str:
        return self.op if not self.args else f"{self.op} {' '.join(map(str, self.args))}"


class StackCodeGenerator:
    BINOPS = {
        "+": "ADD",
        "-": "SUB",
        "*": "MUL",
        "/": "DIV",
        ">": "GT",
        "<": "LT",
        ">=": "GTE",
        "<=": "LTE",
        "==": "EQ",
        "!=": "NEQ",
        "and": "AND",
        "or": "OR",
    }

    def generate(self, ir: list[IRInstruction]) -> list[Instruction]:
        code: list[Instruction] = []
        for inst in ir:
            op = inst.op
            args = inst.args
            if op == "const":
                code.append(Instruction("PUSH", (args[1],)))
                code.append(Instruction("STORE", (args[0],)))
            elif op == "assign":
                self._load_value(code, args[1])
                code.append(Instruction("STORE", (args[0],)))
            elif op == "binop":
                target, left, oper, right = args
                self._load_value(code, left)
                self._load_value(code, right)
                code.append(Instruction(self.BINOPS[oper]))
                code.append(Instruction("STORE", (target,)))
            elif op == "unary":
                target, oper, value = args
                self._load_value(code, value)
                code.append(Instruction("NOT" if oper == "not" else "NEG"))
                code.append(Instruction("STORE", (target,)))
            elif op == "label":
                code.append(Instruction("LABEL", (args[0],)))
            elif op == "jump":
                code.append(Instruction("JUMP", (args[0],)))
            elif op == "jump_if_false":
                self._load_value(code, args[0])
                code.append(Instruction("JUMP_IF_FALSE", (args[1],)))
            elif op == "print":
                for value in args[0]:
                    self._load_value(code, value)
                code.append(Instruction("PRINT", (len(args[0]),)))
            elif op == "input":
                target, prompt_values = args
                for value in prompt_values:
                    self._load_value(code, value)
                code.append(Instruction("INPUT", (len(prompt_values),)))
                code.append(Instruction("STORE", (target,)))
            elif op == "call":
                target, name, call_args = args
                for value in call_args:
                    self._load_value(code, value)
                code.append(Instruction("CALL", (name, len(call_args))))
                code.append(Instruction("STORE", (target,)))
            elif op == "function":
                code.append(Instruction("FUNCTION", (args[0], tuple(args[1]))))
            elif op == "end_function":
                code.append(Instruction("END_FUNCTION", (args[0],)))
            elif op == "return":
                if args[0] is None:
                    code.append(Instruction("PUSH", (None,)))
                else:
                    self._load_value(code, args[0])
                code.append(Instruction("RETURN"))
            elif op == "list":
                target, items = args
                for value in items:
                    self._load_value(code, value)
                code.append(Instruction("BUILD_LIST", (len(items),)))
                code.append(Instruction("STORE", (target,)))
            elif op == "iter_start":
                target, iterable = args
                self._load_value(code, iterable)
                code.append(Instruction("ITER_START"))
                code.append(Instruction("STORE", (target,)))
            elif op == "iter_next":
                has_next, iterator, item_var = args
                code.append(Instruction("LOAD", (iterator,)))
                code.append(Instruction("ITER_NEXT", (item_var,)))
                code.append(Instruction("STORE", (has_next,)))
            else:
                raise ValueError(f"IR no soportada para stack machine: {op}")
        return code

    def _load_value(self, code: list[Instruction], value: Any) -> None:
        if isinstance(value, str):
            code.append(Instruction("LOAD", (value,)))
        else:
            code.append(Instruction("PUSH", (value,)))

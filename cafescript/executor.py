from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ast_nodes import BinaryOp, FunctionCall, InputCall, ListLiteral, Literal, UnaryOp, Variable
from code_generator import CodeInstruction


class ExecutionError(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


@dataclass
class FunctionDef:
    params: tuple[str, ...]
    body: list[CodeInstruction]


class Executor:
    def __init__(
        self,
        instructions: list[CodeInstruction],
        input_func: Callable[[str], str] = input,
        output_func: Callable[..., None] = print,
    ) -> None:
        self.instructions = instructions
        self.input_func = input_func
        self.output_func = output_func
        self.globals: dict[str, Any] = {}
        self.frames: list[dict[str, Any]] = []
        self.functions: dict[str, FunctionDef] = {}

    def execute(self) -> None:
        for instruction in self.instructions:
            if instruction.op == "FUNCTION":
                name, params = instruction.args
                self.functions[name] = FunctionDef(params, instruction.body)
        self._execute_block(self.instructions)

    @property
    def env(self) -> dict[str, Any]:
        return self.frames[-1] if self.frames else self.globals

    def _execute_block(self, instructions: list[CodeInstruction]) -> None:
        for instruction in instructions:
            self._execute_instruction(instruction)

    def _execute_instruction(self, instruction: CodeInstruction) -> None:
        op = instruction.op
        args = instruction.args
        if op == "DECLARE":
            name, expr, _expr_code = args
            self.env[name] = self._eval(expr)
        elif op == "SET":
            name, expr, _expr_code = args
            self._assign(name, self._eval(expr))
        elif op == "PRINT":
            exprs, _expr_codes = args
            self.output_func(*(self._eval(expr) for expr in exprs))
        elif op == "IF":
            condition, _condition_code = args
            if self._eval(condition):
                self._execute_block(instruction.body)
                return
            for elif_condition, _elif_code, elif_body in instruction.elif_blocks:
                if self._eval(elif_condition):
                    self._execute_block(elif_body)
                    return
            self._execute_block(instruction.else_body)
        elif op == "WHILE":
            condition, _condition_code = args
            while self._eval(condition):
                self._execute_block(instruction.body)
        elif op == "FOR":
            var_name, iterable_expr, _iterable_code = args
            for value in self._eval(iterable_expr):
                self.env[var_name] = value
                self._execute_block(instruction.body)
        elif op == "FUNCTION":
            name, params = args
            self.functions[name] = FunctionDef(params, instruction.body)
        elif op == "RETURN":
            expr, _expr_code = args
            raise ReturnSignal(self._eval(expr))
        elif op == "EXPR":
            expr, _expr_code = args
            self._eval(expr)
        else:
            raise ExecutionError(f"Instruccion no soportada: {op}")

    def _eval(self, node: object) -> Any:
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, Variable):
            return self._lookup(node.name)
        if isinstance(node, ListLiteral):
            return [self._eval(item) for item in node.items]
        if isinstance(node, UnaryOp):
            value = self._eval(node.expr)
            if node.op == "not":
                return not value
            if node.op == "-":
                return -value
            raise ExecutionError(f"Operador unario no soportado: {node.op}")
        if isinstance(node, BinaryOp):
            left = self._eval(node.left)
            right = self._eval(node.right)
            return self._eval_binary(left, node.op, right)
        if isinstance(node, FunctionCall):
            return self._call_function(node)
        if isinstance(node, InputCall):
            prompt = " ".join(str(self._eval(arg)) for arg in node.prompt_args)
            raw_value = self.input_func(prompt)
            return self._coerce_input_value(raw_value)
        raise ExecutionError(f"Expresion no soportada: {type(node).__name__}")

    def _coerce_input_value(self, value: Any) -> Any:
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("+") or text.startswith("-"):
                candidate = text[1:] if text.startswith("+") else text
                if candidate.isdigit():
                    return int(text)
            if text.isdigit():
                return int(text)
            try:
                return float(text)
            except ValueError:
                return text
        return value

    def _eval_binary(self, left: Any, op: str, right: Any) -> Any:
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == ">":
            return left > right
        if op == "<":
            return left < right
        if op == ">=":
            return left >= right
        if op == "<=":
            return left <= right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "and":
            return bool(left) and bool(right)
        if op == "or":
            return bool(left) or bool(right)
        raise ExecutionError(f"Operador binario no soportado: {op}")

    def _call_function(self, node: FunctionCall) -> Any:
        if node.name not in self.functions:
            raise ExecutionError(f"Funcion '{node.name}' no definida.")
        function = self.functions[node.name]
        values = [self._eval(arg) for arg in node.args]
        local_env = dict(zip(function.params, values))
        self.frames.append(local_env)
        try:
            self._execute_block(function.body)
        except ReturnSignal as signal:
            return signal.value
        finally:
            self.frames.pop()
        return None

    def _lookup(self, name: str) -> Any:
        if self.frames and name in self.frames[-1]:
            return self.frames[-1][name]
        if name in self.globals:
            return self.globals[name]
        raise ExecutionError(f"Variable '{name}' no definida en ejecucion.")

    def _assign(self, name: str, value: Any) -> None:
        if self.frames and name in self.frames[-1]:
            self.frames[-1][name] = value
            return
        if name in self.globals:
            self.globals[name] = value
            return
        raise ExecutionError(f"Variable '{name}' no definida en ejecucion.")

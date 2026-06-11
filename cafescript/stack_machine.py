from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from stack_instructions import Instruction


class StackMachineError(Exception):
    pass


@dataclass
class Frame:
    return_ip: int
    locals: dict[str, Any]


class StackMachine:
    def __init__(
        self,
        instructions: list[Instruction],
        input_func: Callable[[str], str] = input,
        output_func: Callable[..., None] = print,
    ) -> None:
        self.instructions = instructions
        self.input_func = input_func
        self.output_func = output_func
        self.stack: list[Any] = []
        self.globals: dict[str, Any] = {}
        self.frames: list[Frame] = []
        self.labels: dict[str, int] = {}
        self.functions: dict[str, tuple[int, tuple[str, ...]]] = {}
        self.ip = 0
        self._index_code()

    def run(self) -> None:
        while self.ip < len(self.instructions):
            inst = self.instructions[self.ip]
            self.ip += 1
            self._execute(inst)

    @property
    def env(self) -> dict[str, Any]:
        return self.frames[-1].locals if self.frames else self.globals

    def _index_code(self) -> None:
        depth = 0
        for index, inst in enumerate(self.instructions):
            if inst.op == "LABEL":
                self.labels[inst.args[0]] = index
            elif inst.op == "FUNCTION":
                name, params = inst.args
                self.functions[name] = (index + 1, params)
                depth += 1
            elif inst.op == "END_FUNCTION":
                depth = max(0, depth - 1)

    def _execute(self, inst: Instruction) -> None:
        op = inst.op
        args = inst.args
        if op in {"LABEL", "END_FUNCTION"}:
            return
        if op == "FUNCTION":
            self.ip = self._find_matching_end(self.ip - 1) + 1
            return
        if op == "PUSH":
            self.stack.append(args[0])
        elif op == "LOAD":
            self.stack.append(self._get_var(args[0]))
        elif op == "STORE":
            self.env[args[0]] = self._pop()
        elif op == "ADD":
            b, a = self._pop(), self._pop()
            self.stack.append(a + b)
        elif op == "SUB":
            b, a = self._pop(), self._pop()
            self.stack.append(a - b)
        elif op == "MUL":
            b, a = self._pop(), self._pop()
            self.stack.append(a * b)
        elif op == "DIV":
            b, a = self._pop(), self._pop()
            self.stack.append(a / b)
        elif op == "GT":
            b, a = self._pop(), self._pop()
            self.stack.append(a > b)
        elif op == "LT":
            b, a = self._pop(), self._pop()
            self.stack.append(a < b)
        elif op == "GTE":
            b, a = self._pop(), self._pop()
            self.stack.append(a >= b)
        elif op == "LTE":
            b, a = self._pop(), self._pop()
            self.stack.append(a <= b)
        elif op == "EQ":
            b, a = self._pop(), self._pop()
            self.stack.append(a == b)
        elif op == "NEQ":
            b, a = self._pop(), self._pop()
            self.stack.append(a != b)
        elif op == "AND":
            b, a = self._pop(), self._pop()
            self.stack.append(bool(a) and bool(b))
        elif op == "OR":
            b, a = self._pop(), self._pop()
            self.stack.append(bool(a) or bool(b))
        elif op == "NOT":
            self.stack.append(not self._pop())
        elif op == "NEG":
            self.stack.append(-self._pop())
        elif op == "JUMP":
            self.ip = self._label_ip(args[0])
        elif op == "JUMP_IF_FALSE":
            if not self._pop():
                self.ip = self._label_ip(args[0])
        elif op == "PRINT":
            values = [self._pop() for _ in range(args[0])]
            values.reverse()
            self.output_func(*values)
        elif op == "INPUT":
            values = [self._pop() for _ in range(args[0])]
            values.reverse()
            prompt = " ".join(str(value) for value in values)
            self.stack.append(self.input_func(prompt))
        elif op == "CALL":
            self._call(args[0], args[1])
        elif op == "RETURN":
            value = self._pop()
            if not self.frames:
                self.stack.append(value)
                self.ip = len(self.instructions)
                return
            frame = self.frames.pop()
            self.ip = frame.return_ip
            self.stack.append(value)
        elif op == "BUILD_LIST":
            values = [self._pop() for _ in range(args[0])]
            values.reverse()
            self.stack.append(values)
        elif op == "ITER_START":
            self.stack.append(iter(self._pop()))
        elif op == "ITER_NEXT":
            iterator = self._pop()
            try:
                self.env[args[0]] = next(iterator)
                self.stack.append(True)
            except StopIteration:
                self.stack.append(False)
        else:
            raise StackMachineError(f"Instruccion no soportada: {op}")

    def _call(self, name: str, arg_count: int) -> None:
        if name not in self.functions:
            raise StackMachineError(f"Funcion desconocida: {name}")
        start_ip, params = self.functions[name]
        if len(params) != arg_count:
            raise StackMachineError(f"{name} espera {len(params)} argumentos")
        values = [self._pop() for _ in range(arg_count)]
        values.reverse()
        locals_env = dict(zip(params, values))
        self.frames.append(Frame(self.ip, locals_env))
        self.ip = start_ip

    def _get_var(self, name: str) -> Any:
        if self.frames and name in self.frames[-1].locals:
            return self.frames[-1].locals[name]
        if name in self.globals:
            return self.globals[name]
        raise StackMachineError(f"Variable no definida en ejecucion: {name}")

    def _label_ip(self, label: str) -> int:
        if label not in self.labels:
            raise StackMachineError(f"Etiqueta desconocida: {label}")
        return self.labels[label]

    def _find_matching_end(self, start: int) -> int:
        depth = 0
        for index in range(start, len(self.instructions)):
            op = self.instructions[index].op
            if op == "FUNCTION":
                depth += 1
            elif op == "END_FUNCTION":
                depth -= 1
                if depth == 0:
                    return index
        raise StackMachineError("Funcion sin END_FUNCTION")

    def _pop(self) -> Any:
        if not self.stack:
            raise StackMachineError("Stack underflow")
        return self.stack.pop()

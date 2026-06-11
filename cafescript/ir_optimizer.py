from __future__ import annotations

from typing import Any

from intermediate_representation import IRInstruction


class IROptimizer:
    def optimize(self, instructions: list[IRInstruction]) -> list[IRInstruction]:
        folded = self.constant_folding(instructions)
        propagated = self.constant_propagation(folded)
        return self.dead_code_elimination(propagated)

    def constant_folding(self, instructions: list[IRInstruction]) -> list[IRInstruction]:
        constants: dict[str, Any] = {}
        result: list[IRInstruction] = []
        for inst in instructions:
            if inst.op == "const":
                constants[inst.args[0]] = inst.args[1]
                result.append(inst)
            elif inst.op == "assign":
                target, source = inst.args
                if source in constants:
                    constants[target] = constants[source]
                else:
                    constants.pop(target, None)
                result.append(inst)
            elif inst.op == "binop":
                target, left, op, right = inst.args
                if left in constants and right in constants:
                    value = self._eval_binop(constants[left], op, constants[right])
                    constants[target] = value
                    result.append(IRInstruction("const", (target, value)))
                else:
                    constants.pop(target, None)
                    result.append(inst)
            elif inst.op == "unary":
                target, op, value_name = inst.args
                if value_name in constants:
                    value = self._eval_unary(op, constants[value_name])
                    constants[target] = value
                    result.append(IRInstruction("const", (target, value)))
                else:
                    constants.pop(target, None)
                    result.append(inst)
            else:
                self._invalidate_mutations(constants, inst)
                result.append(inst)
        return result

    def constant_propagation(self, instructions: list[IRInstruction]) -> list[IRInstruction]:
        constants: dict[str, Any] = {}
        result: list[IRInstruction] = []
        for inst in instructions:
            op = inst.op
            args = inst.args
            if op == "const":
                constants[args[0]] = args[1]
                result.append(inst)
            elif op == "assign":
                target, source = args
                if source in constants:
                    constants[target] = constants[source]
                    result.append(IRInstruction("const", (target, constants[source])))
                else:
                    constants.pop(target, None)
                    result.append(inst)
            elif op == "binop":
                target, left, oper, right = args
                left = self._literal_or_name(left, constants)
                right = self._literal_or_name(right, constants)
                constants.pop(target, None)
                result.append(IRInstruction("binop", (target, left, oper, right)))
            elif op == "unary":
                target, oper, value = args
                value = self._literal_or_name(value, constants)
                constants.pop(target, None)
                result.append(IRInstruction("unary", (target, oper, value)))
            elif op in {"print", "input", "call", "list"}:
                result.append(self._replace_known_args(inst, constants))
                self._invalidate_mutations(constants, inst)
            else:
                self._invalidate_mutations(constants, inst)
                result.append(inst)
        return result

    def dead_code_elimination(self, instructions: list[IRInstruction]) -> list[IRInstruction]:
        used = self._collect_used_names(instructions)
        result: list[IRInstruction] = []
        for inst in instructions:
            if inst.op in {"const", "assign", "binop", "unary", "call", "input", "list", "iter_start"}:
                target = inst.args[0]
                if isinstance(target, str) and target.startswith("t") and target not in used:
                    continue
            result.append(inst)
        return result

    def _replace_known_args(self, inst: IRInstruction, constants: dict[str, Any]) -> IRInstruction:
        if inst.op == "print":
            return IRInstruction("print", (tuple(self._literal_or_name(v, constants) for v in inst.args[0]),))
        if inst.op == "input":
            return IRInstruction("input", (inst.args[0], tuple(self._literal_or_name(v, constants) for v in inst.args[1])))
        if inst.op == "call":
            return IRInstruction("call", (inst.args[0], inst.args[1], tuple(self._literal_or_name(v, constants) for v in inst.args[2])))
        if inst.op == "list":
            return IRInstruction("list", (inst.args[0], tuple(self._literal_or_name(v, constants) for v in inst.args[1])))
        return inst

    def _literal_or_name(self, value: Any, constants: dict[str, Any]) -> Any:
        if isinstance(value, str) and value in constants:
            constant = constants[value]
            # String literals are also Python strings, so keeping the original
            # temporary avoids confusing a literal with a variable name later.
            if isinstance(constant, str):
                return value
            return constant
        return value

    def _invalidate_mutations(self, constants: dict[str, Any], inst: IRInstruction) -> None:
        if inst.op in {"label", "jump", "jump_if_false", "function", "end_function", "return"}:
            constants.clear()
            return
        if inst.op == "print":
            return
        if inst.op in {"call", "input", "iter_start", "iter_next", "list"} and inst.args:
            constants.pop(inst.args[0], None)

    def _collect_used_names(self, instructions: list[IRInstruction]) -> set[str]:
        used: set[str] = set()
        for inst in instructions:
            if inst.op == "assign":
                self._mark_name(used, inst.args[1])
            elif inst.op == "binop":
                self._mark_name(used, inst.args[1])
                self._mark_name(used, inst.args[3])
            elif inst.op == "unary":
                self._mark_name(used, inst.args[2])
            elif inst.op == "jump_if_false":
                self._mark_name(used, inst.args[0])
            elif inst.op == "print":
                for value in inst.args[0]:
                    self._mark_name(used, value)
            elif inst.op == "input":
                for value in inst.args[1]:
                    self._mark_name(used, value)
            elif inst.op == "call":
                for value in inst.args[2]:
                    self._mark_name(used, value)
            elif inst.op == "return":
                self._mark_name(used, inst.args[0])
            elif inst.op == "iter_start":
                self._mark_name(used, inst.args[1])
            elif inst.op == "iter_next":
                self._mark_name(used, inst.args[1])
        return used

    def _mark_name(self, used: set[str], value: Any) -> None:
        if isinstance(value, str):
            used.add(value)

    def _eval_binop(self, left: Any, op: str, right: Any) -> Any:
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
            return left and right
        if op == "or":
            return left or right
        raise ValueError(f"Operador no soportado: {op}")

    def _eval_unary(self, op: str, value: Any) -> Any:
        if op == "not":
            return not value
        if op == "-":
            return -value
        raise ValueError(f"Operador unario no soportado: {op}")

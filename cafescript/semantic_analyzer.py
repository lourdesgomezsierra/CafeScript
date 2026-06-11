from __future__ import annotations

from dataclasses import dataclass

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


class SemanticError(Exception):
    pass


@dataclass
class FunctionInfo:
    params: list[str]


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.scopes: list[set[str]] = [set()]
        self.functions: dict[str, FunctionInfo] = {}
        self.current_function: str | None = None

    def analyze(self, program: Program) -> None:
        for statement in program.statements:
            if isinstance(statement, FunctionDecl):
                self._declare_function(statement)
        self._analyze_block(program.statements)

    def _declare_function(self, node: FunctionDecl) -> None:
        if node.name in self.functions:
            raise SemanticError(f"Funcion redeclarada: {node.name}")
        if len(set(node.params)) != len(node.params):
            raise SemanticError(f"Parametros repetidos en funcion {node.name}")
        self.functions[node.name] = FunctionInfo(node.params)

    def _push_scope(self) -> None:
        self.scopes.append(set())

    def _pop_scope(self) -> None:
        self.scopes.pop()

    def _declare_var(self, name: str) -> None:
        if name in self.scopes[-1]:
            raise SemanticError(f"Variable redeclarada en el mismo ambito: {name}")
        self.scopes[-1].add(name)

    def _is_declared(self, name: str) -> bool:
        return any(name in scope for scope in reversed(self.scopes))

    def _require_var(self, name: str) -> None:
        if not self._is_declared(name):
            raise SemanticError(f"Variable no declarada: {name}")

    def _analyze_block(self, statements: list[object]) -> None:
        for statement in statements:
            self._analyze_statement(statement)

    def _analyze_statement(self, node: object) -> None:
        if isinstance(node, VarDecl):
            self._analyze_expr(node.expr)
            self._declare_var(node.name)
        elif isinstance(node, Assignment):
            self._require_var(node.name)
            self._analyze_expr(node.expr)
        elif isinstance(node, PrintStmt):
            for arg in node.args:
                self._analyze_expr(arg)
        elif isinstance(node, IfStmt):
            self._analyze_expr(node.condition)
            self._analyze_scoped_block(node.then_block)
            for condition, block in node.elifs:
                self._analyze_expr(condition)
                self._analyze_scoped_block(block)
            if node.else_block:
                self._analyze_scoped_block(node.else_block)
        elif isinstance(node, WhileStmt):
            self._analyze_expr(node.condition)
            self._analyze_scoped_block(node.body)
        elif isinstance(node, ForStmt):
            self._analyze_expr(node.iterable)
            self._push_scope()
            self._declare_var(node.var_name)
            self._analyze_block(node.body.statements)
            self._pop_scope()
        elif isinstance(node, FunctionDecl):
            previous = self.current_function
            self.current_function = node.name
            self._push_scope()
            for param in node.params:
                self._declare_var(param)
            self._analyze_block(node.body.statements)
            self._pop_scope()
            self.current_function = previous
        elif isinstance(node, ReturnStmt):
            if self.current_function is None:
                raise SemanticError("Entregar solo puede usarse dentro de una Receta")
            self._analyze_expr(node.expr)
        elif isinstance(node, ExprStmt):
            self._analyze_expr(node.expr)
        else:
            raise SemanticError(f"Nodo semantico no soportado: {type(node).__name__}")

    def _analyze_scoped_block(self, block: Block) -> None:
        self._push_scope()
        self._analyze_block(block.statements)
        self._pop_scope()

    def _analyze_expr(self, node: object) -> str:
        if isinstance(node, Literal):
            if isinstance(node.value, bool):
                return "bool"
            if isinstance(node.value, (int, float)):
                return "number"
            if isinstance(node.value, str):
                return "string"
            if isinstance(node.value, list):
                return "list"
            return "unknown"
        if isinstance(node, Variable):
            self._require_var(node.name)
            return "unknown"
        if isinstance(node, InputCall):
            for arg in node.prompt_args:
                self._analyze_expr(arg)
            return "string"
        if isinstance(node, ListLiteral):
            for item in node.items:
                self._analyze_expr(item)
            return "list"
        if isinstance(node, FunctionCall):
            if node.name not in self.functions:
                raise SemanticError(f"Funcion no declarada: {node.name}")
            expected = len(self.functions[node.name].params)
            if len(node.args) != expected:
                raise SemanticError(
                    f"Funcion {node.name} espera {expected} argumentos y recibio {len(node.args)}"
                )
            for arg in node.args:
                self._analyze_expr(arg)
            return "unknown"
        if isinstance(node, UnaryOp):
            operand_type = self._analyze_expr(node.expr)
            if node.op == "not" and operand_type not in {"bool", "unknown"}:
                raise SemanticError("'not' requiere una expresion booleana")
            if node.op == "-" and operand_type not in {"number", "unknown"}:
                raise SemanticError("'-' unario requiere una expresion numerica")
            return "bool" if node.op == "not" else "number"
        if isinstance(node, BinaryOp):
            left_type = self._analyze_expr(node.left)
            right_type = self._analyze_expr(node.right)
            if node.op in {"+", "-", "*", "/"}:
                if left_type == right_type == "string" and node.op == "+":
                    return "string"
                if left_type not in {"number", "unknown"} or right_type not in {"number", "unknown"}:
                    raise SemanticError(f"Operador {node.op} requiere operandos numericos")
                return "number"
            if node.op in {">", "<", ">=", "<=", "==", "!="}:
                return "bool"
            if node.op in {"and", "or"}:
                if left_type not in {"bool", "unknown"} or right_type not in {"bool", "unknown"}:
                    raise SemanticError(f"Operador {node.op} requiere booleanos")
                return "bool"
        raise SemanticError(f"Expresion no soportada: {type(node).__name__}")

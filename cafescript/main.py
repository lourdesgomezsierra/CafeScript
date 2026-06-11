from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lark import Lark, Token, Transformer, UnexpectedInput, v_args

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
from intermediate_representation import IRGenerator
from lexer import Lexer, LexicalError
from semantic_analyzer import SemanticAnalyzer, SemanticError


class CafeScriptTransformer(Transformer):
    def program(self, items: list[Any]) -> Program:
        return Program(items)

    def block(self, items: list[Any]) -> Block:
        return Block(items)

    def var_decl(self, items: list[Any]) -> VarDecl:
        return VarDecl(str(items[0]), items[1])

    def assignment(self, items: list[Any]) -> Assignment:
        return Assignment(str(items[0]), items[1])

    def print_stmt(self, items: list[Any]) -> PrintStmt:
        return PrintStmt(self._flatten_optional_list(items))

    def if_stmt(self, items: list[Any]) -> IfStmt:
        condition = items[0]
        then_block = items[1]
        elifs: list[tuple[Any, Block]] = []
        else_block = None
        for item in items[2:]:
            if isinstance(item, tuple) and item[0] == "elif":
                elifs.append((item[1], item[2]))
            elif isinstance(item, tuple) and item[0] == "else":
                else_block = item[1]
        return IfStmt(condition, then_block, elifs, else_block)

    def elif_clause(self, items: list[Any]) -> tuple[str, Any, Block]:
        return ("elif", items[0], items[1])

    def else_clause(self, items: list[Any]) -> tuple[str, Block]:
        return ("else", items[0])

    def while_stmt(self, items: list[Any]) -> WhileStmt:
        return WhileStmt(items[0], items[1])

    def for_stmt(self, items: list[Any]) -> ForStmt:
        return ForStmt(str(items[0]), items[1], items[2])

    def func_decl(self, items: list[Any]) -> FunctionDecl:
        name = str(items[0])
        if len(items) == 2:
            params: list[str] = []
            body = items[1]
        else:
            params = items[1]
            body = items[2]
        return FunctionDecl(name, params, body)

    def parameters(self, items: list[Any]) -> list[str]:
        return [str(item) for item in items]

    def arguments(self, items: list[Any]) -> list[Any]:
        return items

    def return_stmt(self, items: list[Any]) -> ReturnStmt:
        return ReturnStmt(items[0])

    def expr_stmt(self, items: list[Any]) -> ExprStmt:
        return ExprStmt(items[0])

    def binary_op(self, items: list[Any]) -> BinaryOp:
        return BinaryOp(items[0], str(items[1]), items[2])

    def unary_op(self, items: list[Any]) -> UnaryOp:
        return UnaryOp(str(items[0]), items[1])

    @v_args(inline=True)
    def number(self, token: Token) -> Literal:
        text = str(token)
        return Literal(float(text) if "." in text else int(text))

    @v_args(inline=True)
    def string(self, token: Token) -> Literal:
        return Literal(json.loads(str(token)))

    def true(self, _items: list[Any]) -> Literal:
        return Literal(True)

    def false(self, _items: list[Any]) -> Literal:
        return Literal(False)

    @v_args(inline=True)
    def variable(self, token: Token) -> Variable:
        return Variable(str(token))

    def func_call(self, items: list[Any]) -> FunctionCall:
        return FunctionCall(str(items[0]), self._flatten_optional_list(items[1:]))

    def input_call(self, items: list[Any]) -> InputCall:
        return InputCall(self._flatten_optional_list(items))

    def list_literal(self, items: list[Any]) -> ListLiteral:
        return ListLiteral(self._flatten_optional_list(items))

    def _flatten_optional_list(self, items: list[Any]) -> list[Any]:
        if not items:
            return []
        if len(items) == 1 and isinstance(items[0], list):
            return items[0]
        return items


def load_parser() -> Lark:
    grammar_path = Path(__file__).with_name("cafescript.lark")
    return Lark(grammar_path.read_text(encoding="utf-8"), parser="lalr", maybe_placeholders=False)


def compile_source(source: str) -> tuple[list[Any], Any, Program, list[Any]]:
    tokens = Lexer(source).tokenize()
    parser = load_parser()
    parse_tree = parser.parse(source)
    ast = CafeScriptTransformer().transform(parse_tree)
    SemanticAnalyzer().analyze(ast)
    ir = IRGenerator().generate(ast)
    return tokens, parse_tree, ast, ir


def run_file(path: Path, args: argparse.Namespace) -> None:
    source = path.read_text(encoding="utf-8")
    tokens, parse_tree, ast, ir = compile_source(source)

    if args.show_tokens:
        print("=== TOKENS ===")
        for token in tokens:
            print(token)
    if args.show_parse_tree:
        print("=== PARSE TREE ===")
        print(parse_tree.pretty())
    if args.show_ast:
        print("=== AST ===")
        print(ast)
    if args.show_ir:
        print("=== IR ===")
        for instruction in ir:
            print(instruction)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compilador educativo CafeScript")
    parser.add_argument("archivo", type=Path, help="Archivo .cafe a compilar")
    parser.add_argument("--show-tokens", action="store_true", help="Muestra tokens del lexer")
    parser.add_argument("--show-parse-tree", action="store_true", help="Muestra el parse tree de Lark")
    parser.add_argument("--show-ast", action="store_true", help="Muestra el AST")
    parser.add_argument("--show-ir", action="store_true", help="Muestra la representacion intermedia")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    try:
        run_file(args.archivo, args)
    except FileNotFoundError:
        raise SystemExit(f"Error: no existe el archivo {args.archivo}")
    except LexicalError as error:
        raise SystemExit(f"Error lexico: {error}")
    except UnexpectedInput as error:
        raise SystemExit(f"Error sintactico: {error}")
    except SemanticError as error:
        raise SystemExit(f"Error semantico: {error}")


if __name__ == "__main__":
    main()

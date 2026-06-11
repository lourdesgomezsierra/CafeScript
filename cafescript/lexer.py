from __future__ import annotations

from dataclasses import dataclass


class LexicalError(Exception):
    pass


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"TOKEN({self.type}, {self.value})"


class Lexer:
    RESERVED = {
        "Pedido": "PEDIDO",
        "Servir": "SERVIR",
        "TomarPedido": "TOMAR_PEDIDO",
        "SiHay": "SI_HAY",
        "SinoSi": "SINO_SI",
        "Sino": "SINO",
        "Disponible": "DISPONIBLE",
        "Agotado": "AGOTADO",
        "Receta": "RECETA",
        "Entregar": "ENTREGAR",
        "MientrasAbierto": "MIENTRAS_ABIERTO",
        "ParaCadaPedido": "PARA_CADA_PEDIDO",
        "en": "EN",
        "and": "AND",
        "or": "OR",
        "not": "NOT",
    }

    SINGLE_CHAR_TOKENS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "STAR",
        "/": "SLASH",
        "=": "ASSIGN",
        ">": "GT",
        "<": "LT",
        "(": "LPAREN",
        ")": "RPAREN",
        "{": "LBRACE",
        "}": "RBRACE",
        "[": "LBRACKET",
        "]": "RBRACKET",
        ",": "COMMA",
    }

    TWO_CHAR_TOKENS = {
        "==": "EQ",
        "!=": "NEQ",
        ">=": "GTE",
        "<=": "LTE",
    }

    def __init__(self, source: str) -> None:
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        while not self._at_end():
            char = self._peek()
            if char in " \t\r":
                self._advance()
            elif char == "\n":
                self._advance_line()
            elif char == "#":
                self._skip_comment()
            elif char.isalpha() or char == "_":
                self._identifier()
            elif char.isdigit():
                self._number()
            elif char == '"':
                self._string()
            else:
                self._symbol()
        return self.tokens

    def _identifier(self) -> None:
        start = self.index
        line = self.line
        column = self.column
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        value = self.source[start:self.index]
        token_type = self.RESERVED.get(value, "ID")
        self.tokens.append(Token(token_type, value, line, column))

    def _number(self) -> None:
        start = self.index
        line = self.line
        column = self.column
        while not self._at_end() and self._peek().isdigit():
            self._advance()
        self.tokens.append(Token("NUMBER", self.source[start:self.index], line, column))

    def _string(self) -> None:
        line = self.line
        column = self.column
        start = self.index
        self._advance()
        escaped = False
        while not self._at_end():
            char = self._peek()
            if char == "\n":
                raise LexicalError(f"String sin cerrar en linea {line}, columna {column}")
            if char == '"' and not escaped:
                self._advance()
                self.tokens.append(Token("STRING", self.source[start:self.index], line, column))
                return
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
            self._advance()
        raise LexicalError(f"String sin cerrar en linea {line}, columna {column}")

    def _symbol(self) -> None:
        line = self.line
        column = self.column
        two_chars = self.source[self.index : self.index + 2]
        if two_chars in self.TWO_CHAR_TOKENS:
            self.tokens.append(Token(self.TWO_CHAR_TOKENS[two_chars], two_chars, line, column))
            self._advance()
            self._advance()
            return

        char = self._peek()
        if char in self.SINGLE_CHAR_TOKENS:
            self.tokens.append(Token(self.SINGLE_CHAR_TOKENS[char], char, line, column))
            self._advance()
            return

        raise LexicalError(f"Caracter invalido {char!r} en linea {line}, columna {column}")

    def _skip_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _peek(self) -> str:
        return self.source[self.index]

    def _advance(self) -> None:
        self.index += 1
        self.column += 1

    def _advance_line(self) -> None:
        self.index += 1
        self.line += 1
        self.column = 1

    def _at_end(self) -> bool:
        return self.index >= len(self.source)

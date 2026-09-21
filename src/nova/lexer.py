from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .token import Token, TokenType, SourceLocation


@dataclass
class LexerError(Exception):
    message: str
    location: SourceLocation

    def __str__(self) -> str:
        return (
            f"LexerError at "
            f"{self.location.line}:{self.location.column}: "
            f"{self.message}"
        )


class Lexer:
    """
    Nova source-code lexer.

    Converts raw source text into a stream of Token objects.
    """

    KEYWORDS = {
        "let": TokenType.LET,
        "fn": TokenType.FN,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "return": TokenType.RETURN,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "nil": TokenType.NIL,
    }

    SINGLE_CHAR_TOKENS = {
        "(": TokenType.LEFT_PAREN,
        ")": TokenType.RIGHT_PAREN,
        "{": TokenType.LEFT_BRACE,
        "}": TokenType.RIGHT_BRACE,
        "[": TokenType.LEFT_BRACKET,
        "]": TokenType.RIGHT_BRACKET,
        ",": TokenType.COMMA,
        ";": TokenType.SEMICOLON,
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "/": TokenType.SLASH,
        "%": TokenType.PERCENT,
    }

    TWO_CHAR_TOKENS = {
        "==": TokenType.EQUAL_EQUAL,
        "!=": TokenType.NOT_EQUAL,
        "<=": TokenType.LESS_EQUAL,
        ">=": TokenType.GREATER_EQUAL,
        "&&": TokenType.AND,
        "||": TokenType.OR,
    }

    ONE_CHAR_OPERATORS = {
        "=": TokenType.EQUAL,
        "!": TokenType.BANG,
        "<": TokenType.LESS,
        ">": TokenType.GREATER,
    }

    def __init__(self, source: str, filename: str = "<source>"):
        self.source = source
        self.filename = filename

        self.start = 0
        self.current = 0

        self.line = 1
        self.column = 1

        self.token_line = 1
        self.token_column = 1

    def tokenize(self) -> list[Token]:
        """Tokenize the complete source."""
        return list(self.tokens())

    def tokens(self) -> Iterator[Token]:
        """Yield tokens until EOF."""
        while not self.is_at_end():
            self.start = self.current
            self.token_line = self.line
            self.token_column = self.column

            token = self.scan_token()

            if token.type != TokenType.EOF:
                yield token

        yield Token(
            type=TokenType.EOF,
            lexeme="",
            literal=None,
            location=self.location(),
        )

    def scan_token(self) -> Token:
        """
        Scan the next token.

        Whitespace and comments are skipped without recursion.
        Token position is reset after every skipped section.
        """

        while True:
            if self.is_at_end():
                return Token(
                    type=TokenType.EOF,
                    lexeme="",
                    literal=None,
                    location=self.location(),
                )

            char = self.advance()

            if char in " \t\r\n":
                self.start = self.current
                self.token_line = self.line
                self.token_column = self.column
                continue

            if char == "#":
                self.skip_comment()

                self.start = self.current
                self.token_line = self.line
                self.token_column = self.column
                continue

            break

        if char.isalpha() or char == "_":
            return self.identifier()

        if char.isdigit():
            return self.number()

        if char == '"':
            return self.string()

        if char in self.SINGLE_CHAR_TOKENS:
            return self.make_token(
                self.SINGLE_CHAR_TOKENS[char]
            )

        if char in self.ONE_CHAR_OPERATORS:
            return self.make_token(
                self.ONE_CHAR_OPERATORS[char]
            )

        if char in "=!<>|&":
            return self.two_character_operator(char)

        raise LexerError(
            f"Unexpected character {char!r}",
            self.location(
                self.token_line,
                self.token_column,
            ),
        )

    def identifier(self) -> Token:
        while True:
            char = self.peek()

            if char.isalnum() or char == "_":
                self.advance()
            else:
                break

        text = self.source[self.start:self.current]

        token_type = self.KEYWORDS.get(
            text,
            TokenType.IDENTIFIER,
        )

        return self.make_token(token_type)

    def number(self) -> Token:
        while self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()

            while self.peek().isdigit():
                self.advance()

        text = self.source[self.start:self.current]

        try:
            literal = float(text) if "." in text else int(text)
        except ValueError:
            raise LexerError(
                f"Invalid number literal {text!r}",
                self.location(
                    self.token_line,
                    self.token_column,
                ),
            )

        return self.make_token(
            TokenType.NUMBER,
            literal,
        )

    def string(self) -> Token:
        value_chars: list[str] = []

        while not self.is_at_end():
            char = self.peek()

            if char == '"':
                self.advance()

                return self.make_token(
                    TokenType.STRING,
                    "".join(value_chars),
                )

            if char == "\\":
                self.advance()

                if self.is_at_end():
                    break

                escaped = self.advance()

                escapes = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    '"': '"',
                    "\\": "\\",
                }

                value_chars.append(
                    escapes.get(escaped, escaped)
                )
                continue

            if char == "\n":
                self.advance()
                value_chars.append("\n")
                continue

            value_chars.append(self.advance())

        raise LexerError(
            "Unterminated string",
            self.location(
                self.token_line,
                self.token_column,
            ),
        )

    def two_character_operator(self, first: str) -> Token:
        second = self.peek()
        candidate = first + second

        token_type = self.TWO_CHAR_TOKENS.get(candidate)

        if token_type is not None:
            self.advance()
            return self.make_token(token_type)

        raise LexerError(
            f"Unexpected operator {candidate!r}",
            self.location(
                self.token_line,
                self.token_column,
            ),
        )

    def skip_comment(self) -> None:
        while not self.is_at_end() and self.peek() != "\n":
            self.advance()

    def advance(self) -> str:
        if self.is_at_end():
            return "\0"

        char = self.source[self.current]
        self.current += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"

        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def location(
        self,
        line: int | None = None,
        column: int | None = None,
    ) -> SourceLocation:
        return SourceLocation(
            filename=self.filename,
            line=line if line is not None else self.line,
            column=column if column is not None else self.column,
        )

    def make_token(
        self,
        token_type: TokenType,
        literal=None,
    ) -> Token:
        lexeme = self.source[self.start:self.current]

        return Token(
            type=token_type,
            lexeme=lexeme,
            literal=literal,
            location=self.location(
                self.token_line,
                self.token_column,
            ),
        )

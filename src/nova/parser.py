from __future__ import annotations

from dataclasses import dataclass

from .ast import (
    ArrayLiteral,
    Assignment,
    Binary,
    Block,
    Call,
    Expression,
    ExpressionStatement,
    FunctionDeclaration,
    FunctionExpression,
    Identifier,
    IfStatement,
    Index,
    LetStatement,
    Literal,
    Program,
    ReturnStatement,
    SourceSpan,
    Statement,
    Unary,
    WhileStatement,
)
from .token import Token, TokenType


@dataclass
class ParserError(Exception):
    message: str
    token: Token

    def __str__(self) -> str:
        location = self.token.location
        return (
            f"ParserError at "
            f"{location.filename}:"
            f"{location.line}:"
            f"{location.column}: "
            f"{self.message}"
        )


class Parser:
    """Recursive-descent parser for Nova."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    # =========================================================
    # PROGRAM
    # =========================================================

    def parse(self) -> Program:
        statements: list[Statement] = []

        while not self.check(TokenType.EOF):
            statements.append(self.declaration())

        if statements:
            span = self.merge_spans(
                statements[0].span,
                statements[-1].span,
            )
        else:
            span = self.token_span(self.peek())

        return Program(
            declarations=statements,
            span=span,
        )

    # =========================================================
    # DECLARATIONS
    # =========================================================

    def declaration(self) -> Statement:
        if self.match(TokenType.LET):
            return self.let_declaration()

        if self.match(TokenType.FN):
            return self.function_declaration()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.RETURN):
            return self.return_statement()

        return self.expression_statement()

    # =========================================================
    # LET
    # =========================================================

    def let_declaration(self) -> LetStatement:
        name = self.consume(
            TokenType.IDENTIFIER,
            "Expected variable name after 'let'.",
        )

        initializer = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        semicolon = self.consume(
            TokenType.SEMICOLON,
            "Expected ';' after variable declaration.",
        )

        span = self.merge_spans(
            self.token_span(name),
            self.token_span(semicolon),
        )

        return LetStatement(
            name=name.lexeme,
            initializer=initializer,
            span=span,
        )

    # =========================================================
    # FUNCTION DECLARATION
    # =========================================================

    def function_declaration(self) -> FunctionDeclaration:
        name = self.consume(
            TokenType.IDENTIFIER,
            "Expected function name after 'fn'.",
        )

        self.consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after function name.",
        )

        parameters = self.parameters()

        self.consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after parameters.",
        )

        body = self.block()

        span = self.merge_spans(
            self.token_span(name),
            body.span,
        )

        return FunctionDeclaration(
            name=name.lexeme,
            parameters=parameters,
            body=body,
            span=span,
        )

    # =========================================================
    # PARAMETERS
    # =========================================================

    def parameters(self) -> list[str]:
        parameters: list[str] = []

        if self.check(TokenType.RIGHT_PAREN):
            return parameters

        while True:
            parameter = self.consume(
                TokenType.IDENTIFIER,
                "Expected parameter name.",
            )

            parameters.append(parameter.lexeme)

            if not self.match(TokenType.COMMA):
                break

        return parameters

    # =========================================================
    # BLOCK
    # =========================================================

    def block(self) -> Block:
        opening = self.consume(
            TokenType.LEFT_BRACE,
            "Expected '{'.",
        )

        statements: list[Statement] = []

        while (
            not self.check(TokenType.RIGHT_BRACE)
            and not self.check(TokenType.EOF)
        ):
            statements.append(self.declaration())

        closing = self.consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' after block.",
        )

        span = self.merge_spans(
            self.token_span(opening),
            self.token_span(closing),
        )

        return Block(
            statements=statements,
            span=span,
        )

    # =========================================================
    # IF
    # =========================================================

    def if_statement(self) -> IfStatement:
        self.consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'if'.",
        )

        condition = self.expression()

        self.consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after condition.",
        )

        then_branch = self.block()

        else_branch = None

        if self.match(TokenType.ELSE):
            if self.match(TokenType.IF):
                else_branch = self.if_statement()
            else:
                else_branch = self.block()

        end_span = (
            else_branch.span
            if else_branch is not None
            else then_branch.span
        )

        span = self.merge_spans(
            condition.span,
            end_span,
        )

        return IfStatement(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            span=span,
        )

    # =========================================================
    # WHILE
    # =========================================================

    def while_statement(self) -> WhileStatement:
        self.consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'while'.",
        )

        condition = self.expression()

        self.consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after condition.",
        )

        body = self.block()

        span = self.merge_spans(
            condition.span,
            body.span,
        )

        return WhileStatement(
            condition=condition,
            body=body,
            span=span,
        )

    # =========================================================
    # RETURN
    # =========================================================

    def return_statement(self) -> ReturnStatement:
        keyword = self.previous()

        value = None

        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        semicolon = self.consume(
            TokenType.SEMICOLON,
            "Expected ';' after return statement.",
        )

        span = self.merge_spans(
            self.token_span(keyword),
            self.token_span(semicolon),
        )

        return ReturnStatement(
            value=value,
            span=span,
        )

    # =========================================================
    # EXPRESSION STATEMENT
    # =========================================================

    def expression_statement(self) -> ExpressionStatement:
        expression = self.expression()

        semicolon = self.consume(
            TokenType.SEMICOLON,
            "Expected ';' after expression.",
        )

        span = self.merge_spans(
            expression.span,
            self.token_span(semicolon),
        )

        return ExpressionStatement(
            expression=expression,
            span=span,
        )

    # =========================================================
    # EXPRESSIONS
    # =========================================================

    def expression(self) -> Expression:
        return self.assignment()

    # =========================================================
    # ASSIGNMENT
    # =========================================================

    def assignment(self) -> Expression:
        expression = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expression, Identifier):
                return Assignment(
                    name=expression.name,
                    value=value,
                    span=self.merge_spans(
                        expression.span,
                        value.span,
                    ),
                )

            raise ParserError(
                "Invalid assignment target.",
                equals,
            )

        return expression

    # =========================================================
    # LOGICAL OR
    # =========================================================

    def logical_or(self) -> Expression:
        expression = self.logical_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()

            expression = Binary(
                left=expression,
                operator=operator,
                right=right,
                span=self.merge_spans(
                    expression.span,
                    right.span,
                ),
            )

        return expression

    # =========================================================
    # LOGICAL AND
    # =========================================================

    def logical_and(self) -> Expression:
        expression = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()

            expression = Binary(
                left=expression,
                operator=operator,
                right=right,
                span=self.merge_spans(
                    expression.span,
                    right.span,
                ),
            )

        return expression

    # =========================================================
    # EQUALITY
    # =========================================================

    def equality(self) -> Expression:
        expression = self.comparison()

        while self.match(
            TokenType.EQUAL_EQUAL,
            TokenType.NOT_EQUAL,
        ):
            operator = self.previous()
            right = self.comparison()

            expression = Binary(
                left=expression,
                operator=operator,
                right=right,
                span=self.merge_spans(
                    expression.span,
                    right.span,
                ),
            )

        return expression

    # =========================================================
    # COMPARISON
    # =========================================================

    def comparison(self) -> Expression:
        expression = self.term()

        while self.match(
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            operator = self.previous()
            right = self.term()

            expression = Binary(
                left=expression,
                operator=operator,
                right=right,
                span=self.merge_spans(
                    expression.span,
                    right.span,
                ),
            )

        return expression

    # =========================================================
    # TERM
    # =========================================================

    def term(self) -> Expression:
        expression = self.factor()

        while self.match(
            TokenType.PLUS,
            TokenType.MINUS,
        ):
            operator = self.previous()
            right = self.factor()

            expression = Binary(
                left=expression,
                operator=operator,
                right=right,
                span=self.merge_spans(
                    expression.span,
                    right.span,
                ),
            )

        return expression

    # =========================================================
    # FACTOR
    # =========================================================

    def factor(self) -> Expression:
        expression = self.unary()

        while self.match(
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT,
        ):
            operator = self.previous()
            right = self.unary()

            expression = Binary(
                left=expression,
                operator=operator,
                right=right,
                span=self.merge_spans(
                    expression.span,
                    right.span,
                ),
            )

        return expression

    # =========================================================
    # UNARY
    # =========================================================

    def unary(self) -> Expression:
        if self.match(
            TokenType.BANG,
            TokenType.MINUS,
        ):
            operator = self.previous()
            operand = self.unary()

            return Unary(
                operator=operator,
                operand=operand,
                span=self.merge_spans(
                    self.token_span(operator),
                    operand.span,
                ),
            )

        return self.postfix()

    # =========================================================
    # POSTFIX
    # =========================================================

    def postfix(self) -> Expression:
        expression = self.primary()

        while True:

            # Function call
            if self.match(TokenType.LEFT_PAREN):
                arguments: list[Expression] = []

                if not self.check(TokenType.RIGHT_PAREN):
                    while True:
                        arguments.append(self.expression())

                        if not self.match(TokenType.COMMA):
                            break

                closing = self.consume(
                    TokenType.RIGHT_PAREN,
                    "Expected ')' after arguments.",
                )

                expression = Call(
                    callee=expression,
                    arguments=arguments,
                    span=self.merge_spans(
                        expression.span,
                        self.token_span(closing),
                    ),
                )

            # Array indexing
            elif self.match(TokenType.LEFT_BRACKET):
                index = self.expression()

                closing = self.consume(
                    TokenType.RIGHT_BRACKET,
                    "Expected ']' after index.",
                )

                expression = Index(
                    collection=expression,
                    index=index,
                    span=self.merge_spans(
                        expression.span,
                        self.token_span(closing),
                    ),
                )

            else:
                break

        return expression

    # =========================================================
    # PRIMARY
    # =========================================================

    def primary(self) -> Expression:

        # false
        if self.match(TokenType.FALSE):
            return self.literal(False)

        # true
        if self.match(TokenType.TRUE):
            return self.literal(True)

        # nil
        if self.match(TokenType.NIL):
            return self.literal(None)

        # numbers / strings
        if self.match(
            TokenType.NUMBER,
            TokenType.STRING,
        ):
            return self.literal(
                self.previous().literal
            )

        # identifier
        if self.match(TokenType.IDENTIFIER):
            token = self.previous()

            return Identifier(
                name=token.lexeme,
                span=self.token_span(token),
            )

        # grouped expression
        if self.match(TokenType.LEFT_PAREN):
            opening = self.previous()

            expression = self.expression()

            closing = self.consume(
                TokenType.RIGHT_PAREN,
                "Expected ')' after expression.",
            )

            return self.with_span(
                expression,
                self.merge_spans(
                    self.token_span(opening),
                    self.token_span(closing),
                ),
            )

        # array
        if self.match(TokenType.LEFT_BRACKET):
            return self.array_literal()

        # anonymous function
        if self.match(TokenType.FN):
            return self.function_expression()

        raise ParserError(
            "Expected expression.",
            self.peek(),
        )

    # =========================================================
    # LITERALS
    # =========================================================

    def literal(self, value) -> Literal:
        token = self.previous()

        return Literal(
            value=value,
            span=self.token_span(token),
        )

    # =========================================================
    # ARRAY
    # =========================================================

    def array_literal(self) -> ArrayLiteral:
        opening = self.previous()

        elements: list[Expression] = []

        if not self.check(TokenType.RIGHT_BRACKET):
            while True:
                elements.append(self.expression())

                if not self.match(TokenType.COMMA):
                    break

        closing = self.consume(
            TokenType.RIGHT_BRACKET,
            "Expected ']' after array elements.",
        )

        return ArrayLiteral(
            elements=elements,
            span=self.merge_spans(
                self.token_span(opening),
                self.token_span(closing),
            ),
        )

    # =========================================================
    # FUNCTION EXPRESSION
    # =========================================================

    def function_expression(self) -> FunctionExpression:
        opening = self.consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'fn'.",
        )

        parameters = self.parameters()

        self.consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after parameters.",
        )

        body = self.block()

        return FunctionExpression(
            parameters=parameters,
            body=body,
            span=self.merge_spans(
                self.token_span(opening),
                body.span,
            ),
        )

    # =========================================================
    # TOKEN HELPERS
    # =========================================================

    def match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return token_type == TokenType.EOF

        return self.peek().type == token_type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def consume(
        self,
        token_type: TokenType,
        message: str,
    ) -> Token:
        if self.check(token_type):
            return self.advance()

        raise ParserError(
            message,
            self.peek(),
        )

    # =========================================================
    # SOURCE SPANS
    # =========================================================

    @staticmethod
    def token_span(token: Token) -> SourceSpan:
        line = token.location.line
        column = token.location.column

        length = max(len(token.lexeme), 1)

        return SourceSpan(
            filename=token.location.filename,
            start_line=line,
            start_column=column,
            end_line=line,
            end_column=column + length,
        )

    @staticmethod
    def merge_spans(
        first: SourceSpan,
        second: SourceSpan,
    ) -> SourceSpan:
        return SourceSpan(
            filename=first.filename,
            start_line=first.start_line,
            start_column=first.start_column,
            end_line=second.end_line,
            end_column=second.end_column,
        )

    @staticmethod
    def with_span(
        expression: Expression,
        span: SourceSpan,
    ) -> Expression:
        expression.span = span
        return expression

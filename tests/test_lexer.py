from nova.lexer import Lexer
from nova.token import TokenType


def lex(source: str):
    return Lexer(source, filename="test.nova").tokenize()


def test_lexer_keywords():
    tokens = lex(
        "let fn if else while return true false nil"
    )

    types = [token.type for token in tokens]

    assert types == [
        TokenType.LET,
        TokenType.FN,
        TokenType.IF,
        TokenType.ELSE,
        TokenType.WHILE,
        TokenType.RETURN,
        TokenType.TRUE,
        TokenType.FALSE,
        TokenType.NIL,
        TokenType.EOF,
    ]


def test_lexer_numbers():
    tokens = lex("123 45.67")

    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].literal == 123

    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].literal == 45.67


def test_lexer_strings():
    tokens = lex('"Hello Nova"')

    assert tokens[0].type == TokenType.STRING
    assert tokens[0].literal == "Hello Nova"


def test_lexer_operators():
    tokens = lex("+ - * / % = == != < <= > >= && || !")

    types = [token.type for token in tokens]

    assert types == [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
        TokenType.EQUAL,
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.LESS,
        TokenType.LESS_EQUAL,
        TokenType.GREATER,
        TokenType.GREATER_EQUAL,
        TokenType.AND,
        TokenType.OR,
        TokenType.BANG,
        TokenType.EOF,
    ]


def test_lexer_identifiers():
    tokens = lex("nova my_variable counter123")

    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == "nova"

    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "my_variable"

    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[2].lexeme == "counter123"


def test_lexer_comments():
    tokens = lex(
        """
        # This is a comment
        let x = 10;
        """
    )

    types = [token.type for token in tokens]

    assert types == [
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_lexer_source_location():
    tokens = lex("let x = 10;")

    assert tokens[0].location.line == 1
    assert tokens[0].location.column == 1

    assert tokens[1].location.line == 1
    assert tokens[1].location.column == 5

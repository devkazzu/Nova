from nova.ast import (
    Binary,
    FunctionDeclaration,
    LetStatement,
    Literal,
    ReturnStatement,
)
from nova.lexer import Lexer
from nova.parser import Parser


def parse(source: str):
    tokens = Lexer(source, filename="test.nova").tokenize()
    return Parser(tokens).parse()


def test_parse_let_statement():
    program = parse("let x = 10;")

    statement = program.statements[0]

    assert isinstance(statement, LetStatement)
    assert statement.name == "x"
    assert isinstance(statement.initializer, Literal)
    assert statement.initializer.value == 10


def test_parse_binary_expression():
    program = parse("let x = 10 + 5 * 2;")

    statement = program.statements[0]
    expression = statement.initializer

    assert isinstance(expression, Binary)
    assert expression.operator == "+"

    assert isinstance(expression.right, Binary)
    assert expression.right.operator == "*"


def test_parse_function_declaration():
    program = parse(
        """
        fn add(a, b) {
            return a + b;
        }
        """
    )

    statement = program.statements[0]

    assert isinstance(statement, FunctionDeclaration)
    assert statement.name == "add"
    assert statement.parameters == ["a", "b"]
    assert len(statement.body.statements) == 1


def test_parse_return_statement():
    program = parse(
        """
        fn test() {
            return 42;
        }
        """
    )

    function = program.statements[0]
    statement = function.body.statements[0]

    assert isinstance(statement, ReturnStatement)
    assert isinstance(statement.value, Literal)
    assert statement.value.value == 42


def test_parse_if_else():
    program = parse(
        """
        if (true) {
            print(1);
        } else {
            print(2);
        }
        """
    )

    assert len(program.statements) == 1


def test_parse_while():
    program = parse(
        """
        let x = 0;

        while (x < 10) {
            x = x + 1;
        }
        """
    )

    assert len(program.statements) == 2


def test_parse_array_literal():
    program = parse("let values = [1, 2, 3];")

    statement = program.statements[0]

    assert statement.name == "values"
    assert len(statement.initializer.elements) == 3

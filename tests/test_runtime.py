from nova.interpreter import run
from nova.lexer import Lexer
from nova.parser import Parser


def execute(source: str):
    tokens = Lexer(source, filename="test.nova").tokenize()
    program = Parser(tokens).parse()
    return run(program)


def test_arithmetic():
    result = execute("10 + 20;")

    assert result == 30


def test_variable_assignment():
    result = execute(
        """
        let x = 10;
        x = 25;
        x;
        """
    )

    assert result == 25


def test_if_statement():
    result = execute(
        """
        let x = 0;

        if (true) {
            x = 10;
        }

        x;
        """
    )

    assert result == 10


def test_while_loop():
    result = execute(
        """
        let x = 0;

        while (x < 5) {
            x = x + 1;
        }

        x;
        """
    )

    assert result == 5


def test_function_call():
    result = execute(
        """
        fn add(a, b) {
            return a + b;
        }

        add(10, 20);
        """
    )

    assert result == 30


def test_recursive_function():
    result = execute(
        """
        fn factorial(n) {
            if (n <= 1) {
                return 1;
            }

            return n * factorial(n - 1);
        }

        factorial(5);
        """
    )

    assert result == 120


def test_closure():
    result = execute(
        """
        fn make_counter() {
            let count = 0;

            fn counter() {
                count = count + 1;
                return count;
            }

            return counter;
        }

        let counter = make_counter();

        counter();
        counter();
        counter();
        """
    )

    assert result == 3


def test_array_indexing():
    result = execute(
        """
        let values = [10, 20, 30];
        values[1];
        """
    )

    assert result == 20


def test_string_concatenation():
    result = execute(
        """
        "Hello " + "Nova";
        """
    )

    assert result == "Hello Nova"


def test_boolean_logic():
    result = execute(
        """
        true && true;
        """
    )

    assert result is True


def test_len_builtin():
    result = execute(
        """
        len([1, 2, 3, 4]);
        """
    )

    assert result == 4

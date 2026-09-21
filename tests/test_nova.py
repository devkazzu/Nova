from nova.ast import Program
from nova.interpreter import Interpreter
from nova.lexer import Lexer
from nova.parser import Parser


def execute(source: str):
    tokens = Lexer(
        source,
        filename="<test>",
    ).tokenize()

    program = Parser(tokens).parse()

    interpreter = Interpreter()

    return interpreter.interpret(program)


def test_arithmetic():
    result = execute(
        "let x = 10 + 5 * 2;"
    )

    assert result is None


def test_variable_assignment():
    result = execute(
        """
        let x = 10;
        x = 20;
        x;
        """
    )

    assert result == 20


def test_boolean_values():
    assert execute("true;") is True
    assert execute("false;") is False
    assert execute("nil;") is None


def test_if_statement():
    result = execute(
        """
        let x = 0;

        if (true) {
            x = 42;
        }

        x;
        """
    )

    assert result == 42


def test_else_statement():
    result = execute(
        """
        let x = 10;

        if (false) {
            x = 20;
        } else {
            x = 30;
        }

        x;
        """
    )

    assert result == 30


def test_while_loop():
    result = execute(
        """
        let x = 0;
        let total = 0;

        while (x < 5) {
            total = total + x;
            x = x + 1;
        }

        total;
        """
    )

    assert result == 10


def test_function():
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


def test_array():
    result = execute(
        """
        let values = [10, 20, 30];
        values[1];
        """
    )

    assert result == 20


def test_array_length():
    result = execute(
        """
        let values = [1, 2, 3, 4];
        len(values);
        """
    )

    assert result == 4


def test_string():
    result = execute(
        '"Nova" + " Language";'
    )

    assert result == "Nova Language"


def test_string_index():
    result = execute(
        """
        let text = "Nova";
        text[0];
        """
    )

    assert result == "N"


def test_builtin_type():
    assert execute("type(123);") == "number"
    assert execute('type("Nova");') == "string"
    assert execute("type(true);") == "bool"


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

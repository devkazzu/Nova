from __future__ import annotations

from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .interpreter import Interpreter
from .runtime import NovaRuntimeError, stringify


VERSION = "0.1.0"


class NovaREPL:
    """
    Interactive Read-Eval-Print Loop for Nova.
    """

    PROMPT = ">>> "
    CONTINUATION_PROMPT = "... "

    def __init__(self) -> None:
        self.interpreter = Interpreter()

    def start(self) -> None:
        self.print_banner()

        while True:
            try:
                source = self.read_source()

                if not source.strip():
                    continue

                if self.handle_command(source):
                    continue

                self.execute(source)

            except EOFError:
                print()
                print("Goodbye!")
                break

            except KeyboardInterrupt:
                print()
                continue

    def print_banner(self) -> None:
        print(f"Nova {VERSION}")
        print("Interactive Nova interpreter")
        print("Type :help for help, :quit to exit.")
        print()

    def read_source(self) -> str:
        """
        Read one Nova statement or a multi-line block.
        """

        lines: list[str] = []

        first_line = input(self.PROMPT)

        lines.append(first_line)

        stripped = first_line.strip()

        if self.needs_continuation(stripped):
            while True:
                line = input(self.CONTINUATION_PROMPT)

                lines.append(line)

                if self.block_complete("\n".join(lines)):
                    break

        return "\n".join(lines)

    @staticmethod
    def needs_continuation(source: str) -> bool:
        """
        Determine whether the user probably started a block.
        """

        return (
            source.endswith("{")
            or source.count("{") > source.count("}")
        )

    @staticmethod
    def block_complete(source: str) -> bool:
        """
        Check whether braces are balanced.
        """

        depth = 0
        in_string = False
        escaped = False

        for char in source:
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False

                continue

            if char == '"':
                in_string = True

            elif char == "{":
                depth += 1

            elif char == "}":
                depth -= 1

        return depth <= 0 and not in_string

    def handle_command(self, source: str) -> bool:
        """
        Handle REPL commands beginning with ':'.

        Returns True when the input was a command.
        """

        command = source.strip().lower()

        if command == ":help":
            self.print_help()
            return True

        if command in {":quit", ":exit"}:
            raise EOFError

        if command == ":version":
            print(f"Nova {VERSION}")
            return True

        if command == ":clear":
            print("\033[2J\033[H", end="")
            return True

        if command == ":reset":
            self.interpreter = Interpreter()
            print("Interpreter state reset.")
            return True

        return False

    def print_help(self) -> None:
        print()
        print("Nova REPL commands:")
        print("  :help       Show this help message")
        print("  :version    Show Nova version")
        print("  :clear      Clear the terminal")
        print("  :reset      Reset interpreter state")
        print("  :quit       Exit Nova")
        print()
        print("Example:")
        print("  let x = 10;")
        print("  x + 5;")
        print("  print(\"Hello Nova\");")
        print()

    def execute(self, source: str) -> None:
        """
        Lex, parse and execute Nova source code.
        """

        try:
            tokens = Lexer(
                source,
                filename="<repl>",
            ).tokenize()

            program = Parser(tokens).parse()

            result = self.interpreter.interpret(program)

            if result is not None:
                print(stringify(result))

        except LexerError as error:
            print(error)

        except ParserError as error:
            print(error)

        except NovaRuntimeError as error:
            print(error)

        except Exception as error:
            print(
                f"Nova internal error: {error}"
            )


def start_repl() -> None:
    """
    Start the Nova interactive shell.
    """

    NovaREPL().start()


if __name__ == "__main__":
    start_repl()

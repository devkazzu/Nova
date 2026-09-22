from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .interpreter import Interpreter
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .repl import start_repl
from .runtime import NovaRuntimeError, stringify


VERSION = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nova",
        description="Nova programming language interpreter.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Nova {VERSION}",
    )

    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Nova source file to execute.",
    )

    return parser


def execute_file(path: Path) -> int:
    if not path.exists():
        print(
            f"Nova: file not found: {path}",
            file=sys.stderr,
        )
        return 1

    if not path.is_file():
        print(
            f"Nova: not a file: {path}",
            file=sys.stderr,
        )
        return 1

    try:
        source = path.read_text(
            encoding="utf-8"
        )

    except OSError as error:
        print(
            f"Nova: cannot read '{path}': {error}",
            file=sys.stderr,
        )
        return 1

    try:
        tokens = Lexer(
            source,
            filename=str(path),
        ).tokenize()

        program = Parser(tokens).parse()

        interpreter = Interpreter()

        result = interpreter.interpret(program)

        if result is not None:
            print(stringify(result))

        return 0

    except LexerError as error:
        print(error, file=sys.stderr)
        return 1

    except ParserError as error:
        print(error, file=sys.stderr)
        return 1

    except NovaRuntimeError as error:
        print(error, file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    """
    Run the Nova command-line interface.

    argv can be supplied by tests or other Python callers.
    When argv is None, argparse reads sys.argv automatically.
    """

    parser = build_parser()

    args = parser.parse_args(argv)

    if args.file is None:
        start_repl()
        return 0

    return execute_file(args.file)


if __name__ == "__main__":
    raise SystemExit(main())

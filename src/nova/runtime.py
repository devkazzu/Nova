from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class NovaRuntimeError(Exception):
    """Runtime error raised while executing Nova code."""

    def __init__(self, message: str, span=None):
        super().__init__(message)
        self.message = message
        self.span = span

    def __str__(self) -> str:
        if self.span is None:
            return self.message

        return (
            f"{self.span.filename}:"
            f"{self.span.start_line}:"
            f"{self.span.start_column}: "
            f"{self.message}"
        )


class ReturnSignal(Exception):
    """Internal control-flow signal used by Nova return statements."""

    def __init__(self, value: Any):
        super().__init__()
        self.value = value


class Environment:
    """
    Lexical environment for Nova variables.

    Each environment may have a parent environment.
    This provides lexical scoping and closures.
    """

    def __init__(
        self,
        parent: Environment | None = None,
    ):
        self.values: dict[str, Any] = {}
        self.parent = parent

    def define(
        self,
        name: str,
        value: Any,
    ) -> None:
        self.values[name] = value

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]

        if self.parent is not None:
            return self.parent.get(name)

        raise NovaRuntimeError(
            f"Undefined variable '{name}'."
        )

    def assign(
        self,
        name: str,
        value: Any,
    ) -> None:
        if name in self.values:
            self.values[name] = value
            return

        if self.parent is not None:
            self.parent.assign(name, value)
            return

        raise NovaRuntimeError(
            f"Undefined variable '{name}'."
        )

    def contains(self, name: str) -> bool:
        if name in self.values:
            return True

        if self.parent is not None:
            return self.parent.contains(name)

        return False

    def child(self) -> Environment:
        return Environment(parent=self)


@dataclass
class NovaFunction:
    """
    User-defined Nova function.

    The defining environment is captured when the function
    is created, allowing lexical closures.
    """

    name: str
    parameters: list[str]
    body: Any
    closure: Environment

    def call(
        self,
        interpreter: Any,
        arguments: list[Any],
    ) -> Any:
        if len(arguments) != len(self.parameters):
            raise NovaRuntimeError(
                f"Function '{self.name}' expected "
                f"{len(self.parameters)} argument(s), "
                f"got {len(arguments)}."
            )

        environment = Environment(
            parent=self.closure
        )

        for parameter, argument in zip(
            self.parameters,
            arguments,
        ):
            environment.define(
                parameter,
                argument,
            )

        try:
            interpreter.execute_block(
                self.body.statements,
                environment,
            )
        except ReturnSignal as signal:
            return signal.value

        return None

    def __call__(
        self,
        interpreter: Any,
        arguments: list[Any],
    ) -> Any:
        return self.call(
            interpreter,
            arguments,
        )

    def __repr__(self) -> str:
        return f"<fn {self.name}>"


@dataclass
class NativeFunction:
    """
    Built-in function implemented in Python.
    """

    name: str
    function: Callable[..., Any]
    arity: int | None = None

    def call(
        self,
        interpreter: Any,
        arguments: list[Any],
    ) -> Any:
        if self.arity is not None:
            if len(arguments) != self.arity:
                raise NovaRuntimeError(
                    f"Function '{self.name}' expected "
                    f"{self.arity} argument(s), "
                    f"got {len(arguments)}."
                )

        try:
            return self.function(*arguments)
        except NovaRuntimeError:
            raise
        except Exception as exc:
            raise NovaRuntimeError(
                f"Native function '{self.name}' failed: {exc}"
            ) from exc

    def __repr__(self) -> str:
        return f"<native fn {self.name}>"


def is_truthy(value: Any) -> bool:
    """
    Nova truthiness rules.

    false, nil and numeric zero are false.
    Everything else is true.
    """

    if value is None:
        return False

    if value is False:
        return False

    if isinstance(value, (int, float)):
        return value != 0

    return True


def is_equal(left: Any, right: Any) -> bool:
    """
    Nova equality helper.
    """

    return left == right


def stringify(value: Any) -> str:
    """
    Convert a Nova runtime value to user-facing text.
    """

    if value is None:
        return "nil"

    if value is True:
        return "true"

    if value is False:
        return "false"

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))

    if isinstance(value, list):
        return "[" + ", ".join(
            stringify(item)
            for item in value
        ) + "]"

    return str(value)


def check_number_operands(
    left: Any,
    right: Any,
    operator: str,
) -> None:
    """
    Validate numeric operands for arithmetic operations.
    """

    if not isinstance(left, (int, float)):
        raise NovaRuntimeError(
            f"Operator '{operator}' requires numbers, "
            f"got {type(left).__name__}."
        )

    if not isinstance(right, (int, float)):
        raise NovaRuntimeError(
            f"Operator '{operator}' requires numbers, "
            f"got {type(right).__name__}."
        )


def builtin_print(*values: Any) -> None:
    print(
        " ".join(
            stringify(value)
            for value in values
        )
    )


def builtin_len(value: Any) -> int:
    try:
        return len(value)
    except TypeError as exc:
        raise NovaRuntimeError(
            f"len() does not support "
            f"{type(value).__name__}."
        ) from exc


def builtin_type(value: Any) -> str:
    if value is None:
        return "nil"

    if isinstance(value, bool):
        return "bool"

    if isinstance(value, int):
        return "number"

    if isinstance(value, float):
        return "number"

    if isinstance(value, str):
        return "string"

    if isinstance(value, list):
        return "array"

    if isinstance(value, NovaFunction):
        return "function"

    if isinstance(value, NativeFunction):
        return "function"

    return type(value).__name__


def create_global_environment() -> Environment:
    """
    Create Nova's default global environment.
    """

    environment = Environment()

    environment.define(
        "print",
        NativeFunction(
            name="print",
            function=builtin_print,
            arity=None,
        ),
    )

    environment.define(
        "len",
        NativeFunction(
            name="len",
            function=builtin_len,
            arity=1,
        ),
    )

    environment.define(
        "type",
        NativeFunction(
            name="type",
            function=builtin_type,
            arity=1,
        ),
    )

    return environment

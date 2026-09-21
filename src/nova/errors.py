from __future__ import annotations

from dataclasses import dataclass

from .ast import SourceSpan


@dataclass
class NovaError(Exception):
    """
    Base error class for Nova.

    Stores a human-readable message and optional source location.
    """

    message: str
    span: SourceSpan | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def format(self, source: str | None = None) -> str:
        """
        Format the error with source location information.
        """

        if self.span is None:
            return f"NovaError: {self.message}"

        location = (
            f"{self.span.filename}:"
            f"{self.span.start_line}:"
            f"{self.span.start_column}"
        )

        result = f"NovaError: {self.message}\n  --> {location}"

        if source is not None:
            result += "\n"
            result += format_source_line(
                source,
                self.span,
            )

        return result

    def __str__(self) -> str:
        return self.format()


class NovaSyntaxError(NovaError):
    """Raised when Nova source code contains invalid syntax."""


class NovaRuntimeError(NovaError):
    """Raised when a runtime error occurs."""


class NovaNameError(NovaRuntimeError):
    """Raised when an identifier cannot be found."""


class NovaTypeError(NovaRuntimeError):
    """Raised when an operation receives an invalid type."""


class NovaValueError(NovaRuntimeError):
    """Raised when a value is invalid."""


def format_source_line(
    source: str,
    span: SourceSpan,
) -> str:
    """
    Create a source-code snippet with a caret pointing
    to the error location.
    """

    lines = source.splitlines()

    line_index = span.start_line - 1

    if line_index < 0 or line_index >= len(lines):
        return ""

    line = lines[line_index]

    column = max(
        span.start_column - 1,
        0,
    )

    width = max(
        span.end_column - span.start_column,
        1,
    )

    caret = " " * column + "^" * width

    return (
        f"     |\n"
        f"{span.start_line:4} | {line}\n"
        f"     | {caret}"
    )


def format_error(
    message: str,
    span: SourceSpan | None = None,
    source: str | None = None,
) -> str:
    """
    Convenience function for formatting Nova errors.
    """

    error = NovaError(
        message,
        span,
    )

    return error.format(source)

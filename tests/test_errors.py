import pytest

from nova.ast import SourceSpan
from nova.errors import (
    NovaError,
    NovaNameError,
    NovaSyntaxError,
    NovaTypeError,
    NovaValueError,
    format_source_line,
)


def test_error_without_span():
    error = NovaError("Something went wrong")

    assert str(error) == "NovaError: Something went wrong"


def test_error_with_location():
    span = SourceSpan(
        filename="test.nova",
        start_line=2,
        start_column=5,
        end_line=2,
        end_column=8,
    )

    error = NovaError("Invalid value", span)

    message = error.format()

    assert "NovaError: Invalid value" in message
    assert "test.nova:2:5" in message


def test_error_with_source_line():
    source = "let x = 10;\nlet y = unknown;"

    span = SourceSpan(
        filename="test.nova",
        start_line=2,
        start_column=9,
        end_line=2,
        end_column=16,
    )

    error = NovaError("Unknown variable", span)

    message = error.format(source)

    assert "let y = unknown;" in message
    assert "^" in message


def test_format_source_line():
    source = "let value = 42;"

    span = SourceSpan(
        filename="test.nova",
        start_line=1,
        start_column=5,
        end_line=1,
        end_column=10,
    )

    result = format_source_line(source, span)

    assert "let value = 42;" in result
    assert "^" in result


def test_specialized_error_types():
    assert issubclass(NovaSyntaxError, NovaError)
    assert issubclass(NovaNameError, NovaError)
    assert issubclass(NovaTypeError, NovaError)
    assert issubclass(NovaValueError, NovaError)


def test_error_is_exception():
    error = NovaError("Test error")

    with pytest.raises(NovaError):
        raise error

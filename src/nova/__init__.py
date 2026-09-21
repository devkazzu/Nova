"""
Nova Programming Language.

A small, expressive programming language implemented in Python.
"""

__version__ = "0.1.0"
__author__ = "Raju Mahato"
__license__ = "MIT"


from .ast import Program
from .interpreter import Interpreter, run
from .lexer import Lexer
from .parser import Parser


__all__ = [
    "Program",
    "Interpreter",
    "Lexer",
    "Parser",
    "run",
]

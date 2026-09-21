# Nova — Architecture

## Overview

Nova follows a simple language-processing pipeline:

Source Code
    ↓
Lexer
    ↓
Tokens
    ↓
Parser
    ↓
AST
    ↓
Interpreter
    ↓
Runtime

Nova will also have an optional bytecode execution path:

AST
    ↓
Bytecode Compiler
    ↓
Bytecode
    ↓
Virtual Machine
    ↓
Runtime

---

## 1. Lexer

The lexer converts Nova source code into a sequence of tokens.

Responsibilities:

- Read source characters
- Recognize keywords
- Recognize identifiers
- Recognize numbers
- Recognize strings
- Recognize operators
- Recognize punctuation
- Ignore whitespace
- Track source locations
- Report invalid characters

Example:

```nova
let x = 10 + 20;

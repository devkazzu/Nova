# Nova

**Nova** is a small, expressive programming language built from scratch in Python.

Nova is designed as a learning-focused language project that implements the complete front-end and runtime pipeline:

**Source Code → Lexer → Tokens → Parser → AST → Interpreter → Runtime**

The project is currently in an early **0.1.x / Alpha** stage.

---

## ✨ Features

- 🔤 Lexer with source locations
- 🌳 Abstract Syntax Tree (AST)
- 🧩 Recursive-descent parser
- ▶️ Tree-walking interpreter
- 📦 Variables and assignments
- 🔢 Numbers
- 📝 Strings
- 🔘 Booleans
- `nil`
- 📚 Arrays
- ➕ Arithmetic operators
- ⚖️ Comparison operators
- 🔀 `if / else`
- 🔁 `while` loops
- 🧩 User-defined functions
- ♻️ Recursive functions
- 🏷️ First-class functions
- 🔐 Lexical scoping
- 🔗 Closures
- 🧰 Built-in functions
- 💻 Interactive REPL
- ⌨️ Command-line interface
- 🚨 Runtime errors with source locations
- 🧪 Automated tests
- ⚙️ GitHub Actions CI
- 🚧 Experimental bytecode VM roadmap

---

## 🧠 Nova at a Glance

A simple Nova program:

```nova
fn factorial(n) {
    if (n <= 1) {
        return 1;
    }

    return n * factorial(n - 1);
}

factorial(5);
```

Output:

```text
120
```

---

## 🚀 Quick Start

### Requirements

- Python **3.11+**
- Git

### Clone the repository

```bash
git clone https://github.com/devkazzu/Nova.git
cd Nova
```

### Create a virtual environment

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Install Nova

```bash
pip install -e .
```

For development and testing:

```bash
pip install -e ".[dev]"
```

---

# 💻 REPL

Start the interactive Nova interpreter:

```bash
python -m nova
```

You should see:

```text
Nova 0.1.0
Interactive Nova interpreter
Type :help for help, :quit to exit.

>>>
```

Try:

```nova
let x = 10;
x + 5;
```

Output:

```text
15
```

---

# 📄 Running Nova Files

Create a file:

```text
hello.nova
```

Add:

```nova
let name = "Nova";

print("Hello " + name);
```

Run it:

```bash
python -m nova hello.nova
```

Output:

```text
Hello Nova
```

---

# 🔢 Variables

Nova supports variable declarations using `let`.

```nova
let x = 10;
let y = 20;

x + y;
```

Variables can be reassigned:

```nova
let score = 10;

score = 50;

score;
```

Output:

```text
50
```

---

# 🔀 Conditions

Nova supports `if` and `else`.

```nova
let age = 20;

if (age >= 18) {
    print("Adult");
} else {
    print("Minor");
}
```

---

# 🔁 Loops

Nova supports `while` loops.

```nova
let i = 0;

while (i < 5) {
    print(i);
    i = i + 1;
}
```

Output:

```text
0
1
2
3
4
```

---

# 🧩 Functions

Functions are declared using `fn`.

```nova
fn add(a, b) {
    return a + b;
}

add(10, 20);
```

Output:

```text
30
```

---

# ♻️ Recursion

Nova supports recursive functions.

```nova
fn factorial(n) {
    if (n <= 1) {
        return 1;
    }

    return n * factorial(n - 1);
}

factorial(5);
```

Output:

```text
120
```

---

# 🔐 Closures

Nova functions can capture variables from their surrounding environment.

```nova
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
```

The final result is:

```text
3
```

This demonstrates lexical scoping and closures.

---

# 📦 Arrays

Nova supports array literals and indexing.

```nova
let values = [10, 20, 30];

values[1];
```

Output:

```text
20
```

Get the length:

```nova
len(values);
```

Output:

```text
3
```

---

# 📝 Strings

Strings can be created using double quotes.

```nova
let name = "Nova";

"Hello " + name;
```

Output:

```text
Hello Nova
```

String indexing is also supported:

```nova
let text = "Nova";

text[0];
```

Output:

```text
N
```

---

# 🧰 Built-in Functions

Nova currently provides several built-in functions.

## `print`

```nova
print("Hello Nova");
```

## `len`

```nova
let values = [1, 2, 3];

len(values);
```

Output:

```text
3
```

## `type`

```nova
type(123);
type("Nova");
type(true);
```

Results:

```text
number
string
bool
```

---

# 🖥️ REPL Commands

The Nova REPL provides several commands:

```text
:help
:version
:clear
:reset
:quit
```

### `:help`

Displays available REPL commands.

### `:version`

Displays the current Nova version.

### `:clear`

Clears the terminal.

### `:reset`

Resets the interpreter state.

### `:quit`

Exits the Nova REPL.

---

# 🧪 Testing

Nova uses `pytest` for automated testing.

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

The repository also uses **GitHub Actions** to automatically run tests on pushes and pull requests.

---

# 🏗️ Project Structure

```text
Nova/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   ├── 01_PROJECT_VISION.md
│   ├── 02_REQUIREMENTS.md
│   ├── 03_LANGUAGE_DESIGN.md
│   ├── 04_EBNF_GRAMMAR.md
│   ├── 05_ARCHITECTURE.md
│   ├── 06_AST_DESIGN.md
│   ├── 07_RUNTIME_AND_CLOSURES.md
│   ├── 08_ERROR_HANDLING.md
│   ├── 09_REPL_DESIGN.md
│   ├── 10_BYTECODE_VM_PLAN.md
│   ├── 11_STANDARD_LIBRARY_PLAN.md
│   ├── 12_CLI_SPEC.md
│   ├── 13_TEST_PLAN.md
│   ├── 14_EXAMPLES.md
│   ├── 15_DEVELOPMENT_ROADMAP.md
│   ├── 16_REPOSITORY_STRUCTURE.md
│   ├── 17_CONTRIBUTING.md
│   ├── 18_CHANGELOG_TEMPLATE.md
│   └── 19_PROJECT_CHECKLIST.md
│
├── src/
│   └── nova/
│       ├── __init__.py
│       ├── __main__.py
│       ├── ast.py
│       ├── errors.py
│       ├── interpreter.py
│       ├── lexer.py
│       ├── main.py
│       ├── parser.py
│       ├── repl.py
│       ├── runtime.py
│       └── token.py
│
├── tests/
│   └── test_nova.py
│
├── pyproject.toml
├── README.md
└── LICENSE
```

---

# 🧱 Architecture

Nova follows a traditional programming-language pipeline:

```text
                 Nova Source Code
                        │
                        ▼
                     Lexer
                        │
                        ▼
                      Tokens
                        │
                        ▼
                     Parser
                        │
                        ▼
                       AST
                        │
                        ▼
                  Interpreter
                        │
                        ▼
                     Runtime
```

### Lexer

Converts Nova source code into tokens.

### Parser

Converts tokens into an Abstract Syntax Tree.

### AST

Represents the structure of the Nova program.

### Interpreter

Evaluates the AST using a tree-walking execution model.

### Runtime

Provides environments, functions, closures, built-ins and runtime values.

---

# 🗺️ Roadmap

## Phase 0.1 — Foundation

- [x] Token system
- [x] Lexer
- [x] AST
- [x] Parser
- [x] Runtime
- [x] Interpreter
- [x] Functions
- [x] Closures
- [x] Tests
- [x] REPL
- [x] CLI
- [x] CI

## Phase 0.2 — Diagnostics

- [ ] Improved syntax diagnostics
- [ ] Source snippets
- [ ] Caret diagnostics
- [ ] Better error categories
- [ ] Error recovery

## Phase 0.3 — Standard Library

- [ ] String utilities
- [ ] Array utilities
- [ ] Math utilities
- [ ] File utilities
- [ ] More built-in functions

## Phase 0.4 — Tooling

- [ ] Syntax highlighting
- [ ] Formatter
- [ ] Improved REPL
- [ ] Language documentation
- [ ] Example programs

## Phase 0.5 — Bytecode VM

- [ ] Bytecode instruction set
- [ ] Bytecode compiler
- [ ] Virtual machine
- [ ] VM tests
- [ ] Performance benchmarks

## Phase 1.0 — Stable Nova

- [ ] Stable language specification
- [ ] Complete standard library
- [ ] Production-quality diagnostics
- [ ] Complete documentation
- [ ] Release process

---

# 📚 Documentation

The `docs/` directory contains the language and project documentation.

Important documents include:

- Project Vision
- Requirements
- Language Design
- EBNF Grammar
- Architecture
- AST Design
- Runtime and Closures
- Error Handling
- REPL Design
- Bytecode VM Plan
- Standard Library Plan
- CLI Specification
- Test Plan
- Examples
- Development Roadmap
- Repository Structure
- Contributing Guide
- Project Checklist

---

# 🤝 Contributing

Nova is an evolving programming-language project.

Bug reports, ideas, documentation improvements and code contributions are welcome.

Before making significant changes to the language, review the relevant documents in `docs/`, especially:

```text
03_LANGUAGE_DESIGN.md
04_EBNF_GRAMMAR.md
05_ARCHITECTURE.md
15_DEVELOPMENT_ROADMAP.md
```

---

# 📜 License

Nova is released under the MIT License.

See [`LICENSE`](LICENSE) for details.

---

# 📊 Project Status

**Version:** `0.1.0`

**Status:** Alpha

Nova is currently an experimental programming-language project.

The syntax, runtime behavior and standard library may change during development.

---

## ⭐ Nova

Built from scratch with Python.

**Source:** https://github.com/devkazzu/Nova

from __future__ import annotations

from typing import Any

from .ast import (
    ArrayLiteral,
    Assignment,
    Binary,
    Block,
    Call,
    Expression,
    ExpressionStatement,
    FunctionDeclaration,
    FunctionExpression,
    Identifier,
    IfStatement,
    Index,
    LetStatement,
    Literal,
    Program,
    ReturnStatement,
    Statement,
    Unary,
    WhileStatement,
)
from .runtime import (
    Environment,
    NativeFunction,
    NovaFunction,
    NovaRuntimeError,
    ReturnSignal,
    check_number_operands,
    create_global_environment,
    is_equal,
    is_truthy,
)


class Interpreter:
    """
    Tree-walking interpreter for Nova.

    The interpreter evaluates the AST produced by Parser.
    """

    def __init__(
        self,
        environment: Environment | None = None,
    ):
        self.globals = (
            environment
            if environment is not None
            else create_global_environment()
        )

        self.environment = self.globals

    # =========================================================
    # PROGRAM
    # =========================================================

    def interpret(self, program: Program) -> Any:
        result = None

        try:
            for statement in program.declarations:
                result = self.execute(statement)

        except NovaRuntimeError:
            raise

        except ReturnSignal as signal:
            raise NovaRuntimeError(
                "Cannot use 'return' outside a function."
            ) from signal

        return result

    # =========================================================
    # STATEMENTS
    # =========================================================

    def execute(self, statement: Statement) -> Any:

        if isinstance(
            statement,
            ExpressionStatement,
        ):
            return self.evaluate(
                statement.expression
            )

        if isinstance(
            statement,
            LetStatement,
        ):
            return self.execute_let(
                statement
            )

        if isinstance(
            statement,
            Block,
        ):
            return self.execute_block(
                statement.statements,
                Environment(self.environment),
            )

        if isinstance(
            statement,
            IfStatement,
        ):
            return self.execute_if(
                statement
            )

        if isinstance(
            statement,
            WhileStatement,
        ):
            return self.execute_while(
                statement
            )

        if isinstance(
            statement,
            FunctionDeclaration,
        ):
            return self.execute_function_declaration(
                statement
            )

        if isinstance(
            statement,
            ReturnStatement,
        ):
            return self.execute_return(
                statement
            )

        raise NovaRuntimeError(
            f"Unknown statement type: "
            f"{type(statement).__name__}",
            statement.span,
        )

    # =========================================================
    # LET
    # =========================================================

    def execute_let(
        self,
        statement: LetStatement,
    ) -> None:

        if statement.initializer is None:
            value = None
        else:
            value = self.evaluate(
                statement.initializer
            )

        self.environment.define(
            statement.name,
            value,
        )

        return None

    # =========================================================
    # BLOCK
    # =========================================================

    def execute_block(
        self,
        statements: list[Statement],
        environment: Environment,
    ) -> Any:

        previous = self.environment

        try:
            self.environment = environment

            result = None

            for statement in statements:
                result = self.execute(statement)

            return result

        finally:
            self.environment = previous

    # =========================================================
    # IF
    # =========================================================

    def execute_if(
        self,
        statement: IfStatement,
    ) -> Any:

        condition = self.evaluate(
            statement.condition
        )

        if is_truthy(condition):
            return self.execute(
                statement.then_branch
            )

        if statement.else_branch is not None:
            return self.execute(
                statement.else_branch
            )

        return None

    # =========================================================
    # WHILE
    # =========================================================

    def execute_while(
        self,
        statement: WhileStatement,
    ) -> Any:

        result = None

        while is_truthy(
            self.evaluate(statement.condition)
        ):
            result = self.execute(
                statement.body
            )

        return result

    # =========================================================
    # FUNCTION DECLARATION
    # =========================================================

    def execute_function_declaration(
        self,
        statement: FunctionDeclaration,
    ) -> None:

        function = NovaFunction(
            name=statement.name,
            parameters=statement.parameters,
            body=statement.body,
            closure=self.environment,
        )

        self.environment.define(
            statement.name,
            function,
        )

        return None

    # =========================================================
    # RETURN
    # =========================================================

    def execute_return(
        self,
        statement: ReturnStatement,
    ) -> None:

        if statement.value is None:
            value = None
        else:
            value = self.evaluate(
                statement.value
            )

        raise ReturnSignal(value)

    # =========================================================
    # EXPRESSIONS
    # =========================================================

    def evaluate(
        self,
        expression: Expression,
    ) -> Any:

        if isinstance(
            expression,
            Literal,
        ):
            return expression.value

        if isinstance(
            expression,
            Identifier,
        ):
            return self.evaluate_identifier(
                expression
            )

        if isinstance(
            expression,
            Unary,
        ):
            return self.evaluate_unary(
                expression
            )

        if isinstance(
            expression,
            Binary,
        ):
            return self.evaluate_binary(
                expression
            )

        if isinstance(
            expression,
            Assignment,
        ):
            return self.evaluate_assignment(
                expression
            )

        if isinstance(
            expression,
            Call,
        ):
            return self.evaluate_call(
                expression
            )

        if isinstance(
            expression,
            Index,
        ):
            return self.evaluate_index(
                expression
            )

        if isinstance(
            expression,
            ArrayLiteral,
        ):
            return self.evaluate_array(
                expression
            )

        if isinstance(
            expression,
            FunctionExpression,
        ):
            return self.evaluate_function_expression(
                expression
            )

        raise NovaRuntimeError(
            f"Unknown expression type: "
            f"{type(expression).__name__}",
            expression.span,
        )

    # =========================================================
    # IDENTIFIER
    # =========================================================

    def evaluate_identifier(
        self,
        expression: Identifier,
    ) -> Any:

        try:
            return self.environment.get(
                expression.name
            )

        except NovaRuntimeError as error:
            raise NovaRuntimeError(
                error.message,
                expression.span,
            ) from error

    # =========================================================
    # UNARY
    # =========================================================

    def evaluate_unary(
        self,
        expression: Unary,
    ) -> Any:

        operator = expression.operator.type
        operand = self.evaluate(
            expression.operand
        )

        if operator.name == "BANG":
            return not is_truthy(operand)

        if operator.name == "MINUS":

            if not isinstance(
                operand,
                (int, float),
            ):
                raise NovaRuntimeError(
                    "Unary '-' requires a number.",
                    expression.span,
                )

            return -operand

        raise NovaRuntimeError(
            f"Unknown unary operator "
            f"'{expression.operator.lexeme}'.",
            expression.span,
        )

    # =========================================================
    # BINARY
    # =========================================================

    def evaluate_binary(
        self,
        expression: Binary,
    ) -> Any:

        operator = expression.operator.type
        operator_text = expression.operator.lexeme

        # -----------------------------------------------------
        # Short-circuit logical operators
        # -----------------------------------------------------

        if operator.name == "OR":
            left = self.evaluate(
                expression.left
            )

            if is_truthy(left):
                return True

            return is_truthy(
                self.evaluate(expression.right)
            )

        if operator.name == "AND":
            left = self.evaluate(
                expression.left
            )

            if not is_truthy(left):
                return False

            return is_truthy(
                self.evaluate(expression.right)
            )

        # -----------------------------------------------------
        # Normal binary operators
        # -----------------------------------------------------

        left = self.evaluate(
            expression.left
        )

        right = self.evaluate(
            expression.right
        )

        # Equality
        if operator.name == "EQUAL_EQUAL":
            return is_equal(
                left,
                right,
            )

        if operator.name == "NOT_EQUAL":
            return not is_equal(
                left,
                right,
            )

        # Addition
        if operator.name == "PLUS":

            if isinstance(left, str) and isinstance(right, str):
                return left + right

            if isinstance(
                left,
                (int, float),
            ) and isinstance(
                right,
                (int, float),
            ):
                return left + right

            raise NovaRuntimeError(
                "Operator '+' requires two numbers "
                "or two strings.",
                expression.span,
            )

        # Numeric operators
        if operator.name in {
            "MINUS",
            "STAR",
            "SLASH",
            "PERCENT",
            "LESS",
            "LESS_EQUAL",
            "GREATER",
            "GREATER_EQUAL",
        }:

            check_number_operands(
                left,
                right,
                operator_text,
            )

            if operator.name == "MINUS":
                return left - right

            if operator.name == "STAR":
                return left * right

            if operator.name == "SLASH":

                if right == 0:
                    raise NovaRuntimeError(
                        "Division by zero.",
                        expression.span,
                    )

                return left / right

            if operator.name == "PERCENT":

                if right == 0:
                    raise NovaRuntimeError(
                        "Modulo by zero.",
                        expression.span,
                    )

                return left % right

            if operator.name == "LESS":
                return left < right

            if operator.name == "LESS_EQUAL":
                return left <= right

            if operator.name == "GREATER":
                return left > right

            if operator.name == "GREATER_EQUAL":
                return left >= right

        raise NovaRuntimeError(
            f"Unknown binary operator "
            f"'{operator_text}'.",
            expression.span,
        )

    # =========================================================
    # ASSIGNMENT
    # =========================================================

    def evaluate_assignment(
        self,
        expression: Assignment,
    ) -> Any:

        value = self.evaluate(
            expression.value
        )

        try:
            self.environment.assign(
                expression.name,
                value,
            )

        except NovaRuntimeError as error:
            raise NovaRuntimeError(
                error.message,
                expression.span,
            ) from error

        return value

    # =========================================================
    # FUNCTION CALL
    # =========================================================

    def evaluate_call(
        self,
        expression: Call,
    ) -> Any:

        callee = self.evaluate(
            expression.callee
        )

        arguments = [
            self.evaluate(argument)
            for argument in expression.arguments
        ]

        if isinstance(
            callee,
            NovaFunction,
        ):
            try:
                return callee.call(
                    self,
                    arguments,
                )

            except NovaRuntimeError as error:
                if error.span is None:
                    error.span = expression.span

                raise

        if isinstance(
            callee,
            NativeFunction,
        ):
            try:
                return callee.call(
                    self,
                    arguments,
                )

            except NovaRuntimeError as error:
                if error.span is None:
                    error.span = expression.span

                raise

        raise NovaRuntimeError(
            "Can only call functions.",
            expression.span,
        )

    # =========================================================
    # INDEX
    # =========================================================

    def evaluate_index(
        self,
        expression: Index,
    ) -> Any:

        collection = self.evaluate(
            expression.collection
        )

        index = self.evaluate(
            expression.index
        )

        if not isinstance(
            index,
            int,
        ) or isinstance(
            index,
            bool,
        ):
            raise NovaRuntimeError(
                "Array index must be an integer.",
                expression.span,
            )

        if not isinstance(
            collection,
            (list, str),
        ):
            raise NovaRuntimeError(
                "Indexing requires an array or string.",
                expression.span,
            )

        try:
            return collection[index]

        except IndexError as error:
            raise NovaRuntimeError(
                f"Index {index} is out of range.",
                expression.span,
            ) from error

    # =========================================================
    # ARRAY
    # =========================================================

    def evaluate_array(
        self,
        expression: ArrayLiteral,
    ) -> list[Any]:

        return [
            self.evaluate(element)
            for element in expression.elements
        ]

    # =========================================================
    # ANONYMOUS FUNCTION
    # =========================================================

    def evaluate_function_expression(
        self,
        expression: FunctionExpression,
    ) -> NovaFunction:

        return NovaFunction(
            name="<anonymous>",
            parameters=expression.parameters,
            body=expression.body,
            closure=self.environment,
        )


def run(program: Program) -> Any:
    """
    Convenience function for executing a Nova program.
    """

    interpreter = Interpreter()

    return interpreter.interpret(
        program
    )

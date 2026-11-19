# apps/payroll/domain/rules_engine.py

import ast
import math
import logging

from decimal import (
    Decimal,
    ROUND_HALF_UP
)

from functools import lru_cache
from typing import Any, Dict, Callable, Set


logger = logging.getLogger(__name__)


class RulesEngine:
    """
    Enterprise Payroll Formula Engine
    =================================

    Features
    --------
    - Safe AST evaluation
    - No eval / exec
    - Decimal-safe financial calculations
    - Cached parsing
    - Secure whitelist functions
    - Runtime recursion protection
    - Formula complexity protection
    - DOS protection
    - Dependency extraction
    - ERP-grade payroll execution

    Designed for:
    - SAP-style payroll
    - Oracle Payroll
    - Odoo Payroll
    """

    # =====================================
    # ENGINE CONFIG
    # =====================================

    STRICT_MODE = False

    MAX_RECURSION_DEPTH = 50
    MAX_AST_NODES = 200
    MAX_FORMULA_LENGTH = 500
    MAX_POWER = 10
    MAX_DECIMAL_DIGITS = 18

    DECIMAL_PLACES = Decimal("0.01")

    # =====================================
    # SAFE OPERATORS
    # =====================================

    OPERATORS: Dict[Any, Callable] = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.Mod: lambda a, b: a % b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.USub: lambda a: -a,
    }

    # =====================================
    # SAFE COMPARISON OPERATORS
    # =====================================

    COMPARISON_OPERATORS: Dict[Any, Callable] = {
        ast.Gt: lambda a, b: a > b,
        ast.Lt: lambda a, b: a < b,
        ast.GtE: lambda a, b: a >= b,
        ast.LtE: lambda a, b: a <= b,
        ast.Eq: lambda a, b: a == b,
        ast.NotEq: lambda a, b: a != b,
    }

    # =====================================
    # SAFE HELPERS
    # =====================================

    @staticmethod
    def _round_function(value, digits=2):

        digits = int(digits)

        if digits < 0:
            raise ValueError(
                "ROUND digits cannot be negative"
            )

        quantizer = Decimal("1").scaleb(-digits)

        return Decimal(str(value)).quantize(
            quantizer,
            rounding=ROUND_HALF_UP
        )

    @staticmethod
    def _safe_div(a, b):

        b = Decimal(str(b))

        if b == 0:
            return Decimal("0.00")

        return Decimal(str(a)) / b

    # =====================================
    # SAFE FUNCTIONS
    # =====================================

    SAFE_FUNCTIONS = {

        # builtins
        "min": min,
        "max": max,
        "abs": abs,

        # payroll
        "PERCENT": lambda value, percent:
            Decimal(str(value))
            * Decimal(str(percent))
            / Decimal("100"),

        "ZERO_IF_NEGATIVE": lambda value:
            max(
                Decimal("0.00"),
                Decimal(str(value))
            ),

        "ROUND": _round_function.__func__,

        "SAFE_DIV": _safe_div.__func__,

        "GREATEST": max,
        "LEAST": min,

        "CEIL": lambda value:
            Decimal(str(math.ceil(value))),

        "FLOOR": lambda value:
            Decimal(str(math.floor(value))),

        "BETWEEN": lambda value, low, high:
            low <= value <= high,
    }

    # =====================================
    # ALLOWED AST NODES
    # =====================================

    ALLOWED_NODES = (

        # root
        ast.Expression,

        # values
        ast.Constant,
        ast.Name,
        ast.Load,

        # expressions
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.IfExp,
        ast.Call,

        # boolean
        ast.And,
        ast.Or,
        ast.Not,

        # operators
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.FloorDiv,
        ast.Pow,
        ast.USub,

        # comparisons
        ast.Gt,
        ast.Lt,
        ast.GtE,
        ast.LtE,
        ast.Eq,
        ast.NotEq,
    )

    # =====================================
    # PUBLIC API
    # =====================================

    @staticmethod
    def evaluate(
        expression: str,
        context: Dict[str, Any]
    ) -> Any:

        if not expression:
            return Decimal("0.00")

        expression = expression.strip()

        if len(expression) > RulesEngine.MAX_FORMULA_LENGTH:
            raise ValueError(
                "Formula exceeds maximum length"
            )

        RulesEngine.validate_formula(expression)

        tree = RulesEngine._parse(expression)

        return RulesEngine._eval(
            node=tree.body,
            context=context,
            depth=0
        )

    # =====================================
    # VALIDATE FORMULA
    # =====================================

    @staticmethod
    def validate_formula(expression: str) -> None:

        try:
            tree = ast.parse(expression, mode="eval")

        except SyntaxError as e:

            raise ValueError(
                f"Invalid formula syntax: {e}"
            )

        node_count = sum(
            1 for _ in ast.walk(tree)
        )

        if node_count > RulesEngine.MAX_AST_NODES:
            raise ValueError(
                "Formula too complex"
            )

        for node in ast.walk(tree):

            if not isinstance(
                node,
                RulesEngine.ALLOWED_NODES
            ):
                raise ValueError(
                    f"Unsafe AST node: "
                    f"{type(node).__name__}"
                )

            # prevent dunder access
            if isinstance(node, ast.Name):

                if node.id.startswith("__"):
                    raise ValueError(
                        "Unsafe variable access"
                    )

            # prevent attribute access
            if isinstance(node, ast.Attribute):
                raise ValueError(
                    "Attribute access not allowed"
                )

            # prevent imports
            if isinstance(
                node,
                (ast.Import, ast.ImportFrom)
            ):
                raise ValueError(
                    "Imports not allowed"
                )

    # =====================================
    # PARSE CACHE
    # =====================================

    @staticmethod
    @lru_cache(maxsize=5000)
    def _parse(expression: str):

        return ast.parse(
            expression,
            mode="eval"
        )

    # =====================================
    # MAIN EVALUATOR
    # =====================================

    @staticmethod
    def _eval(
        node,
        context: Dict[str, Any],
        depth: int = 0
    ):

        if depth > RulesEngine.MAX_RECURSION_DEPTH:
            raise ValueError(
                "Maximum recursion depth exceeded"
            )

        if not isinstance(
            node,
            RulesEngine.ALLOWED_NODES
        ):
            raise ValueError(
                f"Unsafe node: "
                f"{type(node).__name__}"
            )

        # =====================================
        # CONSTANT
        # =====================================

        if isinstance(node, ast.Constant):

            if isinstance(node.value, bool):
                return node.value

            return Decimal(
                str(node.value or 0)
            )

        # =====================================
        # VARIABLE
        # =====================================

        if isinstance(node, ast.Name):

            value = context.get(node.id)

            if value is None:

                if RulesEngine.STRICT_MODE:
                    raise ValueError(
                        f"Variable '{node.id}' "
                        f"not found"
                    )

                logger.warning(
                    f"Variable '{node.id}' "
                    f"not found in context"
                )

                return Decimal("0.00")

            if isinstance(value, bool):
                return value

            if isinstance(value, Decimal):
                return value

            if isinstance(
                value,
                (int, float, str)
            ):
                return Decimal(str(value))

            return value

        # =====================================
        # BINARY OPERATIONS
        # =====================================

        if isinstance(node, ast.BinOp):

            left = RulesEngine._eval(
                node.left,
                context,
                depth + 1
            )

            right = RulesEngine._eval(
                node.right,
                context,
                depth + 1
            )

            # bool arithmetic protection
            if isinstance(left, bool) or isinstance(right, bool):
                raise ValueError(
                    "Boolean values cannot "
                    "be used in arithmetic"
                )

            op_class = type(node.op)

            # power protection
            if op_class == ast.Pow:

                if abs(right) > RulesEngine.MAX_POWER:
                    raise ValueError(
                        "Power operation exceeds limit"
                    )

                result = left ** right

                RulesEngine._validate_numeric_limits(result)

                return RulesEngine._quantize(result)

            if op_class not in RulesEngine.OPERATORS:
                raise ValueError(
                    f"Operator not allowed: "
                    f"{op_class}"
                )

            try:

                result = RulesEngine.OPERATORS[
                    op_class
                ](left, right)

            except ZeroDivisionError:

                logger.warning(
                    "Division by zero detected"
                )

                return Decimal("0.00")

            RulesEngine._validate_numeric_limits(result)

            if isinstance(result, bool):
                return result

            return RulesEngine._quantize(result)

        # =====================================
        # UNARY OPERATIONS
        # =====================================

        if isinstance(node, ast.UnaryOp):

            if isinstance(node.op, ast.Not):

                operand = RulesEngine._eval(
                    node.operand,
                    context,
                    depth + 1
                )

                return not bool(operand)

            operand = RulesEngine._eval(
                node.operand,
                context,
                depth + 1
            )

            op_class = type(node.op)

            if op_class not in RulesEngine.OPERATORS:
                raise ValueError(
                    "Unary operator not allowed"
                )

            result = RulesEngine.OPERATORS[
                op_class
            ](operand)

            return RulesEngine._quantize(result)

        # =====================================
        # BOOLEAN OPERATIONS
        # =====================================

        if isinstance(node, ast.BoolOp):

            values = [

                RulesEngine._eval(
                    value,
                    context,
                    depth + 1
                )

                for value in node.values
            ]

            if isinstance(node.op, ast.And):
                return all(bool(v) for v in values)

            if isinstance(node.op, ast.Or):
                return any(bool(v) for v in values)

            raise ValueError(
                "Unsupported boolean operator"
            )

        # =====================================
        # COMPARISONS
        # =====================================

        if isinstance(node, ast.Compare):

            left = RulesEngine._eval(
                node.left,
                context,
                depth + 1
            )

            for op, comparator in zip(
                node.ops,
                node.comparators
            ):

                right = RulesEngine._eval(
                    comparator,
                    context,
                    depth + 1
                )

                op_class = type(op)

                if op_class not in RulesEngine.COMPARISON_OPERATORS:
                    raise ValueError(
                        "Unsupported comparison operator"
                    )

                result = RulesEngine.COMPARISON_OPERATORS[
                    op_class
                ](left, right)

                if not result:
                    return False

                left = right

            return True

        # =====================================
        # IF EXPRESSION
        # =====================================

        if isinstance(node, ast.IfExp):

            condition = RulesEngine._eval(
                node.test,
                context,
                depth + 1
            )

            if bool(condition):

                return RulesEngine._eval(
                    node.body,
                    context,
                    depth + 1
                )

            return RulesEngine._eval(
                node.orelse,
                context,
                depth + 1
            )

        # =====================================
        # FUNCTION CALL
        # =====================================

        if isinstance(node, ast.Call):

            if not isinstance(node.func, ast.Name):
                raise ValueError(
                    "Unsafe function call"
                )

            func_name = node.func.id

            # lazy IF
            if func_name == "IF":

                if len(node.args) != 3:
                    raise ValueError(
                        "IF requires 3 arguments"
                    )

                condition = RulesEngine._eval(
                    node.args[0],
                    context,
                    depth + 1
                )

                if bool(condition):

                    return RulesEngine._eval(
                        node.args[1],
                        context,
                        depth + 1
                    )

                return RulesEngine._eval(
                    node.args[2],
                    context,
                    depth + 1
                )

            if func_name not in RulesEngine.SAFE_FUNCTIONS:
                raise ValueError(
                    f"Function not allowed: "
                    f"{func_name}"
                )

            args = [

                RulesEngine._eval(
                    arg,
                    context,
                    depth + 1
                )

                for arg in node.args
            ]

            func = RulesEngine.SAFE_FUNCTIONS[
                func_name
            ]

            result = func(*args)

            RulesEngine._validate_numeric_limits(result)

            if isinstance(result, bool):
                return result

            return RulesEngine._quantize(result)

        raise ValueError(
            f"Unsupported expression: "
            f"{type(node).__name__}"
        )

    # =====================================
    # DECIMAL NORMALIZATION
    # =====================================

    @staticmethod
    def _quantize(value):

        if isinstance(value, bool):
            return value

        if not isinstance(
            value,
            (Decimal, int, float)
        ):
            return value

        return Decimal(
            str(value)
        ).quantize(
            RulesEngine.DECIMAL_PLACES,
            rounding=ROUND_HALF_UP
        )

    # =====================================
    # NUMERIC LIMIT PROTECTION
    # =====================================

    @staticmethod
    def _validate_numeric_limits(value):

        if not isinstance(value, Decimal):
            return

        digits = value.as_tuple().digits

        if len(digits) > RulesEngine.MAX_DECIMAL_DIGITS:
            raise ValueError(
                "Numeric value exceeds "
                "allowed limits"
            )

    # =====================================
    # DEPENDENCY EXTRACTION
    # =====================================

    @staticmethod
    def extract_dependencies(
        expression: str
    ) -> Set[str]:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        variables = set()

        for node in ast.walk(tree):

            if isinstance(node, ast.Name):

                if (
                    node.id
                    not in RulesEngine.SAFE_FUNCTIONS
                ):
                    variables.add(node.id)

        return variables
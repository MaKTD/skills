"""Calculator skill for the personal agent."""

import ast
import math
import operator
from typing import Any, Union

from .base_skill import BaseSkill

# Supported binary operators
_OPERATORS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Safe names available for expressions
_SAFE_NAMES: dict[str, Any] = {
    "abs": abs,
    "round": round,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "pi": math.pi,
    "e": math.e,
}


def _safe_eval(node: ast.AST) -> Union[int, float]:
    """Recursively evaluate a safe AST expression."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    if isinstance(node, ast.Name):
        if node.id in _SAFE_NAMES:
            return _SAFE_NAMES[node.id]  # type: ignore[return-value]
        raise ValueError(f"Unknown name: {node.id!r}")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _OPERATORS[op_type](left, right)  # type: ignore[operator]
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _safe_eval(node.operand)
        return _OPERATORS[op_type](operand)  # type: ignore[operator]
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are supported")
        func = _SAFE_NAMES.get(node.func.id)
        if not callable(func):
            raise ValueError(f"Unknown function: {node.func.id!r}")
        if node.keywords:
            raise ValueError("Keyword arguments are not supported in expressions")
        args = [_safe_eval(a) for a in node.args]
        return func(*args)  # type: ignore[operator]
    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


class CalculatorSkill(BaseSkill):
    """Skill that safely evaluates mathematical expressions."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Evaluate a mathematical expression. "
            "Supports +, -, *, /, //, %, ** and functions: "
            "abs, round, sqrt, sin, cos, tan, log, log10. "
            "Constants: pi, e."
        )

    def execute(self, *, expression: str) -> Union[int, float]:
        """Evaluate a mathematical expression string.

        Args:
            expression: A mathematical expression such as '2 + 3 * sqrt(4)'.

        Returns:
            The numeric result.

        Raises:
            ValueError: If the expression is invalid or uses unsupported features.
        """
        try:
            tree = ast.parse(expression.strip(), mode="eval")
        except SyntaxError as exc:
            raise ValueError(f"Invalid expression syntax: {exc}") from exc
        return _safe_eval(tree)

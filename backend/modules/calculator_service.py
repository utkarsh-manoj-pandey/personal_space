"""
Calculator Subsystem Service
High-precision mathematical and scientific computation engine.
Implements safe Abstract Syntax Tree (AST) expression evaluation, eliminating security risks,
scientific trigonometry/logarithms, and synchronized programmer base conversions (Hex, Dec, Oct, Bin).
"""

import ast
import math
import operator
from typing import List, Dict, Any
from ..database_manager import db_manager


class SafeMathEvaluator(ast.NodeVisitor):
    """
    Whitelisted AST evaluator that only parses and computes mathematical operations.
    Rejects any function calls, variable assignments, or malicious Python constructs.
    """
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.BitAnd: operator.and_,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.Invert: operator.invert,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
    }

    ALLOWED_FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "abs": abs,
        "round": round,
        "ceil": math.ceil,
        "floor": math.floor,
        "factorial": math.factorial,
        "deg2rad": math.radians,
        "rad2deg": math.degrees
    }

    ALLOWED_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "phi": (1 + 5**0.5) / 2
    }

    def evaluate(self, expr: str) -> float:
        clean_expr = expr.replace("^", "**").replace("×", "*").replace("÷", "/")
        tree = ast.parse(clean_expr, mode='eval')
        return self.visit(tree.body)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type in self.ALLOWED_OPERATORS:
            return self.ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in self.ALLOWED_OPERATORS:
            return self.ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants allowed")

    def visit_Name(self, node):
        name = node.id.lower()
        if name in self.ALLOWED_CONSTANTS:
            return self.ALLOWED_CONSTANTS[name]
        raise ValueError(f"Unknown variable: {name}")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function names supported")
        func_name = node.func.id.lower()
        if func_name not in self.ALLOWED_FUNCTIONS:
            raise ValueError(f"Unsupported mathematical function: {func_name}")
        args = [self.visit(arg) for arg in node.args]
        return self.ALLOWED_FUNCTIONS[func_name](*args)

    def generic_visit(self, node):
        raise ValueError(f"Syntax element not permitted: {type(node).__name__}")


class CalculatorService:
    DB = "calculator.db"

    def __init__(self):
        self.evaluator = SafeMathEvaluator()

    def calculate(self, expression: str, mode: str = "Scientific") -> Dict[str, Any]:
        """Safely evaluates an expression and stores it into history."""
        try:
            result_val = self.evaluator.evaluate(expression)
            # Format display
            if isinstance(result_val, float):
                if result_val.is_integer():
                    res_str = str(int(result_val))
                else:
                    res_str = f"{result_val:.8g}"
            else:
                res_str = str(result_val)

            # Store to history
            db_manager.execute_non_query(
                self.DB,
                "INSERT INTO calc_history (expression, result, mode) VALUES (?, ?, ?)",
                (expression, res_str, mode)
            )

            # Generate programmer representations if integer
            programmer_info = None
            try:
                int_val = int(float(res_str))
                programmer_info = {
                    "dec": str(int_val),
                    "hex": hex(int_val).upper(),
                    "bin": bin(int_val),
                    "oct": oct(int_val)
                }
            except Exception:
                pass

            return {
                "success": True,
                "expression": expression,
                "result": res_str,
                "programmer": programmer_info
            }

        except Exception as e:
            return {
                "success": False,
                "expression": expression,
                "error": str(e)
            }

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent calculation tape."""
        return db_manager.execute_query(
            self.DB,
            "SELECT * FROM calc_history ORDER BY id DESC LIMIT ?",
            (limit,)
        )

    def clear_history(self) -> bool:
        """Clear calculation history."""
        db_manager.execute_non_query(self.DB, "DELETE FROM calc_history")
        return True


calculator_service = CalculatorService()

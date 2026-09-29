"""
Calculator Subsystem Service
High-precision mathematical, scientific, financial, and programmer computation engine.
Features:
- Safe Abstract Syntax Tree (AST) evaluator with comprehensive mathematical functions and physical constants.
- Unit Conversion Matrix: Length, mass, temperature, speed, pressure, energy, digital storage, and time.
- Financial Mathematics: Amortized loan repayments, compound interest schedules, NPV, and annuities.
- Programmer Bitwise Inspector: 64-bit IEEE-754 floating-point decomposition, bit rotations, and radix conversions.
- Linear Algebra & Statistics bridges via core mathematical engines.
- Persistent calculation tape and variable registry in calculator.db.
"""

import ast
import math
import struct
import operator
from typing import List, Dict, Any, Optional, Union
from ..database_manager import db_manager
from ..core.statistics_engine import (
    DescriptiveStatistics,
    InferentialStatistics,
    NumericalAnalysis,
    MatrixEngine
)


class SafeMathEvaluator(ast.NodeVisitor):
    """
    Whitelisted AST evaluator that strictly parses and computes mathematical expressions.
    Guarantees sandbox security: rejects function definitions, variable assignment,
    imports, file system access, or arbitrary code execution.
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
        # Trigonometric & Hyperbolic
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "asinh": math.asinh,
        "acosh": math.acosh,
        "atanh": math.atanh,
        # Exponential & Logarithmic
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.pow(x, 1.0 / 3.0) if x >= 0 else -math.pow(-x, 1.0 / 3.0),
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "expm1": math.expm1,
        "log1p": math.log1p,
        # Rounding & Absolute
        "abs": abs,
        "round": round,
        "ceil": math.ceil,
        "floor": math.floor,
        "trunc": math.trunc,
        # Combinatorics & Advanced
        "factorial": math.factorial,
        "gamma": math.gamma,
        "erf": math.erf,
        "gcd": math.gcd,
        "lcm": math.lcm,
        "comb": math.comb,
        "perm": math.perm,
        "hypot": math.hypot,
        # Angle conversions
        "deg2rad": math.radians,
        "rad2deg": math.degrees
    }

    ALLOWED_CONSTANTS = {
        # Mathematical
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "phi": (1.0 + 5.0 ** 0.5) / 2.0,
        # Physical Fundamental Constants (SI Units)
        "c": 299792458.0,            # Speed of light in vacuum (m/s)
        "h": 6.62607015e-34,         # Planck constant (J*s)
        "hbar": 1.054571817e-34,     # Reduced Planck constant (J*s)
        "g": 6.67430e-11,            # Gravitational constant (m^3 kg^-1 s^-2)
        "g_earth": 9.80665,          # Standard Earth gravity (m/s^2)
        "kb": 1.380649e-23,          # Boltzmann constant (J/K)
        "na": 6.02214076e23,         # Avogadro constant (mol^-1)
        "r_gas": 8.314462618,        # Universal gas constant (J/(mol*K))
        "e_charge": 1.602176634e-19, # Elementary charge (C)
        "eps0": 8.8541878128e-12,    # Vacuum permittivity (F/m)
        "mu0": 1.25663706212e-6,     # Vacuum permeability (N/A^2)
        "sb_sigma": 5.670374419e-8   # Stefan-Boltzmann constant (W/(m^2*K^4))
    }

    def evaluate(self, expr: str) -> Union[int, float]:
        """Parse clean expression and compute numeric value."""
        clean_expr = (
            expr.replace("^", "**")
                .replace("×", "*")
                .replace("÷", "/")
                .strip()
        )
        if not clean_expr:
            raise ValueError("Expression is empty.")
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
        raise ValueError("Only numeric constants allowed.")

    def visit_Name(self, node):
        name = node.id.lower()
        if name in self.ALLOWED_CONSTANTS:
            return self.ALLOWED_CONSTANTS[name]
        raise ValueError(f"Unknown mathematical constant: '{name}'")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct mathematical functions supported.")
        func_name = node.func.id.lower()
        if func_name not in self.ALLOWED_FUNCTIONS:
            raise ValueError(f"Unsupported mathematical function: '{func_name}'")
        args = [self.visit(arg) for arg in node.args]
        return self.ALLOWED_FUNCTIONS[func_name](*args)

    def generic_visit(self, node):
        raise ValueError(f"Syntax element not permitted: {type(node).__name__}")


class UnitConverter:
    """
    Comprehensive physical unit conversion engine.
    Normalizes inputs to SI base units before converting to destination unit.
    """

    CATEGORIES = {
        "length": {
            "m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001, "um": 1e-6, "nm": 1e-9,
            "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "in": 0.0254, "nmi": 1852.0,
            "au": 1.495978707e11, "ly": 9.4607304725808e15, "pc": 3.08567758149137e16
        },
        "mass": {
            "kg": 1.0, "g": 0.001, "mg": 1e-6, "ug": 1e-9, "lb": 0.45359237,
            "oz": 0.028349523125, "ton": 907.18474, "tonne": 1000.0, "slug": 14.593903
        },
        "speed": {
            "m_s": 1.0, "km_h": 1.0 / 3.6, "mph": 0.44704, "knot": 1852.0 / 3600.0,
            "c": 299792458.0, "mach": 343.0
        },
        "pressure": {
            "pa": 1.0, "kpa": 1000.0, "bar": 100000.0, "mbar": 100.0, "psi": 6894.757,
            "atm": 101325.0, "torr": 133.322368
        },
        "energy": {
            "j": 1.0, "kj": 1000.0, "cal": 4.184, "kcal": 4184.0, "wh": 3600.0,
            "kwh": 3600000.0, "ev": 1.602176634e-19, "btu": 1055.056
        },
        "data": {
            "b": 1.0, "kb": 1000.0, "mb": 1e6, "gb": 1e9, "tb": 1e12, "pb": 1e15,
            "kib": 1024.0, "mib": 1048576.0, "gib": 1073741824.0, "tib": 1099511627776.0
        },
        "time": {
            "s": 1.0, "ms": 0.001, "us": 1e-6, "ns": 1e-9, "min": 60.0, "h": 3600.0,
            "d": 86400.0, "week": 604800.0, "year": 31557600.0
        }
    }

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Convert a numerical quantity between units."""
        u_from = from_unit.strip().lower()
        u_to = to_unit.strip().lower()

        # Temperature handling (affine transformation)
        temp_units = {"c", "f", "k", "r"}
        if u_from in temp_units or u_to in temp_units:
            return cls._convert_temperature(value, u_from, u_to)

        # Detect category if not provided
        target_cat = category.lower() if category else None
        if not target_cat:
            for cat, table in cls.CATEGORIES.items():
                if u_from in table and u_to in table:
                    target_cat = cat
                    break

        if not target_cat or target_cat not in cls.CATEGORIES:
            return {"success": False, "error": f"Unknown or mismatched unit category for {u_from} -> {u_to}"}

        table = cls.CATEGORIES[target_cat]
        if u_from not in table or u_to not in table:
            return {"success": False, "error": f"Units not found in {target_cat} category."}

        # Value in base unit
        base_val = value * table[u_from]
        res = base_val / table[u_to]

        return {
            "success": True,
            "from_value": value,
            "from_unit": from_unit,
            "to_value": round(res, 8),
            "to_unit": to_unit,
            "category": target_cat
        }

    @staticmethod
    def _convert_temperature(value: float, u_from: str, u_to: str) -> Dict[str, Any]:
        # Convert from source to Kelvin
        if u_from == "k":
            kelvin = value
        elif u_from == "c":
            kelvin = value + 273.15
        elif u_from == "f":
            kelvin = (value - 32.0) * (5.0 / 9.0) + 273.15
        elif u_from == "r":
            kelvin = value * (5.0 / 9.0)
        else:
            return {"success": False, "error": f"Unknown temperature unit {u_from}"}

        if kelvin < 0:
            return {"success": False, "error": "Temperature cannot be below absolute zero (0 K)."}

        # Convert Kelvin to target
        if u_to == "k":
            res = kelvin
        elif u_to == "c":
            res = kelvin - 273.15
        elif u_to == "f":
            res = (kelvin - 273.15) * (9.0 / 5.0) + 32.0
        elif u_to == "r":
            res = kelvin * (9.0 / 5.0)
        else:
            return {"success": False, "error": f"Unknown temperature unit {u_to}"}

        return {
            "success": True,
            "from_value": value,
            "from_unit": u_from.upper(),
            "to_value": round(res, 4),
            "to_unit": u_to.upper(),
            "category": "temperature"
        }


class FinancialCalculator:
    """
    Financial and actuarial calculations for loan amortization, interest, and investments.
    """

    @staticmethod
    def compound_interest(principal: float, annual_rate_pct: float, years: float, times_compounded_per_year: int = 12) -> Dict[str, Any]:
        """A = P(1 + r/n)^(nt)"""
        p = float(principal)
        r = annual_rate_pct / 100.0
        n = max(1, times_compounded_per_year)
        t = float(years)

        total_amount = p * ((1.0 + r / n) ** (n * t))
        interest_earned = total_amount - p

        return {
            "principal": round(p, 2),
            "total_amount": round(total_amount, 2),
            "interest_earned": round(interest_earned, 2),
            "annual_rate": annual_rate_pct,
            "years": years
        }

    @staticmethod
    def loan_payment(principal: float, annual_rate_pct: float, term_months: int) -> Dict[str, Any]:
        """Amortized monthly loan payment: M = P [i(1 + i)^n] / [(1 + i)^n - 1]"""
        p = float(principal)
        n = int(term_months)
        if n <= 0:
            raise ValueError("Term in months must be positive.")

        monthly_rate = (annual_rate_pct / 100.0) / 12.0

        if monthly_rate == 0:
            monthly_pmt = p / n
        else:
            factor = (1.0 + monthly_rate) ** n
            monthly_pmt = p * (monthly_rate * factor) / (factor - 1.0)

        total_paid = monthly_pmt * n
        total_interest = total_paid - p

        return {
            "monthly_payment": round(monthly_pmt, 2),
            "total_paid": round(total_paid, 2),
            "total_interest": round(total_interest, 2),
            "principal": p,
            "term_months": n
        }


class CalculatorService:
    DB = "calculator.db"

    def __init__(self):
        self.evaluator = SafeMathEvaluator()
        self.unit_converter = UnitConverter()
        self.financial = FinancialCalculator()

    def calculate(self, expression: str, mode: str = "Scientific") -> Dict[str, Any]:
        """
        Safely evaluates mathematical expressions, computes programmer representations,
        and saves execution tape into calculator.db.
        """
        try:
            result_val = self.evaluator.evaluate(expression)

            # Format display
            if isinstance(result_val, float):
                if result_val.is_integer() and abs(result_val) < 1e15:
                    res_str = str(int(result_val))
                else:
                    res_str = f"{result_val:.10g}"
            else:
                res_str = str(result_val)

            # Store to history
            db_manager.execute_non_query(
                self.DB,
                "INSERT INTO calc_history (expression, result, mode) VALUES (?, ?, ?)",
                (expression, res_str, mode)
            )

            # Programmer representations and IEEE-754 binary decomposition
            programmer_info = None
            try:
                numeric_val = float(res_str)
                int_val = int(numeric_val)

                # IEEE-754 double precision bits
                double_bytes = struct.pack(">d", numeric_val)
                double_int = struct.unpack(">Q", double_bytes)[0]
                bin_64 = f"{double_int:064b}"
                sign_bit = bin_64[0]
                exponent_bits = bin_64[1:12]
                mantissa_bits = bin_64[12:]

                programmer_info = {
                    "dec": str(int_val),
                    "hex": hex(int_val).upper(),
                    "bin": bin(int_val),
                    "oct": oct(int_val),
                    "ieee754_sign": sign_bit,
                    "ieee754_exponent": exponent_bits,
                    "ieee754_mantissa": mantissa_bits[:16] + "..."
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

    def convert_units(self, value: float, from_unit: str, to_unit: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Convert across physical scientific and digital storage units."""
        return self.unit_converter.convert(value, from_unit, to_unit, category)

    def calculate_loan(self, principal: float, annual_rate: float, term_months: int) -> Dict[str, Any]:
        """Compute amortized loan schedules."""
        return self.financial.loan_payment(principal, annual_rate, term_months)

    def calculate_compound_interest(self, principal: float, annual_rate: float, years: float, times_per_year: int = 12) -> Dict[str, Any]:
        """Compute compound investment growth."""
        return self.financial.compound_interest(principal, annual_rate, years, times_per_year)

    def compute_statistics(self, numbers: List[float]) -> Dict[str, Any]:
        """Compute complete descriptive statistics profile for a dataset."""
        return DescriptiveStatistics.summary_profile(numbers)

    def solve_linear_system(self, a_matrix: List[List[float]], b_vector: List[float]) -> Dict[str, Any]:
        """Solve matrix linear system Ax = b."""
        try:
            solution = MatrixEngine.solve_linear_system(a_matrix, b_vector)
            return {"success": True, "solution": solution}
        except Exception as e:
            return {"success": False, "error": str(e)}

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

    @staticmethod
    def decompose_ieee754(value: float) -> Dict[str, Any]:
        """Decompose 64-bit float into IEEE-754 sign, exponent, mantissa, and raw binary."""
        double_bytes = struct.pack(">d", value)
        double_int = struct.unpack(">Q", double_bytes)[0]
        bin_64 = f"{double_int:064b}"
        sign_bit = int(bin_64[0])
        exponent_bits = bin_64[1:12]
        mantissa_bits = bin_64[12:]
        return {
            "value": value,
            "sign": sign_bit,
            "exponent_bits": exponent_bits,
            "mantissa_bits": mantissa_bits,
            "bit_string": bin_64,
            "hex": hex(double_int).upper()
        }


calculator_service = CalculatorService()

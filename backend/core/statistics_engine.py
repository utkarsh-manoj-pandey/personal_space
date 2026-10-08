"""
Aether Core Scientific Statistics & Numerical Analysis Engine
Pure Python mathematical framework featuring:
- Descriptive Statistics: Mean, geometric/harmonic mean, median, mode, variance, std dev, skewness, kurtosis, quartiles, IQR.
- Inferential Statistics: Pearson correlation, Spearman rank correlation, covariance, OLS linear regression, R-squared.
- Numerical Analysis: Simpson's 1/3 Rule & Trapezoidal Integration, Central Difference Differentiation, Newton-Raphson Solver, RK4 ODE solver.
- Matrix Linear Algebra: Transpose, Determinant, Inversion via Gaussian Elimination, System Solver (Ax = b), Eigenvalues for 2x2 and 3x3.
- Polynomial Engine: Horner evaluation, differentiation, polynomial least-squares curve fitting.
"""

import math
from typing import List, Dict, Any, Optional, Tuple, Callable


# =============================================================================
# 1. DESCRIPTIVE STATISTICS
# =============================================================================

class DescriptiveStatistics:
    """
    Comprehensive single-variable statistical metrics analyzer.
    All calculations are deterministic, pure Python, zero external binary dependency.
    """

    @staticmethod
    def mean(data: List[float]) -> float:
        if not data:
            raise ValueError("Cannot calculate mean of empty dataset.")
        return sum(data) / len(data)

    @staticmethod
    def geometric_mean(data: List[float]) -> float:
        if not data:
            raise ValueError("Dataset cannot be empty.")
        if any(x <= 0 for x in data):
            raise ValueError("All values must be strictly positive for geometric mean.")
        log_sum = sum(math.log(x) for x in data)
        return math.exp(log_sum / len(data))

    @staticmethod
    def harmonic_mean(data: List[float]) -> float:
        if not data:
            raise ValueError("Dataset cannot be empty.")
        if any(x <= 0 for x in data):
            raise ValueError("All values must be strictly positive for harmonic mean.")
        return len(data) / sum(1.0 / x for x in data)

    @staticmethod
    def median(data: List[float]) -> float:
        if not data:
            raise ValueError("Dataset cannot be empty.")
        s = sorted(data)
        n = len(s)
        mid = n // 2
        if n % 2 == 1:
            return float(s[mid])
        return (s[mid - 1] + s[mid]) / 2.0

    @staticmethod
    def mode(data: List[float]) -> Optional[float]:
        if not data:
            return None
        counts: Dict[float, int] = {}
        for x in data:
            counts[x] = counts.get(x, 0) + 1
        max_count = max(counts.values())
        if max_count == 1 and len(data) > 1:
            return None  # No repeated mode
        for val, count in counts.items():
            if count == max_count:
                return val
        return None

    @staticmethod
    def variance(data: List[float], sample: bool = True) -> float:
        if len(data) < 2:
            return 0.0
        m = DescriptiveStatistics.mean(data)
        denom = (len(data) - 1) if sample else len(data)
        return sum((x - m) ** 2 for x in data) / denom

    @staticmethod
    def standard_deviation(data: List[float], sample: bool = True) -> float:
        return math.sqrt(DescriptiveStatistics.variance(data, sample=sample))

    @staticmethod
    def standard_error(data: List[float]) -> float:
        if len(data) < 2:
            return 0.0
        return DescriptiveStatistics.standard_deviation(data, sample=True) / math.sqrt(len(data))

    @staticmethod
    def skewness(data: List[float]) -> float:
        """Fisher-Pearson standardized third moment coefficient."""
        n = len(data)
        if n < 3:
            return 0.0
        m = DescriptiveStatistics.mean(data)
        s = DescriptiveStatistics.standard_deviation(data, sample=True)
        if s == 0:
            return 0.0
        m3 = sum((x - m) ** 3 for x in data) / n
        return m3 / (s ** 3)

    @staticmethod
    def kurtosis(data: List[float]) -> float:
        """Excess kurtosis (normal distribution = 0.0)."""
        n = len(data)
        if n < 4:
            return 0.0
        m = DescriptiveStatistics.mean(data)
        s = DescriptiveStatistics.standard_deviation(data, sample=True)
        if s == 0:
            return 0.0
        m4 = sum((x - m) ** 4 for x in data) / n
        return (m4 / (s ** 4)) - 3.0

    @staticmethod
    def quartiles(data: List[float]) -> Tuple[float, float, float]:
        """Returns (Q1, Q2, Q3) using standard linear interpolation."""
        if not data:
            raise ValueError("Dataset cannot be empty.")
        s = sorted(data)
        n = len(s)

        def _percentile(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return float(s[int(k)])
            d0 = s[int(f)] * (c - k)
            d1 = s[int(c)] * (k - f)
            return d0 + d1

        return _percentile(0.25), _percentile(0.50), _percentile(0.75)

    @staticmethod
    def interquartile_range(data: List[float]) -> float:
        q1, _, q3 = DescriptiveStatistics.quartiles(data)
        return q3 - q1

    @classmethod
    def summary_profile(cls, data: List[float]) -> Dict[str, Any]:
        """Generate comprehensive statistical telemetry profile."""
        if not data:
            return {"error": "Dataset is empty"}
        q1, q2, q3 = cls.quartiles(data)
        mean_val = cls.mean(data)
        std_val = cls.standard_deviation(data)

        # Detect outliers using 1.5 * IQR rule
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = [x for x in data if x < lower_bound or x > upper_bound]

        return {
            "count": len(data),
            "sum": round(sum(data), 6),
            "min": min(data),
            "max": max(data),
            "range": max(data) - min(data),
            "mean": round(mean_val, 6),
            "median": round(q2, 6),
            "mode": cls.mode(data),
            "variance": round(cls.variance(data), 6),
            "std_deviation": round(std_val, 6),
            "std_error": round(cls.standard_error(data), 6),
            "skewness": round(cls.skewness(data), 6),
            "kurtosis": round(cls.kurtosis(data), 6),
            "q1": round(q1, 6),
            "q2": round(q2, 6),
            "q3": round(q3, 6),
            "iqr": round(iqr, 6),
            "outliers_count": len(outliers),
            "outliers": outliers
        }


# =============================================================================
# 2. INFERENTIAL & BIVARIATE STATISTICS
# =============================================================================

class InferentialStatistics:
    """
    Two-variable correlation, covariance, and linear regression models.
    """

    @staticmethod
    def covariance(x: List[float], y: List[float], sample: bool = True) -> float:
        if len(x) != len(y) or len(x) < 2:
            raise ValueError("Datasets must have equal lengths and at least 2 elements.")
        n = len(x)
        mx = DescriptiveStatistics.mean(x)
        my = DescriptiveStatistics.mean(y)
        denom = (n - 1) if sample else n
        return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / denom

    @staticmethod
    def pearson_correlation(x: List[float], y: List[float]) -> float:
        """Pearson correlation coefficient r in [-1.0, 1.0]."""
        cov = InferentialStatistics.covariance(x, y, sample=True)
        sx = DescriptiveStatistics.standard_deviation(x, sample=True)
        sy = DescriptiveStatistics.standard_deviation(y, sample=True)
        if sx == 0 or sy == 0:
            return 0.0
        return max(-1.0, min(1.0, cov / (sx * sy)))

    @staticmethod
    def spearman_rank_correlation(x: List[float], y: List[float]) -> float:
        """Spearman monotonic rank correlation rho."""
        if len(x) != len(y) or len(x) < 2:
            raise ValueError("Datasets must have identical lengths.")

        def _rank(vals: List[float]) -> List[float]:
            indexed = sorted(enumerate(vals), key=lambda item: item[1])
            ranks = [0.0] * len(vals)
            i = 0
            while i < len(vals):
                j = i
                while j + 1 < len(vals) and indexed[j + 1][1] == indexed[i][1]:
                    j += 1
                avg_rank = (i + j + 2) / 2.0
                for k in range(i, j + 1):
                    ranks[indexed[k][0]] = avg_rank
                i = j + 1
            return ranks

        rx = _rank(x)
        ry = _rank(y)
        return InferentialStatistics.pearson_correlation(rx, ry)

    @classmethod
    def linear_regression(cls, x: List[float], y: List[float]) -> Dict[str, Any]:
        """
        Ordinary Least Squares (OLS) Linear Regression: y = slope * x + intercept.
        Returns slope, intercept, R-squared, standard error, and Pearson correlation.
        """
        if len(x) != len(y) or len(x) < 2:
            return {"error": "Invalid dataset dimensions"}

        n = len(x)
        mx = sum(x) / n
        my = sum(y) / n

        ss_xy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        ss_xx = sum((x[i] - mx) ** 2 for i in range(n))
        ss_yy = sum((y[i] - my) ** 2 for i in range(n))

        if ss_xx == 0:
            return {"error": "Zero variance in independent variable x."}

        slope = ss_xy / ss_xx
        intercept = my - slope * mx

        # R-squared calculation
        r = ss_xy / math.sqrt(ss_xx * ss_yy) if ss_yy > 0 else 0.0
        r_squared = r ** 2

        # Residual standard error
        residuals = [y[i] - (slope * x[i] + intercept) for i in range(n)]
        sse = sum(res ** 2 for res in residuals)
        deg_freedom = n - 2
        std_err = math.sqrt(sse / deg_freedom) if deg_freedom > 0 else 0.0

        return {
            "slope": round(slope, 6),
            "intercept": round(intercept, 6),
            "r_squared": round(r_squared, 6),
            "correlation_r": round(r, 6),
            "residual_std_error": round(std_err, 6),
            "equation": f"y = {slope:.4f}x + {intercept:.4f}",
            "sample_size": n
        }


# =============================================================================
# 3. NUMERICAL ANALYSIS
# =============================================================================

class NumericalAnalysis:
    """
    High-precision numerical methods for calculus, root-finding, and differential equations.
    """

    @staticmethod
    def simpson_integrate(func: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
        r"""
        Composite Simpson's 1/3 Rule for numerical definite integration: \int_a^b f(x) dx.
        n must be even.
        """
        if n % 2 != 0:
            n += 1
        h = (b - a) / n
        s = func(a) + func(b)

        for i in range(1, n, 2):
            s += 4.0 * func(a + i * h)
        for i in range(2, n - 1, 2):
            s += 2.0 * func(a + i * h)

        return (h / 3.0) * s

    @staticmethod
    def trapezoidal_integrate(func: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
        """Composite trapezoidal numerical integration."""
        h = (b - a) / n
        s = 0.5 * (func(a) + func(b))
        for i in range(1, n):
            s += func(a + i * h)
        return h * s

    @staticmethod
    def central_difference_derivative(func: Callable[[float], float], x: float, h: float = 1e-6) -> float:
        """
        High-precision 4th-order central difference numerical derivative f'(x):
        f'(x) \approx (-f(x+2h) + 8f(x+h) - 8f(x-h) + f(x-2h)) / (12h)
        """
        return (-func(x + 2 * h) + 8 * func(x + h) - 8 * func(x - h) + func(x - 2 * h)) / (12 * h)

    @staticmethod
    def newton_raphson_root(
        func: Callable[[float], float],
        initial_guess: float,
        tol: float = 1e-8,
        max_iter: int = 100
    ) -> Dict[str, Any]:
        """
        Newton-Raphson numerical root finder: x_{n+1} = x_n - f(x_n)/f'(x_n).
        """
        x = initial_guess
        for i in range(max_iter):
            y = func(x)
            if abs(y) < tol:
                return {"converged": True, "root": round(x, 8), "iterations": i + 1, "f_value": y}
            dy = NumericalAnalysis.central_difference_derivative(func, x)
            if abs(dy) < 1e-12:
                return {"converged": False, "error": "Derivative near zero, iteration halted.", "root": x}
            x = x - y / dy

        return {"converged": False, "error": "Maximum iterations reached", "root": x}

    @staticmethod
    def runge_kutta_4(
        dydt: Callable[[float, float], float],
        t0: float,
        y0: float,
        t_end: float,
        steps: int = 100
    ) -> List[Tuple[float, float]]:
        """
        Classic Runge-Kutta 4th Order (RK4) ODE solver for dy/dt = f(t, y).
        Returns list of (t, y) trajectory points.
        """
        h = (t_end - t0) / steps
        t = t0
        y = y0
        trajectory = [(t, y)]

        for _ in range(steps):
            k1 = dydt(t, y)
            k2 = dydt(t + 0.5 * h, y + 0.5 * h * k1)
            k3 = dydt(t + 0.5 * h, y + 0.5 * h * k2)
            k4 = dydt(t + h, y + h * k3)

            y += (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            t += h
            trajectory.append((round(t, 6), round(y, 6)))

        return trajectory


# =============================================================================
# 4. MATRIX LINEAR ALGEBRA
# =============================================================================

class MatrixEngine:
    """
    I have written this part of code because solving linear systems (Ax = b) and computing matrix
    inverses is essential for polynomial curve fitting, navigation projections, and econometric models.
    Implementing this natively in pure Python gives our workstation scientific computing power
    with zero bloat or native C dependency conflicts!
    """

    @staticmethod
    def transpose(matrix: List[List[float]]) -> List[List[float]]:
        if not matrix or not matrix[0]:
            return []
        rows = len(matrix)
        cols = len(matrix[0])
        return [[matrix[r][c] for r in range(rows)] for c in range(cols)]

    @staticmethod
    def multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        rows_a = len(a)
        cols_a = len(a[0])
        rows_b = len(b)
        cols_b = len(b[0])

        if cols_a != rows_b:
            raise ValueError(f"Incompatible matrix dimensions: ({rows_a}x{cols_a}) and ({rows_b}x{cols_b})")

        res = [[0.0] * cols_b for _ in range(rows_a)]
        for i in range(rows_a):
            for k in range(cols_a):
                r = a[i][k]
                for j in range(cols_b):
                    res[i][j] += r * b[k][j]
        return res

    @staticmethod
    def determinant(matrix: List[List[float]]) -> float:
        """Compute determinant of square matrix using Gaussian LU decomposition."""
        n = len(matrix)
        if any(len(row) != n for row in matrix):
            raise ValueError("Determinant requires a square matrix.")

        # Special fast cases
        if n == 1:
            return matrix[0][0]
        if n == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        if n == 3:
            return (
                matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) -
                matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) +
                matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
            )

        # General n x n Gaussian elimination
        m = [row[:] for row in matrix]
        det = 1.0

        for col in range(n):
            # Pivot selection
            pivot_row = col
            for r in range(col + 1, n):
                if abs(m[r][col]) > abs(m[pivot_row][col]):
                    pivot_row = r

            if abs(m[pivot_row][col]) < 1e-14:
                return 0.0

            if pivot_row != col:
                m[col], m[pivot_row] = m[pivot_row], m[col]
                det = -det

            pivot = m[col][col]
            det *= pivot

            for r in range(col + 1, n):
                factor = m[r][col] / pivot
                for c in range(col + 1, n):
                    m[r][c] -= factor * m[col][c]

        return det

    @staticmethod
    def solve_linear_system(a: List[List[float]], b: List[float]) -> List[float]:
        """
        Solves the system Ax = b using Gaussian elimination with partial pivoting.
        """
        n = len(a)
        if any(len(row) != n for row in a) or len(b) != n:
            raise ValueError("Matrix A must be square and match vector b length.")

        # Create augmented matrix [A | b]
        aug = [a[i][:] + [b[i]] for i in range(n)]

        for col in range(n):
            # Partial pivot
            pivot_row = col
            for r in range(col + 1, n):
                if abs(aug[r][col]) > abs(aug[pivot_row][col]):
                    pivot_row = r

            if abs(aug[pivot_row][col]) < 1e-12:
                raise ValueError("Matrix is singular or near-singular, unique solution does not exist.")

            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

            pivot = aug[col][col]
            for c in range(col, n + 1):
                aug[col][c] /= pivot

            for r in range(n):
                if r != col:
                    factor = aug[r][col]
                    for c in range(col, n + 1):
                        aug[r][c] -= factor * aug[col][c]

        return [round(aug[i][n], 8) for i in range(n)]

    @staticmethod
    def invert(matrix: List[List[float]]) -> List[List[float]]:
        """Invert square matrix via Gauss-Jordan elimination against identity matrix."""
        n = len(matrix)
        if any(len(row) != n for row in matrix):
            raise ValueError("Only square matrices can be inverted.")

        # Augmented matrix [A | I]
        aug = [matrix[i][:] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        for col in range(n):
            pivot_row = col
            for r in range(col + 1, n):
                if abs(aug[r][col]) > abs(aug[pivot_row][col]):
                    pivot_row = r

            if abs(aug[pivot_row][col]) < 1e-12:
                raise ValueError("Matrix is singular and cannot be inverted.")

            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

            pivot = aug[col][col]
            for c in range(2 * n):
                aug[col][c] /= pivot

            for r in range(n):
                if r != col:
                    factor = aug[r][col]
                    for c in range(col, 2 * n):
                        aug[r][c] -= factor * aug[col][c]

        return [[round(aug[r][c + n], 8) for c in range(n)] for r in range(n)]

    @staticmethod
    def eigenvalues_2x2(matrix: List[List[float]]) -> Tuple[complex, complex]:
        """Compute exact eigenvalues for a 2x2 matrix."""
        a, b = matrix[0][0], matrix[0][1]
        c, d = matrix[1][0], matrix[1][1]
        tr = a + d
        det = a * d - b * c
        disc = tr * tr - 4 * det
        if disc >= 0:
            root = math.sqrt(disc)
            return ((tr + root) / 2.0, (tr - root) / 2.0)
        else:
            root_im = math.sqrt(-disc)
            return (complex(tr / 2.0, root_im / 2.0), complex(tr / 2.0, -root_im / 2.0))


# =============================================================================
# 5. POLYNOMIAL ENGINE
# =============================================================================

class PolynomialEngine:
    """
    Polynomial operations and least-squares curve fitting.
    Coefficients stored in descending degree: [a_n, a_{n-1}, ..., a_1, a_0].
    """

    @staticmethod
    def evaluate(coeffs: List[float], x: float) -> float:
        """Horner's method for O(N) polynomial evaluation."""
        res = 0.0
        for c in coeffs:
            res = res * x + c
        return res

    @staticmethod
    def differentiate(coeffs: List[float]) -> List[float]:
        """Compute derivative coefficients."""
        n = len(coeffs) - 1
        if n <= 0:
            return [0.0]
        return [coeffs[i] * (n - i) for i in range(n)]

    @staticmethod
    def fit_polynomial(x: List[float], y: List[float], degree: int = 2) -> List[float]:
        """
        Least-squares polynomial curve fit of given degree.
        Solves normal equations (X^T * X) * c = X^T * y.
        """
        if len(x) != len(y) or len(x) <= degree:
            raise ValueError("Sample points count must strictly exceed polynomial degree.")

        m = degree + 1
        # Build normal equations matrix
        # sum(x^(i+j)) * c_j = sum(y * x^i)
        powers = [sum(val ** p for val in x) for p in range(2 * degree + 1)]
        mat = [[powers[i + j] for j in range(m)] for i in range(m)]
        rhs = [sum(y[k] * (x[k] ** i) for k in range(len(x))) for i in range(m)]

        # Solves for ascending order coefficients [c_0, c_1, ..., c_degree]
        c_asc = MatrixEngine.solve_linear_system(mat, rhs)
        # Return in descending order standard
        return list(reversed(c_asc))

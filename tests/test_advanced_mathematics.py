"""
Automated Test Suite for Scientific Mathematics & Statistics
Validates descriptive/inferential statistics, numerical calculus,
matrix linear algebra, and polynomial curve fitting.
"""

import math
import pytest
from backend.core.statistics_engine import (
    DescriptiveStatistics,
    InferentialStatistics,
    NumericalAnalysis,
    MatrixEngine,
    PolynomialEngine
)


# =============================================================================
# 1. DESCRIPTIVE STATISTICS TESTS
# =============================================================================

def test_descriptive_statistics_metrics():
    data = [12.0, 15.0, 12.0, 18.0, 22.0, 25.0, 30.0]
    mean_val = DescriptiveStatistics.mean(data)
    assert round(mean_val, 2) == 19.14

    median_val = DescriptiveStatistics.median(data)
    assert median_val == 18.0

    mode_val = DescriptiveStatistics.mode(data)
    assert mode_val == 12.0

    var_val = DescriptiveStatistics.variance(data, sample=True)
    std_val = DescriptiveStatistics.standard_deviation(data, sample=True)
    assert round(std_val ** 2, 4) == round(var_val, 4)

    # Quartiles
    q1, q2, q3 = DescriptiveStatistics.quartiles(data)
    assert q1 < q2 < q3
    assert q2 == median_val

    # Summary profile
    profile = DescriptiveStatistics.summary_profile(data)
    assert profile["count"] == 7
    assert profile["min"] == 12.0
    assert profile["max"] == 30.0
    assert "skewness" in profile
    assert "kurtosis" in profile


def test_geometric_and_harmonic_mean():
    data = [2.0, 4.0, 8.0]
    geo = DescriptiveStatistics.geometric_mean(data)
    assert round(geo, 4) == 4.0

    har = DescriptiveStatistics.harmonic_mean(data)
    assert round(har, 4) == round(3.0 / (1/2 + 1/4 + 1/8), 4)


# =============================================================================
# 2. INFERENTIAL & BIVARIATE TESTS
# =============================================================================

def test_correlation_and_linear_regression():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]  # Perfect linear correlation: y = 2x

    r = InferentialStatistics.pearson_correlation(x, y)
    assert round(r, 4) == 1.0

    rho = InferentialStatistics.spearman_rank_correlation(x, y)
    assert round(rho, 4) == 1.0

    reg = InferentialStatistics.linear_regression(x, y)
    assert round(reg["slope"], 4) == 2.0
    assert round(reg["intercept"], 4) == 0.0
    assert round(reg["r_squared"], 4) == 1.0


# =============================================================================
# 3. NUMERICAL ANALYSIS TESTS
# =============================================================================

def test_numerical_integration_and_differentiation():
    # \int_0^\pi \sin(x) dx = 2.0
    integral = NumericalAnalysis.simpson_integrate(math.sin, 0, math.pi, n=1000)
    assert abs(integral - 2.0) < 1e-6

    # Derivative of x^3 at x = 2 is 3 * 2^2 = 12
    cube_func = lambda x: x ** 3
    d_val = NumericalAnalysis.central_difference_derivative(cube_func, 2.0)
    assert abs(d_val - 12.0) < 1e-4

    # Newton-Raphson root of x^2 - 4 = 0 -> root = 2.0
    poly_root = NumericalAnalysis.newton_raphson_root(lambda x: x ** 2 - 4, initial_guess=3.0)
    assert poly_root["converged"] is True
    assert abs(poly_root["root"] - 2.0) < 1e-6

    # Runge-Kutta 4th Order: dy/dt = y, y(0)=1 -> y(t) = e^t
    traj = NumericalAnalysis.runge_kutta_4(lambda t, y: y, t0=0, y0=1.0, t_end=1.0, steps=100)
    final_t, final_y = traj[-1]
    assert abs(final_y - math.e) < 1e-4


# =============================================================================
# 4. MATRIX LINEAR ALGEBRA TESTS
# =============================================================================

def test_matrix_operations_and_solver():
    # Multiplication
    a = [[1.0, 2.0], [3.0, 4.0]]
    b = [[2.0, 0.0], [1.0, 2.0]]
    prod = MatrixEngine.multiply(a, b)
    assert prod == [[4.0, 4.0], [10.0, 8.0]]

    # Transpose
    assert MatrixEngine.transpose(a) == [[1.0, 3.0], [2.0, 4.0]]

    # Determinant: det([[1, 2], [3, 4]]) = 1*4 - 2*3 = -2
    det = MatrixEngine.determinant(a)
    assert abs(det - (-2.0)) < 1e-6

    # Invert
    inv_a = MatrixEngine.invert(a)
    ident = MatrixEngine.multiply(a, inv_a)
    for i in range(2):
        for j in range(2):
            expected = 1.0 if i == j else 0.0
            assert abs(ident[i][j] - expected) < 1e-5

    # Solve Ax = b
    # 2x + y = 5
    # x + 3y = 5
    # Solution: x = 2, y = 1
    sys_a = [[2.0, 1.0], [1.0, 3.0]]
    sys_b = [5.0, 5.0]
    sol = MatrixEngine.solve_linear_system(sys_a, sys_b)
    assert round(sol[0], 4) == 2.0
    assert round(sol[1], 4) == 1.0

    # 2x2 Eigenvalues: [[2, 1], [1, 2]] -> det([[2-L, 1], [1, 2-L]]) = (2-L)^2 - 1 = L^2 - 4L + 3 = 0 -> L = 3, 1
    sym_mat = [[2.0, 1.0], [1.0, 2.0]]
    l1, l2 = MatrixEngine.eigenvalues_2x2(sym_mat)
    assert {round(l1.real, 2), round(l2.real, 2)} == {3.0, 1.0}


# =============================================================================
# 5. POLYNOMIAL ENGINE TESTS
# =============================================================================

def test_polynomial_evaluation_and_curve_fit():
    # P(x) = 2x^2 + 3x + 1
    coeffs = [2.0, 3.0, 1.0]
    val = PolynomialEngine.evaluate(coeffs, 2.0)
    assert val == 2 * (4) + 3 * (2) + 1  # 15.0

    # P'(x) = 4x + 3
    deriv = PolynomialEngine.differentiate(coeffs)
    assert deriv == [4.0, 3.0]

    # Fit quadratic curve: y = 2x^2 + 1
    x_pts = [0.0, 1.0, 2.0, 3.0, 4.0]
    y_pts = [2.0 * (x ** 2) + 1.0 for x in x_pts]
    fitted = PolynomialEngine.fit_polynomial(x_pts, y_pts, degree=2)
    assert abs(fitted[0] - 2.0) < 1e-4  # a = 2
    assert abs(fitted[1] - 0.0) < 1e-4  # b = 0
    assert abs(fitted[2] - 1.0) < 1e-4  # c = 1

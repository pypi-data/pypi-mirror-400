'''
' Core Derivatives Library (No Visualizations)
' --------------------------------------------
'
' This module provides core derivative calculations and formulas
' without any visualization dependencies.
'
' @file: derivatives_core.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
'''

import numpy as np
import sympy as sp
from typing import Dict, List, Tuple, Callable


class CommonDerivativesCore:
    '''Core class for derivative calculations and formulas.'''

    def __init__(self):
        self.x = sp.Symbol('x')
        self.a = sp.Symbol('a', positive=True)
        self.n = sp.Symbol('n')

        # Dictionary of common derivative formulas
        self.derivative_formulas = {
            # Basic functions
            "constant": {"function": "c", "derivative": "0", "example": "5"},
            "linear": {"function": "ax + b", "derivative": "a", "example": "3*x + 2"},
            "power": {"function": "x^n", "derivative": "n*x^(n-1)", "example": "x**3"},
            "square_root": {"function": "√x", "derivative": "1/(2√x)", "example": "sqrt(x)"},
            "reciprocal": {"function": "1/x", "derivative": "-1/x²", "example": "1/x"},

            # Exponential and logarithmic
            "exponential_e": {"function": "eˣ", "derivative": "eˣ", "example": "exp(x)"},
            "exponential_a": {"function": "aˣ", "derivative": "aˣ ln(a)", "example": "2**x"},
            "natural_log": {"function": "ln(x)", "derivative": "1/x", "example": "log(x)"},
            "log_a": {"function": "log_a(x)", "derivative": "1/(x ln(a))", "example": "log(x, 2)"},

            # Trigonometric functions
            "sin": {"function": "sin(x)", "derivative": "cos(x)", "example": "sin(x)"},
            "cos": {"function": "cos(x)", "derivative": "-sin(x)", "example": "cos(x)"},
            "tan": {"function": "tan(x)", "derivative": "sec²(x)", "example": "tan(x)"},
            "csc": {"function": "csc(x)", "derivative": "-csc(x)cot(x)", "example": "csc(x)"},
            "sec": {"function": "sec(x)", "derivative": "sec(x)tan(x)", "example": "sec(x)"},
            "cot": {"function": "cot(x)", "derivative": "-csc²(x)", "example": "cot(x)"},

            # Inverse trigonometric functions
            "arcsin": {"function": "arcsin(x)", "derivative": "1/√(1-x²)", "example": "asin(x)"},
            "arccos": {"function": "arccos(x)", "derivative": "-1/√(1-x²)", "example": "acos(x)"},
            "arctan": {"function": "arctan(x)", "derivative": "1/(1+x²)", "example": "atan(x)"},

            # Hyperbolic functions
            "sinh": {"function": "sinh(x)", "derivative": "cosh(x)", "example": "sinh(x)"},
            "cosh": {"function": "cosh(x)", "derivative": "sinh(x)", "example": "cosh(x)"},
            "tanh": {"function": "tanh(x)", "derivative": "sech²(x)", "example": "tanh(x)"},
        }

    def calculate_function_and_derivative(self, func_str: str, x_vals: np.ndarray) -> Tuple[np.ndarray, np.ndarray, sp.Expr, sp.Expr]:
        '''
        Calculate function values and derivative values.

        Args:
            func_str: Function as string
            x_vals: Array of x values

        Returns:
            Tuple of (y_vals, dy_vals, func_expr, derivative_expr)
        '''
        func = sp.sympify(func_str)
        derivative = sp.diff(func, self.x)

        try:
            func_numpy = sp.lambdify(self.x, func, ['numpy', 'math'])
            deriv_numpy = sp.lambdify(self.x, derivative, ['numpy', 'math'])
            y_vals = func_numpy(x_vals)
            dy_vals = deriv_numpy(x_vals)
            return y_vals, dy_vals, func, derivative
        except:
            raise ValueError(f"Could not convert function to numpy: {func}")

    def get_derivative_patterns(self) -> Dict[str, List[str]]:
        '''Get common derivative patterns grouped by type.'''
        return {
            "Power Functions": ["x**2", "x**3", "x**4", "x**0.5"],
            "Exponential Functions": ["exp(x)", "2**x", "exp(-x)"],
            "Trigonometric Functions": ["sin(x)", "cos(x)", "tan(x)"],
            "Logarithmic Functions": ["log(x)", "log(x**2)", "x*log(x)"],
        }

    def calculate_chain_rule_examples(self) -> List[Dict]:
        '''Calculate chain rule examples.'''
        examples = [
            "sin(x**2)",
            "exp(cos(x))",
            "log(sin(x))",
            "sqrt(1 + x**2)",
            "(x**2 + 1)**3",
            "sin(exp(x))"
        ]

        results = []
        for func_str in examples:
            try:
                func = sp.sympify(func_str)
                derivative = sp.diff(func, self.x)

                results.append({
                    'function': func,
                    'derivative': derivative,
                    'simplified': sp.simplify(derivative),
                    'func_str': func_str
                })
            except Exception as e:
                continue

        return results

    def calculate_higher_order_derivatives(self, func_str: str, n_derivatives: int = 4) -> List[sp.Expr]:
        '''
        Calculate higher-order derivatives.

        Args:
            func_str: Function to differentiate
            n_derivatives: Number of derivatives to calculate

        Returns:
            List of derivative expressions
        '''
        func = sp.sympify(func_str)
        derivatives = [func]

        current = func
        for i in range(n_derivatives):
            current = sp.diff(current, self.x)
            derivatives.append(current)

        return derivatives

    def find_critical_points(self, func_str: str) -> Dict:
        '''
        Find critical points of a function.

        Args:
            func_str: Function to analyze

        Returns:
            Dictionary with critical points analysis
        '''
        func = sp.sympify(func_str)
        first_derivative = sp.diff(func, self.x)
        second_derivative = sp.diff(first_derivative, self.x)

        # Find critical points (where f'(x) = 0)
        critical_points = sp.solve(first_derivative, self.x)
        critical_points = [float(cp.evalf()) for cp in critical_points if cp.is_real]

        # Analyze each critical point
        analyzed_points = []
        func_numpy = sp.lambdify(self.x, func, 'numpy')
        second_deriv_numpy = sp.lambdify(self.x, second_derivative, 'numpy')

        for cp in critical_points:
            y_cp = func_numpy(cp)
            second_deriv_at_cp = second_deriv_numpy(cp)

            if second_deriv_at_cp > 0:
                point_type = 'Local minimum'
            elif second_deriv_at_cp < 0:
                point_type = 'Local maximum'
            else:
                point_type = 'Inflection point'

            analyzed_points.append({
                'x': cp,
                'y': y_cp,
                'type': point_type,
                'second_derivative': second_deriv_at_cp
            })

        return {
            'function': func,
            'first_derivative': first_derivative,
            'second_derivative': second_derivative,
            'critical_points': critical_points,
            'analyzed_points': analyzed_points
        }

    def calculate_slope_field_data(self, func_str: str, x_range: Tuple[float, float],
                                 y_range: Tuple[float, float], grid_size: Tuple[int, int] = (20, 15)) -> Dict:
        '''
        Calculate slope field data for a derivative function.

        Args:
            func_str: Function whose derivative defines the slope field
            x_range: Range for x values
            y_range: Range for y values
            grid_size: Grid size for slope field

        Returns:
            Dictionary with slope field data
        '''
        func = sp.sympify(func_str)
        derivative = sp.diff(func, self.x)

        try:
            slope_func = sp.lambdify(self.x, derivative, 'numpy')
            func_numpy = sp.lambdify(self.x, func, 'numpy')

            # Create grid
            x = np.linspace(x_range[0], x_range[1], grid_size[0])
            y = np.linspace(y_range[0], y_range[1], grid_size[1])
            X, Y = np.meshgrid(x, y)

            # Calculate slopes at each point
            slopes = slope_func(X)

            # Normalize for better visualization
            dx = np.ones_like(slopes)
            dy = slopes

            # Normalize vectors
            magnitude = np.sqrt(dx**2 + dy**2)
            dx_norm = dx / magnitude * 0.1
            dy_norm = dy / magnitude * 0.1

            # Calculate function values for plotting
            x_continuous = np.linspace(x_range[0], x_range[1], 1000)
            y_continuous = func_numpy(x_continuous)

            # Only include parts within y_range
            mask = (y_continuous >= y_range[0]) & (y_continuous <= y_range[1])

            return {
                'X': X,
                'Y': Y,
                'dx_norm': dx_norm,
                'dy_norm': dy_norm,
                'slopes': slopes,
                'x_continuous': x_continuous,
                'y_continuous': y_continuous,
                'valid_mask': mask,
                'func_expr': func,
                'derivative_expr': derivative,
                'calculation_success': True
            }

        except Exception as e:
            return {'calculation_success': False, 'error': str(e)}


def get_function_families() -> Dict[str, List[str]]:
    '''Get common function families for pattern analysis.'''
    return {
        "Polynomial": ["x", "x**2", "x**3", "x**4", "x**5"],
        "Radical": ["sqrt(x)", "x**(1/3)", "x**(2/3)"],
        "Exponential": ["exp(x)", "2**x", "3**x", "exp(-x)"],
        "Logarithmic": ["log(x)", "log(x, 2)", "log(x, 10)"],
        "Trigonometric": ["sin(x)", "cos(x)", "tan(x)", "sec(x)", "csc(x)", "cot(x)"],
        "Inverse Trig": ["asin(x)", "acos(x)", "atan(x)"],
        "Hyperbolic": ["sinh(x)", "cosh(x)", "tanh(x)"]
    }


def format_derivative_table() -> str:
    '''Format the derivative formulas table as text.'''
    core = CommonDerivativesCore()

    table = "COMMON DERIVATIVES REFERENCE TABLE\n"
    table += "=" * 80 + "\n"
    table += f"{'Function':<20} {'Derivative':<25} {'Example':<20}\n"
    table += "-" * 80 + "\n"

    for name, formula in core.derivative_formulas.items():
        table += f"{formula['function']:<20} {formula['derivative']:<25} {formula['example']:<20}\n"

    table += "=" * 80
    return table

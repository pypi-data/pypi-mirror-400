'''
' Core Fundamental Theorem of Calculus (No Visualizations)
' --------------------------------------------------------
'
' This module implements core FTC calculations without visualization dependencies.
'
' @file: fundamental_theorem_core.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
'''

import numpy as np
import sympy as sp
from scipy import integrate
from typing import Tuple, Dict, Optional


class FundamentalTheoremCore:
    '''Core class for FTC calculations.'''

    def __init__(self):
        self.x = sp.Symbol('x')
        self.t = sp.Symbol('t')

    def calculate_riemann_sum(self, func_str: str, interval: Tuple[float, float],
                             n_rectangles: int, method: str = "right") -> Dict:
        '''
        Calculate Riemann sum approximation.

        Args:
            func_str: Function to integrate
            interval: Integration bounds
            n_rectangles: Number of rectangles
            method: "left", "right", "midpoint"

        Returns:
            Dictionary with Riemann sum data
        '''
        func = sp.sympify(func_str)
        func_numpy = sp.lambdify(self.x, func, 'numpy')

        a, b = interval
        dx = (b - a) / n_rectangles

        if method == "left":
            x_rects = np.linspace(a, b - dx, n_rectangles)
            y_rects = func_numpy(x_rects)
        elif method == "right":
            x_rects = np.linspace(a + dx, b, n_rectangles)
            y_rects = func_numpy(x_rects)
        else:  # midpoint
            x_rects = np.linspace(a + dx/2, b - dx/2, n_rectangles)
            y_rects = func_numpy(x_rects)

        riemann_sum = np.sum(y_rects * dx)

        # Calculate exact integral if possible
        try:
            exact_integral = float(sp.integrate(func, (self.x, a, b)))
            symbolic_integral = sp.integrate(func, self.x)
        except:
            exact_integral = None
            symbolic_integral = None

        return {
            'func_expr': func,
            'riemann_sum': riemann_sum,
            'exact_integral': exact_integral,
            'symbolic_integral': symbolic_integral,
            'dx': dx,
            'x_rects': x_rects,
            'y_rects': y_rects,
            'n_rectangles': n_rectangles,
            'method': method,
            'interval': interval
        }

    def calculate_riemann_convergence(self, func_str: str, interval: Tuple[float, float],
                                    max_n: int = 100) -> Dict:
        '''
        Calculate convergence of Riemann sums.

        Args:
            func_str: Function to integrate
            interval: Integration bounds
            max_n: Maximum number of rectangles to test

        Returns:
            Dictionary with convergence data
        '''
        func = sp.sympify(func_str)
        func_numpy = sp.lambdify(self.x, func, 'numpy')
        a, b = interval

        n_values = range(1, max_n + 1)
        riemann_values = []

        for n in n_values:
            dx = (b - a) / n
            x_temp = np.linspace(a, b - dx, n)
            y_temp = func_numpy(x_temp + dx)  # Right endpoint rule
            riemann_values.append(np.sum(y_temp * dx))

        # Get exact value
        try:
            exact_value = float(sp.integrate(func, (self.x, a, b)))
        except:
            exact_value, _ = integrate.quad(func_numpy, a, b)

        return {
            'n_values': list(n_values),
            'riemann_values': riemann_values,
            'exact_value': exact_value,
            'func_expr': func
        }

    def calculate_ftc_part1_data(self, func_str: str, lower_bound: float,
                                upper_range: Tuple[float, float] = (0, 5)) -> Dict:
        '''
        Calculate data for FTC Part 1: If F(x) = ∫[a to x] f(t) dt, then F'(x) = f(x)

        Args:
            func_str: Integrand function
            lower_bound: Lower bound of integration
            upper_range: Range for upper bound x

        Returns:
            Dictionary with FTC Part 1 data
        '''
        func = sp.sympify(func_str)
        # Replace any 'x' symbols with 't' symbols for proper integration variable
        if 'x' in func_str:
            x_sym = sp.Symbol('x')
            func = func.subs(x_sym, self.t)
        func_numpy = sp.lambdify(self.t, func, 'numpy')

        x_vals = np.linspace(upper_range[0], upper_range[1], 100)
        F_vals = []
        F_prime_vals = []

        # Calculate F(x) and F'(x) numerically
        for x_val in x_vals:
            if x_val == lower_bound:
                F_val = 0
            else:
                try:
                    F_val, _ = integrate.quad(func_numpy, lower_bound, x_val)
                except:
                    F_val = 0
            F_vals.append(F_val)

            # F'(x) should equal f(x) by FTC Part 1
            F_prime_vals.append(func_numpy(x_val))

        # Calculate numerical derivative of F(x) for comparison
        F_vals = np.array(F_vals)
        dx = x_vals[1] - x_vals[0]
        F_prime_numerical = np.gradient(F_vals, dx)

        # Calculate error
        error = np.mean(np.abs(np.array(F_prime_vals) - F_prime_numerical))

        return {
            'func_expr': func,
            'x_vals': x_vals,
            'F_vals': F_vals,
            'F_prime_theoretical': F_prime_vals,
            'F_prime_numerical': F_prime_numerical,
            'lower_bound': lower_bound,
            'error': error
        }

    def calculate_ftc_part2_data(self, func_str: str, interval: Tuple[float, float]) -> Dict:
        '''
        Calculate data for FTC Part 2: ∫[a to b] f(x) dx = F(b) - F(a)

        Args:
            func_str: Function to integrate
            interval: Integration bounds

        Returns:
            Dictionary with FTC Part 2 data
        '''
        func = sp.sympify(func_str)
        a, b = interval

        # Find antiderivative symbolically
        try:
            antiderivative = sp.integrate(func, self.x)
            F_b = float(antiderivative.subs(self.x, b))
            F_a = float(antiderivative.subs(self.x, a))
            definite_integral = F_b - F_a
            symbolic_success = True
        except:
            antiderivative = None
            F_b = F_a = definite_integral = None
            symbolic_success = False

        # Numerical verification
        func_numpy = sp.lambdify(self.x, func, 'numpy')
        numerical_integral, error = integrate.quad(func_numpy, a, b)

        return {
            'func_expr': func,
            'antiderivative': antiderivative,
            'F_b': F_b,
            'F_a': F_a,
            'definite_integral': definite_integral,
            'numerical_integral': numerical_integral,
            'error': abs(definite_integral - numerical_integral) if definite_integral else None,
            'symbolic_success': symbolic_success,
            'interval': interval
        }

    def calculate_mean_value_theorem_data(self, func_str: str, interval: Tuple[float, float]) -> Dict:
        '''
        Calculate data for Mean Value Theorem for integrals.

        Args:
            func_str: Function to analyze
            interval: Interval [a, b]

        Returns:
            Dictionary with MVT data
        '''
        func_numpy = sp.lambdify(self.x, sp.sympify(func_str), 'numpy')
        a, b = interval

        # Calculate average value of function over interval
        integral_value, _ = integrate.quad(func_numpy, a, b)
        average_value = integral_value / (b - a)

        # Find point c where f(c) = average value (approximately)
        x_vals = np.linspace(a, b, 1000)
        y_vals = func_numpy(x_vals)

        # Find closest point to average value
        diff = np.abs(y_vals - average_value)
        min_idx = np.argmin(diff)
        c = x_vals[min_idx]
        f_c = y_vals[min_idx]

        return {
            'func_expr': sp.sympify(func_str),
            'integral_value': integral_value,
            'average_value': average_value,
            'c': c,
            'f_c': f_c,
            'x_vals': x_vals,
            'y_vals': y_vals,
            'interval': interval
        }

    def calculate_net_change_data(self, rate_func_str: str, interval: Tuple[float, float]) -> Dict:
        '''
        Calculate data for Net Change Theorem: ∫[a to b] f'(x) dx = f(b) - f(a)

        Args:
            rate_func_str: Rate of change function f'(x)
            interval: Time interval [a, b]

        Returns:
            Dictionary with net change data
        '''
        rate_func = sp.sympify(rate_func_str)
        a, b = interval

        # Find the position function by integration
        try:
            position_func = sp.integrate(rate_func, self.x)
            symbolic_success = True
        except:
            print("Could not find symbolic antiderivative")
            return {'symbolic_success': False}

        # Calculate net change
        rate_numpy = sp.lambdify(self.x, rate_func, 'numpy')
        net_change, _ = integrate.quad(rate_numpy, a, b)

        # Calculate position values (assuming C = 0)
        position_numpy = sp.lambdify(self.x, position_func, 'numpy')
        f_a = position_numpy(a)
        f_b = position_numpy(b)

        return {
            'rate_func': rate_func,
            'position_func': position_func,
            'net_change': net_change,
            'f_a': f_a,
            'f_b': f_b,
            'position_change': f_b - f_a,
            'error': abs(net_change - (f_b - f_a)),
            'interval': interval,
            'symbolic_success': True
        }


def compare_integration_methods_data(func_str: str, interval: Tuple[float, float] = (0, 2),
                                   n_values: Optional[list] = None) -> Dict:
    '''
    Compare different numerical integration methods.

    Args:
        func_str: Function to integrate
        interval: Integration bounds
        n_values: List of n values to test

    Returns:
        Dictionary with method comparison data
    '''
    if n_values is None:
        n_values = [5, 10, 20, 50, 100, 200]

    func = sp.sympify(func_str)
    func_numpy = sp.lambdify(sp.Symbol('x'), func, 'numpy')
    a, b = interval

    # Get exact value for comparison
    exact_value, _ = integrate.quad(func_numpy, a, b)

    methods_data = {}

    for method_name in ['Left Riemann', 'Right Riemann', 'Midpoint', 'Trapezoidal']:
        errors = []

        for n in n_values:
            dx = (b - a) / n

            if method_name == 'Left Riemann':
                x_points = np.linspace(a, b - dx, n)
                y_points = func_numpy(x_points)
                approx = np.sum(y_points) * dx
            elif method_name == 'Right Riemann':
                x_points = np.linspace(a + dx, b, n)
                y_points = func_numpy(x_points)
                approx = np.sum(y_points) * dx
            elif method_name == 'Midpoint':
                x_points = np.linspace(a + dx/2, b - dx/2, n)
                y_points = func_numpy(x_points)
                approx = np.sum(y_points) * dx
            elif method_name == 'Trapezoidal':
                x_points = np.linspace(a, b, n + 1)
                y_points = func_numpy(x_points)
                approx = dx * (y_points[0]/2 + np.sum(y_points[1:-1]) + y_points[-1]/2)

            errors.append(abs(approx - exact_value))

        methods_data[method_name] = {
            'errors': errors,
            'n_values': n_values
        }

    return {
        'func_expr': func,
        'exact_value': exact_value,
        'methods_data': methods_data,
        'interval': interval
    }

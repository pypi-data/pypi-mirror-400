'''
' Core Basic Calculus Rules (No Visualizations)
' ---------------------------------------------
'
' This module implements fundamental calculus rules and calculations
' without any visualization dependencies.
'
' @file: basic_rules_core.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
'''

import numpy as np
import sympy as sp
from typing import Callable, List, Tuple, Union


class CalculusRulesCore:
    '''Core class containing basic calculus rules calculations.'''

    def __init__(self):
        self.x = sp.Symbol("x")
        self.h = sp.Symbol("h")

    def power_rule_calculation(
    self, n: float, x_vals: np.ndarray
  ) -> Tuple[np.ndarray, np.ndarray]:
        '''
    Calculate power rule: d/dx(x^n) = n*x^(n-1)

    Args:
      n: Power exponent
      x_vals: Array of x values

    Returns:
      Tuple of (original_function_values, derivative_values)
    '''
        y_original   = x_vals ** n
        y_derivative = n * x_vals ** (n - 1) if n != 0 else np.zeros_like(x_vals)

        return y_original, y_derivative

    def product_rule_calculation(
    self, func1_str: str, func2_str: str, x_vals: np.ndarray
  ) -> dict:
        '''
    Calculate product rule: (fg)' = f'g + fg'

    Args:
      func1_str: First function as string
      func2_str: Second function as string
      x_vals: Array of x values

    Returns:
      Dictionary with all calculated values
    '''
        # Parse functions
        f = sp.sympify(func1_str)
        g = sp.sympify(func2_str)

        # Calculate derivatives
        f_prime = sp.diff(f, self.x)
        g_prime = sp.diff(g, self.x)
        product = f * g
        product_derivative = sp.diff(product, self.x)

        # Q: why the result here not returned?
        # A: because indivaul components are returuned and summed on the graph (term1 + term2).
        #    However, we can return it for use cases where needed.
        product_rule_result = f_prime * g + f * g_prime

        # Convert to numpy functions
        f_func = sp.lambdify(self.x, f, "numpy")
        g_func = sp.lambdify(self.x, g, "numpy")
        product_func = sp.lambdify(self.x, product, "numpy")
        product_deriv_func = sp.lambdify(self.x, product_derivative, "numpy")
        f_prime_func = sp.lambdify(self.x, f_prime, "numpy")
        g_prime_func = sp.lambdify(self.x, g_prime, "numpy")

        return {
            "f_vals": f_func(x_vals),
            "g_vals": g_func(x_vals),
            "product_vals": product_func(x_vals),
            "product_derivative_vals": product_deriv_func(x_vals),
            "f_prime_vals": f_prime_func(x_vals),
            "g_prime_vals": g_prime_func(x_vals),
            "term1": f_prime_func(x_vals) * g_func(x_vals),
            "term2": f_func(x_vals) * g_prime_func(x_vals),
            "f_expr": f,
            "g_expr": g,
            "f_prime_expr": f_prime,
            "g_prime_expr": g_prime,
            "product_expr": product,
            "product_derivative_expr": product_derivative,
            "product_rule_result": product_rule_result,
        }

    def chain_rule_calculation(self, outer_func: str, inner_func: str) -> dict:
        '''
    Calculate chain rule: d/dx[f(g(x))] = f'(g(x)) * g'(x)

    Args:
      outer_func: Outer function as string
      inner_func: Inner function as string

    Returns:
      Dictionary with symbolic expressions and derivatives
    '''
        # Parse functions
        u = sp.sympify(inner_func)  # inner function
        f_u = sp.sympify(outer_func.replace("x", "u"))  # outer function in terms of u

        # Create composite function
        composite = f_u.subs("u", u)

        # Calculate derivatives using chain rule
        du_dx = sp.diff(u, self.x)
        df_du = sp.diff(f_u, "u")
        chain_rule_result = df_du.subs("u", u) * du_dx
        direct_derivative = sp.diff(composite, self.x)

        return {
      "inner_func": u,
      "outer_func": f_u,
      "composite": composite,
      "du_dx": du_dx,
      "df_du": df_du,
      "chain_rule_result": chain_rule_result,
      "direct_derivative": direct_derivative,
      "verification": sp.simplify(chain_rule_result - direct_derivative) == 0,
    }

    def quotient_rule_calculation(
    self, numerator: str, denominator: str, x_vals: np.ndarray
  ) -> dict:
        '''
    Calculate quotient rule: (f/g)' = (f'g - fg')/g^2

    Args:
        numerator: Numerator function as string
        denominator: Denominator function as string
        x_vals: Array of x values

    Returns:
        Dictionary with calculated values
    '''
        f = sp.sympify(numerator)
        g = sp.sympify(denominator)

        f_prime = sp.diff(f, self.x)
        g_prime = sp.diff(g, self.x)

        quotient = f / g
        quotient_derivative = sp.diff(quotient, self.x)
        quotient_rule_result = (f_prime * g - f * g_prime) / (g**2)

        # Filter out points where denominator is close to zero
        g_func = sp.lambdify(self.x, g, "numpy")
        g_vals = g_func(x_vals)
        valid_mask = np.abs(g_vals) > 0.01
        x_vals_filtered = x_vals[valid_mask]

        f_func = sp.lambdify(self.x, f, "numpy")
        quotient_func = sp.lambdify(self.x, quotient, "numpy")
        quotient_deriv_func = sp.lambdify(self.x, quotient_derivative, "numpy")

        return {
      "x_vals": x_vals,
      "x_vals_filtered": x_vals_filtered,
      "f_vals": f_func(x_vals),
      "g_vals": g_vals,
      "quotient_vals": quotient_func(x_vals_filtered),
      "quotient_derivative_vals": quotient_deriv_func(x_vals_filtered),
      "f_expr": f,
      "g_expr": g,
      "f_prime_expr": f_prime,
      "g_prime_expr": g_prime,
      "quotient_expr": quotient,
      "quotient_derivative_expr": quotient_derivative,
      "quotient_rule_result": quotient_rule_result,
    }

    def limit_calculation(
    self, func_str: str, approach_point: float, x_range: Tuple[float, float]
  ) -> dict:
        '''
    Calculate limit as x approaches a point.

    Args:
      func_str: Function as string
      approach_point: Point to approach
      x_range: Range around the point

    Returns:
      Dictionary with limit calculation results
    '''
        x = sp.Symbol("x")
        func = sp.sympify(func_str)

        # Calculate limit
        try:
            limit_val = float(sp.limit(func, x, approach_point))
        except:
            limit_val = None

        # Create x values excluding the approach point
        x_vals = np.linspace(x_range[0], x_range[1], 1000)
        mask = np.abs(x_vals - approach_point) > 0.001
        x_filtered = x_vals[mask]

        func_numpy = sp.lambdify(x, func, "numpy")

        try:
            y_vals = func_numpy(x_filtered)
            calculation_success = True
        except Exception as e:
            y_vals = None
            calculation_success = False

        return {
      "func_expr": func,
      "limit_val": limit_val,
      "approach_point": approach_point,
      "x_vals": x_vals,
      "x_filtered": x_filtered,
      "y_vals": y_vals,
      "calculation_success": calculation_success,
    }


def create_x_range(start: float, end: float, num_points: int = 1000) -> np.ndarray:
  '''Utility function to create x value arrays.'''
  return np.linspace(start, end, num_points)


def verify_derivatives_match(expr1: sp.Expr, expr2: sp.Expr) -> bool:
  '''Verify if two symbolic expressions are equivalent.'''
  return sp.simplify(expr1 - expr2) == 0

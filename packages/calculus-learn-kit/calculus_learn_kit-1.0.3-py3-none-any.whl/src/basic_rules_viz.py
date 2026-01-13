'''
' Visualization for Basic Calculus Rules
' --------------------------------------
'
' This module handles all visualization logic for basic calculus rules,
' separated from the core mathematical calculations.
'
' @file: basic_rules_viz.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Tuple

try:
  from .basic_rules_core import CalculusRulesCore, create_x_range
except ImportError:
  from basic_rules_core import CalculusRulesCore, create_x_range


class CalculusRulesVisualizer:
  '''Handles all visualizations for basic calculus rules.'''

  def __init__(self):
    self.core = CalculusRulesCore()

  def power_rule_demo(self, n: float = 3, x_range: Tuple[float, float] = (-3, 3)) -> None:
    '''
    Visualize the power rule: d/dx(x^n) = n*x^(n-1)

    Args:
        n: Power exponent
        x_range: Range for x values
    '''
    x_vals = create_x_range(x_range[0], x_range[1])
    y_original, y_derivative = self.core.power_rule_calculation(n, x_vals)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot original function
    ax1.plot(x_vals, y_original, 'b-', linewidth=2, label=f'f(x) = x^{n}')
    ax1.set_title(f'Original Function: f(x) = x^{n}')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlabel('x')
    ax1.set_ylabel('f(x)')

    # Plot derivative
    ax2.plot(x_vals, y_derivative, 'r-', linewidth=2, label=f"f'(x) = {n}x^{n-1}")
    ax2.set_title(f"Derivative: f'(x) = {n}x^{n-1}")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xlabel('x')
    ax2.set_ylabel("f'(x)")

    plt.tight_layout()
    plt.show()

  def product_rule_visualization(self, func1_str: str = "x**2", func2_str: str = "sin(x)") -> None:
    '''
    Visualize the product rule: (fg)' = f'g + fg'

    Args:
      func1_str: First function as string
      func2_str: Second function as string
    '''
    x_vals = create_x_range(-2*np.pi, 2*np.pi)
    results = self.core.product_rule_calculation(func1_str, func2_str, x_vals)

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

    # Plot individual functions
    ax1.plot(x_vals, results['f_vals'], 'b-', label=f'f(x) = {results["f_expr"]}')
    ax1.plot(x_vals, results['g_vals'], 'g-', label=f'g(x) = {results["g_expr"]}')
    ax1.set_title('Individual Functions')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot product
    ax2.plot(x_vals, results['product_vals'], 'purple', linewidth=2,
            label=f'f(x)g(x) = {results["product_expr"]}')
    ax2.set_title('Product f(x)g(x)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot derivative of product
    ax3.plot(x_vals, results['product_derivative_vals'], 'r-', linewidth=2, label="(fg)'")
    ax3.set_title('Derivative of Product')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Show product rule components
    ax4.plot(x_vals, results['term1'], '--', label="f'g", alpha=0.7)
    ax4.plot(x_vals, results['term2'], '--', label="fg'", alpha=0.7)
    ax4.plot(x_vals, results['term1'] + results['term2'], 'r-', linewidth=2, label="f'g + fg'")
    ax4.set_title('Product Rule: (fg)\' = f\'g + fg\'')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

  def chain_rule_animation(self, outer_func: str = "sin(x)", inner_func: str = "x**2") -> None:
    '''
    Display chain rule calculation results.

    Args:
        outer_func: Outer function as string
        inner_func: Inner function as string
    '''
    results = self.core.chain_rule_calculation(outer_func, inner_func)

    print(f"Inner function u(x) = {results['inner_func']}")
    print(f"Outer function f(u) = {results['outer_func']}")
    print(f"Composite function f(u(x)) = {results['composite']}")
    print(f"Chain rule: df/dx = (df/du)(du/dx) = ({results['df_du']}) * ({results['du_dx']})")
    print(f"Simplified: {results['chain_rule_result']}")
    print(f"Direct derivative: {results['direct_derivative']}")
    print(f"Verification: {results['verification']}")

  def quotient_rule_demo(self, numerator: str = "x**2", denominator: str = "x+1") -> None:
    '''
    Visualize the quotient rule: (f/g)' = (f'g - fg')/g^2

    Args:
        numerator: Numerator function as string
        denominator: Denominator function as string
    '''
    x_vals = create_x_range(-5, 5)
    results = self.core.quotient_rule_calculation(numerator, denominator, x_vals)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    # Plot numerator and denominator
    ax1.plot(x_vals, results['f_vals'], 'b-', label=f'f(x) = {results["f_expr"]}')
    ax1.plot(x_vals, results['g_vals'], 'g-', label=f'g(x) = {results["g_expr"]}')
    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax1.set_title('Numerator and Denominator')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot quotient
    ax2.plot(results['x_vals_filtered'], results['quotient_vals'], 'purple', linewidth=2,
            label=f'f(x)/g(x) = {results["f_expr"]}/{results["g_expr"]}')
    ax2.set_title('Quotient f(x)/g(x)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-10, 10)

    # Plot derivative
    ax3.plot(results['x_vals_filtered'], results['quotient_derivative_vals'], 'r-', linewidth=2,
            label="(f/g)'")
    ax3.set_title('Derivative of Quotient')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(-10, 10)

    plt.tight_layout()
    plt.show()

    print(f"Quotient rule formula: (f/g)' = (f'g - fg')/g²")
    print(f"f'(x) = {results['f_prime_expr']}")
    print(f"g'(x) = {results['g_prime_expr']}")
    print(f"Result: {results['quotient_rule_result']}")


  def interactive_limit_demo(self):
    '''Interactive demonstration of limits approaching a point.'''
    core = self.core

    def limit_visualization(func_str: str = "sin(x)/x", approach_point: float = 0):
      '''Visualize limits as x approaches a point.'''
      results = core.limit_calculation(func_str, approach_point, (approach_point - 2, approach_point + 2))

      if results['limit_val'] is not None:
        print(f"lim(x→{approach_point}) {results['func_expr']} = {results['limit_val']}")
      else:
        print(f"Limit may not exist or is complex")

      if results['calculation_success']:
        plt.figure(figsize=(12, 8))
        plt.plot(results['x_filtered'], results['y_vals'], 'b-', linewidth=2,
                label=f'f(x) = {results["func_expr"]}')

        if results['limit_val'] is not None:
            plt.plot(results['approach_point'], results['limit_val'], 'ro', markersize=8,
                    label=f'Limit = {results["limit_val"]:.4f}')
            plt.axhline(y=results['limit_val'], color='r', linestyle='--', alpha=0.5)

        plt.axvline(x=results['approach_point'], color='g', linestyle='--', alpha=0.5,
                    label=f'x → {results["approach_point"]}')
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title(f'Limit as x approaches {results["approach_point"]}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
      else:
        print("Error plotting function")

    print("=== Limit Demonstrations ===")
    limit_visualization("sin(x)/x", 0)
    limit_visualization("(x**2 - 1)/(x - 1)", 1)
    limit_visualization("(x**2 - 4)/(x - 2)", 2)


class CalculusRules:
  """Wrapper class that maintains the original interface for convenience."""

  def __init__(self):
    self.visualizer = CalculusRulesVisualizer()
    self.core = self.visualizer.core

  def power_rule_demo(self, n: float = 3, x_range: Tuple[float, float] = (-3, 3)) -> None:
    self.visualizer.power_rule_demo(n, x_range)

  def product_rule_visualization(self, func1_str: str = "x**2", func2_str: str = "sin(x)") -> None:
    self.visualizer.product_rule_visualization(func1_str, func2_str)

  def chain_rule_animation(self, outer_func: str = "sin(x)", inner_func: str = "x**2") -> None:
    self.visualizer.chain_rule_animation(outer_func, inner_func)

  def quotient_rule_demo(self, numerator: str = "x**2", denominator: str = "x+1") -> None:
    self.visualizer.quotient_rule_demo(numerator, denominator)

  def interactive_limit_demo(self) -> None:
    self.visualizer.interactive_limit_demo()

'''
' Visualization for Fundamental Theorem of Calculus
' --------------------------------------------------
'
' This module handles all visualization logic for FTC demonstrations,
' separated from the core mathematical calculations.
'
' @file: fundamental_theorem_viz.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sympy as sp
from typing import Tuple
try:
    from .fundamental_theorem_core import FundamentalTheoremCore, compare_integration_methods_data
except ImportError:
    from fundamental_theorem_core import FundamentalTheoremCore, compare_integration_methods_data


class FundamentalTheoremVisualizer:
    '''Handles all visualizations for FTC demonstrations.'''

    def __init__(self):
        self.core = FundamentalTheoremCore()

    def riemann_sum_visualization(self, func_str: str = "x**2", interval: Tuple[float, float] = (0, 2),
                                  n_rectangles: int = 10) -> None:
        '''
        Visualize Riemann sums approximating definite integrals.

        Args:
            func_str: Function to integrate as string
            interval: Integration interval (a, b)
            n_rectangles: Number of rectangles for approximation
        '''
        data = self.core.calculate_riemann_sum(func_str, interval, n_rectangles)
        conv_data = self.core.calculate_riemann_convergence(func_str, interval)

        a, b = interval
        x_vals = np.linspace(a - 0.5, b + 0.5, 1000)
        func_numpy = sp.lambdify(self.core.x, data['func_expr'], 'numpy')
        y_vals = func_numpy(x_vals)

        # Area under curve
        x_area = np.linspace(a, b, 1000)
        y_area = func_numpy(x_area)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Left plot: Function with Riemann rectangles
        ax1.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'f(x) = {data["func_expr"]}')

        for i, (x_rect, y_rect) in enumerate(zip(data['x_rects'], data['y_rects'])):
            rect = patches.Rectangle((x_rect, 0), data['dx'], y_rect,
                                   linewidth=1, edgecolor='red', facecolor='lightblue', alpha=0.6)
            ax1.add_patch(rect)

        ax1.fill_between(x_area, y_area, alpha=0.3, color='green', label='Exact area')
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.set_title(f'Riemann Sum (n={n_rectangles})')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Right plot: Convergence of Riemann sums
        ax2.plot(conv_data['n_values'], conv_data['riemann_values'], 'ro-', markersize=3, label='Riemann sums')
        if data['exact_integral'] is not None:
            ax2.axhline(y=data['exact_integral'], color='green', linestyle='--',
                       label=f'Exact = {data["exact_integral"]:.6f}')
        ax2.set_xlabel('Number of rectangles')
        ax2.set_ylabel('Approximate integral')
        ax2.set_title('Convergence to Exact Value')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        print(f"Function: f(x) = {data['func_expr']}")
        print(f"Interval: [{a}, {b}]")
        print(f"Riemann sum (n={n_rectangles}): {data['riemann_sum']:.6f}")
        if data['exact_integral'] is not None:
            print(f"Exact integral: {data['exact_integral']:.6f}")
            print(f"Error: {abs(data['riemann_sum'] - data['exact_integral']):.6f}")

    def fundamental_theorem_part1_demo(self, func_str: str = "2*x", lower_bound: float = 0) -> None:
        '''
        Demonstrate FTC Part 1: If F(x) = ∫[a to x] f(t) dt, then F'(x) = f(x)

        Args:
            func_str: Integrand function as string
            lower_bound: Lower bound of integration
        '''
        data = self.core.calculate_ftc_part1_data(func_str, lower_bound)

        # Create function for plotting original f(t) using sympy lambdify
        func_numpy = sp.lambdify(self.core.t, data['func_expr'], 'numpy')
        t_vals = np.linspace(lower_bound, lower_bound + 5, 1000)
        f_vals = func_numpy(t_vals)

        # Handle case where f_vals is a scalar (constant function)
        if np.isscalar(f_vals):
            f_vals = np.full_like(t_vals, f_vals)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))

        # Plot original function f(t)
        ax1.plot(t_vals, f_vals, 'b-', linewidth=2, label=f'f(t) = {data["func_expr"]}')
        ax1.set_xlabel('t')
        ax1.set_ylabel('f(t)')
        ax1.set_title('Original Function f(t)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot accumulator function F(x)
        ax2.plot(data['x_vals'], data['F_vals'], 'g-', linewidth=2,
                label=f'F(x) = ∫[{lower_bound} to x] f(t) dt')
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.set_title('Accumulator Function F(x)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Compare F'(x) with f(x)
        ax3.plot(data['x_vals'], data['F_prime_theoretical'], 'b-', linewidth=2,
                label='f(x) (theoretical F\'(x))')
        ax3.plot(data['x_vals'], data['F_prime_numerical'], 'r--', linewidth=2,
                label='F\'(x) (numerical)')
        ax3.set_xlabel('x')
        ax3.set_ylabel("F'(x)")
        ax3.set_title("FTC Part 1: F'(x) = f(x)")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        print(f"FTC Part 1 Verification:")
        print(f"Function: f(t) = {data['func_expr']}")
        print(f"F(x) = ∫[{lower_bound} to x] f(t) dt")
        print(f"Average error between f(x) and numerical F'(x): {data['error']:.8f}")

    def fundamental_theorem_part2_demo(self, func_str: str = "x**2", interval: Tuple[float, float] = (0, 2)) -> None:
        '''
        Demonstrate FTC Part 2: ∫[a to b] f(x) dx = F(b) - F(a) where F'(x) = f(x)

        Args:
            func_str: Function to integrate
            interval: Integration bounds (a, b)
        '''
        data = self.core.calculate_ftc_part2_data(func_str, interval)
        a, b = interval

        if data['symbolic_success']:
            print(f"Function: f(x) = {data['func_expr']}")
            print(f"Antiderivative: F(x) = {data['antiderivative']}")
            print(f"F({b}) = {data['F_b']:.6f}")
            print(f"F({a}) = {data['F_a']:.6f}")
            print(f"∫[{a} to {b}] f(x) dx = F({b}) - F({a}) = {data['definite_integral']:.6f}")

        print(f"Numerical integration: {data['numerical_integral']:.6f}")
        if data['error'] is not None:
            print(f"Error: {data['error']:.8f}")

        # Visualization
        func_numpy = sp.lambdify(self.core.x, data['func_expr'], 'numpy')

        x_vals = np.linspace(a - 1, b + 1, 1000)
        y_vals = func_numpy(x_vals)

        # Area under curve
        x_area = np.linspace(a, b, 1000)
        y_area = func_numpy(x_area)

        plt.figure(figsize=(12, 8))

        # Plot function
        plt.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'f(x) = {data["func_expr"]}')

        # Shade area under curve
        plt.fill_between(x_area, y_area, alpha=0.3, color='lightblue',
                        label=f'Area = {data["numerical_integral"]:.4f}')

        # Mark integration bounds
        plt.axvline(x=a, color='red', linestyle='--', alpha=0.7, label=f'x = {a}')
        plt.axvline(x=b, color='red', linestyle='--', alpha=0.7, label=f'x = {b}')

        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title(f'FTC Part 2: ∫[{a} to {b}] f(x) dx')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

        # Plot antiderivative if available
        if data['antiderivative'] is not None:
            antideriv_numpy = sp.lambdify(self.core.x, data['antiderivative'], 'numpy')
            F_vals = antideriv_numpy(x_vals)

            plt.figure(figsize=(12, 6))
            plt.plot(x_vals, F_vals, 'g-', linewidth=2, label=f'F(x) = {data["antiderivative"]}')
            plt.plot([a, b], [data['F_a'], data['F_b']], 'ro', markersize=8, label='F(a) and F(b)')
            plt.xlabel('x')
            plt.ylabel('F(x)')
            plt.title('Antiderivative Function')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.show()

    def mean_value_theorem_demo(self, func_str: str = "x**3 - 3*x**2 + 2*x",
                               interval: Tuple[float, float] = (0, 3)) -> None:
        '''
        Demonstrate the Mean Value Theorem for integrals.

        Args:
            func_str: Function to analyze
            interval: Interval [a, b]
        '''
        data = self.core.calculate_mean_value_theorem_data(func_str, interval)
        a, b = interval

        plt.figure(figsize=(12, 8))

        # Plot function
        plt.plot(data['x_vals'], data['y_vals'], 'b-', linewidth=2, label=f'f(x) = {data["func_expr"]}')

        # Fill area under curve
        plt.fill_between(data['x_vals'], data['y_vals'], alpha=0.3, color='lightblue',
                        label=f'Area = {data["integral_value"]:.4f}')

        # Plot average value line
        plt.axhline(y=data['average_value'], color='red', linestyle='--',
                   label=f'Average value = {data["average_value"]:.4f}')

        # Mark the point c
        plt.plot(data['c'], data['f_c'], 'ro', markersize=10,
                label=f'f({data["c"]:.3f}) ≈ {data["f_c"]:.4f}')

        # Mark interval bounds
        plt.axvline(x=a, color='gray', linestyle=':', alpha=0.5)
        plt.axvline(x=b, color='gray', linestyle=':', alpha=0.5)

        # Draw rectangle representing average value
        rect = patches.Rectangle((a, 0), b-a, data['average_value'],
                               linewidth=2, edgecolor='orange',
                               facecolor='none', linestyle='-',
                               label='Rectangle with same area')
        plt.gca().add_patch(rect)

        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title(f'Mean Value Theorem for Integrals on [{a}, {b}]')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

        print(f"Function: f(x) = {data['func_expr']}")
        print(f"Interval: [{a}, {b}]")
        print(f"Integral: ∫[{a} to {b}] f(x) dx = {data['integral_value']:.6f}")
        print(f"Average value: {data['average_value']:.6f}")
        print(f"Point c ≈ {data['c']:.6f} where f(c) ≈ {data['f_c']:.6f}")
        print(f"Rectangle area: {(b-a) * data['average_value']:.6f}")

    def net_change_theorem_demo(self, rate_func_str: str = "2*x + 1",
                               interval: Tuple[float, float] = (0, 3)) -> None:
        '''
        Demonstrate the Net Change Theorem: ∫[a to b] f'(x) dx = f(b) - f(a)

        Args:
            rate_func_str: Rate of change function f'(x)
            interval: Time interval [a, b]
        '''
        data = self.core.calculate_net_change_data(rate_func_str, interval)

        if not data['symbolic_success']:
            print("Could not calculate net change theorem data")
            return

        a, b = interval

        # Create functions for plotting
        rate_numpy = sp.lambdify(self.core.x, data['rate_func'], 'numpy')
        position_numpy = sp.lambdify(self.core.x, data['position_func'], 'numpy')

        x_vals = np.linspace(a - 1, b + 1, 1000)
        rate_vals = rate_numpy(x_vals)
        position_vals = position_numpy(x_vals)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot rate function
        ax1.plot(x_vals, rate_vals, 'b-', linewidth=2, label=f"Rate: f'(x) = {data['rate_func']}")

        # Shade area under rate curve
        x_area = np.linspace(a, b, 1000)
        rate_area = [rate_numpy(x) for x in x_area]
        ax1.fill_between(x_area, rate_area, alpha=0.3, color='lightgreen',
                        label=f'Net change = {data["net_change"]:.4f}')

        ax1.axvline(x=a, color='red', linestyle='--', alpha=0.7)
        ax1.axvline(x=b, color='red', linestyle='--', alpha=0.7)
        ax1.set_xlabel('x (time)')
        ax1.set_ylabel("f'(x) (rate)")
        ax1.set_title('Rate of Change Function')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot position function
        ax2.plot(x_vals, position_vals, 'g-', linewidth=2, label=f'Position: f(x) = {data["position_func"]}')

        # Mark change in position
        ax2.plot([a, b], [data['f_a'], data['f_b']], 'ro', markersize=8)
        ax2.plot([a, b], [data['f_a'], data['f_b']], 'r--', linewidth=2, alpha=0.7,
                label=f'Change: f({b}) - f({a}) = {data["position_change"]:.4f}')

        ax2.set_xlabel('x (time)')
        ax2.set_ylabel('f(x) (position)')
        ax2.set_title('Position Function')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        print(f"Net Change Theorem Verification:")
        print(f"∫[{a} to {b}] f'(x) dx = {data['net_change']:.6f}")
        print(f"f({b}) - f({a}) = {data['f_b']:.6f} - {data['f_a']:.6f} = {data['position_change']:.6f}")
        print(f"Error: {data['error']:.8f}")

    def compare_integration_methods(self, func_str: str, interval: Tuple[float, float] = (0, 2)) -> None:
        '''
        Compare different numerical integration methods.

        Args:
            func_str: Function to integrate
            interval: Integration bounds
        '''
        data = compare_integration_methods_data(func_str, interval)

        plt.figure(figsize=(15, 10))

        for i, (method_name, method_data) in enumerate(data['methods_data'].items()):
            plt.subplot(2, 2, i + 1)
            plt.loglog(method_data['n_values'], method_data['errors'], 'o-', linewidth=2, markersize=6)
            plt.xlabel('Number of subdivisions')
            plt.ylabel('Absolute error')
            plt.title(f'{method_name} Rule')
            plt.grid(True, alpha=0.3)

        plt.suptitle(f'Integration Method Convergence for f(x) = {data["func_expr"]}', fontsize=14)
        plt.tight_layout()
        plt.show()

        print(f"Exact value: {data['exact_value']:.8f}")
        print("\nFinal errors with largest n:")
        for method_name, method_data in data['methods_data'].items():
            final_error = method_data['errors'][-1]
            print(f"{method_name}: {final_error:.2e}")


def interactive_fundamental_theorem_explorer():
    '''Interactive exploration of FTC concepts.'''
    print("=== Interactive FTC Explorer ===")
    print("Exploring different functions and their properties under FTC")

    test_functions = [
        "x**2",
        "sin(x)",
        "exp(x)",
        "1/(x**2 + 1)",
        "x*exp(-x**2/2)"
    ]

    visualizer = FundamentalTheoremVisualizer()

    for i, func in enumerate(test_functions):
        print(f"\n--- Function {i+1}: f(x) = {func} ---")

        try:
            # Test Riemann sums
            visualizer.riemann_sum_visualization(func, (0, 2), 20)

            # Test FTC Part 1
            visualizer.ftc_part1_demo(func, 0)

            # Test FTC Part 2
            visualizer.ftc_part2_demo(func, (0, 2))

        except Exception as e:
            print(f"Error with function {func}: {e}")


# Convenience class that maintains the same interface as before
class FundamentalTheorem:
    '''Wrapper class that maintains the original interface.'''

    def __init__(self):
        self.visualizer = FundamentalTheoremVisualizer()
        self.core = self.visualizer.core

    def riemann_sum_visualization(self, func_str: str = "x**2", interval: Tuple[float, float] = (0, 2),
                                  n_rectangles: int = 10) -> None:
        self.visualizer.riemann_sum_visualization(func_str, interval, n_rectangles)

    def fundamental_theorem_part1_demo(self, func_str: str = "2*x", lower_bound: float = 0) -> None:
        self.visualizer.fundamental_theorem_part1_demo(func_str, lower_bound)

    def fundamental_theorem_part2_demo(self, func_str: str = "x**2", interval: Tuple[float, float] = (0, 2)) -> None:
        self.visualizer.fundamental_theorem_part2_demo(func_str, interval)

    def mean_value_theorem_demo(self, func_str: str = "x**3 - 3*x**2 + 2*x",
                               interval: Tuple[float, float] = (0, 3)) -> None:
        self.visualizer.mean_value_theorem_demo(func_str, interval)

    def net_change_theorem_demo(self, rate_func_str: str = "2*x + 1",
                               interval: Tuple[float, float] = (0, 3)) -> None:
        self.visualizer.net_change_theorem_demo(rate_func_str, interval)

    def compare_integration_methods(self, func_str: str, interval: Tuple[float, float] = (0, 2)) -> None:
        self.visualizer.compare_integration_methods(func_str, interval)

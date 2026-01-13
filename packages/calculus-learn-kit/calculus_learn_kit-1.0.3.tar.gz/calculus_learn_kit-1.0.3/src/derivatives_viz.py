'''
' Visualization for Common Derivatives
' ------------------------------------
'
' This module handles all visualization logic for derivatives,
' separated from the core mathematical calculations.
'
' @file: derivatives_viz.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sympy as sp
from mpl_toolkits.mplot3d import Axes3D
from typing import Tuple
try:
    from .derivatives_core import CommonDerivativesCore, get_function_families, format_derivative_table
except ImportError:
    from derivatives_core import CommonDerivativesCore, get_function_families, format_derivative_table


class CommonDerivativesVisualizer:
    '''Handles all visualizations for common derivatives.'''

    def __init__(self):
        self.core = CommonDerivativesCore()

    def display_derivative_table(self) -> None:
        '''Display a formatted table of common derivatives.'''
        print(format_derivative_table())

    def visualize_function_and_derivative(self, func_str: str, x_range: Tuple[float, float] = (-3, 3),
                                        title: str = None) -> None:
        '''
        Visualize a function and its derivative side by side.

        Args:
            func_str: Function as string (SymPy format)
            x_range: Range for x values
            title: Optional title for the plot
        '''
        x_vals = np.linspace(x_range[0], x_range[1], 1000)

        try:
            y_vals, dy_vals, func, derivative = self.core.calculate_function_and_derivative(func_str, x_vals)

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            # Plot original function
            ax1.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'f(x) = {func}')
            ax1.set_title(f'Function: f(x) = {func}')
            ax1.set_xlabel('x')
            ax1.set_ylabel('f(x)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # Plot derivative
            ax2.plot(x_vals, dy_vals, 'r-', linewidth=2, label=f"f'(x) = {derivative}")
            ax2.set_title(f"Derivative: f'(x) = {derivative}")
            ax2.set_xlabel('x')
            ax2.set_ylabel("f'(x)")
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            if title:
                fig.suptitle(title, fontsize=16)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error plotting function {func_str}: {e}")

    def demonstrate_derivative_patterns(self) -> None:
        '''Demonstrate common derivative patterns with visualizations.'''
        patterns = self.core.get_derivative_patterns()

        for pattern_name, functions in patterns.items():
            print(f"\n=== {pattern_name} ===")

            fig, axes = plt.subplots(2, len(functions), figsize=(4*len(functions), 8))
            if len(functions) == 1:
                axes = axes.reshape(2, 1)

            for i, func_str in enumerate(functions):
                try:
                    if "log" in func_str:
                        x_vals = np.linspace(0.1, 5, 1000)
                    elif "exp" in func_str:
                        x_vals = np.linspace(-2, 2, 1000)
                    else:
                        x_vals = np.linspace(-3, 3, 1000)

                    y_vals, dy_vals, func, derivative = self.core.calculate_function_and_derivative(func_str, x_vals)

                    # Plot function
                    axes[0, i].plot(x_vals, y_vals, 'b-', linewidth=2)
                    axes[0, i].set_title(f'f(x) = {func}')
                    axes[0, i].grid(True, alpha=0.3)
                    axes[0, i].set_xlabel('x')
                    axes[0, i].set_ylabel('f(x)')

                    # Plot derivative
                    axes[1, i].plot(x_vals, dy_vals, 'r-', linewidth=2)
                    axes[1, i].set_title(f"f'(x) = {derivative}")
                    axes[1, i].grid(True, alpha=0.3)
                    axes[1, i].set_xlabel('x')
                    axes[1, i].set_ylabel("f'(x)")

                except Exception as e:
                    print(f"Error with function {func_str}: {e}")
                    continue

            plt.suptitle(f'{pattern_name} and Their Derivatives', fontsize=16)
            plt.tight_layout()
            plt.show()

    def slope_field_visualization(self, func_str: str, x_range: Tuple[float, float] = (-3, 3),
                                y_range: Tuple[float, float] = (-3, 3)) -> None:
        '''
        Create a slope field visualization for a derivative.

        Args:
            func_str: Function whose derivative defines the slope field
            x_range: Range for x values
            y_range: Range for y values
        '''
        data = self.core.calculate_slope_field_data(func_str, x_range, y_range)

        if not data['calculation_success']:
            print(f"Error creating slope field: {data.get('error', 'Unknown error')}")
            return

        plt.figure(figsize=(12, 8))

        # Plot slope field
        plt.quiver(data['X'], data['Y'], data['dx_norm'], data['dy_norm'],
                  data['slopes'], cmap='viridis', alpha=0.7)

        # Plot the actual function if it exists in our y range
        if np.any(data['valid_mask']):
            plt.plot(data['x_continuous'][data['valid_mask']],
                    data['y_continuous'][data['valid_mask']], 'r-', linewidth=3,
                    label=f'f(x) = {data["func_expr"]}')

        plt.xlim(x_range)
        plt.ylim(y_range)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(f"Slope Field for f'(x) = {data['derivative_expr']}")
        plt.colorbar(label='Slope value')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def derivative_chain_rule_examples(self) -> None:
        '''Demonstrate chain rule with complex composite functions.'''
        examples = self.core.calculate_chain_rule_examples()

        print("\n=== Chain Rule Examples ===")

        for example in examples:
            print(f"\nFunction: f(x) = {example['function']}")
            print(f"Derivative: f'(x) = {example['derivative']}")
            print(f"Simplified: f'(x) = {example['simplified']}")

            # Visualize if possible
            try:
                self.visualize_function_and_derivative(example['func_str'], (-2, 2),
                                                     f"Chain Rule: f(x) = {example['function']}")
            except Exception as e:
                print(f"Could not visualize {example['func_str']}: {e}")

    def higher_order_derivatives(self, func_str: str = "x**4 - 4*x**3 + 6*x**2 - 4*x + 1",
                                n_derivatives: int = 4) -> None:
        '''
        Calculate and visualize higher-order derivatives.

        Args:
            func_str: Function to differentiate
            n_derivatives: Number of derivatives to calculate
        '''
        derivatives = self.core.calculate_higher_order_derivatives(func_str, n_derivatives)

        # Create visualizations
        fig, axes = plt.subplots(1, len(derivatives), figsize=(4*len(derivatives), 6))
        if len(derivatives) == 1:
            axes = [axes]

        x_vals = np.linspace(-2, 3, 1000)
        colors = ['blue', 'red', 'green', 'orange', 'purple']

        for i, deriv in enumerate(derivatives):
            try:
                deriv_numpy = sp.lambdify(self.core.x, deriv, 'numpy')
                y_vals = deriv_numpy(x_vals)

                order = "f(x)" if i == 0 else f"f^({i})(x)"
                axes[i].plot(x_vals, y_vals, color=colors[i % len(colors)],
                           linewidth=2, label=f'{order} = {deriv}')
                axes[i].set_title(f'{order}')
                axes[i].grid(True, alpha=0.3)
                axes[i].set_xlabel('x')
                axes[i].set_ylabel(f'{order}')

                # Add zero crossings
                zero_crossings = []
                for j in range(len(y_vals)-1):
                    if y_vals[j] * y_vals[j+1] < 0:
                        zero_crossings.append(x_vals[j])

                if zero_crossings:
                    axes[i].plot(zero_crossings, [0]*len(zero_crossings), 'ko', markersize=6)

            except Exception as e:
                print(f"Error plotting derivative {i}: {e}")

        plt.suptitle(f'Higher Order Derivatives of f(x) = {derivatives[0]}', fontsize=14)
        plt.tight_layout()
        plt.show()

        # Print derivatives
        print(f"\nHigher-order derivatives of f(x) = {derivatives[0]}:")
        for i, deriv in enumerate(derivatives):
            order = "f(x)" if i == 0 else f"f^({i})(x)"
            print(f"{order} = {deriv}")

    def critical_points_analysis(self, func_str: str = "x**3 - 3*x**2 + 2") -> None:
        '''
        Find and analyze critical points using derivatives.

        Args:
            func_str: Function to analyze
        '''
        analysis = self.core.find_critical_points(func_str)

        print(f"Function: f(x) = {analysis['function']}")
        print(f"First derivative: f'(x) = {analysis['first_derivative']}")
        print(f"Second derivative: f''(x) = {analysis['second_derivative']}")
        print(f"Critical points: {analysis['critical_points']}")

        # Create visualization
        if analysis['critical_points']:
            func_numpy = lambda x: np.array([float(analysis['function'].subs(analysis['function'].free_symbols.pop(), val)) for val in x])
            first_deriv_numpy = lambda x: np.array([float(analysis['first_derivative'].subs(analysis['first_derivative'].free_symbols.pop(), val)) for val in x])
            second_deriv_numpy = lambda x: np.array([float(analysis['second_derivative'].subs(analysis['second_derivative'].free_symbols.pop(), val)) for val in x])

            x_vals = np.linspace(min(analysis['critical_points'])-2, max(analysis['critical_points'])+2, 1000)

            try:
                y_vals = func_numpy(x_vals)
                y_prime = first_deriv_numpy(x_vals)
                y_double_prime = second_deriv_numpy(x_vals)
            except:
                # Fallback to sympy lambdify
                func_lambdified = analysis['function'].lambdify(analysis['function'].free_symbols.pop(), 'numpy')
                first_deriv_lambdified = analysis['first_derivative'].lambdify(analysis['first_derivative'].free_symbols.pop(), 'numpy')
                second_deriv_lambdified = analysis['second_derivative'].lambdify(analysis['second_derivative'].free_symbols.pop(), 'numpy')

                y_vals = func_lambdified(x_vals)
                y_prime = first_deriv_lambdified(x_vals)
                y_double_prime = second_deriv_lambdified(x_vals)

            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))

            # Plot function
            ax1.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'f(x) = {analysis["function"]}')

            # Mark critical points
            for point_data in analysis['analyzed_points']:
                cp = point_data['x']
                y_cp = point_data['y']
                point_type = point_data['type']

                if 'minimum' in point_type:
                    color, marker = 'red', 'o'
                elif 'maximum' in point_type:
                    color, marker = 'green', '^'
                else:
                    color, marker = 'orange', 's'

                ax1.plot(cp, y_cp, marker, color=color, markersize=10,
                        label=f'{point_type} at x={cp:.2f}')

                print(f"At x = {cp:.2f}: f''(x) = {point_data['second_derivative']:.2f} → {point_type}")

            ax1.set_title('Function with Critical Points')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_xlabel('x')
            ax1.set_ylabel('f(x)')

            # Plot first derivative
            ax2.plot(x_vals, y_prime, 'r-', linewidth=2, label=f"f'(x) = {analysis['first_derivative']}")
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)

            for cp in analysis['critical_points']:
                ax2.plot(cp, 0, 'ko', markersize=8)

            ax2.set_title('First Derivative')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_xlabel('x')
            ax2.set_ylabel("f'(x)")

            # Plot second derivative
            ax3.plot(x_vals, y_double_prime, 'g-', linewidth=2, label=f"f''(x) = {analysis['second_derivative']}")
            ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)

            for point_data in analysis['analyzed_points']:
                cp = point_data['x']
                second_val = point_data['second_derivative']
                ax3.plot(cp, second_val, 'ko', markersize=8)

            ax3.set_title('Second Derivative')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            ax3.set_xlabel('x')
            ax3.set_ylabel("f''(x)")

            plt.tight_layout()
            plt.show()


def derivative_game():
    '''Interactive game for practicing derivatives.'''

    visualizer = CommonDerivativesVisualizer()

    # Sample functions for the game
    functions = [
        "x**2", "x**3", "sin(x)", "cos(x)", "exp(x)", "log(x)",
        "x*sin(x)", "exp(x)*cos(x)", "x**2 + 3*x + 1", "sqrt(x)"
    ]

    print("\n=== Derivative Practice Game ===")
    print("I'll show you a function, and you can see its derivative!")

    for i, func_str in enumerate(functions[:5]):  # Show first 5
        print(f"\nFunction {i+1}: f(x) = {func_str}")

        try:
            func = sp.sympify(func_str)
            derivative = sp.diff(func, visualizer.core.x)

            input("Press Enter to see the derivative...")
            print(f"Answer: f'(x) = {derivative}")

            # Show visualization
            visualizer.visualize_function_and_derivative(func_str, (-2, 2))

        except Exception as e:
            print(f"Error with function {func_str}: {e}")


# Convenience class that maintains the same interface as before
class CommonDerivatives:
    '''Wrapper class that maintains the original interface.'''

    def __init__(self):
        self.visualizer = CommonDerivativesVisualizer()
        self.core = self.visualizer.core
        # For backward compatibility
        self.derivative_formulas = self.core.derivative_formulas

    def display_derivative_table(self) -> None:
        self.visualizer.display_derivative_table()

    def visualize_function_and_derivative(self, func_str: str, x_range: Tuple[float, float] = (-3, 3),
                                        title: str = None) -> None:
        self.visualizer.visualize_function_and_derivative(func_str, x_range, title)

    def demonstrate_derivative_patterns(self) -> None:
        self.visualizer.demonstrate_derivative_patterns()

    def slope_field_visualization(self, func_str: str, x_range: Tuple[float, float] = (-3, 3),
                                y_range: Tuple[float, float] = (-3, 3)) -> None:
        self.visualizer.slope_field_visualization(func_str, x_range, y_range)

    def derivative_chain_rule_examples(self) -> None:
        self.visualizer.derivative_chain_rule_examples()

    def higher_order_derivatives(self, func_str: str = "x**4 - 4*x**3 + 6*x**2 - 4*x + 1",
                                n_derivatives: int = 4) -> None:
        self.visualizer.higher_order_derivatives(func_str, n_derivatives)

    def critical_points_analysis(self, func_str: str = "x**3 - 3*x**2 + 2") -> None:
        self.visualizer.critical_points_analysis(func_str)

"""
' Common Integrals Visualization Module
' -------------------------------------
'
' This module provides visualization functionality for common integrals.
'
' @file: integrals_viz.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from typing import Dict, List, Tuple, Optional
import matplotlib.patches as patches
try:
    from .integrals_core import CommonIntegralsCore
except ImportError:
    from integrals_core import CommonIntegralsCore
import random


class CommonIntegralsVisualizer:
    """Visualization for common integrals."""

    def __init__(self):
        self.core = CommonIntegralsCore()

    @property
    def integral_formulas(self):
        """Access to integral formulas from the core module."""
        return self.core.integral_formulas

    def display_integral_table(self) -> None:
        """Display a comprehensive table of common integral formulas."""
        formulas = self.core.get_integral_table_data()

        print("\n" + "=" * 80)
        print("COMMON INTEGRAL FORMULAS")
        print("=" * 80)

        for name, formula in formulas.items():
            print(f"\n{name.upper().replace('_', ' ')}:")
            print(f"  Function:      {formula['function']}")
            print(f"  Integral:      {formula['integral']}")
            print(
                f"  Example:       ∫({formula['example']}) dx = {formula['antiderivative']} + C"
            )

    def visualize_integral_as_area(
        self,
        func_str: str,
        interval: Tuple[float, float] = (0, 2),
        num_points: int = 1000,
    ) -> None:
        """Visualize an integral as the area under a curve."""
        data = self.core.calculate_integral_area(func_str, interval, num_points)

        if data is None:
            return

        plt.figure(figsize=(12, 8))

        # Plot the function
        plt.plot(
            data["x_plot"],
            data["y_plot"],
            "b-",
            linewidth=2,
            label=f"f(x) = {func_str}",
        )

        # Fill the area under the curve
        plt.fill_between(
            data["x_fill"],
            0,
            data["y_fill"],
            alpha=0.3,
            color="lightblue",
            label="Area under curve",
        )

        # Add vertical lines at bounds
        a, b = interval
        plt.axvline(x=a, color="red", linestyle="--", alpha=0.7, label=f"x = {a}")
        plt.axvline(x=b, color="red", linestyle="--", alpha=0.7, label=f"x = {b}")

        plt.axhline(y=0, color="black", linewidth=0.5)
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Add area information
        title = f"Integral as Area: ∫[{a}, {b}] ({func_str}) dx"
        if data["exact_area"] is not None:
            title += f'\nExact Area = {data["exact_area"]:.6f}'
        if data["numerical_area"] is not None:
            title += f'\nNumerical Area = {data["numerical_area"]:.6f}'
            if data["error"] is not None:
                title += f' (±{data["error"]:.2e})'

        plt.title(title)
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.tight_layout()
        plt.show()

    def compare_integration_methods(
        self, func_str: str, interval: Tuple[float, float] = (0, 2)
    ) -> None:
        """Compare different numerical integration methods."""
        data = self.core.compare_integration_methods_calc(func_str, interval)

        if data is None:
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot the function
        ax1.plot(
            data["x_vals"],
            data["y_vals"],
            "b-",
            linewidth=2,
            label=f"f(x) = {func_str}",
        )

        # Fill area
        a, b = interval
        ax1.fill_between(
            data["x_vals"], 0, data["y_vals"], alpha=0.3, color="lightblue"
        )
        ax1.axvline(x=a, color="red", linestyle="--", alpha=0.7)
        ax1.axvline(x=b, color="red", linestyle="--", alpha=0.7)
        ax1.axhline(y=0, color="black", linewidth=0.5)
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f"Function: {func_str}")
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")

        # Compare methods
        methods = list(data["methods_results"].keys())
        values = list(data["methods_results"].values())

        # Filter out None values
        valid_methods = []
        valid_values = []
        for method, value in zip(methods, values):
            if value is not None:
                valid_methods.append(method)
                valid_values.append(value)

        bars = ax2.bar(range(len(valid_methods)), valid_values, alpha=0.7)
        ax2.set_xticks(range(len(valid_methods)))
        ax2.set_xticklabels(valid_methods, rotation=45, ha="right")
        ax2.set_ylabel("Integral Value")
        ax2.set_title("Comparison of Integration Methods")
        ax2.grid(True, alpha=0.3)

        # Add exact value line if available
        if data["exact_value"] is not None:
            ax2.axhline(
                y=data["exact_value"],
                color="red",
                linestyle="--",
                label=f'Exact: {data["exact_value"]:.6f}',
            )
            ax2.legend()

        # Color bars based on accuracy
        if data["exact_value"] is not None:
            for bar, value in zip(bars, valid_values):
                error = abs(value - data["exact_value"])
                if error < 0.01:
                    bar.set_color("green")
                elif error < 0.1:
                    bar.set_color("orange")
                else:
                    bar.set_color("red")

        plt.tight_layout()
        plt.show()

        # Print numerical comparison
        print(f"\nIntegration Methods Comparison for ∫[{a}, {b}] ({func_str}) dx:")
        print("-" * 60)
        if data["exact_value"] is not None:
            print(f"Exact Value: {data['exact_value']:.10f}")
            print("-" * 60)

        for method, value in data["methods_results"].items():
            if value is not None:
                if data["exact_value"] is not None:
                    error = abs(value - data["exact_value"])
                    print(f"{method:<20}: {value:.10f} (Error: {error:.2e})")
                else:
                    print(f"{method:<20}: {value:.10f}")

    def integration_by_parts_demo(
        self, u_str: str = "x", dv_str: str = "exp(x)"
    ) -> None:
        """Demonstrate integration by parts step by step."""
        data = self.core.integration_by_parts_calc(u_str, dv_str)

        if data is None:
            return

        print("\n" + "=" * 60)
        print("INTEGRATION BY PARTS DEMONSTRATION")
        print("=" * 60)
        print(f"∫ u dv = uv - ∫ v du")
        print(f"\nGiven: ∫ ({data['u']}) × ({data['dv']}) dx")
        print(f"\nStep 1: Choose u and dv")
        print(f"  u = {data['u']}")
        print(f"  dv = {data['dv']} dx")
        print(f"\nStep 2: Find du and v")
        print(f"  du = d({data['u']})/dx = {data['du']} dx")
        print(f"  v = ∫({data['dv']}) dx = {data['v']}")
        print(f"\nStep 3: Apply the formula")
        print(f"  uv = ({data['u']}) × ({data['v']}) = {data['uv']}")
        print(f"  v du = ({data['v']}) × ({data['du']}) = {data['v_du']}")
        print(f"  ∫ v du = ∫({data['v_du']}) dx = {data['remaining_integral']}")
        print(f"\nStep 4: Final result")
        print(
            f"  ∫ ({data['original']}) dx = {data['uv']} - ({data['remaining_integral']}) + C"
        )
        print(f"                          = {data['result']} + C")

        # Visualization
        x_vals = np.linspace(-2, 2, 1000)
        try:
            u_func = sp.lambdify(sp.Symbol("x"), data["u"], "numpy")
            original_func = sp.lambdify(sp.Symbol("x"), data["original"], "numpy")
            result_func = sp.lambdify(sp.Symbol("x"), data["result"], "numpy")

            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

            # Plot u
            ax1.plot(x_vals, u_func(x_vals), "b-", linewidth=2)
            ax1.set_title(f'u = {data["u"]}')
            ax1.grid(True, alpha=0.3)
            ax1.set_xlabel("x")
            ax1.set_ylabel("u(x)")

            # Plot original integrand
            y_orig = original_func(x_vals)
            ax2.plot(x_vals, y_orig, "g-", linewidth=2)
            ax2.fill_between(
                x_vals[400:600], 0, y_orig[400:600], alpha=0.3, color="lightgreen"
            )
            ax2.set_title(f'Original: {data["original"]}')
            ax2.grid(True, alpha=0.3)
            ax2.set_xlabel("x")
            ax2.set_ylabel("f(x)")

            # Plot result (antiderivative)
            y_result = result_func(x_vals)
            ax3.plot(x_vals, y_result, "r-", linewidth=2)
            ax3.set_title(f'Antiderivative: {data["result"]}')
            ax3.grid(True, alpha=0.3)
            ax3.set_xlabel("x")
            ax3.set_ylabel("F(x)")

            # Show the process
            ax4.text(
                0.1,
                0.8,
                f"∫ {data['original']} dx",
                fontsize=12,
                transform=ax4.transAxes,
            )
            ax4.text(
                0.1,
                0.6,
                f"= {data['uv']} - ∫ {data['v_du']} dx",
                fontsize=12,
                transform=ax4.transAxes,
            )
            ax4.text(
                0.1,
                0.4,
                f"= {data['uv']} - {data['remaining_integral']}",
                fontsize=12,
                transform=ax4.transAxes,
            )
            ax4.text(
                0.1,
                0.2,
                f"= {data['result']} + C",
                fontsize=12,
                transform=ax4.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5),
            )
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
            ax4.axis("off")
            ax4.set_title("Integration by Parts Steps")

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error in visualization: {e}")

    def substitution_method_demo(
        self, func_str: str = "2*x*exp(x**2)", substitution: str = "u = x**2"
    ) -> None:
        """Demonstrate the substitution method for integration."""
        data = self.core.substitution_method_calc(func_str, substitution)

        if data is None:
            return

        print("\n" + "=" * 70)
        print("SUBSTITUTION METHOD DEMONSTRATION")
        print("=" * 70)
        print(f"∫ {data['func_str']} dx")
        print(f"\nStep 1: Choose substitution")
        print(f"  Let {substitution}")
        print(f"  Then du/dx = {data['du_dx']}")
        print(f"  So dx = ({data['dx_in_du']}) du")
        print(f"\nStep 2: Substitute")
        print(f"  ∫ {data['func_str']} dx = ∫ ({data['func_in_u']}) du")
        print(f"\nStep 3: Integrate")
        print(f"  ∫ ({data['func_in_u']}) du = {data['integral_u']} + C")
        print(f"\nStep 4: Substitute back")
        print(f"  = {data['final_result']} + C")

        # Visualization
        try:
            x_vals = np.linspace(-2, 2, 1000)
            original_func = sp.lambdify(sp.Symbol("x"), data["original_func"], "numpy")
            result_func = sp.lambdify(sp.Symbol("x"), data["final_result"], "numpy")

            # u substitution values - ensure it returns an array
            u_substitution_func = sp.lambdify(
                sp.Symbol("x"), data["u_substitution"], "numpy"
            )
            u_vals = u_substitution_func(x_vals)
            # Handle case where u_substitution is a constant
            if np.isscalar(u_vals):
                u_vals = np.full_like(x_vals, u_vals)

            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

            # Original function
            y_orig = original_func(x_vals)
            ax1.plot(x_vals, y_orig, "b-", linewidth=2)
            ax1.fill_between(
                x_vals[400:600], 0, y_orig[400:600], alpha=0.3, color="lightblue"
            )
            ax1.set_title(f'Original: f(x) = {data["func_str"]}')
            ax1.grid(True, alpha=0.3)
            ax1.set_xlabel("x")
            ax1.set_ylabel("f(x)")

            # Substitution u(x)
            ax2.plot(x_vals, u_vals, "g-", linewidth=2)
            ax2.set_title(f"Substitution: {substitution}")
            ax2.grid(True, alpha=0.3)
            ax2.set_xlabel("x")
            ax2.set_ylabel("u")

            # Result (antiderivative)
            y_result = result_func(x_vals)
            ax3.plot(x_vals, y_result, "r-", linewidth=2)
            ax3.set_title(f'Antiderivative: F(x) = {data["final_result"]}')
            ax3.grid(True, alpha=0.3)
            ax3.set_xlabel("x")
            ax3.set_ylabel("F(x)")

            # Show the process
            ax4.text(
                0.1,
                0.9,
                f"∫ {data['func_str']} dx",
                fontsize=12,
                transform=ax4.transAxes,
            )
            ax4.text(
                0.1, 0.7, f"Let {substitution}", fontsize=12, transform=ax4.transAxes
            )
            ax4.text(
                0.1,
                0.5,
                f"du = {data['du_dx']} dx",
                fontsize=12,
                transform=ax4.transAxes,
            )
            ax4.text(
                0.1,
                0.3,
                f"= ∫ {data['func_in_u']} du",
                fontsize=12,
                transform=ax4.transAxes,
            )
            ax4.text(
                0.1,
                0.1,
                f"= {data['final_result']} + C",
                fontsize=12,
                transform=ax4.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5),
            )
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
            ax4.axis("off")
            ax4.set_title("Substitution Method Steps")

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error in visualization: {e}")

    def area_between_curves(
        self,
        func1_str: str = "x**2",
        func2_str: str = "x + 2",
        interval: Optional[Tuple[float, float]] = None,
    ) -> None:
        """Visualize and calculate area between two curves."""
        data = self.core.calculate_area_between_curves(func1_str, func2_str, interval)

        if data is None:
            return

        a, b = data["interval"]

        plt.figure(figsize=(12, 8))

        # Plot both functions
        plt.plot(
            data["x_plot"],
            data["y1_plot"],
            "b-",
            linewidth=2,
            label=f"f₁(x) = {func1_str}",
        )
        plt.plot(
            data["x_plot"],
            data["y2_plot"],
            "r-",
            linewidth=2,
            label=f"f₂(x) = {func2_str}",
        )

        # Fill area between curves
        plt.fill_between(
            data["x_fill"],
            data["y1_fill"],
            data["y2_fill"],
            alpha=0.3,
            color="lightgreen",
            label="Area between curves",
        )

        # Mark intersection points
        plt.axvline(
            x=a, color="purple", linestyle="--", alpha=0.7, label=f"x = {a:.2f}"
        )
        plt.axvline(
            x=b, color="purple", linestyle="--", alpha=0.7, label=f"x = {b:.2f}"
        )
        plt.plot([a, b], [data["y1_fill"][0], data["y1_fill"][-1]], "ro", markersize=8)
        plt.plot([a, b], [data["y2_fill"][0], data["y2_fill"][-1]], "ro", markersize=8)

        plt.axhline(y=0, color="black", linewidth=0.5)
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Title with area information
        title = f"Area Between Curves: {func1_str} and {func2_str}"
        if data["exact_area"] is not None:
            title += f'\nExact Area = {data["exact_area"]:.6f}'
        if data["numerical_area"] is not None:
            title += f'\nNumerical Area = {data["numerical_area"]:.6f}'
            if data["error"] is not None:
                title += f' (±{data["error"]:.2e})'

        plt.title(title)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.tight_layout()
        plt.show()

        # Print mathematical explanation
        print(f"\nArea between {func1_str} and {func2_str}:")
        print(f"Upper function: {data['upper_func']}")
        print(f"Lower function: {data['lower_func']}")
        print(
            f"Area = ∫[{a:.3f}, {b:.3f}] |({data['upper_func']}) - ({data['lower_func']})| dx"
        )
        if data["exact_area"] is not None:
            print(f"     = {data['exact_area']:.6f}")

    def improper_integrals_demo(self) -> None:
        """Demonstrate improper integrals with examples and visualizations."""
        print("\n" + "=" * 60)
        print("∫ IMPROPER INTEGRALS DEMONSTRATION")
        print("=" * 60)

        examples = [
            {
                'name': 'Type I: Infinite Upper Limit',
                'function': '1/(x**2)',
                'interval': (1, None),
                'description': '∫[1,∞] 1/x² dx (converges)'
            },
            {
                'name': 'Type I: Infinite Lower Limit',
                'function': 'exp(x)',
                'interval': (None, 0),
                'description': '∫[-∞,0] eˣ dx (converges)'
            },
            {
                'name': 'Type I: Divergent Example',
                'function': '1/x',
                'interval': (1, None),
                'description': '∫[1,∞] 1/x dx (diverges)'
            },
            {
                'name': 'Type I: Both Infinite Limits',
                'function': '1/(1 + x**2)',
                'interval': (None, None),
                'description': '∫[-∞,∞] 1/(1+x²) dx (converges to π)'
            }
        ]

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()

        for i, example in enumerate(examples):
            ax = axes[i]

            # Calculate the improper integral
            result = self.core.calculate_improper_integral(
                example['function'],
                example['interval']
            )

            if result is None:
                continue

            # Create function for plotting
            try:
                func_expr = sp.sympify(example['function'])
                x = sp.Symbol('x')
                func_lambda = sp.lambdify(x, func_expr, 'numpy')

                # Determine plotting range
                a, b = example['interval']
                if a is None and b is None:  # (-∞, ∞)
                    x_range = np.linspace(-10, 10, 1000)
                elif a is None:  # (-∞, b]
                    x_range = np.linspace(b-10, b, 1000)
                elif b is None:  # [a, ∞)
                    x_range = np.linspace(a, a+10, 1000)
                else:  # [a, b]
                    x_range = np.linspace(a, b, 1000)

                # Evaluate function, handle division by zero
                y_values = []
                x_plot = []
                for xi in x_range:
                    try:
                        yi = func_lambda(xi)
                        if np.isfinite(yi) and abs(yi) < 100:  # Filter out infinite values
                            y_values.append(yi)
                            x_plot.append(xi)
                    except:
                        continue

                x_plot = np.array(x_plot)
                y_values = np.array(y_values)

                # Plot function
                ax.plot(x_plot, y_values, 'b-', linewidth=2, label=f"f(x) = {example['function']}")

                # Fill area under curve for finite portions
                if a is not None and b is not None:
                    # Regular definite integral visualization
                    x_fill = x_plot[(x_plot >= a) & (x_plot <= b)]
                    y_fill = y_values[(x_plot >= a) & (x_plot <= b)]
                    ax.fill_between(x_fill, 0, y_fill, alpha=0.3, color='lightblue')
                elif a is not None:  # [a, ∞)
                    x_fill = x_plot[x_plot >= a]
                    y_fill = y_values[x_plot >= a]
                    if len(x_fill) > 0:
                        ax.fill_between(x_fill, 0, y_fill, alpha=0.3, color='lightgreen')
                elif b is not None:  # (-∞, b]
                    x_fill = x_plot[x_plot <= b]
                    y_fill = y_values[x_plot <= b]
                    if len(x_fill) > 0:
                        ax.fill_between(x_fill, 0, y_fill, alpha=0.3, color='lightcoral')

                # Mark boundaries
                if a is not None:
                    ax.axvline(x=a, color='red', linestyle='--', alpha=0.7, label=f'x = {a}')
                if b is not None:
                    ax.axvline(x=b, color='red', linestyle='--', alpha=0.7, label=f'x = {b}')

                ax.axhline(y=0, color='black', linewidth=0.5)
                ax.grid(True, alpha=0.3)

                # Set title with result
                if result['converges']:
                    convergence_text = f"Converges to {result['convergence_value']:.4f}" if result['convergence_value'] is not None else "Converges"
                    ax.set_title(f"{example['name']}\n{example['description']}\n{convergence_text}",
                                fontsize=10, pad=10)
                else:
                    ax.set_title(f"{example['name']}\n{example['description']}\nDiverges",
                                fontsize=10, pad=10)

                ax.legend(fontsize=8)
                ax.set_xlabel('x')
                ax.set_ylabel('f(x)')

            except Exception as e:
                ax.text(0.5, 0.5, f"Error plotting:\n{str(e)}",
                       transform=ax.transAxes, ha='center', va='center')
                ax.set_title(example['name'])

        plt.tight_layout()
        plt.suptitle("Improper Integrals Examples", fontsize=16, y=1.02)
        plt.show()

        # Print detailed results
        print("\nDetailed Analysis:")
        print("-" * 60)
        for i, example in enumerate(examples):
            result = self.core.calculate_improper_integral(
                example['function'],
                example['interval']
            )
            if result:
                print(f"\n{i+1}. {example['name']}")
                print(f"   Function: f(x) = {example['function']}")
                print(f"   Integral: {example['description']}")
                print(f"   Result: {result['symbolic_result']}")
                if result['converges']:
                    if result['convergence_value'] is not None:
                        print(f"   Value: {result['convergence_value']:.6f}")
                    print("   Status: ✅ CONVERGES")
                else:
                    print("   Status: ❌ DIVERGES")

    def volume_of_revolution(
        self,
        func_str: str = "sqrt(x)",
        interval: Tuple[float, float] = (0, 4),
        method: str = "disk",
        axis: str = "x",
    ) -> None:
        """Visualize volume of revolution using disk/washer method."""
        data = self.core.calculate_volume_of_revolution(
            func_str, interval, method, axis
        )

        if data is None:
            return

        fig = plt.figure(figsize=(15, 10))

        # 2D view
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(
            data["x_vals"],
            data["y_vals"],
            "b-",
            linewidth=3,
            label=f"f(x) = {func_str}",
        )
        ax1.fill_between(
            data["x_vals"], 0, data["y_vals"], alpha=0.3, color="lightblue"
        )
        ax1.axhline(y=0, color="black", linewidth=1)
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.set_title("Function to be revolved")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 3D surface of revolution
        ax2 = fig.add_subplot(2, 2, 2, projection="3d")
        ax2.plot_surface(
            data["X_surf"], data["Y_surf"], data["Z_surf"], alpha=0.7, cmap="viridis"
        )
        ax2.set_xlabel("x")
        ax2.set_ylabel("y")
        ax2.set_zlabel("z")
        ax2.set_title("Volume of Revolution")

        # Cross-section view
        ax3 = plt.subplot(2, 2, 3)
        x_mid = (interval[0] + interval[1]) / 2
        y_mid = data["y_vals"][len(data["y_vals"]) // 2]
        circle = plt.Circle((0, 0), y_mid, fill=False, color="red", linewidth=2)
        filled_circle = plt.Circle((0, 0), y_mid, alpha=0.3, color="red")
        ax3.add_patch(filled_circle)
        ax3.add_patch(circle)
        ax3.set_xlim(-y_mid * 1.2, y_mid * 1.2)
        ax3.set_ylim(-y_mid * 1.2, y_mid * 1.2)
        ax3.set_aspect("equal")
        ax3.set_title(f"Cross-section at x = {x_mid:.2f}\\nRadius = {y_mid:.3f}")
        ax3.grid(True, alpha=0.3)

        # Volume calculation info
        ax4 = plt.subplot(2, 2, 4)
        ax4.text(
            0.1,
            0.8,
            f"Volume of Revolution",
            fontsize=14,
            fontweight="bold",
            transform=ax4.transAxes,
        )
        ax4.text(
            0.1,
            0.7,
            f"Function: f(x) = {func_str}",
            fontsize=12,
            transform=ax4.transAxes,
        )
        ax4.text(
            0.1,
            0.6,
            f"Interval: [{interval[0]}, {interval[1]}]",
            fontsize=12,
            transform=ax4.transAxes,
        )
        ax4.text(
            0.1,
            0.5,
            f"Method: {method.capitalize()}",
            fontsize=12,
            transform=ax4.transAxes,
        )
        ax4.text(0.1, 0.4, f"Axis: {axis}", fontsize=12, transform=ax4.transAxes)

        if data["exact_volume"] is not None:
            ax4.text(
                0.1,
                0.3,
                f'Exact Volume: {data["exact_volume"]:.6f}',
                fontsize=12,
                transform=ax4.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5),
            )

        if data["numerical_volume"] is not None:
            ax4.text(
                0.1,
                0.2,
                f'Numerical Volume: {data["numerical_volume"]:.6f}',
                fontsize=12,
                transform=ax4.transAxes,
            )
            if data["error"] is not None:
                ax4.text(
                    0.1,
                    0.1,
                    f'Error: ±{data["error"]:.2e}',
                    fontsize=12,
                    transform=ax4.transAxes,
                )

        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis("off")

        plt.tight_layout()
        plt.show()

        # Print volume calculation
        print(f"\nVolume of Revolution:")
        print(f"V = π ∫[{interval[0]}, {interval[1]}] [f(x)]² dx")
        print(f"V = π ∫[{interval[0]}, {interval[1]}] [{func_str}]² dx")
        if data["exact_volume"] is not None:
            print(f"V = {data['exact_volume']:.6f} cubic units")


# Create instance for backward compatibility
CommonIntegrals = CommonIntegralsVisualizer


def integral_practice_game():
    """Interactive integral practice game."""
    core = CommonIntegralsCore()

    print("\n" + "=" * 60)
    print("🎯 INTEGRAL PRACTICE GAME")
    print("=" * 60)
    print("Solve the integral problems below!")
    print("Type 'quit' to exit, 'hint' for help, or 'new' for a new problem.")

    score = 0
    total_problems = 0

    while True:
        # Generate a new problem
        problem = core.generate_practice_problem()
        total_problems += 1

        print(f"\n📝 Problem {total_problems}:")
        print(f"   {problem['problem_text']}")
        print(f"   (Type: {problem['type']})")

        while True:
            user_answer = input("\n💡 Your answer (without +C): ").strip()

            if user_answer.lower() == "quit":
                print(f"\n🎊 Final Score: {score}/{total_problems-1}")
                print("Thanks for playing!")
                return
            elif user_answer.lower() == "hint":
                if problem["type"] == "Power rule":
                    print("💡 Hint: For x^n, the antiderivative is x^(n+1)/(n+1)")
                elif problem["type"] == "Exponential":
                    print("💡 Hint: For e^(ax), the antiderivative is e^(ax)/a")
                elif problem["type"] == "Trigonometric":
                    print("💡 Hint: d/dx[sin(x)] = cos(x), d/dx[cos(x)] = -sin(x)")
                else:
                    print("💡 Hint: Use the power rule for each term separately")
                continue
            elif user_answer.lower() == "new":
                break

            try:
                # Check the answer
                user_expr = sp.sympify(user_answer)
                correct_expr = sp.sympify(problem["solution"])

                # Check if they're equivalent (derivatives should be the same)
                if (
                    sp.simplify(
                        sp.diff(user_expr, sp.Symbol("x"))
                        - sp.diff(correct_expr, sp.Symbol("x"))
                    )
                    == 0
                ):
                    print("✅ Correct! Great job!")
                    score += 1
                    break
                else:
                    print("❌ Not quite right. Try again!")
                    print(f"   Your answer: {user_answer}")
                    print(f"   Correct answer: {problem['solution']}")
                    break

            except Exception as e:
                print("❌ Invalid input. Please check your syntax.")
                continue

    print(f"\n🎊 Final Score: {score}/{total_problems}")
    print("Thanks for playing!")


# Re-export the practice game
__all__ = ["CommonIntegrals", "integral_practice_game"]

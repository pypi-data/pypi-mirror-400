'''
' Common Integrals Core Module
' ----------------------------
'
' This module provides core calculations for common integrals without visualization.
'
' @file: integrals_core.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
'''

import numpy as np
import sympy as sp
from typing import Dict, List, Tuple, Callable, Optional
from scipy import integrate
import warnings
warnings.filterwarnings('ignore')


class CommonIntegralsCore:
    '''Core calculations for common integrals.'''

    def __init__(self):
        self.x = sp.Symbol('x')
        self.a = sp.Symbol('a', positive=True)
        self.n = sp.Symbol('n')
        self.C = sp.Symbol('C')  # Integration constant

        # Dictionary of common integral formulas
        self.integral_formulas = {
            # Basic functions
            "constant": {
                "function": "c",
                "integral": "cx + C",
                "example": "5",
                "antiderivative": "5*x"
            },
            "power": {
                "function": "x^n",
                "integral": "x^(n+1)/(n+1) + C",
                "example": "x**3",
                "antiderivative": "x**4/4"
            },
            "reciprocal": {
                "function": "1/x",
                "integral": "ln|x| + C",
                "example": "1/x",
                "antiderivative": "log(x)"
            },
            "square_root": {
                "function": "√x",
                "integral": "(2/3)x^(3/2) + C",
                "example": "sqrt(x)",
                "antiderivative": "2*x**(3/2)/3"
            },
            "inverse_square_root": {
                "function": "1/√x",
                "integral": "2√x + C",
                "example": "1/sqrt(x)",
                "antiderivative": "2*sqrt(x)"
            },

            # Trigonometric functions
            "sin": {
                "function": "sin(x)",
                "integral": "-cos(x) + C",
                "example": "sin(x)",
                "antiderivative": "-cos(x)"
            },
            "cos": {
                "function": "cos(x)",
                "integral": "sin(x) + C",
                "example": "cos(x)",
                "antiderivative": "sin(x)"
            },
            "tan": {
                "function": "tan(x)",
                "integral": "-ln|cos(x)| + C",
                "example": "tan(x)",
                "antiderivative": "-log(cos(x))"
            },
            "sec_squared": {
                "function": "sec²(x)",
                "integral": "tan(x) + C",
                "example": "sec(x)**2",
                "antiderivative": "tan(x)"
            },
            "csc_squared": {
                "function": "csc²(x)",
                "integral": "-cot(x) + C",
                "example": "csc(x)**2",
                "antiderivative": "-cot(x)"
            },

            # Exponential and logarithmic functions
            "exponential_e": {
                "function": "e^x",
                "integral": "e^x + C",
                "example": "exp(x)",
                "antiderivative": "exp(x)"
            },
            "exponential_a": {
                "function": "a^x",
                "integral": "a^x/ln(a) + C",
                "example": "2**x",
                "antiderivative": "2**x/log(2)"
            },
            "logarithm_natural": {
                "function": "ln(x)",
                "integral": "x*ln(x) - x + C",
                "example": "log(x)",
                "antiderivative": "x*log(x) - x"
            },

            # Inverse trigonometric functions
            "arcsin": {
                "function": "arcsin(x)",
                "integral": "x*arcsin(x) + √(1-x²) + C",
                "example": "asin(x)",
                "antiderivative": "x*asin(x) + sqrt(1-x**2)"
            },
            "arctan": {
                "function": "arctan(x)",
                "integral": "x*arctan(x) - (1/2)*ln(1+x²) + C",
                "example": "atan(x)",
                "antiderivative": "x*atan(x) - log(1+x**2)/2"
            }
        }

    def get_integral_table_data(self) -> Dict:
        '''Get integral formulas data without displaying.'''
        return self.integral_formulas

    def calculate_integral_area(self, func_str: str, interval: Tuple[float, float] = (0, 2),
                               num_points: int = 1000) -> Dict:
        '''Calculate integral as area between function and x-axis.'''
        try:
            # Parse the function
            x_sym = sp.Symbol('x')
            func = sp.sympify(func_str)
            func_lambda = sp.lambdify(x_sym, func, 'numpy')

            # Create points for area calculation
            a, b = interval
            x_fill = np.linspace(a, b, num_points)
            y_fill = func_lambda(x_fill)

            # Calculate symbolic integral
            try:
                symbolic_integral = sp.integrate(func, (x_sym, a, b))
                exact_area = float(symbolic_integral)
            except:
                exact_area = None

            # Calculate numerical integral
            try:
                numerical_area, error = integrate.quad(func_lambda, a, b)
            except:
                numerical_area, error = None, None

            # Create plotting data
            x_plot = np.linspace(a - 0.5, b + 0.5, 1000)
            y_plot = func_lambda(x_plot)

            return {
                'func_expr': func,
                'func_str': func_str,
                'interval': interval,
                'x_plot': x_plot,
                'y_plot': y_plot,
                'x_fill': x_fill,
                'y_fill': y_fill,
                'exact_area': exact_area,
                'numerical_area': numerical_area,
                'error': error
            }

        except Exception as e:
            print(f"Error in integral area calculation: {e}")
            return None

    def compare_integration_methods_calc(self, func_str: str, interval: Tuple[float, float] = (0, 2)) -> Dict:
        '''Calculate integrals using different methods for comparison.'''
        try:
            x_sym = sp.Symbol('x')
            func = sp.sympify(func_str)
            func_lambda = sp.lambdify(x_sym, func, 'numpy')

            a, b = interval
            x_vals = np.linspace(a, b, 1000)

            # Exact (symbolic) integration
            try:
                exact_integral = sp.integrate(func, (x_sym, a, b))
                exact_value = float(exact_integral)
            except:
                exact_value = None

            # Numerical integration methods
            methods_results = {}

            # Trapezoidal rule with different subdivisions
            for n in [10, 50, 100, 500]:
                x_trap = np.linspace(a, b, n + 1)
                y_trap = func_lambda(x_trap)
                trap_result = np.trapz(y_trap, x_trap)
                methods_results[f'Trapezoidal (n={n})'] = trap_result

            # Simpson's rule
            try:
                simpson_result = integrate.simpson(func_lambda(x_vals), x_vals)
                methods_results['Simpson'] = simpson_result
            except:
                methods_results['Simpson'] = None

            # Quad (adaptive quadrature)
            try:
                quad_result, quad_error = integrate.quad(func_lambda, a, b)
                methods_results['Adaptive Quad'] = quad_result
            except:
                methods_results['Adaptive Quad'] = None

            return {
                'func_expr': func,
                'func_str': func_str,
                'interval': interval,
                'exact_value': exact_value,
                'methods_results': methods_results,
                'x_vals': x_vals,
                'y_vals': func_lambda(x_vals)
            }

        except Exception as e:
            print(f"Error in integration methods comparison: {e}")
            return None

    def integration_by_parts_calc(self, u_str: str = "x", dv_str: str = "exp(x)") -> Dict:
        '''Calculate integration by parts: ∫u dv = uv - ∫v du.'''
        try:
            x_sym = sp.Symbol('x')
            u = sp.sympify(u_str)
            dv = sp.sympify(dv_str)

            # Calculate du and v
            du = sp.diff(u, x_sym)
            v = sp.integrate(dv, x_sym)

            # Integration by parts formula: ∫u dv = uv - ∫v du
            uv = u * v
            v_du = v * du

            # The remaining integral ∫v du
            remaining_integral = sp.integrate(v_du, x_sym)

            # Final result
            result = uv - remaining_integral

            # Original integrand
            original = u * dv

            return {
                'u': u,
                'dv': dv,
                'du': du,
                'v': v,
                'uv': uv,
                'v_du': v_du,
                'remaining_integral': remaining_integral,
                'result': result,
                'original': original,
                'u_str': u_str,
                'dv_str': dv_str
            }

        except Exception as e:
            print(f"Error in integration by parts calculation: {e}")
            return None

    def substitution_method_calc(self, func_str: str = "2*x*exp(x**2)",
                                substitution: str = "u = x**2") -> Dict:
        '''Calculate integral using substitution method.'''
        try:
            x_sym = sp.Symbol('x')
            u_sym = sp.Symbol('u')

            # Parse function and substitution
            func = sp.sympify(func_str)

            # Extract substitution
            if '=' in substitution:
                u_expr = sp.sympify(substitution.split('=')[1].strip())
            else:
                u_expr = sp.sympify(substitution)

            # Calculate du/dx
            du_dx = sp.diff(u_expr, x_sym)

            # Try to solve for dx in terms of du
            dx_in_du = 1 / du_dx

            # Substitute u into the function
            func_in_u = func.subs(x_sym, sp.solve(sp.Eq(u_sym, u_expr), x_sym)[0])
            func_in_u = func_in_u * dx_in_du
            func_in_u = func_in_u.subs(u_expr, u_sym)

            # Integrate in terms of u
            integral_u = sp.integrate(func_in_u, u_sym)

            # Substitute back to x
            final_result = integral_u.subs(u_sym, u_expr)

            return {
                'original_func': func,
                'u_substitution': u_expr,
                'du_dx': du_dx,
                'dx_in_du': dx_in_du,
                'func_in_u': func_in_u,
                'integral_u': integral_u,
                'final_result': final_result,
                'func_str': func_str,
                'substitution': substitution
            }

        except Exception as e:
            print(f"Error in substitution method calculation: {e}")
            return None

    def calculate_area_between_curves(self, func1_str: str = "x**2", func2_str: str = "x + 2",
                                     interval: Optional[Tuple[float, float]] = None) -> Dict:
        '''Calculate area between two curves.'''
        try:
            x_sym = sp.Symbol('x')
            func1 = sp.sympify(func1_str)
            func2 = sp.sympify(func2_str)

            # Find intersection points if interval not provided
            if interval is None:
                intersections = sp.solve(func1 - func2, x_sym)
                real_intersections = [float(sol) for sol in intersections if sol.is_real]
                real_intersections.sort()

                if len(real_intersections) >= 2:
                    a, b = real_intersections[0], real_intersections[1]
                else:
                    a, b = -2, 2  # Default interval
            else:
                a, b = interval

            # Create lambda functions
            func1_lambda = sp.lambdify(x_sym, func1, 'numpy')
            func2_lambda = sp.lambdify(x_sym, func2, 'numpy')

            # Calculate which function is on top
            mid_point = (a + b) / 2
            if func1_lambda(mid_point) > func2_lambda(mid_point):
                upper_func, lower_func = func1, func2
                upper_lambda, lower_lambda = func1_lambda, func2_lambda
            else:
                upper_func, lower_func = func2, func1
                upper_lambda, lower_lambda = func2_lambda, func1_lambda

            # Calculate area
            difference = upper_func - lower_func
            try:
                symbolic_area = sp.integrate(difference, (x_sym, a, b))
                exact_area = float(symbolic_area)
            except:
                exact_area = None

            # Numerical integration
            try:
                numerical_area, error = integrate.quad(lambda x: upper_lambda(x) - lower_lambda(x), a, b)
            except:
                numerical_area, error = None, None

            # Generate plotting data
            x_plot = np.linspace(a - 1, b + 1, 1000)
            y1_plot = func1_lambda(x_plot)
            y2_plot = func2_lambda(x_plot)

            # Fill data
            x_fill = np.linspace(a, b, 1000)
            y1_fill = func1_lambda(x_fill)
            y2_fill = func2_lambda(x_fill)

            return {
                'func1': func1,
                'func2': func2,
                'func1_str': func1_str,
                'func2_str': func2_str,
                'interval': (a, b),
                'upper_func': upper_func,
                'lower_func': lower_func,
                'exact_area': exact_area,
                'numerical_area': numerical_area,
                'error': error,
                'x_plot': x_plot,
                'y1_plot': y1_plot,
                'y2_plot': y2_plot,
                'x_fill': x_fill,
                'y1_fill': y1_fill,
                'y2_fill': y2_fill
            }

        except Exception as e:
            print(f"Error in area between curves calculation: {e}")
            return None

    def calculate_volume_of_revolution(self, func_str: str = "sqrt(x)",
                                      interval: Tuple[float, float] = (0, 4),
                                      method: str = "disk", axis: str = "x") -> Dict:
        '''Calculate volume of revolution using disk/washer method.'''
        try:
            x_sym = sp.Symbol('x')
            func = sp.sympify(func_str)
            func_lambda = sp.lambdify(x_sym, func, 'numpy')

            a, b = interval

            if method == "disk" and axis == "x":
                # Disk method: V = π ∫[a,b] [f(x)]² dx
                integrand = sp.pi * func**2

                try:
                    symbolic_volume = sp.integrate(integrand, (x_sym, a, b))
                    exact_volume = float(symbolic_volume)
                except:
                    exact_volume = None

                # Numerical integration
                try:
                    numerical_volume, error = integrate.quad(lambda x: np.pi * func_lambda(x)**2, a, b)
                except:
                    numerical_volume, error = None, None

                # Generate data for 3D visualization
                x_vals = np.linspace(a, b, 100)
                y_vals = func_lambda(x_vals)

                # Create revolution surface data
                theta = np.linspace(0, 2*np.pi, 50)
                X, Theta = np.meshgrid(x_vals, theta)
                Y = np.outer(np.cos(theta), y_vals)
                Z = np.outer(np.sin(theta), y_vals)

                return {
                    'func': func,
                    'func_str': func_str,
                    'interval': interval,
                    'method': method,
                    'axis': axis,
                    'integrand': integrand,
                    'exact_volume': exact_volume,
                    'numerical_volume': numerical_volume,
                    'error': error,
                    'x_vals': x_vals,
                    'y_vals': y_vals,
                    'X_surf': X,
                    'Y_surf': Y,
                    'Z_surf': Z
                }

        except Exception as e:
            print(f"Error in volume of revolution calculation: {e}")
            return None

    def generate_practice_problem(self) -> Dict:
        '''Generate a random integration practice problem.'''
        import random

        # Select a random integral type
        integral_types = [
            ("Power rule", "x**{}", lambda n: f"x**{n+1}/{n+1}"),
            ("Exponential", "exp({}*x)", lambda a: f"exp({a}*x)/{a}"),
            ("Trigonometric", "sin({}*x)", lambda a: f"-cos({a}*x)/{a}"),
            ("Trigonometric", "cos({}*x)", lambda a: f"sin({a}*x)/{a}"),
            ("Polynomial", "{}*x**2 + {}*x + {}", lambda a, b, c: f"{a}*x**3/3 + {b}*x**2/2 + {c}*x")
        ]

        problem_type, template, solution_func = random.choice(integral_types)

        if problem_type == "Power rule":
            n = random.randint(2, 5)
            function = template.format(n)
            solution = solution_func(n)
        elif problem_type == "Exponential":
            a = random.choice([1, 2, -1, 0.5])
            function = template.format(a)
            solution = solution_func(a)
        elif problem_type == "Trigonometric":
            a = random.choice([1, 2, 3, 0.5])
            function = template.format(a)
            solution = solution_func(a)
        elif problem_type == "Polynomial":
            a, b, c = random.randint(1, 5), random.randint(-5, 5), random.randint(-10, 10)
            function = template.format(a, b, c)
            solution = solution_func(a, b, c)

        return {
            'type': problem_type,
            'function': function,
            'solution': solution,
            'problem_text': f"Find ∫({function}) dx"
        }

    def calculate_improper_integral(self, func_str: str, interval: Tuple[Optional[float], Optional[float]]) -> Dict:
        '''Calculate improper integrals.'''
        try:
            func_expr = sp.sympify(func_str)
            x = sp.Symbol('x')
            a, b = interval

            # Type 1 improper integrals - infinite limits
            if a is None:  # (-∞, b]
                limit_result = sp.integrate(func_expr, (x, -sp.oo, b))
            elif b is None:  # [a, ∞)
                limit_result = sp.integrate(func_expr, (x, a, sp.oo))
            elif a is None and b is None:  # (-∞, ∞)
                limit_result = sp.integrate(func_expr, (x, -sp.oo, sp.oo))
            else:  # Regular definite integral
                limit_result = sp.integrate(func_expr, (x, a, b))

            # Check if the integral converges
            converges = limit_result.is_finite if limit_result is not None else False

            # Numerical approximation for finite bounds
            numerical_result = None
            if converges and a is not None and b is not None:
                try:
                    func_lambda = sp.lambdify(x, func_expr, 'numpy')
                    numerical_result, _ = integrate.quad(func_lambda, a, b)
                except:
                    numerical_result = None

            return {
                'function': func_str,
                'interval': interval,
                'symbolic_result': limit_result,
                'numerical_result': numerical_result,
                'converges': converges,
                'convergence_value': float(limit_result) if limit_result.is_real and limit_result.is_finite else None
            }

        except Exception as e:
            print(f"Error calculating improper integral: {e}")
            return None

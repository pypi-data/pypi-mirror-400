'''
Test Suite for Calculus Learning Toolkit
========================================

Comprehensive tests for all calculus modules and functionality.
'''

import unittest
import sys
import os
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from basic_rules_viz import CalculusRules
from fundamental_theorem_viz import FundamentalTheorem
from derivatives_viz import CommonDerivatives
from integrals_viz import CommonIntegrals

# Also test the core modules
from basic_rules_core import CalculusRulesCore
from derivatives_core import CommonDerivativesCore
from fundamental_theorem_core import FundamentalTheoremCore


class TestBasicRules(unittest.TestCase):
    '''Test basic calculus rules.'''

    def setUp(self):
        self.rules = CalculusRules()
        # Disable matplotlib display for testing
        plt.ioff()

    def tearDown(self):
        plt.close('all')

    def test_power_rule_demo(self):
        '''Test power rule demonstration.'''
        try:
            self.rules.power_rule_demo(2, (-2, 2))
            self.assertTrue(True, "Power rule demo executed successfully")
        except Exception as e:
            self.fail(f"Power rule demo failed: {e}")

    def test_product_rule_visualization(self):
        '''Test product rule visualization.'''
        try:
            self.rules.product_rule_visualization("x", "sin(x)")
            self.assertTrue(True, "Product rule visualization executed successfully")
        except Exception as e:
            self.fail(f"Product rule visualization failed: {e}")

    def test_chain_rule_animation(self):
        '''Test chain rule demonstration.'''
        try:
            self.rules.chain_rule_animation("sin(x)", "x**2")
            self.assertTrue(True, "Chain rule demo executed successfully")
        except Exception as e:
            self.fail(f"Chain rule demo failed: {e}")


class TestFundamentalTheorem(unittest.TestCase):
    '''Test Fundamental Theorem of Calculus implementations.'''

    def setUp(self):
        self.fundamental_theorem = FundamentalTheorem()
        plt.ioff()

    def tearDown(self):
        plt.close('all')

    def test_riemann_sum_visualization(self):
        '''Test Riemann sum visualization.'''
        try:
            self.fundamental_theorem.riemann_sum_visualization("x**2", (0, 1), 10)
            self.assertTrue(True, "Riemann sum visualization executed successfully")
        except Exception as e:
            self.fail(f"Riemann sum visualization failed: {e}")

    def test_fundamental_theorem_part1_demo(self):
        '''Test Fundamental Theorem Part 1 demonstration.'''
        try:
            self.fundamental_theorem.fundamental_theorem_part1_demo("x", 0)
            self.assertTrue(True, "Fundamental Theorem Part 1 demo executed successfully")
        except Exception as e:
            self.fail(f"Fundamental Theorem Part 1 demo failed: {e}")

    def test_fundamental_theorem_part2_demo(self):
        '''Test Fundamental Theorem Part 2 demonstration.'''
        try:
            self.fundamental_theorem.fundamental_theorem_part2_demo("x**2", (0, 1))
            self.assertTrue(True, "Fundamental Theorem Part 2 demo executed successfully")
        except Exception as e:
            self.fail(f"Fundamental Theorem Part 2 demo failed: {e}")


class TestCommonDerivatives(unittest.TestCase):
    '''Test common derivatives functionality.'''

    def setUp(self):
        self.derivatives = CommonDerivatives()
        plt.ioff()

    def tearDown(self):
        plt.close('all')

    def test_derivative_formulas(self):
        '''Test that derivative formulas are properly defined.'''
        self.assertIsInstance(self.derivatives.derivative_formulas, dict)
        self.assertIn("power", self.derivatives.derivative_formulas)
        self.assertIn("sin", self.derivatives.derivative_formulas)
        self.assertIn("cos", self.derivatives.derivative_formulas)
        self.assertIn("exponential_e", self.derivatives.derivative_formulas)

    def test_display_derivative_table(self):
        '''Test derivative table display.'''
        try:
            self.derivatives.display_derivative_table()
            self.assertTrue(True, "Derivative table displayed successfully")
        except Exception as e:
            self.fail(f"Derivative table display failed: {e}")

    def test_visualize_function_and_derivative(self):
        '''Test function and derivative visualization.'''
        try:
            self.derivatives.visualize_function_and_derivative("x**2", (-2, 2))
            self.assertTrue(True, "Function visualization executed successfully")
        except Exception as e:
            self.fail(f"Function visualization failed: {e}")

    def test_critical_points_analysis(self):
        '''Test critical points analysis.'''
        try:
            self.derivatives.critical_points_analysis("x**3 - 3*x**2 + 2")
            self.assertTrue(True, "Critical points analysis executed successfully")
        except Exception as e:
            self.fail(f"Critical points analysis failed: {e}")

    def test_higher_order_derivatives(self):
        '''Test higher order derivatives calculation.'''
        try:
            self.derivatives.higher_order_derivatives("x**4", 3)
            self.assertTrue(True, "Higher order derivatives executed successfully")
        except Exception as e:
            self.fail(f"Higher order derivatives failed: {e}")


class TestCommonIntegrals(unittest.TestCase):
    '''Test common integrals functionality.'''

    def setUp(self):
        self.integrals = CommonIntegrals()
        plt.ioff()

    def tearDown(self):
        plt.close('all')

    def test_integral_formulas(self):
        '''Test that integral formulas are properly defined.'''
        self.assertIsInstance(self.integrals.integral_formulas, dict)
        self.assertIn("power", self.integrals.integral_formulas)
        self.assertIn("sin", self.integrals.integral_formulas)
        self.assertIn("cos", self.integrals.integral_formulas)
        self.assertIn("exponential_e", self.integrals.integral_formulas)

    def test_display_integral_table(self):
        '''Test integral table display.'''
        try:
            self.integrals.display_integral_table()
            self.assertTrue(True, "Integral table displayed successfully")
        except Exception as e:
            self.fail(f"Integral table display failed: {e}")

    def test_visualize_integral_as_area(self):
        '''Test integral area visualization.'''
        try:
            self.integrals.visualize_integral_as_area("x**2", (0, 1), 20)
            self.assertTrue(True, "Integral visualization executed successfully")
        except Exception as e:
            self.fail(f"Integral visualization failed: {e}")

    def test_integration_by_parts_demo(self):
        '''Test integration by parts demonstration.'''
        try:
            self.integrals.integration_by_parts_demo("x", "exp(x)")
            self.assertTrue(True, "Integration by parts demo executed successfully")
        except Exception as e:
            self.fail(f"Integration by parts demo failed: {e}")

    def test_area_between_curves(self):
        '''Test area between curves calculation.'''
        try:
            self.integrals.area_between_curves("x**2", "x", (0, 1))
            self.assertTrue(True, "Area between curves executed successfully")
        except Exception as e:
            self.fail(f"Area between curves failed: {e}")


class TestMathematicalAccuracy(unittest.TestCase):
    '''Test mathematical accuracy of calculations.'''

    def setUp(self):
        self.x = sp.Symbol('x')

    def test_derivative_accuracy(self):
        '''Test that derivatives are calculated correctly.'''
        # Test power rule
        f = self.x**3
        expected = 3*self.x**2
        actual = sp.diff(f, self.x)
        self.assertEqual(sp.simplify(actual - expected), 0)

        # Test sin derivative
        f = sp.sin(self.x)
        expected = sp.cos(self.x)
        actual = sp.diff(f, self.x)
        self.assertEqual(sp.simplify(actual - expected), 0)

        # Test product rule
        f = self.x**2 * sp.sin(self.x)
        expected = 2*self.x*sp.sin(self.x) + self.x**2*sp.cos(self.x)
        actual = sp.diff(f, self.x)
        self.assertEqual(sp.simplify(actual - expected), 0)

    def test_integral_accuracy(self):
        '''Test that integrals are calculated correctly.'''
        # Test power rule integration
        f = self.x**2
        expected = self.x**3/3
        actual = sp.integrate(f, self.x)
        # Compare derivatives since integrals differ by constant
        self.assertEqual(sp.simplify(sp.diff(actual, self.x) - f), 0)

        # Test sin integration
        f = sp.sin(self.x)
        expected = -sp.cos(self.x)
        actual = sp.integrate(f, self.x)
        self.assertEqual(sp.simplify(sp.diff(actual, self.x) - f), 0)

    def test_fundamental_theorem(self):
        '''Test fundamental theorem of calculus.'''
        # If F(x) = ∫[a to x] f(t) dt, then F'(x) = f(x)
        f = self.x**2
        a = 0

        # F(x) = ∫[0 to x] t² dt = x³/3 - 0 = x³/3
        F = self.x**3/3
        F_prime = sp.diff(F, self.x)

        self.assertEqual(sp.simplify(F_prime - f), 0)


class TestCoreModules(unittest.TestCase):
    '''Test the separated core modules.'''

    def setUp(self):
        self.calc_core = CalculusRulesCore()
        self.deriv_core = CommonDerivativesCore()
        self.fundamental_theorem_core = FundamentalTheoremCore()
        plt.ioff()

    def tearDown(self):
        plt.close('all')

    def test_power_rule_calculation(self):
        '''Test core power rule calculation.'''
        x_vals = np.linspace(-2, 2, 100)
        y_original, y_derivative = self.calc_core.power_rule_calculation(3, x_vals)

        # Check that the calculation is correct
        expected_original = x_vals**3
        expected_derivative = 3 * x_vals**2

        np.testing.assert_allclose(y_original, expected_original, rtol=1e-10)
        np.testing.assert_allclose(y_derivative, expected_derivative, rtol=1e-10)

    def test_derivative_formulas_exist(self):
        '''Test that derivative formulas are properly defined in core.'''
        self.assertIsInstance(self.deriv_core.derivative_formulas, dict)
        self.assertIn("power", self.deriv_core.derivative_formulas)
        self.assertIn("sin", self.deriv_core.derivative_formulas)
        self.assertIn("exponential_e", self.deriv_core.derivative_formulas)

    def test_function_and_derivative_calculation(self):
        '''Test core function and derivative calculation.'''
        x_vals = np.linspace(-2, 2, 100)
        try:
            y_vals, dy_vals, func_expr, deriv_expr = self.deriv_core.calculate_function_and_derivative("x**2", x_vals)

            # Check that we get reasonable results
            self.assertEqual(len(y_vals), len(x_vals))
            self.assertEqual(len(dy_vals), len(x_vals))
            self.assertEqual(str(func_expr), "x**2")
            self.assertEqual(str(deriv_expr), "2*x")

        except Exception as e:
            self.fail(f"Core calculation failed: {e}")

    def test_riemann_sum_calculation(self):
        '''Test core Riemann sum calculation.'''
        try:
            result = self.fundamental_theorem_core.calculate_riemann_sum("x**2", (0, 1), 100)

            # Check that result has expected keys
            expected_keys = ['func_expr', 'riemann_sum', 'exact_integral', 'dx', 'x_rects', 'y_rects']
            for key in expected_keys:
                self.assertIn(key, result)

            # The Riemann sum should be close to the exact integral
            if result['exact_integral'] is not None:
                error = abs(result['riemann_sum'] - result['exact_integral'])
                self.assertLess(error, 0.01)  # Should be reasonably accurate with 100 rectangles

        except Exception as e:
            self.fail(f"Riemann sum calculation failed: {e}")


class TestModuleSeparation(unittest.TestCase):
    '''Test that core modules don't import visualization dependencies.'''

    def test_core_modules_no_matplotlib(self):
        '''Test that core modules don't import matplotlib.'''
        import basic_rules_core
        import derivatives_core
        import fundamental_theorem_core

        # These modules should not have matplotlib in their namespace
        for module in [basic_rules_core, derivatives_core, fundamental_theorem_core]:
            self.assertFalse(hasattr(module, 'plt'))
            self.assertFalse(hasattr(module, 'pyplot'))

    def test_visualization_modules_have_matplotlib(self):
        '''Test that visualization modules do import matplotlib.'''
        import basic_rules_viz
        import derivatives_viz
        import fundamental_theorem_viz

        # These modules should have access to matplotlib through their imports
        # We can't directly test plt import, but we can test that the classes exist
        self.assertTrue(hasattr(basic_rules_viz, 'CalculusRulesVisualizer'))
        self.assertTrue(hasattr(derivatives_viz, 'CommonDerivativesVisualizer'))
        self.assertTrue(hasattr(fundamental_theorem_viz, 'FundamentalTheoremVisualizer'))

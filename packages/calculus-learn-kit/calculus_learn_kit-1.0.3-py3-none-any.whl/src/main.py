"""
' Calculus Learning and Visualization Toolkit
' -------------------------------------------
'
' A comprehensive toolkit for learning and visualizing calculus concepts including
' derivatives, integrals, limits, and the Fundamental Theorem of Calculus.
'
' @file: main.py
' @authors: Claude Sonnet 4, Abdullah Barrak.
' @date: 1/1/2026
"""

import matplotlib.pyplot as plt

# Import the refactored modules with separated visualization
try:
  # Try relative imports first (when used as package)
  from .basic_rules_viz import CalculusRules
  from .fundamental_theorem_viz import (
      FundamentalTheorem,
      interactive_fundamental_theorem_explorer,
  )
  from .derivatives_viz import CommonDerivatives, derivative_game
  from .integrals_viz import CommonIntegralsVisualizer, integral_practice_game
except ImportError:
  # Fall back to direct imports (when run as script)
  from basic_rules_viz import CalculusRules
  from fundamental_theorem_viz import (
      FundamentalTheorem,
      interactive_fundamental_theorem_explorer,
  )
  from derivatives_viz import CommonDerivatives, derivative_game
  from integrals_viz import CommonIntegralsVisualizer, integral_practice_game


class CalculusToolkit:
  """Main class for the Calculus Learning Toolkit."""

  def __init__(self):
    self.rules = CalculusRules()
    self.fundamental_theorem = FundamentalTheorem()
    self.derivatives = CommonDerivatives()
    self.integrals = CommonIntegralsVisualizer()

    # Configure matplotlib for better display
    plt.rcParams["figure.figsize"] = (12, 8)
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.3

  def display_main_menu(self):
    """Display the main menu for the toolkit."""
    print("\n" + "=" * 60)
    print("🧮 CALCULUS LEARNING & VISUALIZATION TOOLKIT 🧮")
    print("=" * 60)
    print("Select a topic to explore:")
    print()
    print("📏 BASIC RULES & CONCEPTS")
    print("  1. Power Rule Demonstration")
    print("  2. Product Rule Visualization")
    print("  3. Chain Rule Examples")
    print("  4. Quotient Rule Demo")
    print("  5. Limits and Continuity")
    print()
    print("🔄 FUNDAMENTAL THEOREM OF CALCULUS")
    print("  6. Riemann Sums & Area Approximation")
    print("  7. Fundamental Theorem Part 1: Derivative of Integral")
    print("  8. Fundamental Theorem Part 2: Evaluating Definite Integrals")
    print("  9. Mean Value Theorem")
    print("  10. Net Change Theorem")
    print()
    print("📊 DERIVATIVES LIBRARY")
    print("  11. Common Derivatives Table")
    print("  12. Derivative Patterns & Examples")
    print("  13. Critical Points Analysis")
    print("  14. Higher Order Derivatives")
    print("  15. Slope Fields Visualization")
    print()
    print("∫ INTEGRALS LIBRARY")
    print("  16. Common Integrals Table")
    print("  17. Area Under Curves")
    print("  18. Integration by Parts")
    print("  19. U-Substitution Method")
    print("  20. Improper Integrals")
    print("  21. Area Between Curves")
    print("  22. Volumes of Revolution")
    print()
    print("🎮 INTERACTIVE LEARNING")
    print("  23. Derivative Practice Game")
    print("  24. Integral Practice Game")
    print("  25. Complete Fundamental Theorem Explorer")
    print("  26. Custom Function Explorer")
    print()
    print("  0. Exit")
    print("=" * 60)

  def run_demo(self, choice: int):
    """Run the selected demonstration."""

    try:
      if choice == 1:
        print("\n📏 Power Rule Demonstration")
        self.rules.power_rule_demo(3)

      elif choice == 2:
        print("\n📏 Product Rule Visualization")
        self.rules.product_rule_visualization("x**2", "sin(x)")

      elif choice == 3:
        print("\n📏 Chain Rule Examples")
        self.rules.chain_rule_animation("sin(x)", "x**2")

      elif choice == 4:
        print("\n📏 Quotient Rule Demo")
        self.rules.quotient_rule_demo("x**2", "x+1")

      elif choice == 5:
        print("\n📏 Limits and Continuity")
        self.rules.interactive_limit_demo()

      elif choice == 6:
        print("\n🔄 Riemann Sums & Area Approximation")
        self.fundamental_theorem.riemann_sum_visualization("x**2", (0, 2), 20)

      elif choice == 7:
        print("\n🔄 Fundamental Theorem Part 1: Derivative of Integral")
        self.fundamental_theorem.fundamental_theorem_part1_demo("2*x", 0)

      elif choice == 8:
        print("\n🔄 Fundamental Theorem Part 2: Evaluating Definite Integrals")
        self.fundamental_theorem.fundamental_theorem_part2_demo("x**2", (0, 2))

      elif choice == 9:
        print("\n🔄 Mean Value Theorem")
        self.fundamental_theorem.mean_value_theorem_demo(
            "x**3 - 3*x**2 + 2*x", (0, 3)
        )

      elif choice == 10:
        print("\n🔄 Net Change Theorem")
        self.fundamental_theorem.net_change_theorem_demo("2*x + 1", (0, 3))

      elif choice == 11:
        print("\n📊 Common Derivatives Table")
        self.derivatives.display_derivative_table()

      elif choice == 12:
        print("\n📊 Derivative Patterns & Examples")
        self.derivatives.demonstrate_derivative_patterns()

      elif choice == 13:
        print("\n📊 Critical Points Analysis")
        self.derivatives.critical_points_analysis("x**3 - 3*x**2 + 2")

      elif choice == 14:
        print("\n📊 Higher Order Derivatives")
        self.derivatives.higher_order_derivatives("x**4 - 4*x**3 + 6*x**2", 3)

      elif choice == 15:
        print("\n📊 Slope Fields Visualization")
        self.derivatives.slope_field_visualization("x**2", (-2, 2), (-1, 4))

      elif choice == 16:
        print("\n∫ Common Integrals Table")
        self.integrals.display_integral_table()

      elif choice == 17:
        print("\n∫ Area Under Curves")
        self.integrals.visualize_integral_as_area("x**2", (0, 2))

      elif choice == 18:
        print("\n∫ Integration by Parts")
        self.integrals.integration_by_parts_demo("x", "exp(x)")

      elif choice == 19:
        print("\n∫ U-Substitution Method")
        self.integrals.substitution_method_demo("2*x*exp(x**2)", "x**2")

      elif choice == 20:
        print("\n∫ Improper Integrals")
        self.integrals.improper_integrals_demo()

      elif choice == 21:
        print("\n∫ Area Between Curves")
        self.integrals.area_between_curves("x**2", "x + 2")

      elif choice == 22:
        print("\n∫ Volumes of Revolution")
        self.integrals.volume_of_revolution("sqrt(x)", (0, 4))

      elif choice == 23:
        print("\n🎮 Derivative Practice Game")
        derivative_game()

      elif choice == 24:
        print("\n🎮 Integral Practice Game")
        integral_practice_game()

      elif choice == 25:
        print("\n🎮 Complete Fundamental Theorem Explorer")
        interactive_fundamental_theorem_explorer()

      elif choice == 26:
        print("\n🎮 Custom Function Explorer")
        self.custom_function_explorer()

      else:
        print("Invalid choice. Please try again.")

    except Exception as e:
      print(f"❌ Error running demo: {e}")
      print("Please try again or choose a different option.")

  def custom_function_explorer(self):
    """Allow users to explore custom functions."""
    print("\n🎮 Custom Function Explorer")
    print("Explore derivatives and integrals of your own functions!")
    print("Enter functions using Python/SymPy syntax:")
    print("Examples: x**2, sin(x), exp(x), log(x), sqrt(x), etc.")
    print()

    while True:
      try:
        func_input = input("\nEnter a function f(x) = ").strip()
        if not func_input or func_input.lower() in ["quit", "exit", "q"]:
          break
        print(f"\n🔍 Analyzing function: f(x) = {func_input}")

        # Show derivative
        print("\n📊 Derivative Analysis:")
        self.derivatives.visualize_function_and_derivative(func_input, (-3, 3))

        # Show integral
        print("\n∫ Integral Analysis:")
        self.integrals.visualize_integral_as_area(func_input, (0, 2))

        # Critical points if applicable
        try:
          print("\n📈 Critical Points Analysis:")
          self.derivatives.critical_points_analysis(func_input)
        except:
          print("Could not perform critical points analysis for this function.")

        continue_choice = input("\nAnalyze another function? (y/n): ").lower()
        if continue_choice != "y":
          break

      except KeyboardInterrupt:
        print("\nReturning to main menu...")
        break

      except Exception as e:
        print(f"❌ Error analyzing function: {e}")
        print("Please check your function syntax and try again.")

  def run(self):
    """Main application loop."""
    print("\n🎓 Welcome to the Calculus Learning Toolkit!")
    print("This toolkit provides interactive visualizations and")
    print("demonstrations of key calculus concepts.")

    while True:
      try:
        self.display_main_menu()
        choice = input("\nEnter your choice (0-26): ").strip()

        if not choice.isdigit():
          print("❌ Please enter a valid number.")
          continue

        choice = int(choice)

        if choice == 0:
          print("\n👋 Thank you for using the Calculus Learning Toolkit!")
          print("Keep exploring and learning calculus! 📚")
          break

        if 1 <= choice <= 26:
          self.run_demo(choice)
          input("\n⏸️  Press Enter to continue...")
        else:
          print("❌ Please enter a number between 0 and 26.")

      except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for learning calculus with us!")
        break
      except ValueError:
        print("❌ Please enter a valid number.")
      except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please try again.")

def main():
  """Main entry point for the application."""
  try:
    toolkit = CalculusToolkit()
    toolkit.run()
  except Exception as e:
    print(f"❌ Error starting toolkit: {e}")
    print("Please check your installation and try again.")

if __name__ == "__main__":
  main()

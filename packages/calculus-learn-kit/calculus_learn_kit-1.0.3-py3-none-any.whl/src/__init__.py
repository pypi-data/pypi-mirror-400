'''
Calculus.py - A comprehensive toolkit for learning and visualizing calculus concepts

This package provides interactive demonstrations and visualizations for:
  * Basic calculus rules (power, product, chain, quotient)
  * Derivatives and their applications
  * Integrals and integration techniques
  * Fundamental Theorem of Calculus
  * Interactive learning games and exercises

@author: Abdullah Barrak, Claude Sonnet 4
@license: MIT
'''

__version__ = "1.0.3"
__author__ = "Abdullah Barrak, Claude Sonnet 4"
__license__ = "MIT"

# Import main classes for easier access
from .basic_rules_viz import CalculusRules
from .derivatives_viz import CommonDerivatives, derivative_game
from .integrals_viz import CommonIntegralsVisualizer, integral_practice_game
from .fundamental_theorem_viz import FundamentalTheorem, interactive_fundamental_theorem_explorer
from .main import CalculusToolkit

# Define what gets imported with "from src import *"
__all__ = [
  'CalculusToolkit',
  'CalculusRules',
  'CommonDerivatives',
  'CommonIntegralsVisualizer',
  'FundamentalTheorem',
  'derivative_game',
  'integral_practice_game',
  'interactive_fundamental_theorem_explorer'
]

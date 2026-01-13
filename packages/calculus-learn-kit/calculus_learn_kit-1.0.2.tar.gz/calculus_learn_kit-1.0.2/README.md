# Calculus.py

![Tests](https://github.com/abarrak/calculus.py/workflows/Tests/badge.svg)
[![PyPI version](https://badge.fury.io/py/calculus-learn-kit.svg)](https://badge.fury.io/py/calculus-learn-kit)
[![Python versions](https://img.shields.io/pypi/pyversions/calculus-learn-kit.svg)](https://pypi.org/project/calculus-learn-kit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/calculus-learn-kit)](https://pepy.tech/project/calculus-learn-kit)

A comprehensive Python toolkit for learning and visualizing single-variable calculus concepts through interactive demonstrations.

## ✨ Features

- **Basic Rules**: Power, Product, Chain, and Quotient rule demonstrations
- **Fundamental Theorem**: FTC Parts 1 & 2 with Riemann sum visualizations
- **Derivatives**: Complete library with pattern recognition and critical point analysis
- **Integrals**: Advanced techniques including integration by parts and u-substitution
- **Interactive Games**: Practice exercises with instant feedback
- **Custom Explorer**: Analyze user-defined functions

<img src="https://raw.githubusercontent.com/abarrak/calculus.py/refs/heads/main/pictures/1.png" width="40%"><img src="https://raw.githubusercontent.com/abarrak/calculus.py/refs/heads/main/pictures/2.png" width="40%">

## 🚀 Quick Start

```bash
pip install calculus-learn-kit
```

Then run it.

```bash
calculus
```

Or build from the source:

```bash
# Clone and install
git clone https://github.com/aalotai1/calculus.py.git
cd calculus.py
pip install -r requirements.txt

# Run interactive toolkit
python src/main.py
```

## 📦 Dependencies

- **NumPy** - Numerical computations
- **Matplotlib** - Visualizations and plotting
- **SymPy** - Symbolic mathematics
- **SciPy** - Scientific computing

## 💻 Usage

```python
from src.basic_rules_viz import CalculusRules
from src.derivatives_viz import CommonDerivatives

# Demonstrate calculus concepts
rules = CalculusRules()
rules.power_rule_demo(3)

derivatives = CommonDerivatives()
derivatives.demonstrate_derivative_patterns()
```

## 🏗️ Architecture

```
src/
├── *_core.py     # Mathematical computation engines
├── *_viz.py      # Visualization and demonstration layers
└── main.py       # Interactive CLI interface
test/
└── main_test.py  # Comprehensive test suite
```

**Core Modules:**

- `basic_rules_*` - Fundamental calculus rules
- `fundamental_theorem_*` - FTC demonstrations and Riemann sums
- `derivatives_*` - Comprehensive derivatives library
- `integrals_*` - Advanced integration techniques

## 🧪 Testing

```bash
python -m pytest test/ -v
```

<img src="https://raw.githubusercontent.com/abarrak/calculus.py/refs/heads/main/pictures/test-suite.png" width="70%">

## 📚 Educational Use

- **Students**: Visual learning with step-by-step demonstrations
- **Educators**: Lecture support and assignment generation
- **Coverage**: Calculus I/II, AP Calculus, University-level concepts

## 📄 License

MIT License.

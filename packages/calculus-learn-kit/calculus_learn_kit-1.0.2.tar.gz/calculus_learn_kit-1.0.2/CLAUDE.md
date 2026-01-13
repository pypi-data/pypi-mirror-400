# Calculus Learning Toolkit - Agent Development Guide

## Project Overview

The Calculus Learning Toolkit is a comprehensive Python-based educational platform for learning and visualizing calculus concepts. It provides interactive demonstrations of derivatives, integrals, limits, and the Fundamental Theorem of Calculus through both computational engines and rich visualizations.

### Architecture

The project follows a modular architecture with clear separation of concerns:

```
calculus.py/
├── src/                          # Core source code
│   ├── *_core.py                # Mathematical computation engines
│   ├── *_viz.py                 # Visualization and demonstration layers
│   ├── main.py                  # Main entry point and CLI interface
│   └── __init__.py              # Package initialization
├── test/                        # Comprehensive test suite
│   └── main_test.py            # All module tests
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── AGENT_GUIDE.md              # This development guide
```

## Core Modules

### 1. Basic Rules Module (`basic_rules_core.py` + `basic_rules_viz.py`)
**Purpose**: Fundamental calculus rules and operations
- Power rule demonstrations
- Product rule calculations
- Chain rule applications
- Interactive visualizations

### 2. Derivatives Module (`derivatives_core.py` + `derivatives_viz.py`)
**Purpose**: Common derivative formulas and applications
- Extensive derivative formula library
- Real-time derivative plotting
- Comparative analysis tools
- Function family demonstrations

### 3. Integrals Module (`integrals_core.py` + `integrals_viz.py`)
**Purpose**: Integration techniques and common integrals
- Integration by parts demonstrations
- U-substitution method walkthroughs
- Area under curve calculations
- Interactive problem generators

### 4. Fundamental Theorem Module (`fundamental_theorem_core.py` + `fundamental_theorem_viz.py`)
**Purpose**: FTC Parts 1 & 2 with visual proofs
- Accumulator function demonstrations
- Numerical integration comparisons
- Riemann sum approximations
- Interactive theorem verification

## Dependencies

### Core Requirements
```python
numpy>=1.21.0          # Numerical computations
sympy>=1.9.0           # Symbolic mathematics
matplotlib>=3.5.0      # Plotting and visualization
scipy>=1.8.0           # Scientific computing
```

### Development Requirements
```python
pytest>=6.2.0         # Testing framework
```

## Installation & Setup

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv calculus_env
source calculus_env/bin/activate  # Linux/Mac
# calculus_env\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Application
```bash
# Interactive CLI interface
python src/main.py

# Run specific demonstrations
python -c "
from src.basic_rules_viz import CalculusRules
rules = CalculusRules()
rules.power_rule_demo()
"
```

### 3. Testing
```bash
# Run all tests
python -m pytest test/ -v

# Run specific test modules
python -m pytest test/main_test.py::TestBasicRules -v
```

## Development Patterns

### Core-Viz Separation Pattern
Every mathematical concept follows this pattern:
- **Core Module**: Pure computational logic, no matplotlib dependencies
- **Visualization Module**: UI/display logic, depends on core module

```python
# Example: basic_rules_core.py
class CalculusRulesCore:
    def calculate_power_rule(self, exponent, x_range):
        # Pure mathematical computation
        return {'derivative': result, 'original': func}

# Example: basic_rules_viz.py
class CalculusRules:
    def __init__(self):
        self.core = CalculusRulesCore()

    def power_rule_demo(self, exp, x_range):
        data = self.core.calculate_power_rule(exp, x_range)
        # Visualization logic using matplotlib
```

### Symbol Management
- Use consistent symbol definitions across modules
- Handle 'x'/'t' variable substitutions properly
- Ensure lambdify functions work with numpy arrays

### Error Handling
- Graceful degradation for invalid inputs
- Clear error messages for educational context
- Fallback calculations when symbolic math fails

## Key Technical Fixes

### 1. Import Dependencies
**Issue**: Missing `sympy as sp` imports in visualization modules
**Solution**: Added `import sympy as sp` to all visualization files
**Files**: `fundamental_theorem_viz.py`, `derivatives_viz.py`

### 2. Scalar Array Handling
**Issue**: `ValueError: x and y must have same first dimension` when lambdified functions return scalars
**Solution**: Check for scalar results and convert to arrays
```python
if np.isscalar(f_vals):
    f_vals = np.full_like(x_vals, f_vals)
```
**Files**: `fundamental_theorem_viz.py`, `integrals_viz.py`

### 3. Symbol Substitution
**Issue**: Function strings like "x" not properly converted to integration variable "t"
**Solution**: Explicit symbol substitution before lambdifying
```python
if 'x' in func_str:
    x_sym = sp.Symbol('x')
    func = func.subs(x_sym, self.t)
```
**Files**: `fundamental_theorem_core.py`

### 4. Property Exposure
**Issue**: Missing `integral_formulas` attribute in visualization classes
**Solution**: Added property decorators to expose core data
```python
@property
def integral_formulas(self):
    return self.core.integral_formulas
```
**Files**: `integrals_viz.py`

## Testing Strategy

### Test Coverage
- **Unit Tests**: Core mathematical functions
- **Integration Tests**: Visualization rendering without display
- **Error Handling**: Invalid input scenarios
- **Cross-Module**: Inter-module dependencies

### Test Patterns
```python
def test_power_rule_demo(self):
    '''Test power rule demonstration.'''
    try:
        self.rules.power_rule_demo(2, (-2, 2))
        self.assertTrue(True, "Demo executed successfully")
    except Exception as e:
        self.fail(f"Demo failed: {e}")
```

## Development Workflow

### 1. Adding New Features
1. Implement core mathematical logic in `*_core.py`
2. Add visualization layer in `*_viz.py`
3. Write comprehensive tests
4. Update main interface if needed
5. Document new functionality

### 2. Code Style
- 2-space indentation for Python files
- single quote for docstring and files
- Descriptive function/variable names
- Comprehensive docstrings with examples
- Type hints for function parameters

### 3. Documentation Headers
All files should include standardized headers:
```python
'''
Module Name
-----------

Brief description of module purpose and functionality.

@file: filename.py
@authors: Claude Sonnet 4, Abdullah Barrak.
@date: 1/1/2026
'''
```

## Common Debugging Scenarios

### 1. Matplotlib Display Issues
```python
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing
```

### 2. SymPy Integration Issues
- Verify symbol definitions match across modules
- Check lambdify parameter ordering
- Test with simple expressions first

### 3. Numerical Precision
- Use appropriate tolerances for floating point comparisons
- Handle edge cases (division by zero, infinity)
- Provide fallback methods when symbolic computation fails

## Future Enhancement Areas

### 1. Additional Mathematical Topics
- Limits and continuity demonstrations
- Series expansions and convergence
- Multivariable calculus visualizations
- Differential equations solvers

### 2. Interactive Features
- Web-based interface using Jupyter widgets
- Real-time parameter adjustment sliders
- Step-by-step solution breakdowns
- Practice problem generation

### 3. Performance Optimizations
- Caching of expensive symbolic computations
- Parallel computation for large datasets
- Memory-efficient plotting for complex functions

## Deployment Notes

### Production Considerations
- Disable interactive matplotlib backends
- Set appropriate memory limits for symbolic computation
- Handle timeout scenarios for complex calculations
- Provide progress indicators for long-running operations

### Educational Integration
- Clear learning objectives for each module
- Progressive difficulty levels
- Assessment and feedback mechanisms
- Export capabilities for academic use

# MCPost: Monte Carlo Post-analysis Package

[![PyPI version](https://badge.fury.io/py/mcpost.svg)](https://badge.fury.io/py/mcpost)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCPost is a comprehensive Python package for post-analysis of Monte Carlo samples, providing tools for global sensitivity analysis (GSA) and Monte Carlo integration with modern packaging standards and extensive documentation.

## Features

### Global Sensitivity Analysis
- **Multiple sensitivity metrics**: Mutual Information, Distance Correlation, Permutation Importance
- **Gaussian Process surrogates** with Automatic Relevance Determination (ARD)
- **Sobol' indices** for variance-based sensitivity analysis
- **Partial Dependence Plots** for interpretable results
- **Robust preprocessing** with automatic constant column detection

### Monte Carlo Integration
- **Standard Monte Carlo** integration with importance sampling
- **Automatic integration** with adaptive sampling strategies
- **Flexible PDF specification** for target and sampling distributions

### Modern Package Features
- **Type hints** and comprehensive documentation
- **Modular design** with clean public APIs
- **Optional dependencies** for visualization and development
- **Extensive testing** with property-based tests
- **Performance optimizations** for large datasets

## Installation

MCPost supports multiple installation methods to suit different use cases:

### Basic Installation

For core functionality (GSA and integration without plotting):

```bash
pip install MC-post
```

### Installation from Source

For the latest development version:

```bash
pip install git+https://github.com/zzhang0123/mcpost.git
```


### Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/mcpost/mcpost.git
cd mcpost

# Install in development mode with all dependencies
pip install -e .[dev]

# Run tests to verify installation
pytest
```


## Quick Start

### Global Sensitivity Analysis

MCPost provides comprehensive GSA capabilities with multiple sensitivity metrics:

```python
import numpy as np
from mcpost import gsa_pipeline

# Define a simple test function
def polynomial_function(X):
    """
    Simple polynomial: f(x1, x2, x3) = x1^2 + 2*x2 + 0.1*x3
    
    We expect x2 to be most influential, x1 moderately influential, 
    and x3 to have minimal influence.
    """
    x1, x2, x3 = X[:, 0], X[:, 1], X[:, 2]
    return x1**2 + 2*x2 + 0.1*x3

# Generate parameter samples
n_samples = 1000
X = np.random.uniform(-1, 1, (n_samples, 3))  # 3 parameters in [-1, 1]

# Evaluate function
y = polynomial_function(X)
Y = y.reshape(-1, 1)  # GSA expects 2D array

# Run comprehensive GSA analysis
# Run GSA analysis
param_names = ["x1", "x2", "x3"]
feature_names = ["polynomial"]

print("Running GSA analysis...")
results = gsa_pipeline(
    X, Y,
    param_names=param_names,
    feature_names=feature_names,
    scaler="minmax",
    enable_sobol=True,
    enable_gp=True,
    enable_perm=True,
    make_pdp=False,  # Skip PDPs for this simple example
    N_sobol=2048
)

# Display results
sensitivity_table = results["results"]["polynomial"]["table"]
print("\nSensitivity Analysis Results:")
print(sensitivity_table)


```

### Monte Carlo Integration

Integration with Custom Distributions

```python
# Define integration problem: E[x^2] where x ~ N(0,1)
# Analytical solution: 1.0

def integrand(theta):
    """Function to integrate: f(x) = x^2"""
    return theta[:, 0]**2

def target_pdf(theta):
    """Standard normal PDF"""
    return np.exp(-0.5 * theta[:, 0]**2) / np.sqrt(2 * np.pi)

print("Integration Problem: E[X^2] where X ~ N(0,1)")
print("Analytical solution: 1.0")
print()

# Method 1: Standard Monte Carlo
n_samples = 5000
theta_samples = np.random.normal(0, 1, (n_samples, 1))
f_values = integrand(theta_samples)

mc_result = monte_carlo_integral(theta_samples, f_values, target_pdf)

print("Standard Monte Carlo:")
print(f"  Integral estimate: {mc_result['integral'][0]:.6f}")
print(f"  Uncertainty: {mc_result['uncertainty'][0]:.6f}")
print(f"  Effective sample size: {mc_result['effective_sample_size']:.0f}")
print(f"  Error: {abs(mc_result['integral'][0] - 1.0):.6f}")
```

## Documentation and Resources

### Complete Documentation
- **[Getting Started Tutorial](docs/tutorials/getting_started.ipynb)**: Your first MCPost analysis
- **[GSA Deep Dive](docs/tutorials/gsa_comprehensive.md)**: Advanced sensitivity analysis
- **[Extension Guide](docs/extension_guide.md)**: Creating custom methods

### Quick References

### Learning Resources
- **[Getting Started Tutorial](docs/tutorials/getting_started.ipynb)**: Your first MCPost analysis
- **[GSA Deep Dive](docs/tutorials/gsa_comprehensive.md)**: Advanced sensitivity analysis

### Example Applications
- **[Climate Modeling](examples/climate_sensitivity.py)**: GSA for climate model parameters
- **[Integration Comparison](examples/integration_comparison.py)**: Monte Carlo integration examples

## Requirements

### Core Dependencies
- Python 3.8+
- NumPy >= 1.20.0, <2.4.0
- Pandas >= 1.3.0
- Scikit-learn >= 1.0.0
- SciPy >= 1.7.0
- dcor >= 0.5.0
- SALib >= 1.4.0

### Optional Dependencies
- **Visualization**: matplotlib >= 3.5.0
- **Development**: pytest, hypothesis, black, mypy
- **Documentation**: sphinx, jupyter, nbsphinx

### Development Setup

```bash
git clone https://github.com/zzhang0123/mcpost.git
cd mcpost
pip install -e .[dev]
pytest
```

### Testing

MCPost includes a comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_gsa/          # GSA functionality tests
pytest tests/test_integration/  # Integration tests
pytest tests/test_utils/        # Utility tests

# Run property-based tests
pytest tests/ -k "property"

# Run with coverage
pytest tests/ --cov=mcpost --cov-report=html
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use MCPost in your research, please cite:

```bibtex
@software{mcpost,
  title={MCPost: Monte Carlo Post-analysis Package},
  author={MCPost Contributors},
  url={https://zh-zhang.com/mcpost/},
  version={0.1.3},
  year={2026}
}
```

## Acknowledgments

MCPost builds upon several excellent open-source libraries:
- [Scikit-learn](https://scikit-learn.org/) for machine learning algorithms
- [SALib](https://salib.readthedocs.io/) for Sobol' sensitivity analysis
- [dcor](https://dcor.readthedocs.io/) for distance correlation
- [SciPy](https://scipy.org/) for scientific computing
- [NumPy](https://numpy.org/) for numerical computing
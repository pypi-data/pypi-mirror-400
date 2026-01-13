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
- **Quasi-Monte Carlo** methods (Sobol, Halton sequences)
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
pip install mcpost
```

### Installation with Visualization Support

For full functionality including plotting and visualization:

```bash
pip install mcpost[viz]
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

### Installation from Source

For the latest development version:

```bash
pip install git+https://github.com/zzhang0123/mcpost.git
```

### Conda Installation

MCPost will be available on conda-forge (coming soon):

```bash
conda install -c conda-forge mcpost
```

## Quick Start

### Global Sensitivity Analysis

MCPost provides comprehensive GSA capabilities with multiple sensitivity metrics:

```python
import numpy as np
from mcpost import gsa_pipeline

# Generate sample data (Ishigami function example)
np.random.seed(42)
n_samples = 1000
X = np.random.uniform(-np.pi, np.pi, (n_samples, 3))

# Ishigami function: f(x1,x2,x3) = sin(x1) + 7*sin(x2)^2 + 0.1*x3^4*sin(x1)
y = (np.sin(X[:, 0]) + 
     7 * np.sin(X[:, 1])**2 + 
     0.1 * X[:, 2]**4 * np.sin(X[:, 0]))
Y = y.reshape(-1, 1)

# Run comprehensive GSA analysis
results = gsa_pipeline(
    X, Y,
    param_names=["x1", "x2", "x3"],
    feature_names=["ishigami"],
    scaler="minmax",
    enable_sobol=True,
    enable_gp=True,
    enable_perm=True,
    make_pdp=True
)

# View sensitivity results
print("Sensitivity Analysis Results:")
print(results["results"]["ishigami"]["table"])

# Plot sensitivity metrics (requires matplotlib)
from mcpost import plot_sensitivity_metrics
plot_sensitivity_metrics(results, save_path="sensitivity_plot.png")
```

### Advanced GSA Usage

```python
# Custom GSA configuration
from mcpost import GSAConfig, gsa_for_target

# Configure GSA parameters
config = GSAConfig()
config.DEFAULT_SCALER = "standard"
config.DEFAULT_N_SOBOL = 8192

# Run GSA for specific target
target_results = gsa_for_target(
    X, Y[:, 0],  # Single target
    param_names=["x1", "x2", "x3"],
    target_name="ishigami",
    scaler=config.DEFAULT_SCALER,
    n_sobol=config.DEFAULT_N_SOBOL
)
```

### Monte Carlo Integration

MCPost supports various integration methods for different use cases:

```python
import numpy as np
from mcpost import monte_carlo_integral, qmc_integral_auto

# Define integration problem: E[x*sin(y)] where (x,y) ~ N(0,I)
def target_pdf(theta):
    """Target probability density function (standard normal)"""
    return np.exp(-0.5 * np.sum(theta**2, axis=1)) / (2 * np.pi)

def integrand(theta):
    """Function to integrate: f(x,y) = x * sin(y)"""
    return theta[:, 0] * np.sin(theta[:, 1])

# Method 1: Standard Monte Carlo
np.random.seed(42)
theta_samples = np.random.normal(0, 1, (5000, 2))
f_values = integrand(theta_samples)

mc_result = monte_carlo_integral(theta_samples, f_values, target_pdf)
print(f"Monte Carlo result: {mc_result['integral']:.6f} ± {mc_result['uncertainty']:.6f}")

# Method 2: Quasi-Monte Carlo (automatic)
qmc_result = qmc_integral_auto(
    N_samples=4096,
    N_params=2, 
    data_func=integrand,
    p_target=target_pdf,
    bounds=[(-4, 4), (-4, 4)]  # Integration bounds
)
print(f"QMC result: {qmc_result['integral']:.6f}")

# Method 3: QMC with importance sampling
from mcpost import qmc_integral_importance

def importance_pdf(theta):
    """Importance sampling distribution"""
    return np.exp(-0.25 * np.sum(theta**2, axis=1)) / (4 * np.pi)

qmc_is_result = qmc_integral_importance(
    N_samples=2048,
    N_params=2,
    data_func=integrand,
    p_target=target_pdf,
    q_sample=importance_pdf,
    bounds=[(-3, 3), (-3, 3)]
)
print(f"QMC + Importance Sampling: {qmc_is_result['integral']:.6f}")
```

### Integration with Custom Distributions

```python
# Example: Integration over custom parameter space
def custom_target(theta):
    """Custom target distribution (mixture of Gaussians)"""
    comp1 = 0.6 * np.exp(-0.5 * np.sum((theta - 1)**2, axis=1))
    comp2 = 0.4 * np.exp(-0.5 * np.sum((theta + 1)**2, axis=1))
    return (comp1 + comp2) / (2 * np.pi)

def complex_integrand(theta):
    """More complex integrand"""
    return np.exp(theta[:, 0]) * np.cos(theta[:, 1]) * theta[:, 0]**2

# Use adaptive QMC integration
result = qmc_integral_auto(
    N_samples=8192,
    N_params=2,
    data_func=complex_integrand,
    p_target=custom_target,
    bounds=[(-3, 3), (-3, 3)],
    qmc_method="sobol"  # or "halton"
)
```

## Documentation and Resources

### Complete Documentation
- **[Getting Started Tutorial](docs/tutorials/getting_started.ipynb)**: Your first MCPost analysis
- **[GSA Deep Dive](docs/tutorials/gsa_comprehensive.md)**: Advanced sensitivity analysis
- **[Extension Guide](docs/extension_guide.md)**: Creating custom methods
- **[Migration Guide](docs/MIGRATION_GUIDE.md)**: Migrating from legacy scripts

### Quick References
- **[Backward Compatibility](docs/BACKWARD_COMPATIBILITY.md)**: Version compatibility policy
- **[Release Guide](docs/RELEASE_GUIDE.md)**: Release process and versioning

### Learning Resources
- **[Getting Started Tutorial](docs/tutorials/getting_started.ipynb)**: Your first MCPost analysis
- **[GSA Deep Dive](docs/tutorials/gsa_comprehensive.md)**: Advanced sensitivity analysis

### Example Applications
- **[Climate Modeling](examples/climate_sensitivity.py)**: GSA for climate model parameters
- **[Integration Comparison](examples/integration_comparison.py)**: Monte Carlo integration examples

## Requirements

### Core Dependencies
- Python 3.8+
- NumPy >= 1.20.0
- Pandas >= 1.3.0
- Scikit-learn >= 1.0.0
- SciPy >= 1.7.0
- dcor >= 0.5.0
- SALib >= 1.4.0

### Optional Dependencies
- **Visualization**: matplotlib >= 3.5.0
- **Development**: pytest, hypothesis, black, mypy
- **Documentation**: sphinx, jupyter, nbsphinx

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

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
# Run all tests (excludes backward compatibility tests)
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

**Backward Compatibility Tests**: These require the legacy mock files `gsa_pipeline.py` and `mc_int.py` located in `tests/legacy_mocks/` and are skipped in CI. For local development:

```bash
# Place original files in repository root, then:
pytest tests/test_gsa_backward_compatibility.py
pytest tests/test_integration_backward_compatibility.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use MCPost in your research, please cite:

```bibtex
@software{mcpost,
  title={MCPost: Monte Carlo Post-analysis Package},
  author={MCPost Contributors},
  url={https://github.com/zzhang0123/mcpost},
  version={0.1.0},
  year={2024}
}
```

## Acknowledgments

MCPost builds upon several excellent open-source libraries:
- [Scikit-learn](https://scikit-learn.org/) for machine learning algorithms
- [SALib](https://salib.readthedocs.io/) for Sobol' sensitivity analysis
- [dcor](https://dcor.readthedocs.io/) for distance correlation
- [SciPy](https://scipy.org/) for scientific computing
- [NumPy](https://numpy.org/) for numerical computing
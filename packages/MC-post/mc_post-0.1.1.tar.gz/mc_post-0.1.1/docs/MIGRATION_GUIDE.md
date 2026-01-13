# Migration Guide: From Legacy Scripts to MCPost Package

This guide helps users migrate from the original `gsa_pipeline.py` and `mc_int.py` scripts to the new MCPost package. Note that legacy compatibility mock files are maintained in `tests/legacy_mocks/` for testing purposes only.

## Overview

The MCPost package provides the same functionality as the legacy scripts but with improved:
- Error handling and input validation
- Performance and memory efficiency
- Type hints and IDE support
- Testing and reliability
- Documentation and examples

## Quick Migration

### Before (Legacy Scripts)

```python
# Old way - importing from scripts
from gsa_pipeline import gsa_for_target, gsa_pipeline
from mc_int import monte_carlo_integral, qmc_integral

# Usage remains the same
result = gsa_for_target(X, y, param_names)
integral = monte_carlo_integral(params, data, p_target)
```

### After (MCPost Package)

```python
# New way - importing from package
from mcpost import gsa_for_target, gsa_pipeline
from mcpost import monte_carlo_integral, qmc_integral

# Usage is identical - no code changes needed!
result = gsa_for_target(X, y, param_names)
integral = monte_carlo_integral(params, data, p_target)
```

## Installation

### Remove Legacy Scripts

If you have the old scripts in your project:

```bash
# Remove old files (backup first!)
rm gsa_pipeline.py mc_int.py
```

### Install MCPost Package

```bash
# Install from PyPI
pip install mcpost

# Or install with optional dependencies
pip install mcpost[viz]  # For plotting
pip install mcpost[all]  # For everything
```

## Detailed Migration Steps

### Step 1: Update Imports

Replace script imports with package imports:

```python
# OLD
from gsa_pipeline import (
    gsa_for_target,
    gsa_pipeline, 
    plot_sensitivity_metrics
)
from mc_int import (
    monte_carlo_integral,
    qmc_integral,
    qmc_integral_auto
)

# NEW
from mcpost import (
    gsa_for_target,
    gsa_pipeline,
    plot_sensitivity_metrics,
    monte_carlo_integral,
    qmc_integral,
    qmc_integral_auto
)
```

### Step 2: Update Function Calls (No Changes Needed!)

All function signatures remain identical:

```python
# GSA functions - no changes needed
result = gsa_for_target(
    X=X, 
    y=y, 
    param_names=param_names,
    scaler='minmax',
    enable_perm=True,
    enable_gp=True,
    enable_sobol=True
)

# Integration functions - no changes needed  
integral = monte_carlo_integral(
    params=params,
    data=data, 
    p_target=p_target,
    q_sample=q_sample,
    n_samples=10000
)
```

### Step 3: Update Configuration (Optional)

The package provides better configuration management:

```python
# OLD - manual configuration
scaler = 'minmax'
enable_gp = True

# NEW - using configuration classes (optional)
from mcpost.utils import GSAConfig, configure_defaults

# Set global defaults
configure_defaults(GSAConfig(
    DEFAULT_SCALER='minmax',
    DEFAULT_ENABLE_GP=True
))
```

### Step 4: Update Error Handling (Recommended)

The package provides better error handling:

```python
# OLD - generic exceptions
try:
    result = gsa_for_target(X, y, param_names)
except Exception as e:
    print(f"Error: {e}")

# NEW - specific exceptions
from mcpost import ValidationError, GSAError

try:
    result = gsa_for_target(X, y, param_names)
except ValidationError as e:
    print(f"Input validation error: {e}")
except GSAError as e:
    print(f"GSA computation error: {e}")
```

## New Features Available

### Chunked Processing for Large Datasets

```python
# New feature - handle large datasets efficiently
from mcpost import chunked_gsa_for_target

# Process large datasets in chunks
result = chunked_gsa_for_target(
    X=large_X,
    y=large_y, 
    param_names=param_names,
    chunk_size=1000  # Process 1000 samples at a time
)
```

### Enhanced Validation

```python
# New feature - explicit input validation
from mcpost.utils import validate_inputs

# Validate inputs before processing
X_clean, y_clean = validate_inputs(X, y, param_names)
result = gsa_for_target(X_clean, y_clean, param_names)
```

### Type Hints Support

```python
# New feature - full type hints for better IDE support
import numpy as np
import pandas as pd
from mcpost import gsa_for_target

def my_analysis(X: np.ndarray, y: np.ndarray) -> pd.DataFrame:
    return gsa_for_target(X, y, param_names=['x1', 'x2'])
```

### Extension Interfaces

```python
# New feature - extend with custom methods
from mcpost.gsa.base import BaseSensitivityMethod, register_gsa_method

class MyCustomMethod(BaseSensitivityMethod):
    def compute_sensitivity(self, X, y):
        # Your custom implementation
        return sensitivity_scores

# Register your method
register_gsa_method('my_method', MyCustomMethod)
```

## Performance Improvements

The package includes several performance improvements:

### Memory Efficiency

```python
# Automatic memory optimization for large datasets
result = gsa_for_target(
    X=very_large_X,  # Package automatically optimizes memory usage
    y=very_large_y,
    param_names=param_names
)
```

### Progress Indicators

```python
# Built-in progress bars for long computations
result = gsa_for_target(
    X=X, y=y, param_names=param_names,
    verbose=True  # Shows progress bar
)
```

### Parallel Processing

```python
# Automatic parallelization where beneficial
result = gsa_for_target(
    X=X, y=y, param_names=param_names,
    n_jobs=-1  # Use all available cores
)
```

## Testing Your Migration

### Validation Script

Create a script to validate your migration:

```python
# test_migration.py
import numpy as np
from mcpost import gsa_for_target, monte_carlo_integral

# Test data
np.random.seed(42)
X = np.random.randn(100, 3)
y = X[:, 0] + 0.5 * X[:, 1] + np.random.randn(100) * 0.1
param_names = ['x1', 'x2', 'x3']

# Test GSA
print("Testing GSA...")
gsa_result = gsa_for_target(X, y, param_names)
print(f"GSA result shape: {gsa_result.shape}")
print("✓ GSA working")

# Test integration
print("Testing integration...")
params = np.random.randn(50, 2)
data = np.random.randn(50)

def p_target(x):
    return np.exp(-0.5 * np.sum(x**2, axis=1))

integral_result = monte_carlo_integral(params, data, p_target)
print(f"Integral result: {integral_result}")
print("✓ Integration working")

print("🎉 Migration successful!")
```

Run the validation:

```bash
python test_migration.py
```

### Compare Results

Verify that results are identical:

```python
# Compare old vs new results
import numpy as np

# Set same random seed for reproducibility
np.random.seed(42)

# OLD: Using legacy scripts (if still available)
# from gsa_pipeline import gsa_for_target as old_gsa
# old_result = old_gsa(X, y, param_names)

# NEW: Using MCPost package
from mcpost import gsa_for_target as new_gsa
new_result = new_gsa(X, y, param_names)

# Results should be identical (within numerical precision)
# np.testing.assert_allclose(old_result.values, new_result.values)
```

## Common Issues and Solutions

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'mcpost'`

**Solution**: 
```bash
pip install mcpost
```

### Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'matplotlib'`

**Solution**:
```bash
pip install mcpost[viz]  # For plotting dependencies
# or
pip install matplotlib
```

### Version Conflicts

**Problem**: Dependency version conflicts

**Solution**:
```bash
# Create fresh environment
python -m venv mcpost_env
source mcpost_env/bin/activate  # On Windows: mcpost_env\Scripts\activate
pip install mcpost[all]
```

### Performance Differences

**Problem**: Different performance characteristics

**Solution**: The package may be faster or slower depending on your use case. Use profiling to identify bottlenecks:

```python
import cProfile
cProfile.run('gsa_for_target(X, y, param_names)')
```

## Rollback Plan

If you need to rollback to legacy scripts:

1. **Keep backups**: Always backup your original scripts
2. **Version control**: Use git to track changes
3. **Gradual migration**: Migrate one module at a time
4. **Parallel testing**: Run both versions in parallel during transition

```python
# Rollback example
# Temporarily use both versions
try:
    from mcpost import gsa_for_target as new_gsa
    result = new_gsa(X, y, param_names)
except Exception:
    # Fallback to legacy script
    from gsa_pipeline import gsa_for_target as old_gsa
    result = old_gsa(X, y, param_names)
```

## Getting Help

If you encounter issues during migration:

1. **Check documentation**: [MCPost Documentation](https://mcpost.readthedocs.io)
2. **Search issues**: [GitHub Issues](https://github.com/mcpost/mcpost/issues)
3. **Create issue**: Use the "migration" label
4. **Community support**: Ask questions in discussions

### Issue Template for Migration Problems

```markdown
**Migration Issue**

**From**: Legacy scripts (gsa_pipeline.py, mc_int.py)
**To**: MCPost v0.1.0
**Python Version**: 3.9

**Problem Description**: 
Brief description of the issue

**Code Example**:
```python
# Minimal example that reproduces the issue
```

**Expected Behavior**: 
What you expected to happen

**Actual Behavior**: 
What actually happened

**Error Message** (if any):
```
Full error traceback
```
```

## Benefits of Migration

After migration, you'll benefit from:

✅ **Better reliability**: Comprehensive testing and error handling  
✅ **Improved performance**: Optimizations for large datasets  
✅ **Enhanced usability**: Better documentation and examples  
✅ **Future updates**: Regular bug fixes and new features  
✅ **Community support**: Active development and user community  
✅ **Type safety**: Full type hints for better IDE support  
✅ **Extensibility**: Plugin system for custom methods  

## Next Steps

After successful migration:

1. **Remove legacy scripts**: Clean up old files
2. **Update documentation**: Update your project docs
3. **Share feedback**: Help improve the package
4. **Explore new features**: Try chunked processing and extensions
5. **Stay updated**: Watch for new releases

Welcome to the MCPost community! 🎉
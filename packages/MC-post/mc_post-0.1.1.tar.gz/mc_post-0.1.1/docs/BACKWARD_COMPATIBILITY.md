# MCPost Backward Compatibility Policy

This document outlines MCPost's commitment to backward compatibility and provides guidelines for maintaining stable APIs across versions.

## Our Commitment

MCPost is committed to providing a stable and reliable API for users. We understand that breaking changes can disrupt workflows and cause significant overhead for users upgrading their code.

### Semantic Versioning Promise

MCPost follows [Semantic Versioning](https://semver.org/) strictly:

- **PATCH** releases (1.0.0 → 1.0.1): Only bug fixes, no API changes
- **MINOR** releases (1.0.0 → 1.1.0): New features, fully backward compatible
- **MAJOR** releases (1.0.0 → 2.0.0): May include breaking changes

## What We Guarantee

### Within Major Versions (e.g., 1.x.x)

✅ **Safe to upgrade without code changes:**
- All public APIs remain unchanged
- Function signatures stay the same
- Default behaviors are preserved
- Return value formats are maintained
- Exception types remain consistent

✅ **Safe additions:**
- New functions and classes
- New optional parameters with sensible defaults
- New modules and subpackages
- Additional return values (when backward compatible)

### Across Major Versions (e.g., 1.x.x → 2.x.x)

⚠️ **May require code changes:**
- Public API changes
- Function signature modifications
- Behavior changes
- Module reorganization
- Dependency updates

## Public vs Private APIs

### Public APIs (Guaranteed Stable)

Public APIs are covered by our backward compatibility guarantee:

```python
# Main package imports
from mcpost import gsa_pipeline, monte_carlo_integral

# Module-level imports
from mcpost.gsa import gsa_for_target
from mcpost.integration import qmc_integral

# Utility functions
from mcpost.utils import validate_inputs, GSAConfig
```

### Private APIs (No Guarantee)

Private APIs may change without notice:

```python
# Functions/classes starting with underscore
mcpost._internal_function()
mcpost.gsa._private_helper()

# Implementation details
mcpost.gsa.pipeline._fit_gp_model()
mcpost.utils.validation._check_array_shape()
```

**Rule of thumb:** If it starts with `_`, it's private and may change.

## Deprecation Process

When we need to make breaking changes, we follow a structured deprecation process:

### Phase 1: Deprecation Warning

- Old API remains functional
- Warning message guides users to new API
- Minimum duration: One minor release cycle

```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated since v1.2.0 and will be removed in v2.0.0. "
        "Use new_function instead. See migration guide: https://...",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()
```

### Phase 2: Removal

- Old API is removed in next major version
- Clear migration guide provided
- Breaking change documented in CHANGELOG

## Testing Backward Compatibility

MCPost includes automated tests to ensure backward compatibility:

### Compatibility Test Suite

```python
# tests/test_backward_compatibility.py
def test_legacy_api_compatibility():
    """Test that legacy function signatures still work."""
    # Test old-style function calls
    result = gsa_for_target(X, y, param_names)
    assert isinstance(result, pd.DataFrame)

def test_return_value_compatibility():
    """Test that return values maintain expected structure."""
    result = monte_carlo_integral(params, data, p_target)
    assert 'integral' in result
    assert 'uncertainty' in result
```

### Property-Based Compatibility Tests

```python
@given(valid_gsa_inputs())
def test_gsa_api_stability(inputs):
    """Property test ensuring GSA API remains stable."""
    X, y, param_names = inputs
    
    # Test that function accepts same inputs
    result = gsa_for_target(X, y, param_names)
    
    # Test that output format is consistent
    assert isinstance(result, pd.DataFrame)
    assert all(col in result.columns for col in EXPECTED_COLUMNS)
```

## Migration Support

### Automated Migration Tools

For major version upgrades, we provide migration tools:

```bash
# Future: Automated migration script
python -m mcpost.migrate --from=1.x --to=2.0 --path=my_project/
```

### Migration Guides

Detailed migration guides for each major version:

- Step-by-step instructions
- Before/after code examples
- Common pitfalls and solutions
- Performance considerations

### Compatibility Shims

When possible, we provide compatibility layers:

```python
# mcpost/compat.py - Compatibility layer for v1.x users
from mcpost.gsa import gsa_for_target as _gsa_for_target

def legacy_gsa_function(*args, **kwargs):
    """Legacy wrapper for backward compatibility."""
    warnings.warn("Use gsa_for_target instead", DeprecationWarning)
    return _gsa_for_target(*args, **kwargs)
```

## Exception Handling Compatibility

### Stable Exception Hierarchy

Exception types and hierarchy remain stable within major versions:

```python
# These exception types won't change in minor/patch releases
mcpost.ValidationError
mcpost.GSAError
mcpost.IntegrationError
```

### Exception Message Stability

While we may improve error messages, the exception types remain consistent:

```python
try:
    result = gsa_for_target(invalid_input)
except mcpost.ValidationError as e:
    # Exception type guaranteed stable
    # Message may improve but type stays same
    handle_validation_error(e)
```

## Configuration Compatibility

### Configuration File Formats

Configuration file formats remain backward compatible:

```python
# Old config format continues to work
config = {
    'gsa': {'enable_sobol': True},
    'integration': {'method': 'qmc'}
}

# New config format is additive
config = {
    'gsa': {
        'enable_sobol': True,
        'new_option': 'default_value'  # New options have defaults
    }
}
```

### Environment Variables

Environment variable names and behavior remain stable:

```bash
# These remain consistent across minor versions
export MCPOST_GSA_SCALER=minmax
export MCPOST_INTEGRATION_METHOD=sobol
```

## Data Format Compatibility

### Input Data Formats

Supported input formats remain consistent:

```python
# These input formats continue to work
X = np.array(...)           # NumPy arrays
X = pd.DataFrame(...)       # Pandas DataFrames
X = [[1, 2], [3, 4]]       # Lists of lists
```

### Output Data Formats

Output formats maintain structure:

```python
# GSA results maintain DataFrame structure
result = gsa_for_target(X, y)
assert isinstance(result, pd.DataFrame)
assert 'MI' in result.columns  # Column names stable

# Integration results maintain dict structure
result = monte_carlo_integral(...)
assert 'integral' in result
assert 'uncertainty' in result
```

## Performance Compatibility

### Performance Guarantees

While we continuously improve performance, we guarantee:

- No significant performance regressions in minor/patch releases
- Memory usage remains stable or improves
- Algorithmic complexity doesn't worsen

### Performance Monitoring

We track performance across releases:

```python
# Automated performance tests
@pytest.mark.performance
def test_gsa_performance_regression():
    """Ensure GSA performance doesn't regress."""
    start_time = time.time()
    result = gsa_for_target(large_dataset)
    duration = time.time() - start_time
    
    assert duration < PERFORMANCE_THRESHOLD
```

## Dependency Compatibility

### Core Dependencies

Core dependencies maintain compatibility:

- NumPy: Support for versions within reasonable range
- Pandas: Maintain compatibility with stable versions
- SciPy: Support for LTS versions

### Optional Dependencies

Optional dependencies may have more flexibility:

```python
# Optional dependencies with graceful degradation
try:
    import matplotlib
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    
def plot_results():
    if not HAS_PLOTTING:
        raise ImportError("matplotlib required for plotting")
```

## Reporting Compatibility Issues

If you encounter backward compatibility issues:

1. **Check the CHANGELOG**: Verify if it's a documented change
2. **Create an Issue**: Use the "compatibility" label
3. **Provide Details**: Include version numbers and minimal reproduction
4. **Suggest Solutions**: Help us understand the impact

### Issue Template

```markdown
**MCPost Version**: 1.2.0
**Previous Working Version**: 1.1.0
**Python Version**: 3.9

**Description**: 
Function X no longer accepts parameter Y

**Minimal Example**:
```python
# This worked in 1.1.0 but fails in 1.2.0
result = mcpost.function_x(param_y=value)
```

**Expected Behavior**: 
Should continue to work as in 1.1.0

**Actual Behavior**: 
Raises TypeError: unexpected keyword argument
```

## Future Compatibility Plans

### Long-term Support (LTS)

We're considering LTS releases for enterprise users:

- Extended support period (2+ years)
- Security and critical bug fixes only
- Predictable upgrade cycles

### API Stability Levels

Future API stability levels:

- **Stable**: Full backward compatibility guarantee
- **Provisional**: May change with deprecation warning
- **Experimental**: May change without notice

## Best Practices for Users

### Version Pinning

For production environments:

```toml
# pyproject.toml - Pin to specific minor version
dependencies = [
    "mcpost>=1.2.0,<1.3.0"
]
```

### Testing Upgrades

Before upgrading in production:

```bash
# Test in isolated environment
python -m venv test_env
source test_env/bin/activate
pip install mcpost==1.3.0
python -m pytest your_tests/
```

### Monitoring Deprecations

Enable deprecation warnings in tests:

```python
import warnings
warnings.simplefilter('error', DeprecationWarning)
```

## Conclusion

MCPost's backward compatibility policy ensures that your code continues to work as you upgrade versions. We take this commitment seriously and continuously test to ensure we meet these guarantees.

For questions about compatibility, please open an issue or contact the maintainers.
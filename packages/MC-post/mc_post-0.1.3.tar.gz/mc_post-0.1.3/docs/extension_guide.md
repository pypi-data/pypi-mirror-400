# MCPost Extension Guide

This guide explains how to extend MCPost with custom sensitivity analysis and integration methods using the provided base classes and interfaces.

## Overview

MCPost provides extensible base classes that allow you to:

1. **Add custom GSA methods** - Implement new sensitivity analysis techniques
2. **Add custom integration methods** - Implement new Monte Carlo integration approaches
3. **Maintain compatibility** - Ensure your methods work seamlessly with existing MCPost workflows

## Extending GSA Methods

### Basic GSA Method Extension

To create a custom GSA method, inherit from `BaseSensitivityMethod`:

```python
import numpy as np
from mcpost.gsa.base import BaseSensitivityMethod, GSAResult

class CorrelationBasedGSA(BaseSensitivityMethod):
    """
    Simple GSA method based on Pearson correlation coefficients.
    """
    
    def __init__(self, absolute_values=True):
        super().__init__()
        self.absolute_values = absolute_values
    
    def compute_sensitivity(self, X, y, **kwargs):
        """Compute sensitivity using correlation coefficients."""
        # Validate inputs
        self.validate_inputs(X, y)
        
        # Compute correlations
        correlations = np.array([
            np.corrcoef(X[:, i], y)[0, 1] 
            for i in range(X.shape[1])
        ])
        
        # Handle NaN values (constant parameters)
        correlations = np.nan_to_num(correlations, nan=0.0)
        
        # Take absolute values if requested
        if self.absolute_values:
            sensitivity_values = np.abs(correlations)
        else:
            sensitivity_values = correlations
        
        # Create parameter names
        param_names = [f"p{i}" for i in range(X.shape[1])]
        
        # Compute rankings
        rankings = np.argsort(sensitivity_values)[::-1]
        
        return GSAResult(
            sensitivity_values=sensitivity_values,
            parameter_names=param_names,
            method_name="CorrelationGSA",
            metadata={
                "absolute_values": self.absolute_values,
                "raw_correlations": correlations
            },
            rankings=rankings
        )

# Usage example
X = np.random.random((1000, 5))
y = 2*X[:, 0] + X[:, 1] + 0.1*np.random.random(1000)

method = CorrelationBasedGSA()
result = method.compute_sensitivity(X, y)
print(result.to_dataframe())
```

### Variance-Based GSA Method

For methods that decompose output variance, inherit from `VarianceBasedMethod`:

```python
from mcpost.gsa.base import VarianceBasedMethod, GSAResult

class SimpleVarianceDecomposition(VarianceBasedMethod):
    """
    Simple variance decomposition using conditional variance.
    """
    
    def __init__(self, n_bins=10, n_bootstrap=100):
        super().__init__(n_bootstrap=n_bootstrap)
        self.n_bins = n_bins
    
    def compute_sensitivity(self, X, y, **kwargs):
        """Compute sensitivity using conditional variance."""
        self.validate_inputs(X, y)
        
        n_params = X.shape[1]
        total_var = self.estimate_total_variance(y)
        sensitivity_values = np.zeros(n_params)
        
        for i in range(n_params):
            # Bin the parameter values
            bins = np.linspace(X[:, i].min(), X[:, i].max(), self.n_bins + 1)
            bin_indices = np.digitize(X[:, i], bins) - 1
            bin_indices = np.clip(bin_indices, 0, self.n_bins - 1)
            
            # Compute conditional variance
            conditional_vars = []
            for bin_idx in range(self.n_bins):
                mask = bin_indices == bin_idx
                if np.sum(mask) > 1:
                    conditional_vars.append(np.var(y[mask], ddof=1))
            
            if conditional_vars:
                avg_conditional_var = np.mean(conditional_vars)
                sensitivity_values[i] = 1 - avg_conditional_var / total_var
            else:
                sensitivity_values[i] = 0.0
        
        # Estimate uncertainty using bootstrap
        uncertainty = self.bootstrap_uncertainty(X, y, **kwargs)
        
        param_names = [f"p{i}" for i in range(n_params)]
        rankings = np.argsort(sensitivity_values)[::-1]
        
        return GSAResult(
            sensitivity_values=sensitivity_values,
            parameter_names=param_names,
            method_name="SimpleVarianceDecomposition",
            metadata={
                "n_bins": self.n_bins,
                "total_variance": total_var
            },
            uncertainty=uncertainty,
            rankings=rankings
        )
```

### Model-Based GSA Method

For methods using surrogate models, inherit from `ModelBasedMethod`:

```python
from sklearn.ensemble import RandomForestRegressor
from mcpost.gsa.base import ModelBasedMethod, GSAResult

class RandomForestGSA(ModelBasedMethod):
    """
    GSA method using Random Forest feature importance.
    """
    
    def __init__(self, n_estimators=100, random_state=None):
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state
        )
        super().__init__(model=model)
    
    def fit_model(self, X, y):
        """Fit the Random Forest model."""
        self.model.fit(X, y)
    
    def predict_model(self, X):
        """Make predictions using the fitted model."""
        return self.model.predict(X)
    
    def compute_sensitivity(self, X, y, **kwargs):
        """Compute sensitivity using RF feature importance."""
        self.validate_inputs(X, y)
        
        # Fit the model if not already fitted
        if not self.is_model_fitted:
            self.fit_model(X, y)
        
        # Get feature importances
        sensitivity_values = self.model.feature_importances_
        
        param_names = [f"p{i}" for i in range(X.shape[1])]
        rankings = np.argsort(sensitivity_values)[::-1]
        
        return GSAResult(
            sensitivity_values=sensitivity_values,
            parameter_names=param_names,
            method_name="RandomForestGSA",
            metadata={
                "model_score": self.model.score(X, y),
                "n_estimators": self.model.n_estimators
            },
            rankings=rankings
        )
```

### Registering GSA Methods

Use the registry system to make your methods discoverable:

```python
from mcpost.gsa.base import gsa_registry, register_gsa_method

# Method 1: Direct registration
gsa_registry.register(
    'correlation', 
    CorrelationBasedGSA, 
    'Correlation-based sensitivity analysis'
)

# Method 2: Using decorator
@register_gsa_method('rf_importance', 'Random Forest feature importance')
class RFImportanceGSA(ModelBasedMethod):
    # Implementation here
    pass

# List available methods
print("Available GSA methods:", gsa_registry.list_methods())

# Create method instance
method = gsa_registry.create('correlation', absolute_values=True)
```

## Extending Integration Methods

### Basic Monte Carlo Method

To create a custom Monte Carlo integration method, inherit from `MonteCarloMethod`:

```python
import numpy as np
from mcpost.integration.base import MonteCarloMethod, IntegrationResult

class StratifiedMonteCarlo(MonteCarloMethod):
    """
    Stratified Monte Carlo integration method.
    """
    
    def __init__(self, n_strata_per_dim=2, random_state=None):
        super().__init__(random_state=random_state)
        self.n_strata_per_dim = n_strata_per_dim
    
    def integrate(self, func, bounds, n_samples=1000, **kwargs):
        """Perform stratified Monte Carlo integration."""
        self.validate_inputs(func, bounds, n_samples)
        
        n_dims = len(bounds)
        total_strata = self.n_strata_per_dim ** n_dims
        samples_per_stratum = max(1, n_samples // total_strata)
        
        all_values = []
        total_samples_used = 0
        
        # Generate samples for each stratum
        for stratum_idx in range(total_strata):
            # Convert linear index to multi-dimensional stratum coordinates
            coords = []
            temp_idx = stratum_idx
            for _ in range(n_dims):
                coords.append(temp_idx % self.n_strata_per_dim)
                temp_idx //= self.n_strata_per_dim
            
            # Generate samples within this stratum
            stratum_samples = np.random.random((samples_per_stratum, n_dims))
            
            for i, (low, high) in enumerate(bounds):
                stratum_low = low + coords[i] * (high - low) / self.n_strata_per_dim
                stratum_high = low + (coords[i] + 1) * (high - low) / self.n_strata_per_dim
                stratum_samples[:, i] = (stratum_low + 
                                       stratum_samples[:, i] * (stratum_high - stratum_low))
            
            # Evaluate function
            stratum_values = func(stratum_samples)
            all_values.extend(stratum_values)
            total_samples_used += samples_per_stratum
        
        # Compute integral and uncertainty
        all_values = np.array(all_values)
        volume = self.estimate_volume(bounds)
        integral = np.mean(all_values) * volume
        uncertainty = self.estimate_uncertainty(all_values, volume)
        
        return IntegrationResult(
            integral=integral,
            uncertainty=uncertainty,
            n_samples=total_samples_used,
            method_name="StratifiedMC",
            metadata={
                "n_strata_per_dim": self.n_strata_per_dim,
                "total_strata": total_strata,
                "samples_per_stratum": samples_per_stratum
            }
        )
```

### Quasi-Monte Carlo Method

For QMC methods, inherit from `QuasiMonteCarloMethod`:

```python
from mcpost.integration.base import QuasiMonteCarloMethod, IntegrationResult

class HaltonQMC(QuasiMonteCarloMethod):
    """
    Quasi-Monte Carlo integration using Halton sequence.
    """
    
    def __init__(self):
        super().__init__(sequence_type="halton")
    
    def generate_qmc_samples(self, bounds, n_samples):
        """Generate Halton sequence samples."""
        n_dims = len(bounds)
        
        # Simple Halton sequence implementation
        def halton_sequence(n, base):
            sequence = []
            for i in range(1, n + 1):
                f = 1.0
                r = 0.0
                while i > 0:
                    f = f / base
                    r = r + f * (i % base)
                    i = i // base
                sequence.append(r)
            return np.array(sequence)
        
        # Use different prime bases for each dimension
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        if n_dims > len(primes):
            raise ValueError(f"Too many dimensions ({n_dims}), max supported: {len(primes)}")
        
        samples = np.zeros((n_samples, n_dims))
        for dim in range(n_dims):
            samples[:, dim] = halton_sequence(n_samples, primes[dim])
        
        # Transform to actual bounds
        for i, (low, high) in enumerate(bounds):
            samples[:, i] = low + samples[:, i] * (high - low)
        
        return samples
    
    def integrate(self, func, bounds, n_samples=1000, **kwargs):
        """Perform Halton QMC integration."""
        self.validate_inputs(func, bounds, n_samples)
        
        # Generate QMC samples
        samples = self.generate_qmc_samples(bounds, n_samples)
        
        # Evaluate function
        values = func(samples)
        
        # Compute integral and uncertainty
        volume = self.estimate_volume(bounds)
        integral = np.mean(values) * volume
        uncertainty = self.estimate_qmc_uncertainty(values, volume)
        
        return IntegrationResult(
            integral=integral,
            uncertainty=uncertainty,
            n_samples=n_samples,
            method_name="HaltonQMC",
            metadata={
                "sequence_type": self.sequence_type,
                "volume": volume
            }
        )
```

### Adaptive Integration Method

For adaptive methods, inherit from `AdaptiveMethod`:

```python
from mcpost.integration.base import AdaptiveMethod, IntegrationResult

class AdaptiveMonteCarlo(AdaptiveMethod):
    """
    Adaptive Monte Carlo with automatic sample size adjustment.
    """
    
    def __init__(self, tolerance=1e-3, max_iterations=20, initial_samples=100):
        super().__init__(tolerance=tolerance, max_iterations=max_iterations)
        self.initial_samples = initial_samples
    
    def integrate(self, func, bounds, n_samples=1000, **kwargs):
        """Perform adaptive Monte Carlo integration."""
        self.validate_inputs(func, bounds, n_samples)
        
        # Start with initial estimate
        samples = np.random.random((self.initial_samples, len(bounds)))
        for i, (low, high) in enumerate(bounds):
            samples[:, i] = low + samples[:, i] * (high - low)
        
        values = func(samples)
        volume = self.estimate_volume(bounds)
        
        current_estimate = np.mean(values) * volume
        current_uncertainty = np.std(values, ddof=1) * volume / np.sqrt(len(values))
        
        total_samples = self.initial_samples
        all_values = [values]
        
        # Adaptive refinement
        for iteration in range(self.max_iterations):
            # Check convergence
            if self.check_convergence(current_estimate, current_uncertainty, iteration):
                break
            
            # Add more samples
            new_samples_count = min(self.initial_samples * (2 ** iteration), 
                                  n_samples - total_samples)
            if new_samples_count <= 0:
                break
            
            new_estimate, new_uncertainty, converged = self.adaptive_step(
                func, bounds, current_estimate, iteration, 
                new_samples_count=new_samples_count
            )
            
            current_estimate = new_estimate
            current_uncertainty = new_uncertainty
            total_samples += new_samples_count
            
            if converged:
                break
        
        return IntegrationResult(
            integral=current_estimate,
            uncertainty=current_uncertainty,
            n_samples=total_samples,
            method_name="AdaptiveMC",
            metadata={
                "iterations": iteration + 1,
                "initial_samples": self.initial_samples,
                "tolerance": self.tolerance
            },
            convergence_info={
                "converged": iteration < self.max_iterations - 1,
                "final_relative_error": abs(current_uncertainty / current_estimate)
            }
        )
    
    def adaptive_step(self, func, bounds, current_estimate, iteration, **kwargs):
        """Perform one adaptive step."""
        new_samples_count = kwargs.get('new_samples_count', 100)
        
        # Generate new samples
        new_samples = np.random.random((new_samples_count, len(bounds)))
        for i, (low, high) in enumerate(bounds):
            new_samples[:, i] = low + new_samples[:, i] * (high - low)
        
        new_values = func(new_samples)
        volume = self.estimate_volume(bounds)
        
        # Update estimate (simple average for now)
        new_estimate = np.mean(new_values) * volume
        new_uncertainty = np.std(new_values, ddof=1) * volume / np.sqrt(len(new_values))
        
        # Check local convergence
        converged = abs(new_uncertainty / new_estimate) < self.tolerance
        
        return new_estimate, new_uncertainty, converged
```

### Registering Integration Methods

Use the registry system for integration methods:

```python
from mcpost.integration.base import integration_registry, register_integration_method

# Direct registration
integration_registry.register(
    'stratified_mc', 
    StratifiedMonteCarlo, 
    'Stratified Monte Carlo integration'
)

# Using decorator
@register_integration_method('halton_qmc', 'Halton sequence QMC')
class HaltonQMCMethod(QuasiMonteCarloMethod):
    # Implementation here
    pass

# List and use methods
print("Available integration methods:", integration_registry.list_methods())
method = integration_registry.create('stratified_mc', n_strata_per_dim=3)
```

## Integration with MCPost Pipeline

### Using Custom Methods in GSA Pipeline

```python
from mcpost.gsa.base import gsa_registry
from mcpost import gsa_pipeline

# Register your custom method
gsa_registry.register('my_method', MyCustomGSAMethod)

# Use in pipeline (would require pipeline modifications to support registry)
# This is a conceptual example - actual integration would need pipeline updates
```

### Using Custom Methods in Integration Pipeline

```python
from mcpost.integration.base import integration_registry

# Register and use custom integration method
integration_registry.register('my_integration', MyCustomIntegrationMethod)

# Create and use method
method = integration_registry.create('my_integration', custom_param=1.5)

def test_function(x):
    return np.sum(x**2, axis=1)

bounds = [[0, 1], [0, 1], [0, 1]]
result = method.integrate(test_function, bounds, n_samples=10000)
print(result.summary())
```

## Best Practices

### 1. Input Validation
Always validate inputs in your custom methods:

```python
def compute_sensitivity(self, X, y, **kwargs):
    # Use base class validation
    self.validate_inputs(X, y)
    
    # Add custom validation
    if X.shape[1] > 100:
        warnings.warn("Large number of parameters may slow computation")
    
    # Your implementation here
```

### 2. Error Handling
Provide informative error messages:

```python
def integrate(self, func, bounds, n_samples=1000, **kwargs):
    try:
        self.validate_inputs(func, bounds, n_samples)
        # Implementation
    except Exception as e:
        raise ValueError(f"Integration failed in {self.name}: {str(e)}")
```

### 3. Metadata and Documentation
Include comprehensive metadata and docstrings:

```python
def compute_sensitivity(self, X, y, **kwargs):
    \"\"\"
    Compute sensitivity using custom method.
    
    Parameters
    ----------
    X : np.ndarray
        Input parameters
    y : np.ndarray  
        Output values
    custom_param : float, optional
        Custom parameter for the method
        
    Returns
    -------
    GSAResult
        Sensitivity analysis results
        
    Notes
    -----
    This method implements the algorithm described in [1]_.
    
    References
    ----------
    .. [1] Author, "Title", Journal, Year.
    \"\"\"
    # Implementation with rich metadata
    return GSAResult(
        sensitivity_values=values,
        parameter_names=names,
        method_name=self.name,
        metadata={
            "algorithm_version": "1.0",
            "computation_time": time.time() - start_time,
            "custom_parameters": kwargs
        }
    )
```

### 4. Testing Custom Methods
Always test your custom methods:

```python
def test_custom_method():
    # Create test data
    X = np.random.random((100, 3))
    y = X[:, 0] + 2*X[:, 1] + np.random.normal(0, 0.1, 100)
    
    # Test method
    method = MyCustomMethod()
    result = method.compute_sensitivity(X, y)
    
    # Validate results
    assert len(result.sensitivity_values) == X.shape[1]
    assert result.method_name == "MyCustomMethod"
    assert np.all(np.isfinite(result.sensitivity_values))
    
    print("Custom method test passed!")

test_custom_method()
```

This extension guide provides the foundation for creating custom GSA and integration methods that integrate seamlessly with the MCPost ecosystem while maintaining consistency and reliability.
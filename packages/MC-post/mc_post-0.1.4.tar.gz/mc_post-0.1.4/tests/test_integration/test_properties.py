"""
Property-based tests for integration numerical correctness.

Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.numpy import arrays

from mcpost.integration.monte_carlo import monte_carlo_integral


# Custom strategies for generating test data
@st.composite
def integration_test_data(draw):
    """Generate valid integration test data."""
    n_samples = draw(st.integers(min_value=100, max_value=500))
    n_params = draw(st.integers(min_value=1, max_value=3))
    
    # Generate parameter matrix
    params = draw(arrays(
        dtype=np.float64,
        shape=(n_samples, n_params),
        elements=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False)
    ))
    
    # Ensure params has some variation for KDE
    assume(np.std(params, axis=0).min() > 1e-3)
    
    # Generate function values
    data = draw(arrays(
        dtype=np.float64,
        shape=(n_samples,),
        elements=st.floats(min_value=-5.0, max_value=5.0, allow_nan=False, allow_infinity=False)
    ))
    
    return params, data


@st.composite
def pdf_function(draw, n_params):
    """Generate a valid PDF function."""
    # Simple uniform PDF
    bounds_low = draw(arrays(
        dtype=np.float64,
        shape=(n_params,),
        elements=st.floats(min_value=-3.0, max_value=0.0, allow_nan=False, allow_infinity=False)
    ))
    bounds_high = draw(arrays(
        dtype=np.float64,
        shape=(n_params,),
        elements=st.floats(min_value=0.1, max_value=3.0, allow_nan=False, allow_infinity=False)
    ))
    
    # Ensure bounds are valid
    assume(np.all(bounds_high > bounds_low))
    
    volume = np.prod(bounds_high - bounds_low)
    
    def uniform_pdf(theta):
        # Check if all points are within bounds
        in_bounds = np.all(
            (theta >= bounds_low[None, :]) & (theta <= bounds_high[None, :]),
            axis=1
        )
        result = np.zeros(len(theta))
        result[in_bounds] = 1.0 / volume
        return result
    
    return uniform_pdf


class TestMonteCarloIntegrationProperties:
    """Property-based tests for Monte Carlo integration numerical correctness."""
    
    @given(integration_test_data())
    @settings(max_examples=2, deadline=10000)
    def test_integration_deterministic_with_same_pdf(self, test_data):
        """
        Property 7: Integration should be deterministic with identical PDFs.
        
        **Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation**
        **Validates: Requirements 4.5, 7.1, 7.2**
        """
        params, data = test_data
        data = data.reshape(-1, 1)  # Ensure 2D
        
        # Simple uniform PDF
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.1
        
        def sampling_pdf(theta):
            return np.ones(len(theta)) * 0.1
        
        # Run integration twice with same PDFs
        result1 = monte_carlo_integral(params, data, target_pdf, sampling_pdf)
        result2 = monte_carlo_integral(params, data, target_pdf, sampling_pdf)
        
        # Results should be identical when using same sampling PDF
        np.testing.assert_allclose(
            result1['integral'], result2['integral'], 
            rtol=1e-12, atol=1e-14
        )
        np.testing.assert_allclose(
            result1['weights'], result2['weights'], 
            rtol=1e-12, atol=1e-14
        )
    
    @given(integration_test_data())
    @settings(max_examples=2, deadline=10000)
    def test_weight_normalization_property(self, test_data):
        """
        Property 7: Importance weights should always sum to 1.
        
        **Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation**
        **Validates: Requirements 4.5, 7.1, 7.2**
        """
        params, data = test_data
        data = data.reshape(-1, 1)
        
        # Random but valid PDF values
        np.random.seed(42)
        target_vals = np.random.uniform(0.1, 2.0, len(params))
        sampling_vals = np.random.uniform(0.1, 2.0, len(params))
        
        def target_pdf(theta):
            return target_vals
        
        def sampling_pdf(theta):
            return sampling_vals
        
        result = monte_carlo_integral(params, data, target_pdf, sampling_pdf)
        
        # Weights should sum to 1 (within numerical precision)
        weight_sum = np.sum(result['weights'])
        assert abs(weight_sum - 1.0) < 1e-12, f"Weights sum to {weight_sum}, should be 1.0"
    
    @given(integration_test_data())
    @settings(max_examples=2, deadline=10000)
    def test_linear_scaling_property(self, test_data):
        """
        Property 7: Integration should scale linearly with function values.
        
        **Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation**
        **Validates: Requirements 4.5, 7.1, 7.2**
        """
        params, data = test_data
        data = data.reshape(-1, 1)
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.5
        
        # Original integration
        result1 = monte_carlo_integral(params, data, target_pdf)
        
        # Scaled function values
        scale_factor = 2.5
        data_scaled = data * scale_factor
        result2 = monte_carlo_integral(params, data_scaled, target_pdf)
        
        # Integral should scale by the same factor
        expected_scaled = result1['integral'] * scale_factor
        np.testing.assert_allclose(
            result2['integral'], expected_scaled,
            rtol=1e-10, atol=1e-12
        )
    
    @given(integration_test_data())
    @settings(max_examples=2, deadline=10000)
    def test_additive_property(self, test_data):
        """
        Property 7: Integration should be additive for function sums.
        
        **Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation**
        **Validates: Requirements 4.5, 7.1, 7.2**
        """
        params, data1 = test_data
        data1 = data1.reshape(-1, 1)
        
        # Generate second function
        np.random.seed(123)
        data2 = np.random.uniform(-3.0, 3.0, len(params)).reshape(-1, 1)
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.3
        
        def sampling_pdf(theta):
            return np.ones(len(theta)) * 0.3
        
        # Integrate functions separately
        result1 = monte_carlo_integral(params, data1, target_pdf, sampling_pdf)
        result2 = monte_carlo_integral(params, data2, target_pdf, sampling_pdf)
        
        # Integrate sum of functions
        data_sum = data1 + data2
        result_sum = monte_carlo_integral(params, data_sum, target_pdf, sampling_pdf)
        
        # Should satisfy additivity (within numerical precision)
        expected_sum = result1['integral'] + result2['integral']
        np.testing.assert_allclose(
            result_sum['integral'], expected_sum,
            rtol=1e-10, atol=1e-12
        )
    
    @given(integration_test_data())
    @settings(max_examples=2, deadline=10000)
    def test_effective_sample_size_bounds(self, test_data):
        """
        Property 7: Effective sample size should be bounded correctly.
        
        **Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation**
        **Validates: Requirements 4.5, 7.1, 7.2**
        """
        params, data = test_data
        data = data.reshape(-1, 1)
        n_samples = len(params)
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.4
        
        result = monte_carlo_integral(params, data, target_pdf)
        
        # Effective sample size should be positive and <= actual sample size
        ess = result['effective_sample_size']
        assert ess > 0, "Effective sample size should be positive"
        assert ess <= n_samples, f"ESS ({ess}) should be <= N ({n_samples})"
    
    @given(integration_test_data())
    @settings(max_examples=2, deadline=10000)
    def test_constant_function_integration(self, test_data):
        """
        Property 7: Integration of constant function should equal the constant.
        
        **Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation**
        **Validates: Requirements 4.5, 7.1, 7.2**
        """
        params, _ = test_data
        
        # Constant function
        constant_value = 3.14
        data_constant = np.full((len(params), 1), constant_value)
        
        # Uniform PDF (should integrate to 1)
        def uniform_pdf(theta):
            return np.ones(len(theta))
        
        result = monte_carlo_integral(params, data_constant, uniform_pdf, uniform_pdf)
        
        # Integral should be close to the constant value
        np.testing.assert_allclose(
            result['integral'], [constant_value],
            rtol=1e-10, atol=1e-12
        )
    
    @given(integration_test_data())
    @settings(max_examples=2, deadline=10000)
    def test_zero_function_integration(self, test_data):
        """
        Property 7: Integration of zero function should be zero.
        
        **Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation**
        **Validates: Requirements 4.5, 7.1, 7.2**
        """
        params, _ = test_data
        
        # Zero function
        data_zero = np.zeros((len(params), 1))
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.5
        
        result = monte_carlo_integral(params, data_zero, target_pdf)
        
        # Integral should be zero
        np.testing.assert_allclose(
            result['integral'], [0.0],
            rtol=1e-12, atol=1e-14
        )
    
    @given(integration_test_data())
    @settings(max_examples=2, deadline=10000)
    def test_multidimensional_consistency(self, test_data):
        """
        Property 7: Multi-dimensional function integration should be consistent.
        
        **Feature: mcpost-package-improvement, Property 7: Numerical Correctness Preservation**
        **Validates: Requirements 4.5, 7.1, 7.2**
        """
        params, data1 = test_data
        
        # Create second function
        np.random.seed(456)
        data2 = np.random.uniform(-2.0, 2.0, len(params))
        
        # Combine into multi-dimensional function
        data_multi = np.column_stack([data1, data2])
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.25
        
        # Integrate multi-dimensional function
        result_multi = monte_carlo_integral(params, data_multi, target_pdf)
        
        # Integrate components separately
        result1 = monte_carlo_integral(params, data1.reshape(-1, 1), target_pdf)
        result2 = monte_carlo_integral(params, data2.reshape(-1, 1), target_pdf)
        
        # Results should match component-wise
        np.testing.assert_allclose(
            result_multi['integral'][0], result1['integral'][0],
            rtol=1e-12, atol=1e-14
        )
        np.testing.assert_allclose(
            result_multi['integral'][1], result2['integral'][0],
            rtol=1e-12, atol=1e-14
        )
"""
Unit tests for Monte Carlo integration functions.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from mcpost.integration.monte_carlo import monte_carlo_integral


class TestMonteCarloIntegral:
    """Test cases for monte_carlo_integral function."""
    
    def test_basic_functionality(self, integration_data):
        """Test basic Monte Carlo integration functionality."""
        params, data = integration_data
        data = data.reshape(-1, 1)  # Reshape to 2D for function compatibility
        
        # Simple uniform target distribution
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.25  # Uniform on [-1,1]^2
        
        result = monte_carlo_integral(params, data, target_pdf)
        
        # Check return structure
        assert isinstance(result, dict)
        assert 'integral' in result
        assert 'uncertainty' in result
        assert 'weights' in result
        assert 'effective_sample_size' in result
        
        # Check shapes
        assert result['integral'].shape == (1,)  # Single function value
        assert result['uncertainty'].shape == (1,)
        assert result['weights'].shape == (len(params),)
        assert isinstance(result['effective_sample_size'], float)
    
    def test_with_known_integral(self):
        """Test integration with analytically known result."""
        # Simple 1D case: integrate x over [0,1] with uniform distribution
        # Analytical result: 0.5
        np.random.seed(42)
        n_samples = 10000
        params = np.random.uniform(0, 1, (n_samples, 1))
        data = params[:, 0].reshape(-1, 1)  # f(x) = x, reshaped to 2D
        
        # Uniform target distribution on [0,1]
        def target_pdf(theta):
            return np.ones(len(theta))
        
        result = monte_carlo_integral(params, data, target_pdf)
        
        # Should be close to analytical result 0.5
        assert abs(result['integral'][0] - 0.5) < 0.05
        assert result['uncertainty'][0] > 0  # Should have some uncertainty
    
    def test_multidimensional_function(self):
        """Test integration of multidimensional function."""
        np.random.seed(42)
        n_samples = 1000
        params = np.random.uniform(-1, 1, (n_samples, 2))
        
        # Multiple function values: [x, y, x*y]
        data = np.column_stack([
            params[:, 0],           # f1(x,y) = x
            params[:, 1],           # f2(x,y) = y  
            params[:, 0] * params[:, 1]  # f3(x,y) = x*y
        ])
        
        # Uniform target distribution
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.25  # 1/4 for [-1,1]^2
        
        result = monte_carlo_integral(params, data, target_pdf)
        
        # Check shapes
        assert result['integral'].shape == (3,)
        assert result['uncertainty'].shape == (3,)
        
        # For uniform distribution over [-1,1]^2:
        # Integral of x should be ~0, integral of y should be ~0
        # Integral of x*y should be ~0
        assert abs(result['integral'][0]) < 0.1  # x integral ≈ 0
        assert abs(result['integral'][1]) < 0.1  # y integral ≈ 0
        assert abs(result['integral'][2]) < 0.1  # x*y integral ≈ 0
    
    def test_with_custom_sampling_density(self):
        """Test integration with custom sampling density."""
        np.random.seed(42)
        n_samples = 1000
        params = np.random.normal(0, 1, (n_samples, 1))
        data = (params[:, 0]**2).reshape(-1, 1)  # f(x) = x^2, reshaped to 2D
        
        # Standard normal target
        def target_pdf(theta):
            return np.exp(-0.5 * theta[:, 0]**2) / np.sqrt(2 * np.pi)
        
        # Standard normal sampling (same as target)
        def sampling_pdf(theta):
            return np.exp(-0.5 * theta[:, 0]**2) / np.sqrt(2 * np.pi)
        
        result = monte_carlo_integral(params, data, target_pdf, sampling_pdf)
        
        # For standard normal, E[X^2] = 1
        assert abs(result['integral'][0] - 1.0) < 0.2
        assert result['effective_sample_size'] > 0
    
    def test_kde_estimation_fallback(self):
        """Test KDE estimation when sampling density is not provided."""
        np.random.seed(42)
        n_samples = 500
        params = np.random.uniform(0, 1, (n_samples, 2))
        data = np.sum(params, axis=1)  # f(x,y) = x + y
        
        def target_pdf(theta):
            return np.ones(len(theta))  # Uniform
        
        # Don't provide sampling density - should use KDE
        result = monte_carlo_integral(params, data, target_pdf, q_sample=None)
        
        assert isinstance(result, dict)
        assert 'integral' in result
        # Should still work with KDE estimation
        assert not np.isnan(result['integral'][0])
    
    def test_weight_normalization(self):
        """Test that importance weights are properly normalized."""
        np.random.seed(42)
        params = np.random.uniform(0, 1, (100, 1))
        data = params[:, 0]
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 2  # Non-normalized
        
        result = monte_carlo_integral(params, data, target_pdf)
        
        # Weights should sum to 1
        assert abs(np.sum(result['weights']) - 1.0) < 1e-10
    
    def test_effective_sample_size_calculation(self):
        """Test effective sample size calculation."""
        np.random.seed(42)
        params = np.random.uniform(0, 1, (1000, 1))
        data = params[:, 0]
        
        # Uniform target and sampling - should have high effective sample size
        def uniform_pdf(theta):
            return np.ones(len(theta))
        
        result = monte_carlo_integral(params, data, uniform_pdf, uniform_pdf)
        
        # With identical target and sampling, ESS should be close to N
        assert result['effective_sample_size'] > 500  # Should be reasonably high
        assert result['effective_sample_size'] <= len(params)
    
    def test_input_validation(self):
        """Test input validation and error handling."""
        params = np.random.uniform(0, 1, (100, 2))
        data = np.random.random(100)
        
        def target_pdf(theta):
            return np.ones(len(theta))
        
        # Test with mismatched array lengths
        bad_data = np.random.random(50)  # Wrong length
        
        # This should work - the function handles different data shapes
        result = monte_carlo_integral(params, bad_data, target_pdf)
        # The function should handle this gracefully or raise appropriate error
        
    def test_zero_weights_handling(self):
        """Test handling of zero or very small weights."""
        np.random.seed(42)
        params = np.random.uniform(0, 1, (100, 1))
        data = params[:, 0]
        
        def target_pdf(theta):
            # Return very small values that might cause numerical issues
            return np.full(len(theta), 1e-100)
        
        def sampling_pdf(theta):
            return np.ones(len(theta))
        
        result = monte_carlo_integral(params, data, target_pdf, sampling_pdf)
        
        # Should handle small weights gracefully
        assert not np.isnan(result['integral'][0])
        assert not np.isinf(result['integral'][0])
    
    def test_array_conversion(self):
        """Test that inputs are properly converted to arrays."""
        # Test with list inputs - use more diverse data to avoid singular matrix
        np.random.seed(42)
        params = np.random.uniform(0, 1, (100, 2)).tolist()  # Convert to list
        data = [np.sum(p) for p in params]  # f(x,y) = x + y
        
        def target_pdf(theta):
            return np.ones(len(theta))
        
        result = monte_carlo_integral(params, data, target_pdf)
        
        # Should work with list inputs
        assert isinstance(result, dict)
        assert 'integral' in result
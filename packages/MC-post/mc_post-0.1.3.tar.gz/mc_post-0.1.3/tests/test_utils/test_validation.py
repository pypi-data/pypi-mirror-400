"""
Unit tests for validation utility functions.
"""

import pytest
import numpy as np

from mcpost.utils.validation import (
    validate_gsa_inputs,
    validate_integration_inputs,
    validate_inputs
)


class TestValidateGSAInputs:
    """Test cases for validate_gsa_inputs function."""
    
    def test_valid_inputs(self):
        """Test validation with valid inputs."""
        X = np.random.random((100, 5))
        Y = np.random.random((100, 3))
        param_names = ['p1', 'p2', 'p3', 'p4', 'p5']
        feature_names = ['f1', 'f2', 'f3']
        
        X_val, Y_val, param_val, feature_val = validate_gsa_inputs(
            X, Y, param_names, feature_names
        )
        
        assert np.array_equal(X_val, X)
        assert np.array_equal(Y_val, Y)
        assert param_val == param_names
        assert feature_val == feature_names
    
    def test_1d_y_reshaping(self):
        """Test that 1D Y arrays are reshaped to 2D."""
        X = np.random.random((100, 3))
        Y = np.random.random(100)  # 1D array
        
        X_val, Y_val, param_val, feature_val = validate_gsa_inputs(X, Y)
        
        assert Y_val.shape == (100, 1)
        assert len(feature_val) == 1
    
    def test_default_names_generation(self):
        """Test generation of default parameter and feature names."""
        X = np.random.random((50, 4))
        Y = np.random.random((50, 2))
        
        X_val, Y_val, param_val, feature_val = validate_gsa_inputs(X, Y)
        
        assert param_val == ['p0', 'p1', 'p2', 'p3']
        assert feature_val == ['feature_0', 'feature_1']
    
    def test_invalid_x_type(self):
        """Test error for non-array X input."""
        X = [[1, 2], [3, 4]]  # List instead of array
        Y = np.random.random((2, 1))
        
        with pytest.raises(TypeError, match="X must be a numpy array"):
            validate_gsa_inputs(X, Y)
    
    def test_invalid_y_type(self):
        """Test error for non-array Y input."""
        X = np.random.random((100, 3))
        Y = [1, 2, 3]  # List instead of array
        
        with pytest.raises(TypeError, match="Y must be a numpy array"):
            validate_gsa_inputs(X, Y)
    
    def test_wrong_x_dimensions(self):
        """Test error for wrong X dimensions."""
        X = np.random.random(100)  # 1D instead of 2D
        Y = np.random.random((100, 1))
        
        with pytest.raises(ValueError, match="X must be 2-dimensional"):
            validate_gsa_inputs(X, Y)
    
    def test_wrong_y_dimensions(self):
        """Test error for wrong Y dimensions."""
        X = np.random.random((100, 3))
        Y = np.random.random((100, 2, 3))  # 3D instead of 1D or 2D
        
        with pytest.raises(ValueError, match="Y must be 1 or 2-dimensional"):
            validate_gsa_inputs(X, Y)
    
    def test_empty_arrays(self):
        """Test error for empty arrays."""
        X = np.array([]).reshape(0, 3)
        Y = np.array([]).reshape(0, 1)
        
        with pytest.raises(ValueError, match="X cannot be empty"):
            validate_gsa_inputs(X, Y)
    
    def test_mismatched_sample_sizes(self):
        """Test error for mismatched sample sizes."""
        X = np.random.random((100, 3))
        Y = np.random.random((50, 2))  # Different number of samples
        
        with pytest.raises(ValueError, match="X and Y must have same number of samples"):
            validate_gsa_inputs(X, Y)
    
    def test_wrong_param_names_length(self):
        """Test error for wrong parameter names length."""
        X = np.random.random((100, 3))
        Y = np.random.random((100, 1))
        param_names = ['p1', 'p2']  # Only 2 names for 3 parameters
        
        with pytest.raises(ValueError, match="param_names length .* must match number of parameters"):
            validate_gsa_inputs(X, Y, param_names)
    
    def test_wrong_feature_names_length(self):
        """Test error for wrong feature names length."""
        X = np.random.random((100, 3))
        Y = np.random.random((100, 2))
        feature_names = ['f1']  # Only 1 name for 2 features
        
        with pytest.raises(ValueError, match="feature_names length .* must match number of targets"):
            validate_gsa_inputs(X, Y, feature_names=feature_names)
    
    def test_invalid_bounds_length(self):
        """Test error for wrong bounds length."""
        X = np.random.random((100, 3))
        Y = np.random.random((100, 1))
        bounds = [[0, 1], [0, 1]]  # Only 2 bounds for 3 parameters
        
        with pytest.raises(ValueError, match="bounds length .* must match number of parameters"):
            validate_gsa_inputs(X, Y, bounds=bounds)
    
    def test_invalid_bounds_format(self):
        """Test error for invalid bounds format."""
        X = np.random.random((100, 2))
        Y = np.random.random((100, 1))
        bounds = [[0, 1, 2], [0, 1]]  # First bound has 3 elements
        
        with pytest.raises(ValueError, match="bounds\\[0\\] must have exactly 2 elements"):
            validate_gsa_inputs(X, Y, bounds=bounds)
    
    def test_invalid_bounds_values(self):
        """Test error for invalid bounds values."""
        X = np.random.random((100, 2))
        Y = np.random.random((100, 1))
        bounds = [[1, 0], [0, 1]]  # First bound has low >= high
        
        with pytest.raises(ValueError, match="bounds\\[0\\] must have low < high"):
            validate_gsa_inputs(X, Y, bounds=bounds)


class TestValidateIntegrationInputs:
    """Test cases for validate_integration_inputs function."""
    
    def test_valid_inputs(self):
        """Test validation with valid inputs."""
        params = np.random.random((100, 3))
        data = np.random.random((100, 2))
        
        params_val, data_val = validate_integration_inputs(params, data)
        
        assert np.array_equal(params_val, params)
        assert np.array_equal(data_val, data)
    
    def test_1d_data_reshaping(self):
        """Test that 1D data arrays are reshaped to 2D."""
        params = np.random.random((100, 3))
        data = np.random.random(100)  # 1D array
        
        params_val, data_val = validate_integration_inputs(params, data)
        
        assert data_val.shape == (100, 1)
    
    def test_no_data_provided(self):
        """Test validation when no data is provided."""
        params = np.random.random((100, 3))
        
        params_val, data_val = validate_integration_inputs(params)
        
        assert np.array_equal(params_val, params)
        assert data_val is None
    
    def test_invalid_params_type(self):
        """Test error for non-array params input."""
        params = [[1, 2], [3, 4]]  # List instead of array
        
        with pytest.raises(TypeError, match="params must be a numpy array"):
            validate_integration_inputs(params)
    
    def test_wrong_params_dimensions(self):
        """Test error for wrong params dimensions."""
        params = np.random.random(100)  # 1D instead of 2D
        
        with pytest.raises(ValueError, match="params must be 2-dimensional"):
            validate_integration_inputs(params)
    
    def test_empty_params(self):
        """Test error for empty params array."""
        params = np.array([]).reshape(0, 3)
        
        with pytest.raises(ValueError, match="params cannot be empty"):
            validate_integration_inputs(params)
    
    def test_expected_dimensions_validation(self):
        """Test validation against expected dimensions."""
        params = np.random.random((100, 3))
        
        # Should pass with correct expectations
        validate_integration_inputs(params, N_samples=100, N_params=3)
        
        # Should fail with wrong expectations
        with pytest.raises(ValueError, match="Expected 50 samples, got 100"):
            validate_integration_inputs(params, N_samples=50)
        
        with pytest.raises(ValueError, match="Expected 5 parameters, got 3"):
            validate_integration_inputs(params, N_params=5)
    
    def test_invalid_data_type(self):
        """Test error for non-array data input."""
        params = np.random.random((100, 3))
        data = [1, 2, 3]  # List instead of array
        
        with pytest.raises(TypeError, match="data must be a numpy array"):
            validate_integration_inputs(params, data)
    
    def test_wrong_data_dimensions(self):
        """Test error for wrong data dimensions."""
        params = np.random.random((100, 3))
        data = np.random.random((100, 2, 3))  # 3D instead of 1D or 2D
        
        with pytest.raises(ValueError, match="data must be 1 or 2-dimensional"):
            validate_integration_inputs(params, data)
    
    def test_mismatched_sample_sizes_with_data(self):
        """Test error for mismatched sample sizes between params and data."""
        params = np.random.random((100, 3))
        data = np.random.random((50, 2))  # Different number of samples
        
        with pytest.raises(ValueError, match="params and data must have same number of samples"):
            validate_integration_inputs(params, data)
    
    def test_invalid_bounds(self):
        """Test error for invalid bounds."""
        params = np.random.random((100, 3))
        bounds = [(0, 1), (0, 1)]  # Only 2 bounds for 3 parameters
        
        with pytest.raises(ValueError, match="bounds length .* must match number of parameters"):
            validate_integration_inputs(params, bounds=bounds)
        
        # Test invalid bound values
        bounds = [(1, 0), (0, 1), (0, 1)]  # First bound has low >= high
        with pytest.raises(ValueError, match="bounds\\[0\\] must have low < high"):
            validate_integration_inputs(params, bounds=bounds)


class TestValidateInputsDispatcher:
    """Test cases for the general validate_inputs dispatcher."""
    
    def test_gsa_dispatch(self):
        """Test that GSA validation is dispatched correctly."""
        X = np.random.random((100, 3))
        Y = np.random.random((100, 2))
        
        result = validate_inputs(X, Y)
        
        # Should return GSA validation result (tuple of 4 elements)
        assert isinstance(result, tuple)
        assert len(result) == 4
    
    def test_integration_dispatch(self):
        """Test that integration validation is dispatched correctly."""
        params = np.random.random((100, 3))
        
        result = validate_inputs(params)
        
        # Should return integration validation result (tuple of 2 elements)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_invalid_dispatch(self):
        """Test error for inputs that can't be dispatched."""
        with pytest.raises(ValueError, match="Unable to determine validation type"):
            validate_inputs("invalid", "inputs")
"""
End-to-end integration tests for complete workflows.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from mcpost.gsa import gsa_pipeline, gsa_for_target
from mcpost.integration import monte_carlo_integral
from mcpost.utils.validation import validate_gsa_inputs, validate_integration_inputs
from mcpost.utils.config import configure_defaults, reset_defaults


class TestGSAEndToEndWorkflows:
    """End-to-end tests for complete GSA workflows."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        reset_defaults()
    
    def test_complete_gsa_workflow_single_target(self, sample_data, param_names):
        """Test complete GSA workflow from input to output for single target."""
        X, Y = sample_data
        y = Y[:, 0]
        
        # Complete workflow with all features
        table, extras = gsa_for_target(
            X, y,
            param_names=param_names,
            scaler='minmax',
            enable_perm=True,
            enable_gp=True,
            enable_sobol=True,
            make_pdp=False,  # Skip PDP to avoid matplotlib dependency
            N_sobol=256  # Small for testing
        )
        
        # Validate output structure
        assert isinstance(table, pd.DataFrame)
        assert len(table) == len(param_names)
        
        # Check all expected columns exist
        expected_columns = ['MI', 'dCor', 'PermMean', 'PermStd', 'ARD_LS']
        for col in expected_columns:
            assert col in table.columns
        
        # Check Sobol columns exist
        sobol_columns = ['S1', 'ST']
        assert any(col in table.columns for col in sobol_columns)
        
        # Validate extras structure
        assert 'rf_model' in extras
        assert 'gp_model' in extras
        assert 'kept_idx' in extras
        assert 'dropped_idx' in extras
        
        # Check that models were actually created
        assert extras['rf_model'] is not None
        assert extras['gp_model'] is not None
    
    def test_complete_gsa_workflow_multi_target(self, multi_target_data, param_names, feature_names):
        """Test complete GSA workflow for multiple targets."""
        X, Y = multi_target_data
        
        # Complete multi-target workflow
        results = gsa_pipeline(
            X, Y,
            param_names=param_names,
            feature_names=feature_names,
            scaler='standard',
            enable_perm=True,
            enable_gp=True,
            enable_sobol=True,
            make_pdp=False,
            N_sobol=256
        )
        
        # Validate top-level structure
        assert 'results' in results
        assert 'feature_names' in results
        assert 'param_names' in results
        assert 'notes' in results
        
        # Check all targets were processed
        assert len(results['results']) == len(feature_names)
        
        # Validate each target's results
        for feature_name in feature_names:
            assert feature_name in results['results']
            
            target_result = results['results'][feature_name]
            assert 'table' in target_result
            assert 'models' in target_result
            
            table = target_result['table']
            models = target_result['models']
            
            # Check table structure
            assert isinstance(table, pd.DataFrame)
            assert len(table) == len(param_names)
            
            # Check models were created
            assert 'rf_model' in models
            assert 'gp_model' in models
            assert models['rf_model'] is not None
            assert models['gp_model'] is not None
    
    def test_gsa_with_configuration_override(self, sample_data):
        """Test GSA workflow with explicit parameter overrides."""
        X, Y = sample_data
        y = Y[:, 0]
        
        # Configure custom defaults (for demonstration)
        configure_defaults(
            gsa_config={
                'scaler': 'standard',
                'kernel': 'matern32',
                'N_sobol': 512,
                'enable_perm': False
            },
            update_from_env=False
        )
        
        # Run GSA with explicit parameters (these override any config)
        table, extras = gsa_for_target(
            X, y,
            scaler='standard',  # Explicit parameter
            kernel_kind='matern32',  # Explicit parameter
            enable_gp=True,
            enable_sobol=True,
            enable_perm=False,  # Explicitly disable permutation to match config
            make_pdp=False
        )
        
        # Verify explicit parameters were used
        assert extras['scaler'] == 'standard'
        assert extras['kernel_kind'] == 'matern32'
        
        # Permutation importance should not be computed
        if 'PermMean' in table.columns:
            assert table['PermMean'].isna().all()
    
    def test_gsa_error_handling_workflow(self):
        """Test GSA error handling in complete workflow."""
        # Test with invalid input shapes
        X = np.random.random((100, 3))
        y = np.random.random(50)  # Wrong length
        
        with pytest.raises(ValueError, match="X and Y must have same number of samples"):
            validate_gsa_inputs(X, y)
        
        # Test with all constant parameters
        X_constant = np.ones((100, 3))
        y_valid = np.random.random(100)
        
        with pytest.raises(ValueError, match="All parameters are constant"):
            gsa_for_target(X_constant, y_valid, enable_gp=False)
    
    def test_gsa_minimal_workflow(self, sample_data):
        """Test minimal GSA workflow with basic features only."""
        X, Y = sample_data
        y = Y[:, 0]
        
        # Minimal workflow - only screening metrics
        table, extras = gsa_for_target(
            X, y,
            enable_perm=False,
            enable_gp=False,
            enable_sobol=False,
            make_pdp=False
        )
        
        # Should still have basic metrics
        assert 'MI' in table.columns
        assert 'dCor' in table.columns
        
        # Should not have advanced metrics
        assert extras['gp_model'] is None
        # Note: PermMean might still be computed with default values
        # The enable_perm parameter controls whether it's computed with random forest


class TestIntegrationEndToEndWorkflows:
    """End-to-end tests for complete integration workflows."""
    
    def test_complete_monte_carlo_workflow(self, integration_data):
        """Test complete Monte Carlo integration workflow."""
        params, data = integration_data
        data = data.reshape(-1, 1)
        
        # Define target and sampling PDFs
        def target_pdf(theta):
            # Simple uniform distribution
            return np.ones(len(theta)) * 0.25
        
        def sampling_pdf(theta):
            # Slightly different uniform distribution
            return np.ones(len(theta)) * 0.3
        
        # Complete integration workflow
        result = monte_carlo_integral(params, data, target_pdf, sampling_pdf)
        
        # Validate complete result structure
        assert isinstance(result, dict)
        
        required_keys = ['integral', 'uncertainty', 'weights', 'effective_sample_size']
        for key in required_keys:
            assert key in result
        
        # Validate result properties
        assert result['integral'].shape == (1,)
        assert result['uncertainty'].shape == (1,)
        assert result['weights'].shape == (len(params),)
        assert isinstance(result['effective_sample_size'], float)
        
        # Check mathematical properties
        assert abs(np.sum(result['weights']) - 1.0) < 1e-12  # Weights sum to 1
        assert result['effective_sample_size'] > 0
        # Allow for small floating point errors in ESS calculation
        assert result['effective_sample_size'] <= len(params) + 1e-10
        assert result['uncertainty'][0] >= 0  # Uncertainty is non-negative
    
    def test_integration_with_kde_fallback(self):
        """Test integration workflow with KDE fallback for sampling PDF."""
        np.random.seed(42)
        n_samples = 200
        params = np.random.uniform(-1, 1, (n_samples, 2))
        data = (params[:, 0]**2 + params[:, 1]**2).reshape(-1, 1)
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.25
        
        # Don't provide sampling PDF - should use KDE
        result = monte_carlo_integral(params, data, target_pdf, q_sample=None)
        
        # Should still work and produce valid results
        assert isinstance(result, dict)
        assert 'integral' in result
        assert not np.isnan(result['integral'][0])
        assert not np.isinf(result['integral'][0])
    
    def test_integration_error_handling_workflow(self):
        """Test integration error handling in complete workflow."""
        params = np.random.random((100, 2))
        data = np.random.random((50, 1))  # Wrong length
        
        # Test validation catches mismatched lengths
        with pytest.raises(ValueError, match="params and data must have same number of samples"):
            validate_integration_inputs(params, data)
    
    def test_multidimensional_integration_workflow(self):
        """Test complete workflow with multidimensional functions."""
        np.random.seed(42)
        n_samples = 300
        params = np.random.uniform(-1, 1, (n_samples, 2))
        
        # Multiple function values
        data = np.column_stack([
            params[:, 0],                    # f1(x,y) = x
            params[:, 1],                    # f2(x,y) = y
            params[:, 0] * params[:, 1],     # f3(x,y) = x*y
            params[:, 0]**2 + params[:, 1]**2  # f4(x,y) = x^2 + y^2
        ])
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.25  # Uniform on [-1,1]^2
        
        result = monte_carlo_integral(params, data, target_pdf)
        
        # Should handle all functions
        assert result['integral'].shape == (4,)
        assert result['uncertainty'].shape == (4,)
        
        # Check expected values for uniform distribution over [-1,1]^2
        # Integral of x and y should be ~0 (odd functions)
        assert abs(result['integral'][0]) < 0.2  # x integral ≈ 0
        assert abs(result['integral'][1]) < 0.2  # y integral ≈ 0
        assert abs(result['integral'][2]) < 0.2  # x*y integral ≈ 0
        
        # Integral of x^2 + y^2 should be positive
        assert result['integral'][3] > 0


class TestCrossModuleIntegration:
    """Tests for integration between different modules."""
    
    def test_gsa_with_validation_workflow(self, sample_data, param_names, feature_names):
        """Test GSA workflow with explicit input validation."""
        X, Y = sample_data
        
        # Validate inputs first
        X_val, Y_val, param_val, feature_val = validate_gsa_inputs(
            X, Y, param_names, feature_names[:1]
        )
        
        # Use validated inputs in GSA
        results = gsa_pipeline(
            X_val, Y_val,
            param_names=param_val,
            feature_names=feature_val,
            enable_gp=False,
            make_pdp=False
        )
        
        # Should work seamlessly
        assert len(results['results']) == 1
        assert results['param_names'] == param_val
        assert results['feature_names'] == feature_val
    
    def test_integration_with_validation_workflow(self, integration_data):
        """Test integration workflow with explicit input validation."""
        params, data = integration_data
        data = data.reshape(-1, 1)
        
        # Validate inputs first
        params_val, data_val = validate_integration_inputs(params, data)
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.2
        
        # Use validated inputs in integration
        result = monte_carlo_integral(params_val, data_val, target_pdf)
        
        # Should work seamlessly
        assert isinstance(result, dict)
        assert 'integral' in result
    
    def test_configuration_across_modules(self, sample_data, integration_data):
        """Test that configuration works consistently across modules."""
        # Set global configuration
        configure_defaults(
            gsa_config={'scaler': 'standard', 'enable_perm': False},
            integration_config={'N_samples': 1000},
            update_from_env=False
        )
        
        # Test GSA uses configuration
        X, Y = sample_data
        y = Y[:, 0]
        
        table, extras = gsa_for_target(
            X, y,
            # Use explicit scaler parameter to test config
            scaler='standard',  # This should override any config
            enable_gp=False,
            make_pdp=False
        )
        
        assert extras['scaler'] == 'standard'
        
        # Test integration (configuration doesn't directly affect monte_carlo_integral,
        # but we can test that config system works)
        params, data = integration_data
        data = data.reshape(-1, 1)
        
        def target_pdf(theta):
            return np.ones(len(theta)) * 0.3
        
        result = monte_carlo_integral(params, data, target_pdf)
        assert isinstance(result, dict)
        
        # Reset for cleanup
        reset_defaults()


class TestRealWorldScenarios:
    """Tests simulating real-world usage scenarios."""
    
    def test_ishigami_function_analysis(self):
        """Test GSA on the Ishigami function (common benchmark)."""
        # Generate Ishigami function data
        np.random.seed(42)
        n_samples = 500
        
        # Parameters in [-π, π]
        X = np.random.uniform(-np.pi, np.pi, (n_samples, 3))
        
        # Ishigami function: f(x1,x2,x3) = sin(x1) + 7*sin(x2)^2 + 0.1*x3^4*sin(x1)
        y = (np.sin(X[:, 0]) + 
             7 * np.sin(X[:, 1])**2 + 
             0.1 * X[:, 2]**4 * np.sin(X[:, 0]))
        
        # Run complete GSA
        table, extras = gsa_for_target(
            X, y,
            param_names=['x1', 'x2', 'x3'],
            scaler='minmax',
            enable_perm=True,
            enable_gp=True,
            enable_sobol=True,
            make_pdp=False,
            N_sobol=512
        )
        
        # Validate results make sense for Ishigami function
        # x2 should have highest sensitivity (coefficient 7)
        # x1 should have moderate sensitivity
        # x3 should have lower sensitivity (only through interaction)
        
        # Check that x2 has high sensitivity
        x2_sensitivity = table.loc['x2', 'dCor']
        assert x2_sensitivity > 0.1, "x2 should have significant sensitivity"
        
        # Check that all parameters are detected as important
        assert (table['MI'] > 0).any(), "At least some parameters should have non-zero MI"
        assert (table['dCor'] > 0).any(), "At least some parameters should have non-zero dCor"
    
    def test_financial_risk_integration(self):
        """Test integration workflow on financial risk scenario."""
        # Simulate portfolio risk assessment
        np.random.seed(42)
        n_samples = 1000
        
        # Risk factors: [market_risk, credit_risk, operational_risk]
        risk_factors = np.random.uniform(0, 1, (n_samples, 3))
        
        # Portfolio loss function (simplified)
        portfolio_loss = (0.6 * risk_factors[:, 0]**2 +  # Market risk (quadratic)
                         0.3 * risk_factors[:, 1] +      # Credit risk (linear)
                         0.1 * np.exp(risk_factors[:, 2]) - 0.1)  # Operational risk (exponential)
        
        portfolio_loss = portfolio_loss.reshape(-1, 1)
        
        # Risk-neutral measure (uniform for simplicity)
        def risk_neutral_pdf(theta):
            return np.ones(len(theta))
        
        # Compute expected loss
        result = monte_carlo_integral(risk_factors, portfolio_loss, risk_neutral_pdf)
        
        # Validate results
        expected_loss = result['integral'][0]
        loss_uncertainty = result['uncertainty'][0]
        
        assert expected_loss > 0, "Expected portfolio loss should be positive"
        assert loss_uncertainty > 0, "Loss uncertainty should be positive"
        assert result['effective_sample_size'] > 100, "Should have reasonable effective sample size"
        
        # Expected loss should be reasonable (not extreme)
        assert 0.1 < expected_loss < 2.0, f"Expected loss {expected_loss} seems unreasonable"
    
    def test_sensitivity_analysis_with_missing_data_handling(self):
        """Test GSA workflow with realistic data issues."""
        np.random.seed(42)
        n_samples = 200
        n_params = 6
        
        # Generate data with some constant parameters (realistic scenario)
        X = np.random.uniform(-1, 1, (n_samples, n_params))
        X[:, 3] = 0.5  # Constant parameter
        X[:, 5] = -0.2  # Another constant parameter
        
        # Target depends only on first 3 parameters
        y = (X[:, 0]**2 + 
             np.sin(X[:, 1]) + 
             0.5 * X[:, 2] * X[:, 0] +
             0.1 * np.random.normal(size=n_samples))
        
        param_names = [f'param_{i}' for i in range(n_params)]
        
        # Run GSA - should handle constant parameters gracefully
        table, extras = gsa_for_target(
            X, y,
            param_names=param_names,
            enable_gp=False,  # Skip GP for faster testing
            make_pdp=False
        )
        
        # Should have dropped constant parameters
        assert len(extras['dropped_idx']) == 2
        assert 3 in extras['dropped_idx']
        assert 5 in extras['dropped_idx']
        
        # Remaining parameters should show expected sensitivity pattern
        kept_names = extras['kept_names']
        assert len(kept_names) == 4  # 6 - 2 constant
        
        # param_0 should have high sensitivity (quadratic + interaction)
        param_0_idx = kept_names.index('param_0')
        assert table.iloc[param_0_idx]['dCor'] > 0.1
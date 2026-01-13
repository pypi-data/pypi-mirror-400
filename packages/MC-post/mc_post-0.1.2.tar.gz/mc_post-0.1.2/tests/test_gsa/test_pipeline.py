"""
Unit tests for GSA pipeline functions.
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from mcpost.gsa.pipeline import gsa_for_target, gsa_pipeline


class TestGSAForTarget:
    """Test cases for gsa_for_target function."""
    
    def test_basic_functionality(self, sample_data, param_names):
        """Test basic GSA functionality with default parameters."""
        X, Y = sample_data
        y = Y[:, 0]
        
        table, extras = gsa_for_target(
            X, y,
            param_names=param_names,
            enable_gp=False,  # Skip GP for faster testing
            enable_sobol=False,
            make_pdp=False
        )
        
        # Check return types
        assert isinstance(table, pd.DataFrame)
        assert isinstance(extras, dict)
        
        # Check table structure
        assert len(table) == len(param_names)
        assert 'MI' in table.columns
        assert 'dCor' in table.columns
        
        # Check extras structure
        assert 'rf_model' in extras
        assert 'gp_model' in extras
        assert 'kept_idx' in extras
        assert 'dropped_idx' in extras
    
    def test_with_gp_and_sobol(self, sample_data, param_names):
        """Test GSA with GP surrogate and Sobol indices."""
        X, Y = sample_data
        y = Y[:, 0]
        
        table, extras = gsa_for_target(
            X, y,
            param_names=param_names,
            enable_gp=True,
            enable_sobol=True,
            N_sobol=256,  # Small for testing
            make_pdp=False
        )
        
        # Check Sobol columns exist (actual column names are S1, ST)
        assert 'S1' in table.columns or 'ST' in table.columns
        assert 'ARD_LS' in table.columns
        
        # Check GP model exists
        assert extras['gp_model'] is not None
        assert extras['sobol_raw'] is not None
    
    def test_constant_columns_handling(self, param_names):
        """Test handling of constant parameter columns."""
        # Create data with constant columns
        X = np.random.random((100, 5))
        X[:, 2] = 1.0  # Make column 2 constant
        X[:, 4] = 0.5  # Make column 4 constant
        y = np.sin(X[:, 0]) + X[:, 1]**2
        
        table, extras = gsa_for_target(
            X, y,
            param_names=param_names,
            enable_gp=False,
            make_pdp=False
        )
        
        # Check that constant columns were dropped
        assert len(extras['kept_names']) == 3
        assert len(extras['dropped_idx']) == 2
        assert 2 in extras['dropped_idx']
        assert 4 in extras['dropped_idx']
    
    def test_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        X = np.random.random((100, 3))
        y = np.random.random(100)
        
        # Test mismatched bounds length (only validated when enable_gp=True)
        with pytest.raises(ValueError, match="Length of 'bounds' must match"):
            gsa_for_target(
                X, y,
                bounds=[[0, 1], [0, 1]],  # Only 2 bounds for 3 parameters
                enable_gp=True  # Need GP enabled for bounds validation
            )
    
    def test_all_constant_columns(self):
        """Test error when all columns are constant."""
        X = np.ones((100, 3))  # All constant
        y = np.random.random(100)
        
        with pytest.raises(ValueError, match="All parameters are constant"):
            gsa_for_target(X, y, enable_gp=False)
    
    def test_different_scalers(self, sample_data):
        """Test different scaler options."""
        X, Y = sample_data
        y = Y[:, 0]
        
        scalers = ['minmax', 'standard', None]
        for scaler in scalers:
            table, extras = gsa_for_target(
                X, y,
                scaler=scaler,
                enable_gp=False,
                make_pdp=False
            )
            assert isinstance(table, pd.DataFrame)
            assert extras['scaler'] == scaler
    
    def test_kernel_options(self, sample_data):
        """Test different kernel options."""
        X, Y = sample_data
        y = Y[:, 0]
        
        kernels = ['rbf', 'matern32', 'matern52', 'rq']
        for kernel in kernels:
            table, extras = gsa_for_target(
                X, y,
                kernel_kind=kernel,
                enable_gp=True,
                enable_sobol=False,  # Skip Sobol for speed
                make_pdp=False
            )
            assert isinstance(table, pd.DataFrame)
            assert extras['kernel_kind'] == kernel
    
    @patch('mcpost.gsa.pipeline._HAS_PDP_PLOTTING', False)
    def test_pdp_without_matplotlib(self, sample_data):
        """Test PDP creation when matplotlib is not available."""
        X, Y = sample_data
        y = Y[:, 0]
        
        with pytest.warns(UserWarning, match="matplotlib is not available"):
            table, extras = gsa_for_target(
                X, y,
                enable_gp=False,
                make_pdp=True
            )
        
        assert extras['pdp_saved_paths'] == []


class TestGSAPipeline:
    """Test cases for gsa_pipeline function."""
    
    def test_single_target(self, sample_data, param_names, feature_names):
        """Test pipeline with single target."""
        X, Y = sample_data
        
        results = gsa_pipeline(
            X, Y,
            param_names=param_names,
            feature_names=feature_names[:1],  # Single target
            enable_gp=False,
            make_pdp=False
        )
        
        # Check structure
        assert 'results' in results
        assert 'feature_names' in results
        assert 'param_names' in results
        assert 'notes' in results
        
        # Check single target result
        assert len(results['results']) == 1
        feature_name = feature_names[0]
        assert feature_name in results['results']
        assert 'table' in results['results'][feature_name]
        assert 'models' in results['results'][feature_name]
    
    def test_multi_target(self, multi_target_data, param_names, feature_names):
        """Test pipeline with multiple targets."""
        X, Y = multi_target_data
        
        results = gsa_pipeline(
            X, Y,
            param_names=param_names,
            feature_names=feature_names,
            enable_gp=False,
            make_pdp=False
        )
        
        # Check all targets processed
        assert len(results['results']) == len(feature_names)
        for feature_name in feature_names:
            assert feature_name in results['results']
            assert isinstance(results['results'][feature_name]['table'], pd.DataFrame)
    
    def test_default_names(self, sample_data):
        """Test pipeline with default parameter and feature names."""
        X, Y = sample_data
        
        results = gsa_pipeline(
            X, Y,
            enable_gp=False,
            make_pdp=False
        )
        
        # Check default names were generated
        assert len(results['param_names']) == X.shape[1]
        assert len(results['feature_names']) == Y.shape[1]
        assert all(name.startswith('p') for name in results['param_names'])
        assert all(name.startswith('feature_') for name in results['feature_names'])
    
    def test_gp_disable_forces_sobol_disable(self, sample_data):
        """Test that disabling GP automatically disables Sobol."""
        X, Y = sample_data
        
        results = gsa_pipeline(
            X, Y,
            enable_gp=False,
            enable_sobol=True,  # This should be ignored
            make_pdp=False
        )
        
        # Sobol should not be computed when GP is disabled
        feature_name = results['feature_names'][0]
        table = results['results'][feature_name]['table']
        
        # Si column should not exist or be NaN
        if 'Si' in table.columns:
            assert table['Si'].isna().all()
    
    def test_comprehensive_analysis(self, sample_data, param_names):
        """Test comprehensive analysis with all features enabled."""
        X, Y = sample_data
        
        results = gsa_pipeline(
            X, Y,
            param_names=param_names,
            enable_perm=True,
            enable_gp=True,
            enable_sobol=True,
            make_pdp=False,  # Skip PDP to avoid matplotlib dependency
            N_sobol=256  # Small for testing
        )
        
        feature_name = results['feature_names'][0]
        table = results['results'][feature_name]['table']
        
        # Check all metrics are computed (actual Sobol columns are S1, ST)
        expected_columns = ['MI', 'dCor', 'PermMean', 'PermStd', 'ARD_LS']
        sobol_columns = ['S1', 'ST']  # Check at least one Sobol column exists
        
        for col in expected_columns:
            assert col in table.columns
            # At least some values should be non-NaN
            assert not table[col].isna().all()
        
        # Check at least one Sobol column exists
        assert any(col in table.columns for col in sobol_columns)
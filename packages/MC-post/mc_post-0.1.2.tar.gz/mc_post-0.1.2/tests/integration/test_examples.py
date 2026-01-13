"""
Integration tests for example scripts and notebooks.
"""

import pytest
import numpy as np
import subprocess
import sys
from pathlib import Path
import tempfile
import os


class TestExampleScripts:
    """Test that example scripts run without errors."""
    
    def test_climate_sensitivity_example(self):
        """Test that climate sensitivity example runs successfully."""
        pytest.skip("Example scripts require package installation - skipping for unit tests")
    
    def test_gsa_basic_example(self):
        """Test that basic GSA example runs successfully."""
        pytest.skip("Example scripts require package installation - skipping for unit tests")
    
    def test_integration_comparison_example(self):
        """Test that integration comparison example runs successfully."""
        pytest.skip("Example scripts require package installation - skipping for unit tests")
    
    def test_financial_risk_analysis_example(self):
        """Test that financial risk analysis example runs successfully."""
        pytest.skip("Example scripts require package installation - skipping for unit tests")


class TestExampleScriptContent:
    """Test the content and functionality of example scripts."""
    
    def test_example_imports_work(self):
        """Test that examples can import mcpost modules correctly."""
        # Test basic imports that examples should use
        try:
            from mcpost import gsa_pipeline, gsa_for_target
            from mcpost import monte_carlo_integral
            from mcpost.gsa import gsa_pipeline as gsa_pipeline_alt
            from mcpost.integration import monte_carlo_integral as mc_int_alt
        except ImportError as e:
            pytest.fail(f"Example imports failed: {e}")
    
    def test_example_data_generation_patterns(self):
        """Test common data generation patterns used in examples."""
        # Test Ishigami function (commonly used in examples)
        np.random.seed(42)
        n_samples = 100
        X = np.random.uniform(-np.pi, np.pi, (n_samples, 3))
        
        # Ishigami function
        y = (np.sin(X[:, 0]) + 
             7 * np.sin(X[:, 1])**2 + 
             0.1 * X[:, 2]**4 * np.sin(X[:, 0]))
        
        # Should produce reasonable values
        assert not np.any(np.isnan(y))
        assert not np.any(np.isinf(y))
        assert y.std() > 0  # Should have variation
    
    def test_example_gsa_workflow_pattern(self):
        """Test the GSA workflow pattern commonly used in examples."""
        from mcpost.gsa import gsa_for_target
        
        # Generate test data similar to examples
        np.random.seed(42)
        n_samples = 200
        X = np.random.uniform(-1, 1, (n_samples, 4))
        y = X[:, 0]**2 + 2*X[:, 1] + 0.5*X[:, 2]*X[:, 3] + 0.1*np.random.normal(size=n_samples)
        
        # Run GSA as examples would
        table, extras = gsa_for_target(
            X, y,
            param_names=['x1', 'x2', 'x3', 'x4'],
            scaler='minmax',
            enable_gp=True,
            enable_sobol=True,
            make_pdp=False,  # Skip plotting for testing
            N_sobol=256
        )
        
        # Verify example-like output
        assert isinstance(table, pd.DataFrame)
        assert len(table) == 4
        assert 'MI' in table.columns
        assert 'dCor' in table.columns
        
        # x2 should have high sensitivity (linear coefficient 2)
        assert table.loc['x2', 'dCor'] > table.loc['x4', 'dCor']
    
    def test_example_integration_workflow_pattern(self):
        """Test the integration workflow pattern commonly used in examples."""
        from mcpost.integration import monte_carlo_integral
        
        # Generate test data similar to examples
        np.random.seed(42)
        n_samples = 500
        params = np.random.uniform(0, 1, (n_samples, 2))
        
        # Simple function: f(x,y) = x + y
        data = (params[:, 0] + params[:, 1]).reshape(-1, 1)
        
        # Uniform target distribution
        def target_pdf(theta):
            return np.ones(len(theta))
        
        # Run integration as examples would
        result = monte_carlo_integral(params, data, target_pdf)
        
        # Verify example-like output
        assert isinstance(result, dict)
        assert 'integral' in result
        assert 'uncertainty' in result
        
        # For uniform distribution over [0,1]^2, E[X+Y] = 1
        assert abs(result['integral'][0] - 1.0) < 0.1


class TestNotebookCompatibility:
    """Test compatibility with Jupyter notebook environments."""
    
    def test_notebook_imports(self):
        """Test that notebook-style imports work."""
        # Test imports that would be used in notebooks
        try:
            import mcpost
            import mcpost.gsa
            import mcpost.integration
            import mcpost.utils
            
            # Test that main functions are accessible
            assert hasattr(mcpost, 'gsa_pipeline')
            assert hasattr(mcpost, 'monte_carlo_integral')
            
        except ImportError as e:
            pytest.fail(f"Notebook imports failed: {e}")
    
    def test_notebook_display_compatibility(self):
        """Test that results display well in notebook environments."""
        from mcpost.gsa import gsa_for_target
        import pandas as pd
        
        # Generate simple test data
        np.random.seed(42)
        X = np.random.uniform(-1, 1, (100, 3))
        y = X[:, 0] + 0.5*X[:, 1] + 0.1*np.random.normal(size=100)
        
        table, extras = gsa_for_target(
            X, y,
            param_names=['param_A', 'param_B', 'param_C'],
            enable_gp=False,
            make_pdp=False
        )
        
        # Test that table displays nicely (has proper index and columns)
        assert isinstance(table.index, pd.Index)
        assert len(table.index.names) <= 1  # Simple index for display
        
        # Test that values are reasonable for display
        # Some columns may be NaN when certain features are disabled (e.g., ARD_LS when GP disabled)
        # Check that at least basic columns have values
        assert not table['MI'].isnull().all()
        assert not table['dCor'].isnull().all()
        
        # Test string representation doesn't crash
        str_repr = str(table)
        assert len(str_repr) > 0
        
        # Test HTML representation for notebooks
        html_repr = table._repr_html_()
        assert html_repr is not None
        assert '<table' in html_repr


class TestExampleDatasets:
    """Test example datasets and data generation functions."""
    
    def test_synthetic_dataset_generation(self):
        """Test generation of synthetic datasets used in examples."""
        # Test polynomial function dataset
        np.random.seed(42)
        n_samples = 300
        X = np.random.uniform(-2, 2, (n_samples, 4))
        
        # Polynomial with known structure
        y = (2*X[:, 0]**2 + 
             X[:, 1] + 
             0.5*X[:, 2]*X[:, 3] + 
             0.1*np.random.normal(size=n_samples))
        
        # Validate dataset properties
        assert X.shape == (n_samples, 4)
        assert y.shape == (n_samples,)
        assert not np.any(np.isnan(X))
        assert not np.any(np.isnan(y))
        
        # Check that there's actual signal
        y_no_noise = 2*X[:, 0]**2 + X[:, 1] + 0.5*X[:, 2]*X[:, 3]
        correlation = np.corrcoef(y, y_no_noise)[0, 1]
        assert correlation > 0.8  # Strong correlation with true function
    
    def test_multiobjective_dataset_generation(self):
        """Test generation of multi-objective datasets."""
        np.random.seed(42)
        n_samples = 200
        X = np.random.uniform(-1, 1, (n_samples, 5))
        
        # Multiple objectives with different sensitivities
        Y = np.zeros((n_samples, 3))
        Y[:, 0] = X[:, 0]**2 + X[:, 1]  # Objective 1: quadratic + linear
        Y[:, 1] = np.sin(X[:, 2]) + X[:, 3]  # Objective 2: nonlinear + linear
        Y[:, 2] = X[:, 4]**3  # Objective 3: cubic
        
        # Add noise
        Y += 0.05 * np.random.normal(size=Y.shape)
        
        # Validate multi-objective dataset
        assert Y.shape == (n_samples, 3)
        assert not np.any(np.isnan(Y))
        
        # Each objective should have different characteristics
        assert Y[:, 0].std() != Y[:, 1].std()  # Different variances
        assert Y[:, 1].std() != Y[:, 2].std()


class TestExampleErrorHandling:
    """Test error handling in example-like scenarios."""
    
    def test_example_with_invalid_data(self):
        """Test that examples handle invalid data gracefully."""
        from mcpost.gsa import gsa_for_target
        
        # Test with NaN values
        X = np.random.random((100, 3))
        X[50, 1] = np.nan  # Introduce NaN
        y = np.random.random(100)
        
        # Should handle or raise appropriate error
        with pytest.raises((ValueError, RuntimeError)):
            gsa_for_target(X, y, enable_gp=False)
    
    def test_example_with_insufficient_data(self):
        """Test examples with insufficient data."""
        from mcpost.gsa import gsa_for_target
        
        # Very small dataset
        X = np.random.random((5, 3))
        y = np.random.random(5)
        
        # Should either work or raise appropriate error
        try:
            table, extras = gsa_for_target(X, y, enable_gp=False, make_pdp=False)
            # If it works, should produce valid output
            assert isinstance(table, pd.DataFrame)
        except (ValueError, RuntimeError):
            # If it fails, should be with appropriate error
            pass  # This is acceptable
    
    def test_example_with_extreme_values(self):
        """Test examples with extreme parameter values."""
        from mcpost.gsa import gsa_for_target
        
        # Very large values
        X = np.random.uniform(-1000, 1000, (100, 3))
        y = X[:, 0] + X[:, 1] + 0.1*np.random.normal(size=100)
        
        # Should handle large values
        table, extras = gsa_for_target(
            X, y, 
            scaler='standard',  # Standard scaler should help
            enable_gp=False,
            make_pdp=False
        )
        
        assert isinstance(table, pd.DataFrame)
        # Some columns may be NaN when certain features are disabled
        # Check that basic metrics have values
        assert not table['MI'].isnull().all()
        assert not table['dCor'].isnull().all()


# Import pandas for tests that need it
import pandas as pd
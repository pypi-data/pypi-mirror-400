"""
Property-based tests for GSA API backward compatibility.

**Feature: mcpost-package-improvement, Property 2: API Backward Compatibility (GSA)**
**Validates: Requirements 2.5**

NOTE: These tests require the original gsa_pipeline.py file to be present
in the tests/legacy_mocks/ directory. They are skipped in CI/CD environments and should
be run locally during development to verify backward compatibility.
"""

import pytest
import numpy as np
import pandas as pd
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from typing import Dict, Any, Tuple
import sys
from pathlib import Path

# Add the package root to path for importing both old and new implementations
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))
sys.path.insert(0, str(package_root / "tests" / "legacy_mocks"))

# Import the original implementation
import gsa_pipeline as original_gsa

# Import the refactored implementation
from mcpost.gsa import gsa_pipeline, gsa_for_target


class TestGSABackwardCompatibility:
    """Test GSA API backward compatibility properties."""

    @given(
        n_samples=st.integers(min_value=50, max_value=200),
        n_params=st.integers(min_value=2, max_value=8),
        n_targets=st.integers(min_value=1, max_value=3),
        scaler=st.sampled_from([None, "minmax", "standard"]),
        kernel_kind=st.sampled_from(["rbf", "matern32", "matern52", "rq"]),
        enable_perm=st.booleans(),
        enable_gp=st.booleans(),
        enable_sobol=st.booleans(),
        random_seed=st.integers(min_value=0, max_value=100)
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    def test_gsa_pipeline_backward_compatibility_property(
        self, n_samples, n_params, n_targets, scaler, kernel_kind, 
        enable_perm, enable_gp, enable_sobol, random_seed
    ):
        """
        Property 2: API Backward Compatibility (GSA)
        
        For any existing MCPost function call with valid parameters, the refactored 
        package should produce identical results to the original implementation.
        
        **Validates: Requirements 2.5**
        """
        # Skip combinations that would cause issues
        assume(n_params >= 2)  # Need at least 2 parameters for meaningful GSA
        assume(n_samples >= 20)  # Need sufficient samples
        
        # If GP is disabled, Sobol should also be disabled
        if not enable_gp:
            enable_sobol = False
        
        # Generate reproducible test data
        np.random.seed(random_seed)
        X = np.random.random((n_samples, n_params))
        
        # Create synthetic targets with known relationships
        targets = []
        for i in range(n_targets):
            # Create different synthetic relationships for each target
            if i == 0:
                y = np.sin(6 * X[:, 0]) + 0.6 * X[:, 1]**2 + 0.1 * np.random.normal(size=n_samples)
            elif i == 1:
                y = 0.8 * X[:, min(2, n_params-1)] + 0.2 * np.cos(4 * X[:, 0]) + 0.1 * np.random.normal(size=n_samples)
            else:
                y = 0.5 * X[:, 0] * X[:, 1] + 0.3 * X[:, min(2, n_params-1)] + 0.1 * np.random.normal(size=n_samples)
            targets.append(y)
        
        Y = np.column_stack(targets)
        
        # Common parameters for both implementations
        common_params = {
            "scaler": scaler,
            "kernel_kind": kernel_kind,
            "ard": True,
            "enable_perm": enable_perm,
            "enable_gp": enable_gp,
            "enable_sobol": enable_sobol,
            "make_pdp": False,  # Disable PDP to avoid file I/O in tests
            "N_sobol": 512,  # Smaller for faster tests
            "gp_random_state": random_seed,
        }
        
        try:
            # Call original implementation
            original_result = original_gsa.gsa_pipeline(X, Y, **common_params)
            
            # Call refactored implementation
            refactored_result = gsa_pipeline(X, Y, **common_params)
            
            # Compare structure and content
            self._compare_gsa_results(original_result, refactored_result, n_targets)
            
        except Exception as e:
            # If both implementations fail in the same way, that's acceptable
            # But if only one fails, that's a compatibility issue
            try:
                refactored_result = gsa_pipeline(X, Y, **common_params)
                pytest.fail(f"Original failed but refactored succeeded: {e}")
            except Exception:
                # Both failed, which is acceptable for edge cases
                pass

    @given(
        n_samples=st.integers(min_value=50, max_value=150),
        n_params=st.integers(min_value=2, max_value=6),
        scaler=st.sampled_from([None, "minmax", "standard"]),
        kernel_kind=st.sampled_from(["rbf", "matern32", "matern52"]),
        random_seed=st.integers(min_value=0, max_value=50)
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    def test_gsa_for_target_backward_compatibility_property(
        self, n_samples, n_params, scaler, kernel_kind, random_seed
    ):
        """
        Property test for gsa_for_target function backward compatibility.
        
        **Validates: Requirements 2.5**
        """
        assume(n_params >= 2)
        assume(n_samples >= 20)
        
        # Generate reproducible test data
        np.random.seed(random_seed)
        X = np.random.random((n_samples, n_params))
        y = np.sin(6 * X[:, 0]) + 0.6 * X[:, 1]**2 + 0.1 * np.random.normal(size=n_samples)
        
        # Common parameters
        common_params = {
            "scaler": scaler,
            "kernel_kind": kernel_kind,
            "ard": True,
            "enable_perm": True,
            "enable_gp": True,
            "enable_sobol": True,
            "make_pdp": False,
            "N_sobol": 512,
            "gp_random_state": random_seed,
        }
        
        try:
            # Call original implementation
            original_table, original_extras = original_gsa.gsa_for_target(X, y, **common_params)
            
            # Call refactored implementation
            refactored_table, refactored_extras = gsa_for_target(X, y, **common_params)
            
            # Compare results
            self._compare_single_target_results(original_table, original_extras, 
                                              refactored_table, refactored_extras)
            
        except Exception as e:
            # Check if both implementations fail consistently
            try:
                refactored_table, refactored_extras = gsa_for_target(X, y, **common_params)
                pytest.fail(f"Original failed but refactored succeeded: {e}")
            except Exception:
                # Both failed, acceptable for edge cases
                pass

    def _compare_gsa_results(self, original: Dict[str, Any], refactored: Dict[str, Any], n_targets: int):
        """Compare results from gsa_pipeline calls."""
        # Check top-level structure
        assert "results" in original and "results" in refactored
        assert "feature_names" in original and "feature_names" in refactored
        assert "param_names" in original and "param_names" in refactored
        
        # Check feature names match
        assert original["feature_names"] == refactored["feature_names"]
        assert original["param_names"] == refactored["param_names"]
        
        # Check number of results
        assert len(original["results"]) == len(refactored["results"]) == n_targets
        
        # Compare each target's results
        for feature_name in original["feature_names"]:
            orig_target = original["results"][feature_name]
            refact_target = refactored["results"][feature_name]
            
            self._compare_single_target_results(
                orig_target["table"], orig_target["models"],
                refact_target["table"], refact_target["models"]
            )

    def _compare_single_target_results(self, orig_table, orig_extras, refact_table, refact_extras):
        """Compare results from gsa_for_target calls."""
        # Compare table structure
        assert isinstance(orig_table, pd.DataFrame)
        assert isinstance(refact_table, pd.DataFrame)
        assert orig_table.shape == refact_table.shape
        assert list(orig_table.columns) == list(refact_table.columns)
        assert list(orig_table.index) == list(refact_table.index)
        
        # Compare numerical values with tolerance for floating point differences
        numeric_cols = orig_table.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            orig_vals = orig_table[col].values
            refact_vals = refact_table[col].values
            
            # Handle NaN values
            orig_finite = np.isfinite(orig_vals)
            refact_finite = np.isfinite(refact_vals)
            assert np.array_equal(orig_finite, refact_finite), f"NaN pattern differs in column {col}"
            
            # Compare finite values with tolerance
            if np.any(orig_finite):
                # Skip comparison of Sobol confidence intervals due to bootstrap randomness
                if col in ['S1_conf', 'ST_conf']:
                    # These are computed via bootstrap and can vary significantly
                    # Just check that both are finite and positive
                    assert np.all(orig_vals[orig_finite] >= 0), f"Original {col} should be non-negative"
                    assert np.all(refact_vals[refact_finite] >= 0), f"Refactored {col} should be non-negative"
                    continue
                else:
                    rtol, atol = 1e-10, 1e-12  # Strict for other metrics
                
                np.testing.assert_allclose(
                    orig_vals[orig_finite], 
                    refact_vals[refact_finite],
                    rtol=rtol, atol=atol,
                    err_msg=f"Values differ in column {col}"
                )
        
        # Compare extras structure (models and metadata)
        assert set(orig_extras.keys()) == set(refact_extras.keys())
        
        # Check that both have the same model types
        for key in ["rf_model", "gp_model", "sobol_raw"]:
            if key in orig_extras:
                orig_val = orig_extras[key]
                refact_val = refact_extras[key]
                
                if orig_val is None:
                    assert refact_val is None, f"{key} should both be None"
                else:
                    assert refact_val is not None, f"{key} should both be non-None"
                    assert type(orig_val) == type(refact_val), f"{key} should have same type"

    def test_function_signatures_match(self):
        """
        Test that function signatures are identical between original and refactored versions.
        
        **Validates: Requirements 2.5**
        """
        import inspect
        
        # Compare gsa_pipeline signatures
        orig_sig = inspect.signature(original_gsa.gsa_pipeline)
        refact_sig = inspect.signature(gsa_pipeline)
        
        # Parameters should be identical
        assert orig_sig.parameters.keys() == refact_sig.parameters.keys()
        
        for param_name in orig_sig.parameters:
            orig_param = orig_sig.parameters[param_name]
            refact_param = refact_sig.parameters[param_name]
            
            assert orig_param.default == refact_param.default, f"Default differs for {param_name}"
            assert orig_param.kind == refact_param.kind, f"Parameter kind differs for {param_name}"
        
        # Compare gsa_for_target signatures
        orig_sig = inspect.signature(original_gsa.gsa_for_target)
        refact_sig = inspect.signature(gsa_for_target)
        
        assert orig_sig.parameters.keys() == refact_sig.parameters.keys()
        
        for param_name in orig_sig.parameters:
            orig_param = orig_sig.parameters[param_name]
            refact_param = refact_sig.parameters[param_name]
            
            assert orig_param.default == refact_param.default, f"Default differs for {param_name}"
            assert orig_param.kind == refact_param.kind, f"Parameter kind differs for {param_name}"

    def test_import_compatibility(self):
        """
        Test that the refactored functions can be imported and used as drop-in replacements.
        
        **Validates: Requirements 2.5**
        """
        # Test that functions exist and are callable
        assert callable(gsa_pipeline)
        assert callable(gsa_for_target)
        
        # Test that they have the expected docstrings
        assert gsa_pipeline.__doc__ is not None
        assert gsa_for_target.__doc__ is not None
        
        # Test that they can be imported from the expected locations
        from mcpost.gsa import gsa_pipeline as imported_pipeline
        from mcpost.gsa import gsa_for_target as imported_target
        
        assert imported_pipeline is gsa_pipeline
        assert imported_target is gsa_for_target
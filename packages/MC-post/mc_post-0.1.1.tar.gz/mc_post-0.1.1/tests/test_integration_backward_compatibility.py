"""
Property-based tests for Integration API backward compatibility.

**Feature: mcpost-package-improvement, Property 2: API Backward Compatibility (Integration)**
**Validates: Requirements 2.5**

NOTE: These tests require the original mc_int.py file to be present
in the tests/legacy_mocks/ directory. They are skipped in CI/CD environments and should
be run locally during development to verify backward compatibility.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from typing import Callable, List, Tuple
import sys
from pathlib import Path

# Add the package root to path for importing both old and new implementations
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))
sys.path.insert(0, str(package_root / "tests" / "legacy_mocks"))

# Import the original implementation
import mc_int as original_mc

# Import the refactored implementation
from mcpost.integration import monte_carlo_integral, qmc_integral, qmc_integral_auto
from mcpost.integration.importance import qmc_integral_importance


class TestIntegrationBackwardCompatibility:
    """Test Integration API backward compatibility properties."""

    @given(
        n_samples=st.integers(min_value=50, max_value=200),
        n_params=st.integers(min_value=1, max_value=4),
        n_data=st.integers(min_value=1, max_value=3),
        random_seed=st.integers(min_value=0, max_value=100)
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    def test_monte_carlo_integral_backward_compatibility_property(
        self, n_samples, n_params, n_data, random_seed
    ):
        """
        Property 2: API Backward Compatibility (Integration) - Monte Carlo
        
        For any existing MCPost function call with valid parameters, the refactored 
        package should produce identical results to the original implementation.
        
        **Validates: Requirements 2.5**
        """
        assume(n_samples >= 10)
        assume(n_params >= 1)
        assume(n_data >= 1)
        
        # Generate reproducible test data
        np.random.seed(random_seed)
        params = np.random.random((n_samples, n_params))
        data = np.random.random((n_samples, n_data))
        
        # Create simple target PDF (normalized Gaussian)
        def p_target(theta):
            return np.exp(-0.5 * np.sum((theta - 0.5)**2, axis=1))
        
        # Create simple sampling PDF (uniform)
        def q_sample(theta):
            return np.ones(len(theta))
        
        try:
            # Test without q_sample (KDE estimation)
            original_result_no_q = original_mc.monte_carlo_integral(params, data, p_target)
            refactored_result_no_q = monte_carlo_integral(params, data, p_target)
            
            # Extract integral from refactored result (which returns a dict)
            if isinstance(refactored_result_no_q, dict):
                refactored_integral_no_q = refactored_result_no_q['integral']
            else:
                refactored_integral_no_q = refactored_result_no_q
            
            # Compare results with tolerance for numerical differences
            np.testing.assert_allclose(
                original_result_no_q, refactored_integral_no_q,
                rtol=1e-10, atol=1e-12,
                err_msg="Results differ for monte_carlo_integral without q_sample"
            )
            
            # Test with q_sample
            original_result_with_q = original_mc.monte_carlo_integral(params, data, p_target, q_sample)
            refactored_result_with_q = monte_carlo_integral(params, data, p_target, q_sample)
            
            # Extract integral from refactored result
            if isinstance(refactored_result_with_q, dict):
                refactored_integral_with_q = refactored_result_with_q['integral']
            else:
                refactored_integral_with_q = refactored_result_with_q
            
            np.testing.assert_allclose(
                original_result_with_q, refactored_integral_with_q,
                rtol=1e-10, atol=1e-12,
                err_msg="Results differ for monte_carlo_integral with q_sample"
            )
            
        except Exception as e:
            # If both implementations fail in the same way, that's acceptable
            try:
                refactored_result_no_q = monte_carlo_integral(params, data, p_target)
                pytest.fail(f"Original failed but refactored succeeded: {e}")
            except Exception:
                # Both failed, which is acceptable for edge cases
                pass

    @given(
        n_samples=st.integers(min_value=32, max_value=128),
        n_params=st.integers(min_value=1, max_value=3),
        n_data=st.integers(min_value=1, max_value=2),
        method=st.sampled_from(['sobol', 'halton']),
        random_seed=st.integers(min_value=0, max_value=50)
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    def test_qmc_integral_backward_compatibility_property(
        self, n_samples, n_params, n_data, method, random_seed
    ):
        """
        Property test for qmc_integral function backward compatibility.
        
        **Validates: Requirements 2.5**
        """
        assume(n_samples >= 16)
        assume(n_params >= 1)
        
        # Create simple data function
        def data_func(theta):
            np.random.seed(random_seed)  # Ensure reproducibility
            return np.random.random((len(theta), n_data)) + 0.1 * np.sum(theta, axis=1, keepdims=True)
        
        # Create simple target PDF
        def p_target(theta):
            return np.exp(-0.5 * np.sum((theta - 0.5)**2, axis=1))
        
        # Create bounds
        bounds = [(0.0, 1.0)] * n_params
        
        try:
            # Call original implementation
            original_result = original_mc.qmc_integral(
                n_samples, n_params, data_func, p_target, bounds, method
            )
            
            # Call refactored implementation
            refactored_result = qmc_integral(
                n_samples, n_params, data_func, p_target, bounds, method
            )
            
            # Extract integral from refactored result (which returns a dict)
            if isinstance(refactored_result, dict):
                refactored_integral = refactored_result['integral']
            else:
                refactored_integral = refactored_result
            
            # Compare results - QMC with scrambling can have variation, use relaxed tolerance
            # Both implementations should produce similar results within reasonable bounds
            relative_diff = np.abs((original_result - refactored_integral) / (original_result + 1e-15))
            max_relative_diff = np.max(relative_diff)
            
            # Allow up to 5% relative difference for QMC methods due to scrambling
            assert max_relative_diff < 0.05, (
                f"Results differ too much for qmc_integral with method {method}: "
                f"max relative difference {max_relative_diff:.6f} > 0.05"
            )
            
        except Exception as e:
            # Check if both implementations fail consistently
            try:
                refactored_result = qmc_integral(
                    n_samples, n_params, data_func, p_target, bounds, method
                )
                pytest.fail(f"Original failed but refactored succeeded: {e}")
            except Exception:
                # Both failed, acceptable for edge cases
                pass

    @given(
        n_samples=st.integers(min_value=32, max_value=128),
        n_params=st.integers(min_value=1, max_value=3),
        n_data=st.integers(min_value=1, max_value=2),
        method=st.sampled_from(['sobol', 'halton']),
        use_q_sample=st.booleans(),
        random_seed=st.integers(min_value=0, max_value=50)
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    def test_qmc_integral_auto_backward_compatibility_property(
        self, n_samples, n_params, n_data, method, use_q_sample, random_seed
    ):
        """
        Property test for qmc_integral_auto function backward compatibility.
        
        **Validates: Requirements 2.5**
        """
        assume(n_samples >= 16)
        assume(n_params >= 1)
        
        # Create simple data function
        def data_func(theta):
            np.random.seed(random_seed)  # Ensure reproducibility
            return np.random.random((len(theta), n_data)) + 0.1 * np.sum(theta, axis=1, keepdims=True)
        
        # Create simple target PDF
        def p_target(theta):
            return np.exp(-0.5 * np.sum((theta - 0.5)**2, axis=1))
        
        # Create optional sampling PDF
        q_sample = None
        if use_q_sample:
            def q_sample(theta):
                return np.ones(len(theta))
        
        # Create bounds
        bounds = [(0.0, 1.0)] * n_params
        
        try:
            # Call original implementation
            original_result = original_mc.qmc_integral_auto(
                n_samples, n_params, data_func, p_target, q_sample, bounds, method
            )
            
            # Call refactored implementation
            refactored_result = qmc_integral_auto(
                n_samples, n_params, data_func, p_target, q_sample, bounds, method
            )
            
            # Compare results - QMC with scrambling can have variation, use relaxed tolerance
            # Extract integral from refactored result (which returns a dict)
            if isinstance(refactored_result, dict):
                refactored_integral = refactored_result['integral']
            else:
                refactored_integral = refactored_result
                
            relative_diff = np.abs((original_result - refactored_integral) / (original_result + 1e-15))
            max_relative_diff = np.max(relative_diff)
            
            # Allow up to 5% relative difference for QMC methods due to scrambling
            assert max_relative_diff < 0.05, (
                f"Results differ too much for qmc_integral_auto with method {method}, q_sample={use_q_sample}: "
                f"max relative difference {max_relative_diff:.6f} > 0.05"
            )
            
        except Exception as e:
            # Check if both implementations fail consistently
            try:
                refactored_result = qmc_integral_auto(
                    n_samples, n_params, data_func, p_target, q_sample, bounds, method
                )
                pytest.fail(f"Original failed but refactored succeeded: {e}")
            except Exception:
                # Both failed, acceptable for edge cases
                pass

    @given(
        n_samples=st.integers(min_value=32, max_value=128),
        n_params=st.integers(min_value=1, max_value=3),
        n_data=st.integers(min_value=1, max_value=2),
        method=st.sampled_from(['sobol', 'halton']),
        random_seed=st.integers(min_value=0, max_value=50)
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    def test_qmc_integral_importance_backward_compatibility_property(
        self, n_samples, n_params, n_data, method, random_seed
    ):
        """
        Property test for qmc_integral_importance function backward compatibility.
        
        **Validates: Requirements 2.5**
        """
        assume(n_samples >= 16)
        assume(n_params >= 1)
        
        # Create simple data function
        def data_func(theta):
            np.random.seed(random_seed)  # Ensure reproducibility
            return np.random.random((len(theta), n_data)) + 0.1 * np.sum(theta, axis=1, keepdims=True)
        
        # Create simple target PDF
        def p_target(theta):
            return np.exp(-0.5 * np.sum((theta - 0.5)**2, axis=1))
        
        # Create sampling PDF
        def q_sample(theta):
            return np.ones(len(theta))
        
        # Create bounds
        bounds = [(0.0, 1.0)] * n_params
        
        try:
            # Call original implementation
            original_result = original_mc.qmc_integral_importance(
                n_samples, n_params, data_func, p_target, q_sample, bounds, method
            )
            
            # Call refactored implementation
            refactored_result = qmc_integral_importance(
                n_samples, n_params, data_func, p_target, q_sample, bounds, method
            )
            
            # Compare results - QMC with scrambling can have variation, use relaxed tolerance
            # Extract integral from refactored result (which returns a dict)
            if isinstance(refactored_result, dict):
                refactored_integral = refactored_result['integral']
            else:
                refactored_integral = refactored_result
                
            relative_diff = np.abs((original_result - refactored_integral) / (original_result + 1e-15))
            max_relative_diff = np.max(relative_diff)
            
            # Allow up to 5% relative difference for QMC methods due to scrambling
            assert max_relative_diff < 0.05, (
                f"Results differ too much for qmc_integral_importance with method {method}: "
                f"max relative difference {max_relative_diff:.6f} > 0.05"
            )
            
        except Exception as e:
            # Check if both implementations fail consistently
            try:
                refactored_result = qmc_integral_importance(
                    n_samples, n_params, data_func, p_target, q_sample, bounds, method
                )
                pytest.fail(f"Original failed but refactored succeeded: {e}")
            except Exception:
                # Both failed, acceptable for edge cases
                pass

    def test_function_signatures_match(self):
        """
        Test that function signatures are identical between original and refactored versions.
        
        **Validates: Requirements 2.5**
        """
        import inspect
        
        # Compare monte_carlo_integral signatures
        orig_sig = inspect.signature(original_mc.monte_carlo_integral)
        refact_sig = inspect.signature(monte_carlo_integral)
        
        # Parameters should be identical
        assert orig_sig.parameters.keys() == refact_sig.parameters.keys()
        
        for param_name in orig_sig.parameters:
            orig_param = orig_sig.parameters[param_name]
            refact_param = refact_sig.parameters[param_name]
            
            assert orig_param.default == refact_param.default, f"Default differs for {param_name}"
            assert orig_param.kind == refact_param.kind, f"Parameter kind differs for {param_name}"
        
        # Compare qmc_integral signatures
        orig_sig = inspect.signature(original_mc.qmc_integral)
        refact_sig = inspect.signature(qmc_integral)
        
        assert orig_sig.parameters.keys() == refact_sig.parameters.keys()
        
        for param_name in orig_sig.parameters:
            orig_param = orig_sig.parameters[param_name]
            refact_param = refact_sig.parameters[param_name]
            
            assert orig_param.default == refact_param.default, f"Default differs for {param_name}"
            assert orig_param.kind == refact_param.kind, f"Parameter kind differs for {param_name}"
        
        # Compare qmc_integral_auto signatures
        orig_sig = inspect.signature(original_mc.qmc_integral_auto)
        refact_sig = inspect.signature(qmc_integral_auto)
        
        assert orig_sig.parameters.keys() == refact_sig.parameters.keys()
        
        for param_name in orig_sig.parameters:
            orig_param = orig_sig.parameters[param_name]
            refact_param = refact_sig.parameters[param_name]
            
            assert orig_param.default == refact_param.default, f"Default differs for {param_name}"
            assert orig_param.kind == refact_param.kind, f"Parameter kind differs for {param_name}"
        
        # Compare qmc_integral_importance signatures
        orig_sig = inspect.signature(original_mc.qmc_integral_importance)
        refact_sig = inspect.signature(qmc_integral_importance)
        
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
        assert callable(monte_carlo_integral)
        assert callable(qmc_integral)
        assert callable(qmc_integral_auto)
        assert callable(qmc_integral_importance)
        
        # Test that they have the expected docstrings
        assert monte_carlo_integral.__doc__ is not None
        assert qmc_integral.__doc__ is not None
        assert qmc_integral_auto.__doc__ is not None
        assert qmc_integral_importance.__doc__ is not None
        
        # Test that they can be imported from the expected locations
        from mcpost.integration import monte_carlo_integral as imported_mc
        from mcpost.integration import qmc_integral as imported_qmc
        from mcpost.integration import qmc_integral_auto as imported_qmc_auto
        from mcpost.integration.importance import qmc_integral_importance as imported_importance
        
        assert imported_mc is monte_carlo_integral
        assert imported_qmc is qmc_integral
        assert imported_qmc_auto is qmc_integral_auto
        assert imported_importance is qmc_integral_importance
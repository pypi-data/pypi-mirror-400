"""
Property-based tests for configuration override consistency.

**Feature: mcpost-package-improvement, Property 5: Configuration Override Consistency**
**Validates: Requirements 6.2**
"""

import os
import pytest
from hypothesis import given, strategies as st, settings
from mcpost.utils.config import (
    GSAConfig, IntegrationConfig, configure_defaults, 
    get_gsa_config, get_integration_config, reset_defaults
)


class TestConfigurationOverrideConsistency:
    """Test configuration override consistency across different methods."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        reset_defaults()
        # Clear any environment variables that might affect tests
        env_vars_to_clear = [
            'MCPOST_GSA_SCALER', 'MCPOST_GSA_KERNEL', 'MCPOST_GSA_N_SOBOL',
            'MCPOST_INT_QMC_METHOD', 'MCPOST_INT_N_SAMPLES'
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_defaults()
        # Clear any environment variables that might have been set during tests
        env_vars_to_clear = [
            'MCPOST_GSA_SCALER', 'MCPOST_GSA_KERNEL', 'MCPOST_GSA_N_SOBOL',
            'MCPOST_INT_QMC_METHOD', 'MCPOST_INT_N_SAMPLES'
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
    
    @given(
        scaler=st.sampled_from(['minmax', 'standard']),
        kernel=st.sampled_from(['rbf', 'matern32', 'matern52', 'rq']),
        n_sobol=st.integers(min_value=1024, max_value=8192)
    )
    @settings(max_examples=2)
    def test_gsa_config_override_via_configure_defaults(self, scaler, kernel, n_sobol):
        """
        Property: For any GSA configuration parameter, setting it via configure_defaults
        should override the default value consistently.
        """
        # Set configuration via configure_defaults
        gsa_overrides = {
            'scaler': scaler,
            'kernel': kernel,
            'N_sobol': n_sobol
        }
        configure_defaults(gsa_config=gsa_overrides, update_from_env=False)
        
        # Verify the configuration was applied
        config = get_gsa_config()
        assert config.scaler == scaler
        assert config.kernel == kernel
        assert config.N_sobol == n_sobol
        
        # Verify other parameters remain at defaults
        assert config.ard == GSAConfig.DEFAULT_ARD
        assert config.enable_perm == GSAConfig.DEFAULT_ENABLE_PERM
    
    @given(
        qmc_method=st.sampled_from(['sobol', 'halton']),
        n_samples=st.integers(min_value=1000, max_value=50000)
    )
    @settings(max_examples=2)
    def test_integration_config_override_via_configure_defaults(self, qmc_method, n_samples):
        """
        Property: For any integration configuration parameter, setting it via configure_defaults
        should override the default value consistently.
        """
        # Set configuration via configure_defaults
        int_overrides = {
            'qmc_method': qmc_method,
            'N_samples': n_samples
        }
        configure_defaults(integration_config=int_overrides, update_from_env=False)
        
        # Verify the configuration was applied
        config = get_integration_config()
        assert config.qmc_method == qmc_method
        assert config.N_samples == n_samples
        
        # Verify other parameters remain at defaults
        assert config.scramble == IntegrationConfig.DEFAULT_SCRAMBLE
    
    @given(
        scaler=st.sampled_from(['minmax', 'standard']),
        kernel=st.sampled_from(['rbf', 'matern32', 'matern52', 'rq'])
    )
    @settings(max_examples=2)
    def test_gsa_config_override_via_environment(self, scaler, kernel):
        """
        Property: For any GSA configuration parameter, setting it via environment variable
        should override the default value consistently when update_from_env=True.
        """
        # Set environment variables
        os.environ['MCPOST_GSA_SCALER'] = scaler
        os.environ['MCPOST_GSA_KERNEL'] = kernel
        
        # Configure with environment update enabled
        configure_defaults(update_from_env=True)
        
        # Verify the configuration was applied from environment
        config = get_gsa_config()
        assert config.scaler == scaler
        assert config.kernel == kernel
        
        # Clean up environment variables
        del os.environ['MCPOST_GSA_SCALER']
        del os.environ['MCPOST_GSA_KERNEL']
    
    @given(
        qmc_method=st.sampled_from(['sobol', 'halton']),
        n_samples=st.integers(min_value=1000, max_value=50000)
    )
    @settings(max_examples=2)
    def test_integration_config_override_via_environment(self, qmc_method, n_samples):
        """
        Property: For any integration configuration parameter, setting it via environment variable
        should override the default value consistently when update_from_env=True.
        """
        # Set environment variables
        os.environ['MCPOST_INT_QMC_METHOD'] = qmc_method
        os.environ['MCPOST_INT_N_SAMPLES'] = str(n_samples)
        
        # Configure with environment update enabled
        configure_defaults(update_from_env=True)
        
        # Verify the configuration was applied from environment
        config = get_integration_config()
        assert config.qmc_method == qmc_method
        assert config.N_samples == n_samples
        
        # Clean up environment variables
        del os.environ['MCPOST_INT_QMC_METHOD']
        del os.environ['MCPOST_INT_N_SAMPLES']
    
    @given(
        scaler_dict=st.sampled_from(['minmax', 'standard']),
        scaler_env=st.sampled_from(['minmax', 'standard']),
        kernel=st.sampled_from(['rbf', 'matern32'])
    )
    @settings(max_examples=2)
    def test_environment_overrides_dict_config(self, scaler_dict, scaler_env, kernel):
        """
        Property: Environment variables should take precedence over configure_defaults
        when both are provided and update_from_env=True.
        """
        # Set different values via dict and environment
        os.environ['MCPOST_GSA_SCALER'] = scaler_env
        
        gsa_overrides = {
            'scaler': scaler_dict,
            'kernel': kernel
        }
        
        # Configure with both dict and environment
        configure_defaults(gsa_config=gsa_overrides, update_from_env=True)
        
        # Environment should override dict for scaler
        config = get_gsa_config()
        assert config.scaler == scaler_env  # Environment wins
        assert config.kernel == kernel      # Dict value used (no env override)
        
        # Clean up
        del os.environ['MCPOST_GSA_SCALER']
    
    def test_reset_defaults_restores_original_values(self):
        """
        Property: reset_defaults() should restore all configuration parameters
        to their original default values regardless of previous overrides.
        """
        # Override some values
        configure_defaults(
            gsa_config={'scaler': 'standard', 'N_sobol': 8192},
            integration_config={'qmc_method': 'halton'},
            update_from_env=False
        )
        
        # Verify overrides were applied
        gsa_config = get_gsa_config()
        int_config = get_integration_config()
        assert gsa_config.scaler == 'standard'
        assert gsa_config.N_sobol == 8192
        assert int_config.qmc_method == 'halton'
        
        # Reset to defaults
        reset_defaults()
        
        # Verify all values are back to defaults
        gsa_config = get_gsa_config()
        int_config = get_integration_config()
        assert gsa_config.scaler == GSAConfig.DEFAULT_SCALER
        assert gsa_config.N_sobol == GSAConfig.DEFAULT_N_SOBOL
        assert gsa_config.kernel == GSAConfig.DEFAULT_KERNEL
        assert int_config.qmc_method == IntegrationConfig.DEFAULT_QMC_METHOD
        assert int_config.N_samples == IntegrationConfig.DEFAULT_N_SAMPLES
    
    @given(
        invalid_scaler=st.text(min_size=1).filter(lambda x: x not in ['minmax', 'standard'])
    )
    @settings(max_examples=2)
    def test_invalid_config_values_raise_errors(self, invalid_scaler):
        """
        Property: Invalid configuration values should raise appropriate errors
        rather than silently failing or corrupting the configuration.
        """
        with pytest.raises(ValueError):
            configure_defaults(
                gsa_config={'scaler': invalid_scaler},
                update_from_env=False
            )
        
        # Configuration should remain unchanged after error
        config = get_gsa_config()
        assert config.scaler == GSAConfig.DEFAULT_SCALER
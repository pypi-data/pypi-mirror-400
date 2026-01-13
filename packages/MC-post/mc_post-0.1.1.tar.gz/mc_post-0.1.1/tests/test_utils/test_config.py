"""
Unit tests for configuration utility functions.
"""

import pytest
import os
from unittest.mock import patch

from mcpost.utils.config import (
    GSAConfig,
    IntegrationConfig,
    get_gsa_config,
    get_integration_config,
    configure_defaults,
    reset_defaults
)


class TestGSAConfig:
    """Test cases for GSAConfig class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = GSAConfig()
        
        assert config.scaler == "minmax"
        assert config.kernel == "rbf"
        assert config.ard is True
        assert config.enable_perm is True
        assert config.enable_gp is True
        assert config.enable_sobol is True
        assert config.N_sobol == 4096
        assert config.topk_pdp == 3
    
    def test_update_from_env_valid(self):
        """Test updating configuration from environment variables."""
        config = GSAConfig()
        
        env_vars = {
            'MCPOST_GSA_SCALER': 'standard',
            'MCPOST_GSA_KERNEL': 'matern32',
            'MCPOST_GSA_ARD': 'false',
            'MCPOST_GSA_N_SOBOL': '8192',
            'MCPOST_GSA_ENABLE_PERM': 'no'
        }
        
        with patch.dict(os.environ, env_vars):
            config.update_from_env()
        
        assert config.scaler == 'standard'
        assert config.kernel == 'matern32'
        assert config.ard is False
        assert config.N_sobol == 8192
        assert config.enable_perm is False
    
    def test_update_from_env_boolean_parsing(self):
        """Test boolean parsing from environment variables."""
        config = GSAConfig()
        
        # Test various boolean representations
        true_values = ['true', 'True', '1', 'yes', 'YES']
        false_values = ['false', 'False', '0', 'no', 'NO']
        
        for true_val in true_values:
            with patch.dict(os.environ, {'MCPOST_GSA_ARD': true_val}):
                config.update_from_env()
                assert config.ard is True
        
        for false_val in false_values:
            with patch.dict(os.environ, {'MCPOST_GSA_ARD': false_val}):
                config.update_from_env()
                assert config.ard is False
    
    def test_update_from_env_invalid_values(self):
        """Test error handling for invalid environment variable values."""
        config = GSAConfig()
        
        # Test invalid integer
        with patch.dict(os.environ, {'MCPOST_GSA_N_SOBOL': 'not_a_number'}):
            with pytest.raises(ValueError, match="Invalid value for MCPOST_GSA_N_SOBOL"):
                config.update_from_env()
        
        # Test invalid float
        with patch.dict(os.environ, {'MCPOST_GSA_BOUNDS_PAD_FRAC': 'invalid'}):
            with pytest.raises(ValueError, match="Invalid value for MCPOST_GSA_BOUNDS_PAD_FRAC"):
                config.update_from_env()
    
    def test_env_vars_not_set(self):
        """Test that configuration remains unchanged when env vars are not set."""
        config = GSAConfig()
        original_scaler = config.scaler
        original_kernel = config.kernel
        
        # Ensure no relevant env vars are set
        with patch.dict(os.environ, {}, clear=True):
            config.update_from_env()
        
        assert config.scaler == original_scaler
        assert config.kernel == original_kernel


class TestIntegrationConfig:
    """Test cases for IntegrationConfig class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = IntegrationConfig()
        
        assert config.qmc_method == "sobol"
        assert config.N_samples == 10000
        assert config.scramble is True
        assert config.bounds is None
    
    def test_update_from_env_valid(self):
        """Test updating configuration from environment variables."""
        config = IntegrationConfig()
        
        env_vars = {
            'MCPOST_INT_QMC_METHOD': 'halton',
            'MCPOST_INT_N_SAMPLES': '5000',
            'MCPOST_INT_SCRAMBLE': 'false'
        }
        
        with patch.dict(os.environ, env_vars):
            config.update_from_env()
        
        assert config.qmc_method == 'halton'
        assert config.N_samples == 5000
        assert config.scramble is False
    
    def test_update_from_env_invalid_values(self):
        """Test error handling for invalid environment variable values."""
        config = IntegrationConfig()
        
        # Test invalid integer
        with patch.dict(os.environ, {'MCPOST_INT_N_SAMPLES': 'not_a_number'}):
            with pytest.raises(ValueError, match="Invalid value for MCPOST_INT_N_SAMPLES"):
                config.update_from_env()


class TestConfigurationFunctions:
    """Test cases for configuration management functions."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        reset_defaults()
    
    def test_get_gsa_config(self):
        """Test getting GSA configuration."""
        config = get_gsa_config()
        assert isinstance(config, GSAConfig)
        assert config.scaler == "minmax"  # Default value
    
    def test_get_integration_config(self):
        """Test getting integration configuration."""
        config = get_integration_config()
        assert isinstance(config, IntegrationConfig)
        assert config.qmc_method == "sobol"  # Default value
    
    def test_configure_defaults_gsa(self):
        """Test configuring GSA defaults."""
        configure_defaults(
            gsa_config={
                'scaler': 'standard',
                'kernel': 'matern32',
                'N_sobol': 8192,
                'enable_perm': False
            },
            update_from_env=False
        )
        
        config = get_gsa_config()
        assert config.scaler == 'standard'
        assert config.kernel == 'matern32'
        assert config.N_sobol == 8192
        assert config.enable_perm is False
    
    def test_configure_defaults_integration(self):
        """Test configuring integration defaults."""
        configure_defaults(
            integration_config={
                'qmc_method': 'halton',
                'N_samples': 5000,
                'scramble': False
            },
            update_from_env=False
        )
        
        config = get_integration_config()
        assert config.qmc_method == 'halton'
        assert config.N_samples == 5000
        assert config.scramble is False
    
    def test_configure_defaults_validation_gsa(self):
        """Test validation in configure_defaults for GSA parameters."""
        # Test invalid scaler
        with pytest.raises(ValueError, match="Invalid scaler 'invalid'"):
            configure_defaults(
                gsa_config={'scaler': 'invalid'},
                update_from_env=False
            )
        
        # Test invalid kernel
        with pytest.raises(ValueError, match="Invalid kernel 'invalid'"):
            configure_defaults(
                gsa_config={'kernel': 'invalid'},
                update_from_env=False
            )
        
        # Test invalid type for integer parameter
        with pytest.raises(ValueError, match="Parameter 'N_sobol' must be an integer"):
            configure_defaults(
                gsa_config={'N_sobol': 'not_an_int'},
                update_from_env=False
            )
        
        # Test invalid type for float parameter
        with pytest.raises(ValueError, match="Parameter 'bounds_pad_frac' must be a number"):
            configure_defaults(
                gsa_config={'bounds_pad_frac': 'not_a_number'},
                update_from_env=False
            )
        
        # Test invalid type for boolean parameter
        with pytest.raises(ValueError, match="Parameter 'ard' must be a boolean"):
            configure_defaults(
                gsa_config={'ard': 'not_a_bool'},
                update_from_env=False
            )
        
        # Test unknown parameter
        with pytest.raises(ValueError, match="Unknown GSA configuration parameter"):
            configure_defaults(
                gsa_config={'unknown_param': 'value'},
                update_from_env=False
            )
    
    def test_configure_defaults_validation_integration(self):
        """Test validation in configure_defaults for integration parameters."""
        # Test invalid QMC method
        with pytest.raises(ValueError, match="Invalid qmc_method 'invalid'"):
            configure_defaults(
                integration_config={'qmc_method': 'invalid'},
                update_from_env=False
            )
        
        # Test invalid type for integer parameter
        with pytest.raises(ValueError, match="Parameter 'N_samples' must be an integer"):
            configure_defaults(
                integration_config={'N_samples': 'not_an_int'},
                update_from_env=False
            )
        
        # Test invalid type for boolean parameter
        with pytest.raises(ValueError, match="Parameter 'scramble' must be a boolean"):
            configure_defaults(
                integration_config={'scramble': 'not_a_bool'},
                update_from_env=False
            )
        
        # Test unknown parameter
        with pytest.raises(ValueError, match="Unknown integration configuration parameter"):
            configure_defaults(
                integration_config={'unknown_param': 'value'},
                update_from_env=False
            )
    
    def test_configure_defaults_with_env_update(self):
        """Test configure_defaults with environment variable updates."""
        env_vars = {
            'MCPOST_GSA_SCALER': 'standard',
            'MCPOST_INT_QMC_METHOD': 'halton'
        }
        
        with patch.dict(os.environ, env_vars):
            configure_defaults(
                gsa_config={'kernel': 'matern32'},
                integration_config={'N_samples': 5000},
                update_from_env=True
            )
        
        gsa_config = get_gsa_config()
        int_config = get_integration_config()
        
        # Should have both manual and env updates
        assert gsa_config.kernel == 'matern32'  # Manual
        assert gsa_config.scaler == 'standard'  # From env
        assert int_config.N_samples == 5000  # Manual
        assert int_config.qmc_method == 'halton'  # From env
    
    def test_reset_defaults(self):
        """Test resetting configuration to defaults."""
        # Modify configuration
        configure_defaults(
            gsa_config={'scaler': 'standard', 'N_sobol': 8192},
            integration_config={'qmc_method': 'halton'},
            update_from_env=False
        )
        
        # Verify changes
        assert get_gsa_config().scaler == 'standard'
        assert get_integration_config().qmc_method == 'halton'
        
        # Reset and verify defaults
        reset_defaults()
        assert get_gsa_config().scaler == 'minmax'
        assert get_gsa_config().N_sobol == 4096
        assert get_integration_config().qmc_method == 'sobol'
    
    def test_valid_parameter_values(self):
        """Test that all valid parameter values are accepted."""
        # Test all valid scalers
        for scaler in ['minmax', 'standard', None]:
            configure_defaults(
                gsa_config={'scaler': scaler},
                update_from_env=False
            )
            assert get_gsa_config().scaler == scaler
            reset_defaults()
        
        # Test all valid kernels
        for kernel in ['rbf', 'matern32', 'matern52', 'rq']:
            configure_defaults(
                gsa_config={'kernel': kernel},
                update_from_env=False
            )
            assert get_gsa_config().kernel == kernel
            reset_defaults()
        
        # Test all valid QMC methods
        for method in ['sobol', 'halton']:
            configure_defaults(
                integration_config={'qmc_method': method},
                update_from_env=False
            )
            assert get_integration_config().qmc_method == method
            reset_defaults()
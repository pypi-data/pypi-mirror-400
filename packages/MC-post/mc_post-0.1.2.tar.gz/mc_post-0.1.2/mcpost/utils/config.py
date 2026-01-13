"""
Configuration management.

This module contains configuration classes and management functions
for GSA and integration default parameters.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field


@dataclass
class GSAConfig:
    """Configuration class for GSA parameters."""
    
    # Scaling and preprocessing
    DEFAULT_SCALER: str = "minmax"
    DEFAULT_DROP_CONST_ATOL: float = 0.0
    DEFAULT_BOUNDS_PAD_FRAC: float = 0.02
    
    # Kernel and GP settings
    DEFAULT_KERNEL: str = "rbf"
    DEFAULT_ARD: bool = True
    DEFAULT_LENGTH_SCALE_INIT: float = 1.0
    DEFAULT_GP_RANDOM_STATE: int = 0
    
    # Method toggles
    DEFAULT_ENABLE_PERM: bool = True
    DEFAULT_ENABLE_GP: bool = True
    DEFAULT_ENABLE_SOBOL: bool = True
    DEFAULT_MAKE_PDP: bool = True
    
    # Sobol settings
    DEFAULT_N_SOBOL: int = 4096
    
    # PDP settings
    DEFAULT_TOPK_PDP: int = 3
    
    # Current configuration values (can be overridden)
    scaler: str = field(default_factory=lambda: GSAConfig.DEFAULT_SCALER)
    drop_const_atol: float = field(default_factory=lambda: GSAConfig.DEFAULT_DROP_CONST_ATOL)
    bounds_pad_frac: float = field(default_factory=lambda: GSAConfig.DEFAULT_BOUNDS_PAD_FRAC)
    kernel: str = field(default_factory=lambda: GSAConfig.DEFAULT_KERNEL)
    ard: bool = field(default_factory=lambda: GSAConfig.DEFAULT_ARD)
    length_scale_init: float = field(default_factory=lambda: GSAConfig.DEFAULT_LENGTH_SCALE_INIT)
    gp_random_state: int = field(default_factory=lambda: GSAConfig.DEFAULT_GP_RANDOM_STATE)
    enable_perm: bool = field(default_factory=lambda: GSAConfig.DEFAULT_ENABLE_PERM)
    enable_gp: bool = field(default_factory=lambda: GSAConfig.DEFAULT_ENABLE_GP)
    enable_sobol: bool = field(default_factory=lambda: GSAConfig.DEFAULT_ENABLE_SOBOL)
    make_pdp: bool = field(default_factory=lambda: GSAConfig.DEFAULT_MAKE_PDP)
    N_sobol: int = field(default_factory=lambda: GSAConfig.DEFAULT_N_SOBOL)
    topk_pdp: int = field(default_factory=lambda: GSAConfig.DEFAULT_TOPK_PDP)
    
    def update_from_env(self) -> None:
        """Update configuration from environment variables."""
        env_mappings = {
            'MCPOST_GSA_SCALER': ('scaler', str),
            'MCPOST_GSA_DROP_CONST_ATOL': ('drop_const_atol', float),
            'MCPOST_GSA_BOUNDS_PAD_FRAC': ('bounds_pad_frac', float),
            'MCPOST_GSA_KERNEL': ('kernel', str),
            'MCPOST_GSA_ARD': ('ard', lambda x: x.lower() in ('true', '1', 'yes')),
            'MCPOST_GSA_LENGTH_SCALE_INIT': ('length_scale_init', float),
            'MCPOST_GSA_GP_RANDOM_STATE': ('gp_random_state', int),
            'MCPOST_GSA_ENABLE_PERM': ('enable_perm', lambda x: x.lower() in ('true', '1', 'yes')),
            'MCPOST_GSA_ENABLE_GP': ('enable_gp', lambda x: x.lower() in ('true', '1', 'yes')),
            'MCPOST_GSA_ENABLE_SOBOL': ('enable_sobol', lambda x: x.lower() in ('true', '1', 'yes')),
            'MCPOST_GSA_MAKE_PDP': ('make_pdp', lambda x: x.lower() in ('true', '1', 'yes')),
            'MCPOST_GSA_N_SOBOL': ('N_sobol', int),
            'MCPOST_GSA_TOPK_PDP': ('topk_pdp', int),
        }
        
        for env_var, (attr_name, converter) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    setattr(self, attr_name, converter(env_value))
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid value for {env_var}: {env_value}") from e


@dataclass
class IntegrationConfig:
    """Configuration class for integration parameters."""
    
    # QMC settings
    DEFAULT_QMC_METHOD: str = "sobol"
    DEFAULT_N_SAMPLES: int = 10000
    DEFAULT_SCRAMBLE: bool = True
    
    # Bounds settings
    DEFAULT_BOUNDS: Optional[list] = None
    
    # Current configuration values (can be overridden)
    qmc_method: str = field(default_factory=lambda: IntegrationConfig.DEFAULT_QMC_METHOD)
    N_samples: int = field(default_factory=lambda: IntegrationConfig.DEFAULT_N_SAMPLES)
    scramble: bool = field(default_factory=lambda: IntegrationConfig.DEFAULT_SCRAMBLE)
    bounds: Optional[list] = field(default_factory=lambda: IntegrationConfig.DEFAULT_BOUNDS)
    
    def update_from_env(self) -> None:
        """Update configuration from environment variables."""
        env_mappings = {
            'MCPOST_INT_QMC_METHOD': ('qmc_method', str),
            'MCPOST_INT_N_SAMPLES': ('N_samples', int),
            'MCPOST_INT_SCRAMBLE': ('scramble', lambda x: x.lower() in ('true', '1', 'yes')),
        }
        
        for env_var, (attr_name, converter) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    setattr(self, attr_name, converter(env_value))
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid value for {env_var}: {env_value}") from e


# Global configuration instances
_gsa_config = GSAConfig()
_integration_config = IntegrationConfig()


def get_gsa_config() -> GSAConfig:
    """Get the current GSA configuration."""
    return _gsa_config


def get_integration_config() -> IntegrationConfig:
    """Get the current integration configuration."""
    return _integration_config


def configure_defaults(
    gsa_config: Optional[Dict[str, Any]] = None,
    integration_config: Optional[Dict[str, Any]] = None,
    update_from_env: bool = True
) -> None:
    """
    Configure default parameters for GSA and integration.
    
    Parameters
    ----------
    gsa_config : Optional[Dict[str, Any]]
        Dictionary of GSA configuration parameters to override
    integration_config : Optional[Dict[str, Any]]
        Dictionary of integration configuration parameters to override
    update_from_env : bool
        Whether to update from environment variables, by default True
        
    Raises
    ------
    ValueError
        If invalid configuration values are provided
        
    Examples
    --------
    >>> configure_defaults(
    ...     gsa_config={'scaler': 'standard', 'N_sobol': 8192},
    ...     integration_config={'qmc_method': 'halton'}
    ... )
    """
    global _gsa_config, _integration_config
    
    # Validation mappings
    valid_scalers = ['minmax', 'standard', None]
    valid_kernels = ['rbf', 'matern32', 'matern52', 'rq']
    valid_qmc_methods = ['sobol', 'halton']
    
    # Update GSA config
    if gsa_config is not None:
        for key, value in gsa_config.items():
            if not hasattr(_gsa_config, key):
                raise ValueError(f"Unknown GSA configuration parameter: {key}")
            
            # Validate specific parameters
            if key == 'scaler' and value not in valid_scalers:
                raise ValueError(f"Invalid scaler '{value}'. Must be one of {valid_scalers}")
            elif key == 'kernel' and value not in valid_kernels:
                raise ValueError(f"Invalid kernel '{value}'. Must be one of {valid_kernels}")
            elif key in ['N_sobol', 'topk_pdp', 'gp_random_state'] and not isinstance(value, int):
                raise ValueError(f"Parameter '{key}' must be an integer, got {type(value).__name__}")
            elif key in ['drop_const_atol', 'bounds_pad_frac', 'length_scale_init'] and not isinstance(value, (int, float)):
                raise ValueError(f"Parameter '{key}' must be a number, got {type(value).__name__}")
            elif key in ['ard', 'enable_perm', 'enable_gp', 'enable_sobol', 'make_pdp'] and not isinstance(value, bool):
                raise ValueError(f"Parameter '{key}' must be a boolean, got {type(value).__name__}")
            
            setattr(_gsa_config, key, value)
    
    # Update integration config
    if integration_config is not None:
        for key, value in integration_config.items():
            if not hasattr(_integration_config, key):
                raise ValueError(f"Unknown integration configuration parameter: {key}")
            
            # Validate specific parameters
            if key == 'qmc_method' and value not in valid_qmc_methods:
                raise ValueError(f"Invalid qmc_method '{value}'. Must be one of {valid_qmc_methods}")
            elif key == 'N_samples' and not isinstance(value, int):
                raise ValueError(f"Parameter '{key}' must be an integer, got {type(value).__name__}")
            elif key == 'scramble' and not isinstance(value, bool):
                raise ValueError(f"Parameter '{key}' must be a boolean, got {type(value).__name__}")
            
            setattr(_integration_config, key, value)
    
    # Update from environment variables
    if update_from_env:
        _gsa_config.update_from_env()
        _integration_config.update_from_env()


def reset_defaults() -> None:
    """Reset all configuration to default values."""
    global _gsa_config, _integration_config
    _gsa_config = GSAConfig()
    _integration_config = IntegrationConfig()
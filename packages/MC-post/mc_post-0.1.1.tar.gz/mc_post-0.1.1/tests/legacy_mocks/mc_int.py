"""
Mock version of original mc_int.py for backward compatibility testing.

This file provides the same API as the original script but delegates
to the new mcpost implementation to ensure backward compatibility.
"""

import numpy as np
from typing import Callable, List, Optional, Tuple, Any

# Import the new implementation
from mcpost.integration import monte_carlo_integral as new_monte_carlo_integral
from mcpost.integration import qmc_integral as new_qmc_integral
from mcpost.integration import qmc_integral_auto as new_qmc_integral_auto
from mcpost.integration.importance import qmc_integral_importance as new_qmc_integral_importance


def monte_carlo_integral(params, data, p_target, q_sample=None):
    """
    Original monte_carlo_integral function signature.
    
    This delegates to the new implementation to ensure backward compatibility.
    """
    result = new_monte_carlo_integral(params, data, p_target, q_sample)
    # Original function returned just the integral value, not a dict
    return result['integral']


def qmc_integral(N_samples, N_params, data_func, p_target, bounds=None, method='sobol'):
    """
    Original qmc_integral function signature.
    
    This delegates to the new implementation to ensure backward compatibility.
    """
    result = new_qmc_integral(N_samples, N_params, data_func, p_target, bounds, method)
    # Original function returned just the integral value, not a dict
    return result['integral']


def qmc_integral_auto(N_samples, N_params, data_func, p_target, q_sample=None, bounds=None, method='sobol'):
    """
    Original qmc_integral_auto function signature.
    
    This delegates to the new implementation to ensure backward compatibility.
    """
    result = new_qmc_integral_auto(N_samples, N_params, data_func, p_target, q_sample, bounds, method)
    # Original function returned just the integral value, not a dict
    return result['integral']


def qmc_integral_importance(N_samples, N_params, data_func, p_target, q_sample, bounds=None, method='sobol'):
    """
    Original qmc_integral_importance function signature.
    
    This delegates to the new implementation to ensure backward compatibility.
    """
    result = new_qmc_integral_importance(N_samples, N_params, data_func, p_target, q_sample, bounds, method)
    # Original function returned just the integral value, not a dict
    return result['integral']


# Additional utility functions that might have been in the original
def _default_bounds(N_params: int) -> List[Tuple[float, float]]:
    """Mock of original default bounds function."""
    return [(0.0, 1.0)] * N_params


def _validate_inputs(N_samples: int, N_params: int, bounds: Optional[List[Tuple[float, float]]]) -> None:
    """Mock of original input validation function."""
    if N_samples <= 0:
        raise ValueError("N_samples must be positive")
    if N_params <= 0:
        raise ValueError("N_params must be positive")
    if bounds is not None and len(bounds) != N_params:
        raise ValueError("bounds must have length N_params")
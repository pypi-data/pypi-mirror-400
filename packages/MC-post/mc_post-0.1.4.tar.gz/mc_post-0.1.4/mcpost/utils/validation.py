"""
Input validation functions.

This module contains input validation and error handling functions
for GSA and integration modules.
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional, Any, Tuple, Union


def validate_gsa_inputs(
    X: np.ndarray,
    Y: np.ndarray,
    param_names: Optional[List[str]] = None,
    feature_names: Optional[List[str]] = None,
    bounds: Optional[List[List[float]]] = None
) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    """
    Validate inputs for GSA functions.
    
    Parameters
    ----------
    X : np.ndarray
        Parameter samples of shape (n_samples, n_params)
    Y : np.ndarray
        Target values of shape (n_samples,) or (n_samples, n_targets)
    param_names : Optional[List[str]]
        Names for parameters, by default None
    feature_names : Optional[List[str]]
        Names for target features, by default None
    bounds : Optional[List[List[float]]]
        Parameter bounds, by default None
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray, List[str], List[str]]
        Validated and potentially reshaped inputs
        
    Raises
    ------
    TypeError
        If inputs are not numpy arrays
    ValueError
        If array shapes are incompatible or invalid
    """
    # Validate X
    if not isinstance(X, np.ndarray):
        raise TypeError("X must be a numpy array")
    if X.ndim != 2:
        raise ValueError("X must be 2-dimensional")
    if len(X) == 0:
        raise ValueError("X cannot be empty")
    
    n_samples, n_params = X.shape
    
    # Validate Y
    if not isinstance(Y, np.ndarray):
        raise TypeError("Y must be a numpy array")
    if Y.ndim == 1:
        Y = Y.reshape(-1, 1)
    elif Y.ndim != 2:
        raise ValueError("Y must be 1 or 2-dimensional")
    if len(Y) == 0:
        raise ValueError("Y cannot be empty")
    if Y.shape[0] != n_samples:
        raise ValueError(f"X and Y must have same number of samples. Got {n_samples} and {Y.shape[0]}")
    
    n_targets = Y.shape[1]
    
    # Validate parameter names
    if param_names is None:
        param_names = [f"p{i}" for i in range(n_params)]
    elif len(param_names) != n_params:
        raise ValueError(f"param_names length ({len(param_names)}) must match number of parameters ({n_params})")
    
    # Validate feature names
    if feature_names is None:
        feature_names = [f"feature_{j}" for j in range(n_targets)]
    elif len(feature_names) != n_targets:
        raise ValueError(f"feature_names length ({len(feature_names)}) must match number of targets ({n_targets})")
    
    # Validate bounds
    if bounds is not None:
        if len(bounds) != n_params:
            raise ValueError(f"bounds length ({len(bounds)}) must match number of parameters ({n_params})")
        for i, bound in enumerate(bounds):
            if len(bound) != 2:
                raise ValueError(f"bounds[{i}] must have exactly 2 elements [low, high]")
            if bound[0] >= bound[1]:
                raise ValueError(f"bounds[{i}] must have low < high, got {bound}")
    
    return X, Y, param_names, feature_names


def validate_integration_inputs(
    params: np.ndarray,
    data: Optional[np.ndarray] = None,
    bounds: Optional[List[Tuple[float, float]]] = None,
    N_samples: Optional[int] = None,
    N_params: Optional[int] = None
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Validate inputs for integration functions.
    
    Parameters
    ----------
    params : np.ndarray
        Parameter samples of shape (n_samples, n_params)
    data : Optional[np.ndarray]
        Function values at parameter samples, by default None
    bounds : Optional[List[Tuple[float, float]]]
        Parameter bounds, by default None
    N_samples : Optional[int]
        Expected number of samples, by default None
    N_params : Optional[int]
        Expected number of parameters, by default None
        
    Returns
    -------
    Tuple[np.ndarray, Optional[np.ndarray]]
        Validated inputs
        
    Raises
    ------
    TypeError
        If inputs are not numpy arrays
    ValueError
        If array shapes are incompatible or invalid
    """
    # Validate params
    if not isinstance(params, np.ndarray):
        raise TypeError("params must be a numpy array")
    if params.ndim != 2:
        raise ValueError("params must be 2-dimensional")
    if len(params) == 0:
        raise ValueError("params cannot be empty")
    
    n_samples, n_params = params.shape
    
    # Validate expected dimensions
    if N_samples is not None and n_samples != N_samples:
        raise ValueError(f"Expected {N_samples} samples, got {n_samples}")
    if N_params is not None and n_params != N_params:
        raise ValueError(f"Expected {N_params} parameters, got {n_params}")
    
    # Validate data if provided
    if data is not None:
        if not isinstance(data, np.ndarray):
            raise TypeError("data must be a numpy array")
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        elif data.ndim != 2:
            raise ValueError("data must be 1 or 2-dimensional")
        if data.shape[0] != n_samples:
            raise ValueError(f"params and data must have same number of samples. Got {n_samples} and {data.shape[0]}")
    
    # Validate bounds
    if bounds is not None:
        if len(bounds) != n_params:
            raise ValueError(f"bounds length ({len(bounds)}) must match number of parameters ({n_params})")
        for i, (low, high) in enumerate(bounds):
            if low >= high:
                raise ValueError(f"bounds[{i}] must have low < high, got ({low}, {high})")
    
    return params, data


def validate_inputs(*args, **kwargs) -> Any:
    """
    General input validation dispatcher.
    
    This function serves as a general entry point for input validation.
    The specific validation logic depends on the context and input types.
    
    Parameters
    ----------
    *args : Any
        Positional arguments to validate
    **kwargs : Any
        Keyword arguments to validate
        
    Returns
    -------
    Any
        Validated inputs
        
    Raises
    ------
    ValueError
        If validation fails
    """
    if len(args) >= 2 and isinstance(args[0], np.ndarray) and isinstance(args[1], np.ndarray):
        # Assume GSA validation if we have two arrays
        return validate_gsa_inputs(*args, **kwargs)
    elif len(args) >= 1 and isinstance(args[0], np.ndarray):
        # Assume integration validation for single array
        return validate_integration_inputs(*args, **kwargs)
    else:
        raise ValueError("Unable to determine validation type from inputs")
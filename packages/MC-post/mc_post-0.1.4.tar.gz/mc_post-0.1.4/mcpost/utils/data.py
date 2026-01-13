"""
Data preprocessing utilities.

This module contains data preprocessing functions extracted from the original
GSA pipeline, including constant column detection and bounds inference.
"""

from __future__ import annotations

import numpy as np
from typing import List, Tuple


def drop_constant_columns(
    X: np.ndarray,
    param_names: List[str],
    atol: float = 0.0
) -> Tuple[np.ndarray, List[str], List[int], List[int]]:
    """
    Drop columns with (max - min) ~= 0 (within atol).
    
    Parameters
    ----------
    X : np.ndarray
        Input data array of shape (n_samples, n_params)
    param_names : List[str]
        Names of parameters corresponding to columns in X
    atol : float, optional
        Absolute tolerance for considering a column constant, by default 0.0
        
    Returns
    -------
    Tuple[np.ndarray, List[str], List[int], List[int]]
        - Filtered array with constant columns removed
        - Parameter names for remaining columns
        - Indices of kept columns
        - Indices of dropped columns
        
    Examples
    --------
    >>> X = np.array([[1, 2, 3], [1, 4, 3], [1, 6, 3]])
    >>> names = ['a', 'b', 'c']
    >>> X_filtered, names_filtered, kept, dropped = drop_constant_columns(X, names)
    >>> print(kept)  # [1] - only column 'b' varies
    >>> print(dropped)  # [0, 2] - columns 'a' and 'c' are constant
    """
    const_mask = np.isclose(X.max(axis=0) - X.min(axis=0), 0.0, atol=atol)
    dropped = np.where(const_mask)[0].tolist()
    kept = np.where(~const_mask)[0].tolist()
    Xr = X[:, kept] if len(kept) > 0 else X[:, :0]
    names_r = [param_names[i] for i in kept]
    return Xr, names_r, kept, dropped


def infer_bounds_from_data(
    X: np.ndarray,
    pad_frac: float = 0.02
) -> List[List[float]]:
    """
    Infer per-parameter [low, high] bounds from data with optional padding.
    
    Parameters
    ----------
    X : np.ndarray
        Input data array of shape (n_samples, n_params)
    pad_frac : float, optional
        Fraction of the range to add as padding on each side, by default 0.02
        
    Returns
    -------
    List[List[float]]
        List of [low, high] bounds for each parameter
        
    Examples
    --------
    >>> X = np.array([[0, 1], [1, 2], [2, 3]])
    >>> bounds = infer_bounds_from_data(X, pad_frac=0.1)
    >>> # Returns approximately [[-0.2, 2.2], [0.8, 3.2]]
    """
    lo = X.min(axis=0)
    hi = X.max(axis=0)
    span = hi - lo
    span = np.where(span == 0.0, 1.0, span)  # avoid zero span
    lo2 = lo - pad_frac * span
    hi2 = hi + pad_frac * span
    return [[float(a), float(b)] for a, b in zip(lo2, hi2)]
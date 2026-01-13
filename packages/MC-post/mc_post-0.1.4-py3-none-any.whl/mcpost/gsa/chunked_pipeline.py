"""
Chunked GSA pipeline functions for memory-efficient analysis of large datasets.

This module provides chunked versions of the main GSA pipeline functions
that can handle large datasets by processing them in memory-efficient chunks.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple
import warnings

from mcpost.gsa.pipeline import gsa_for_target, gsa_pipeline
from mcpost.gsa.metrics import screening_metrics, _drop_constant_columns, _default_param_names
from mcpost.utils.chunked import (
    ChunkedGSAProcessor, suggest_chunking_strategy, estimate_memory_usage
)


def chunked_gsa_for_target(
    X: np.ndarray,
    y: np.ndarray,
    *,
    max_memory_mb: float = 1000.0,
    show_progress: bool = True,
    chunk_size: Optional[int] = None,
    # All other parameters same as gsa_for_target
    param_names: Optional[List[str]] = None,
    scaler: Optional[str] = "minmax",
    bounds: Optional[List[List[float]]] = None,
    bounds_pad_frac: float = 0.02,
    kernel_kind: str = "rbf",
    ard: bool = True,
    length_scale_init: float | np.ndarray = 1.0,
    gp_random_state: int = 0,
    enable_perm: bool = True,
    enable_gp: bool = True,
    enable_sobol: bool = True,
    N_sobol: int = 4096,
    drop_const_atol: float = 0.0,
    make_pdp: bool = True,
    topk_pdp: int = 3,
    pdp_fig_prefix: Optional[str] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run GSA for a single scalar target y with chunked processing for large datasets.
    
    This function automatically determines if chunking is needed based on memory
    constraints and falls back to the standard implementation for smaller datasets.
    
    Parameters
    ----------
    X : np.ndarray
        Input parameters (N_samples, N_params)
    y : np.ndarray
        Target values (N_samples,)
    max_memory_mb : float, default=1000.0
        Maximum memory usage in MB for chunked processing
    show_progress : bool, default=True
        Whether to show progress bars during chunked processing
    chunk_size : int, optional
        Fixed chunk size. If None, calculated automatically
    **kwargs
        All other parameters are the same as gsa_for_target
        
    Returns
    -------
    tuple
        (sensitivity_table, extras_dict) - same as gsa_for_target
        
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.gsa import chunked_gsa_for_target
    >>> 
    >>> # Generate large dataset
    >>> np.random.seed(42)
    >>> X = np.random.uniform(-np.pi, np.pi, (50000, 10))  # Large dataset
    >>> y = np.sin(X[:, 0]) + 7 * np.sin(X[:, 1])**2 + 0.1 * X[:, 2]**4 * np.sin(X[:, 0])
    >>> 
    >>> # Run chunked GSA with memory limit
    >>> table, extras = chunked_gsa_for_target(
    ...     X, y,
    ...     max_memory_mb=500,  # Limit memory usage
    ...     show_progress=True,
    ...     param_names=[f"x{i}" for i in range(10)]
    ... )
    >>> 
    >>> print(f"Processed {len(X)} samples with chunking")
    >>> print(table.head())
    
    Notes
    -----
    - Automatically falls back to standard GSA for datasets that fit in memory
    - Chunked processing may slightly affect numerical results due to aggregation
    - GP fitting and Sobol analysis are still performed on the full dataset
    - Only screening metrics (MI, dCor, permutation) are computed in chunks
    """
    n, d = X.shape
    
    # Check if chunking is needed
    strategy = suggest_chunking_strategy(X, y.reshape(-1, 1), max_memory_mb)
    
    if not strategy["needs_chunking"]:
        # Use standard implementation
        if show_progress:
            print(f"Dataset fits in memory ({strategy['current_memory_mb']:.1f} MB). "
                  "Using standard GSA implementation.")
        
        table, extras = gsa_for_target(
            X, y,
            param_names=param_names,
            scaler=scaler,
            bounds=bounds,
            bounds_pad_frac=bounds_pad_frac,
            kernel_kind=kernel_kind,
            ard=ard,
            length_scale_init=length_scale_init,
            gp_random_state=gp_random_state,
            enable_perm=enable_perm,
            enable_gp=enable_gp,
            enable_sobol=enable_sobol,
            N_sobol=N_sobol,
            drop_const_atol=drop_const_atol,
            make_pdp=make_pdp,
            topk_pdp=topk_pdp,
            pdp_fig_prefix=pdp_fig_prefix
        )
        
        # Add chunking metadata
        extras["chunked_processing"] = False
        extras["chunking_strategy"] = strategy
        
        return table, extras
    
    # Use chunked processing
    if show_progress:
        print(f"Large dataset detected ({strategy['current_memory_mb']:.1f} MB). "
              f"Using chunked processing: {strategy['recommendation']}")
    
    # Setup parameter names
    if param_names is None:
        param_names = _default_param_names(d)
    
    # 1) Drop constant columns (on full dataset - this is fast)
    Xr, names_r, kept_idx, dropped_idx = _drop_constant_columns(X, param_names, atol=drop_const_atol)
    if Xr.shape[1] == 0:
        raise ValueError("All parameters are constant; nothing to analyze.")
    
    # 2) Chunked screening metrics
    processor = ChunkedGSAProcessor(
        max_memory_mb=max_memory_mb,
        show_progress=show_progress,
        chunk_size=chunk_size
    )
    
    def screening_func(X_chunk, y_chunk, **kwargs):
        return screening_metrics(X_chunk, y_chunk, random_state=gp_random_state, enable_perm=enable_perm)
    
    scr = processor.process_screening_metrics(Xr, y, screening_func)
    
    # 3) GP + Sobol (on full dataset - these need the complete data)
    # Note: For very large datasets, this might still be memory intensive
    if enable_gp:
        from mcpost.gsa.metrics import _infer_bounds_from_data, gp_surrogate_and_sobol
        
        if bounds is None:
            bounds_use = _infer_bounds_from_data(Xr, pad_frac=bounds_pad_frac)
        else:
            if len(bounds) != len(param_names):
                raise ValueError(
                    "Length of 'bounds' must match number of input parameters before dropping constants."
                )
            bounds_use = [bounds[i] for i in kept_idx]
        
        # For very large datasets, we might need to subsample for GP fitting
        if len(Xr) > 10000:
            warnings.warn(
                f"Large dataset ({len(Xr)} samples) detected for GP fitting. "
                "Consider subsampling for GP/Sobol analysis or disable with enable_gp=False.",
                UserWarning
            )
        
        gp, Si, ard_ls = gp_surrogate_and_sobol(
            X=Xr, y=y, bounds_orig=bounds_use,
            kernel_kind=kernel_kind, ard=ard, scaler=scaler,
            gp_random_state=gp_random_state, N_sobol=N_sobol,
            enable_sobol=enable_sobol, length_scale_init=length_scale_init
        )
    else:
        gp, Si, ard_ls = None, None, np.full(Xr.shape[1], np.nan)
    
    # 4) Aggregate table (same as standard implementation)
    from mcpost.gsa.metrics import aggregate_table
    
    table = aggregate_table(
        param_names=names_r,
        MI=scr["MI"], dCor=scr["dCor"],
        PermMean=scr["PermMean"], PermStd=scr["PermStd"],
        ARD_LS=ard_ls, Si=Si
    )
    
    # 5) PDPs (same as standard implementation)
    pdp_paths = []
    if make_pdp:
        try:
            from mcpost.gsa.plotting import create_pdp_plots
            k = min(topk_pdp, Xr.shape[1])
            top_params = table.index[:k].tolist()
            pdp_paths = create_pdp_plots(
                scr["rf_model"], Xr, names_r, top_params, pdp_fig_prefix
            )
        except ImportError:
            warnings.warn(
                "Partial dependence plots requested but matplotlib is not available. "
                "Install with: pip install mcpost[viz] or pip install matplotlib",
                UserWarning
            )
    
    extras = {
        "rf_model": scr["rf_model"],
        "gp_model": gp,
        "sobol_raw": Si,
        "kept_idx": kept_idx,
        "dropped_idx": dropped_idx,
        "kept_names": names_r,
        "pdp_saved_paths": pdp_paths,
        "scaler": scaler,
        "kernel_kind": kernel_kind,
        "ard": ard,
        "chunked_processing": True,
        "chunking_strategy": strategy,
    }
    
    return table, extras


def chunked_gsa_pipeline(
    X: np.ndarray,
    Y: np.ndarray,
    *,
    max_memory_mb: float = 1000.0,
    show_progress: bool = True,
    chunk_size: Optional[int] = None,
    # All other parameters same as gsa_pipeline
    feature_names: Optional[List[str]] = None,
    param_names: Optional[List[str]] = None,
    scaler: Optional[str] = "minmax",
    bounds: Optional[List[List[float]]] = None,
    bounds_pad_frac: float = 0.02,
    kernel_kind: str = "rbf",
    ard: bool = True,
    length_scale_init: float | np.ndarray = 1.0,
    gp_random_state: int = 0,
    enable_perm: bool = True,
    enable_gp: bool = True,
    enable_sobol: bool = True,
    make_pdp: bool = True,
    N_sobol: int = 4096,
    drop_const_atol: float = 0.0,
    topk_pdp: int = 3,
    pdp_prefix: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run GSA for each column in Y with chunked processing for large datasets.
    
    Parameters
    ----------
    X : np.ndarray
        Input parameters (N_samples, N_params)
    Y : np.ndarray
        Target values (N_samples, N_targets)
    max_memory_mb : float, default=1000.0
        Maximum memory usage in MB for chunked processing
    show_progress : bool, default=True
        Whether to show progress bars during chunked processing
    chunk_size : int, optional
        Fixed chunk size. If None, calculated automatically
    **kwargs
        All other parameters are the same as gsa_pipeline
        
    Returns
    -------
    dict
        Dictionary containing results for each target feature - same as gsa_pipeline
        
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.gsa import chunked_gsa_pipeline
    >>> 
    >>> # Generate large multi-output dataset
    >>> np.random.seed(42)
    >>> X = np.random.uniform(-1, 1, (100000, 6))  # Very large dataset
    >>> 
    >>> # Multiple outputs
    >>> y1 = X[:, 0]**2 + 2*X[:, 1] + 0.1*X[:, 2]
    >>> y2 = np.sin(X[:, 0]) + np.cos(X[:, 1]) * X[:, 3]
    >>> Y = np.column_stack([y1, y2])
    >>> 
    >>> # Run chunked GSA pipeline
    >>> results = chunked_gsa_pipeline(
    ...     X, Y,
    ...     max_memory_mb=800,
    ...     show_progress=True,
    ...     param_names=[f"x{i}" for i in range(6)],
    ...     feature_names=["polynomial", "trigonometric"]
    ... )
    >>> 
    >>> # Results have same structure as standard pipeline
    >>> for feature in ["polynomial", "trigonometric"]:
    ...     print(f"\\n{feature} sensitivity:")
    ...     print(results["results"][feature]["table"].head())
    """
    n, d = X.shape
    m = Y.shape[1]
    
    if feature_names is None:
        feature_names = [f"feature_{j}" for j in range(m)]
    if param_names is None:
        param_names = _default_param_names(d)
    
    if not enable_gp:
        enable_sobol = False  # Sobol needs the GP surrogate
    
    # Check overall memory requirements
    strategy = suggest_chunking_strategy(X, Y, max_memory_mb)
    
    if not strategy["needs_chunking"]:
        # Use standard implementation
        if show_progress:
            print(f"Dataset fits in memory ({strategy['current_memory_mb']:.1f} MB). "
                  "Using standard GSA pipeline.")
        
        return gsa_pipeline(
            X, Y,
            feature_names=feature_names,
            param_names=param_names,
            scaler=scaler,
            bounds=bounds,
            bounds_pad_frac=bounds_pad_frac,
            kernel_kind=kernel_kind,
            ard=ard,
            length_scale_init=length_scale_init,
            gp_random_state=gp_random_state,
            enable_perm=enable_perm,
            enable_gp=enable_gp,
            enable_sobol=enable_sobol,
            make_pdp=make_pdp,
            N_sobol=N_sobol,
            drop_const_atol=drop_const_atol,
            topk_pdp=topk_pdp,
            pdp_prefix=pdp_prefix
        )
    
    # Use chunked processing
    if show_progress:
        print(f"Large dataset detected ({strategy['current_memory_mb']:.1f} MB). "
              f"Using chunked processing: {strategy['recommendation']}")
    
    results = {}
    for j in range(m):
        y = Y[:, j]
        prefix = f"{pdp_prefix}_{feature_names[j]}" if pdp_prefix else None
        
        if show_progress:
            print(f"\nProcessing feature {j+1}/{m}: {feature_names[j]}")
        
        table, extras = chunked_gsa_for_target(
            X, y,
            max_memory_mb=max_memory_mb,
            show_progress=show_progress,
            chunk_size=chunk_size,
            param_names=param_names,
            scaler=scaler,
            bounds=bounds,
            bounds_pad_frac=bounds_pad_frac,
            kernel_kind=kernel_kind,
            ard=ard,
            length_scale_init=length_scale_init,
            gp_random_state=gp_random_state,
            enable_perm=enable_perm,
            enable_gp=enable_gp,
            enable_sobol=enable_sobol,
            N_sobol=N_sobol,
            drop_const_atol=drop_const_atol,
            make_pdp=make_pdp,
            topk_pdp=topk_pdp,
            pdp_fig_prefix=prefix
        )
        
        results[feature_names[j]] = {"table": table, "models": extras}
    
    return {
        "results": results,
        "feature_names": feature_names,
        "param_names": param_names,
        "chunked_processing": True,
        "chunking_strategy": strategy,
        "notes": (
            "Sobol indices are computed on a GP surrogate. "
            "Sampling occurs in ORIGINAL parameter space and is transformed "
            "through the chosen scaler before GP prediction. "
            "For correlated/constrained inputs, interpret Sobol cautiously and "
            "lean on MI/dCor/Permutation + PDPs. "
            "Results computed using chunked processing for memory efficiency."
        ),
    }
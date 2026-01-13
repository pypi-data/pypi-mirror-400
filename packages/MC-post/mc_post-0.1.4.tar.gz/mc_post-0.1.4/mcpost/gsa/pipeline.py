"""
GSA pipeline functions for Global Sensitivity Analysis.

This module contains the main GSA pipeline functions that orchestrate
the complete sensitivity analysis workflow.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple

from mcpost.gsa.metrics import (
    _default_param_names, _infer_bounds_from_data, _drop_constant_columns,
    screening_metrics, gp_surrogate_and_sobol, aggregate_table
)

# Conditional import for plotting functions that require matplotlib
try:
    from mcpost.gsa.plotting import create_pdp_plots
    _HAS_PDP_PLOTTING = True
except ImportError:
    _HAS_PDP_PLOTTING = False
    create_pdp_plots = None


def gsa_for_target(
    X: np.ndarray,
    y: np.ndarray,
    *,
    param_names: Optional[List[str]] = None,
    # Scaling & bounds
    scaler: Optional[str] = "minmax",          # 'minmax' | 'standard' | None
    bounds: Optional[List[List[float]]] = None, # ORIGINAL space bounds for Sobol; if None, inferred
    bounds_pad_frac: float = 0.02,
    # Kernel / GP
    kernel_kind: str = "rbf",  # 'rbf' | 'matern32' | 'matern52' | 'rq'
    ard: bool = True,
    length_scale_init: float | np.ndarray = 1.0,
    gp_random_state: int = 0,
    # Toggles for heavy steps
    enable_perm: bool = True,
    enable_gp: bool = True,
    enable_sobol: bool = True,
    # Sobol budget
    N_sobol: int = 4096,
    # Preprocessing
    drop_const_atol: float = 0.0,
    # PDPs
    make_pdp: bool = True,
    topk_pdp: int = 3,
    pdp_fig_prefix: Optional[str] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run GSA for a single scalar target y.

    Switch off heavy metrics with:
      enable_perm=False (skip permutation importance),
      enable_gp=False   (skip GP & ARD & Sobol entirely),
      enable_sobol=False (keep GP + ARD but skip Sobol).

    Scaling note:
      Sobol sampling ALWAYS occurs in ORIGINAL space and gets transformed
      into the GP scaled space before prediction. This fixes the
      StandardScaler mismatch bug.
      
    Parameters
    ----------
    X : np.ndarray
        Input parameters (N_samples, N_params)
    y : np.ndarray
        Target values (N_samples,)
    param_names : List[str], optional
        Parameter names. If None, uses default names
    scaler : str, optional, default="minmax"
        Scaler type: 'minmax', 'standard', or None
    bounds : List[List[float]], optional
        Parameter bounds for Sobol sampling. If None, inferred from data
    bounds_pad_frac : float, default=0.02
        Padding fraction for inferred bounds
    kernel_kind : str, default="rbf"
        GP kernel type: 'rbf', 'matern32', 'matern52', 'rq'
    ard : bool, default=True
        Use ARD (Automatic Relevance Determination) kernel
    length_scale_init : float or np.ndarray, default=1.0
        Initial length scale for GP kernel
    gp_random_state : int, default=0
        Random state for GP and other random operations
    enable_perm : bool, default=True
        Whether to compute permutation importance
    enable_gp : bool, default=True
        Whether to fit GP surrogate
    enable_sobol : bool, default=True
        Whether to compute Sobol indices
    N_sobol : int, default=4096
        Number of Sobol samples
    drop_const_atol : float, default=0.0
        Tolerance for dropping constant columns
    make_pdp : bool, default=True
        Whether to create partial dependence plots
    topk_pdp : int, default=3
        Number of top parameters for PDP plots
    pdp_fig_prefix : str, optional
        Prefix for saved PDP figure files
        
    Returns
    -------
    tuple
        (sensitivity_table, extras_dict)
        
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.gsa import gsa_for_target
    >>> 
    >>> # Generate sample data (Ishigami function)
    >>> np.random.seed(42)
    >>> X = np.random.uniform(-np.pi, np.pi, (1000, 3))
    >>> y = np.sin(X[:, 0]) + 7 * np.sin(X[:, 1])**2 + 0.1 * X[:, 2]**4 * np.sin(X[:, 0])
    >>> 
    >>> # Run GSA for single target
    >>> table, extras = gsa_for_target(
    ...     X, y,
    ...     param_names=["x1", "x2", "x3"],
    ...     scaler="minmax",
    ...     enable_sobol=True
    ... )
    >>> 
    >>> # View sensitivity results
    >>> print(table)
    >>> 
    >>> # Access GP model
    >>> gp_model = extras["gp_model"]
    >>> if gp_model is not None:
    ...     print(f"GP R² score: {gp_model.score(X, y):.3f}")
    """
    n, d = X.shape
    if param_names is None:
        param_names = _default_param_names(d)

    # 1) Drop constant columns
    Xr, names_r, kept_idx, dropped_idx = _drop_constant_columns(X, param_names, atol=drop_const_atol)
    if Xr.shape[1] == 0:
        raise ValueError("All parameters are constant; nothing to analyze.")

    # 2) Screening (MI, dCor, optional Permutation)
    scr = screening_metrics(Xr, y, random_state=gp_random_state, enable_perm=enable_perm)

    # 3) GP + Sobol (optional)
    if enable_gp:
        if bounds is None:
            bounds_use = _infer_bounds_from_data(Xr, pad_frac=bounds_pad_frac)
        else:
            if len(bounds) != len(param_names):
                raise ValueError(
                    "Length of 'bounds' must match number of input parameters before dropping constants."
                )
            bounds_use = [bounds[i] for i in kept_idx]
        gp, Si, ard_ls = gp_surrogate_and_sobol(
            X=Xr, y=y, bounds_orig=bounds_use,
            kernel_kind=kernel_kind, ard=ard, scaler=scaler,
            gp_random_state=gp_random_state, N_sobol=N_sobol,
            enable_sobol=enable_sobol, length_scale_init=length_scale_init
        )
    else:
        gp, Si, ard_ls = None, None, np.full(Xr.shape[1], np.nan)

    # 4) Table
    table = aggregate_table(
        param_names=names_r,
        MI=scr["mi"], dCor=scr["dcor"],
        PermMean=scr["PermMean"], PermStd=scr["PermStd"],
        ARD_LS=ard_ls, Si=Si
    )

    # 5) PDPs for top-k using the RF (if requested)
    pdp_paths = []
    if make_pdp:
        if not _HAS_PDP_PLOTTING:
            import warnings
            warnings.warn(
                "Partial dependence plots requested but matplotlib is not available. "
                "Install with: pip install mcpost[viz] or pip install matplotlib",
                UserWarning
            )
        else:
            k = min(topk_pdp, Xr.shape[1])
            top_params = table.index[:k].tolist()
            pdp_paths = create_pdp_plots(
                scr["rf_model"], Xr, names_r, top_params, pdp_fig_prefix
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
    }
    return table, extras


def gsa_pipeline(
    X: np.ndarray,
    Y: np.ndarray,
    *,
    feature_names: Optional[List[str]] = None,
    param_names: Optional[List[str]] = None,
    # Scaling & bounds
    scaler: Optional[str] = "minmax",
    bounds: Optional[List[List[float]]] = None,
    bounds_pad_frac: float = 0.02,
    # Kernel / GP
    kernel_kind: str = "rbf",
    ard: bool = True,
    length_scale_init: float | np.ndarray = 1.0,
    gp_random_state: int = 0,
    # Toggles
    enable_perm: bool = True,
    enable_gp: bool = True,
    enable_sobol: bool = True,
    make_pdp: bool = True,
    # Budgets / misc
    N_sobol: int = 4096,
    drop_const_atol: float = 0.0,
    topk_pdp: int = 3,
    pdp_prefix: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run GSA for each column in Y.

    Time-saving toggles:
      - enable_perm=False  -> skips permutation importance (heavy)
      - enable_sobol=False -> skips Sobol (heavy)
      - make_pdp=False     -> skips PDP plotting (moderate)
      - enable_gp=False    -> skips GP/ARD (and automatically Sobol)

    Parameters
    ----------
    X : np.ndarray
        Input parameters (N_samples, N_params)
    Y : np.ndarray
        Target values (N_samples, N_targets)
    feature_names : List[str], optional
        Target feature names. If None, uses default names
    param_names : List[str], optional
        Parameter names. If None, uses default names
    scaler : str, optional, default="minmax"
        Scaler type: 'minmax', 'standard', or None
    bounds : List[List[float]], optional
        Parameter bounds for Sobol sampling
    bounds_pad_frac : float, default=0.02
        Padding fraction for inferred bounds
    kernel_kind : str, default="rbf"
        GP kernel type: 'rbf', 'matern32', 'matern52', 'rq'
    ard : bool, default=True
        Use ARD kernel
    length_scale_init : float or np.ndarray, default=1.0
        Initial length scale for GP kernel
    gp_random_state : int, default=0
        Random state for reproducibility
    enable_perm : bool, default=True
        Whether to compute permutation importance
    enable_gp : bool, default=True
        Whether to fit GP surrogate
    enable_sobol : bool, default=True
        Whether to compute Sobol indices
    make_pdp : bool, default=True
        Whether to create partial dependence plots
    N_sobol : int, default=4096
        Number of Sobol samples
    drop_const_atol : float, default=0.0
        Tolerance for dropping constant columns
    topk_pdp : int, default=3
        Number of top parameters for PDP plots
    pdp_prefix : str, optional
        Prefix for saved PDP figure files
        
    Returns
    -------
    dict
        Dictionary containing results for each target feature
        
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost import gsa_pipeline
    >>> 
    >>> # Generate multi-output test data
    >>> np.random.seed(42)
    >>> X = np.random.uniform(-1, 1, (1000, 4))
    >>> 
    >>> # Two different functions
    >>> y1 = X[:, 0]**2 + 2*X[:, 1] + 0.1*X[:, 2]  # Polynomial
    >>> y2 = np.sin(X[:, 0]) + np.cos(X[:, 1]) * X[:, 3]  # Trigonometric
    >>> Y = np.column_stack([y1, y2])
    >>> 
    >>> # Run comprehensive GSA
    >>> results = gsa_pipeline(
    ...     X, Y,
    ...     param_names=["x1", "x2", "x3", "x4"],
    ...     feature_names=["polynomial", "trigonometric"],
    ...     scaler="minmax",
    ...     enable_sobol=True,
    ...     make_pdp=True
    ... )
    >>> 
    >>> # View results for each output
    >>> for feature in ["polynomial", "trigonometric"]:
    ...     print(f"\\n{feature} sensitivity:")
    ...     print(results["results"][feature]["table"])
    >>> 
    >>> # Access models and metadata
    >>> gp_model = results["results"]["polynomial"]["models"]["gp_model"]
    >>> print(f"\\nFeatures analyzed: {results['feature_names']}")
    >>> print(f"Parameters: {results['param_names']}")
    """
    n, d = X.shape
    m = Y.shape[1]
    if feature_names is None:
        feature_names = [f"feature_{j}" for j in range(m)]
    if param_names is None:
        param_names = _default_param_names(d)

    if not enable_gp:
        enable_sobol = False  # Sobol needs the GP surrogate

    results = {}
    for j in range(m):
        y = Y[:, j]
        prefix = f"{pdp_prefix}_{feature_names[j]}" if pdp_prefix else None

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
            pdp_fig_prefix=prefix
        )
        results[feature_names[j]] = {"table": table, "models": extras}

    return {
        "results": results,
        "feature_names": feature_names,
        "param_names": param_names,
        "notes": (
            "Sobol indices are computed on a GP surrogate. "
            "Sampling occurs in ORIGINAL parameter space and is transformed "
            "through the chosen scaler before GP prediction. "
            "For correlated/constrained inputs, interpret Sobol cautiously and "
            "lean on MI/dCor/Permutation + PDPs."
        ),
    }
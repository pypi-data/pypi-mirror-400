"""
GSA metrics computation for Global Sensitivity Analysis.

This module contains individual sensitivity metrics computation functions
including mutual information, distance correlation, permutation importance,
and Sobol indices.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple

# Screening
from sklearn.feature_selection import mutual_info_regression
import dcor  # pip install dcor

# Models & utilities
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor

# Variance-based GSA
from SALib.sample import saltelli
from SALib.analyze import sobol

from mcpost.gsa.kernels import build_kernel, extract_lengthscales


def _default_param_names(d: int) -> List[str]:
    """Generate default parameter names."""
    return [f"p{i}" for i in range(d)]


def _infer_bounds_from_data(
    X: np.ndarray,
    pad_frac: float = 0.02
) -> List[List[float]]:
    """Infer per-parameter [low, high] from data with a small padding."""
    lo = X.min(axis=0)
    hi = X.max(axis=0)
    span = hi - lo
    span = np.where(span == 0.0, 1.0, span)  # avoid zero span
    lo2 = lo - pad_frac * span
    hi2 = hi + pad_frac * span
    return [[float(a), float(b)] for a, b in zip(lo2, hi2)]


def _drop_constant_columns(
    X: np.ndarray,
    param_names: List[str],
    atol: float = 0.0
) -> Tuple[np.ndarray, List[str], List[int], List[int]]:
    """Drop columns with (max - min) ~= 0 (within atol)."""
    const_mask = np.isclose(X.max(axis=0) - X.min(axis=0), 0.0, atol=atol)
    dropped = np.where(const_mask)[0].tolist()
    kept = np.where(~const_mask)[0].tolist()
    Xr = X[:, kept] if len(kept) > 0 else X[:, :0]
    names_r = [param_names[i] for i in kept]
    return Xr, names_r, kept, dropped


def _make_scaler(scaler: Optional[str]):
    """Return an initialized scaler object or None."""
    if scaler is None:
        return None
    scaler = scaler.lower()
    if scaler in ("minmax", "min_max", "min-max"):
        return MinMaxScaler(feature_range=(0, 1))
    if scaler in ("standard", "z", "zscore", "z-score"):
        return StandardScaler(with_mean=True, with_std=True)
    raise ValueError(f"Unknown scaler='{scaler}'. Use 'minmax', 'standard', or None.")


def screening_metrics(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int = 0,
    enable_perm: bool = True
) -> Dict[str, Any]:
    """
    Compute MI, dCor and (optionally) permutation importance with a RF.
    
    Parameters
    ----------
    X : np.ndarray
        Input parameters
    y : np.ndarray
        Target values
    random_state : int, default=0
        Random state for reproducibility
    enable_perm : bool, default=True
        Whether to compute permutation importance
        
    Returns
    -------
    dict
        Dictionary containing computed metrics and models
    """
    # Check minimum sample size for mutual information (needs at least 3 neighbors)
    if len(X) < 5:  # Conservative minimum to ensure mutual info works
        # Return NaN values for insufficient data
        n_features = X.shape[1]
        return {
            'mi': np.full(n_features, np.nan),
            'dcor': np.full(n_features, np.nan),
            'rf_model': None,
            'PermMean': np.full(n_features, np.nan),
            'PermStd': np.full(n_features, np.nan),
            'Xte': None, 'yte': None
        }
    
    mi = mutual_info_regression(X, y, random_state=random_state)
    dcor_vals = np.array([dcor.distance_correlation(X[:, i], y) for i in range(X.shape[1])])

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=random_state)

    # RF is handy for PDPs and a robust baseline; keep n_estimators moderate
    rf = RandomForestRegressor(
        n_estimators=600 if enable_perm else 300,
        max_depth=None,
        random_state=random_state,
        n_jobs=-1
    ).fit(Xtr, ytr)

    if enable_perm:
        perm = permutation_importance(rf, Xte, yte, n_repeats=20, random_state=random_state, n_jobs=-1)
        perm_mean = perm.importances_mean
        perm_std = perm.importances_std
    else:
        perm_mean = np.full(X.shape[1], np.nan)
        perm_std = np.full(X.shape[1], np.nan)

    return {
        "mi": mi,
        "dcor": dcor_vals,
        "PermMean": perm_mean,
        "PermStd": perm_std,
        "rf_model": rf,
        "Xte": Xte, "yte": yte
    }


def gp_surrogate_and_sobol(
    X: np.ndarray,
    y: np.ndarray,
    bounds_orig: List[List[float]],
    kernel_kind: str = "rbf",
    ard: bool = True,
    scaler: Optional[str] = "minmax",
    gp_random_state: int = 0,
    N_sobol: int = 4096,
    enable_sobol: bool = True,
    length_scale_init: float | np.ndarray = 1.0,
) -> Tuple[Optional[GaussianProcessRegressor], Optional[Dict[str, Any]], np.ndarray]:
    """
    Fit a GP on scaled X->y and (optionally) compute Sobol indices on the GP surrogate.

    IMPORTANT: Sobol sampling is done in ORIGINAL space using bounds_orig.
    The Saltelli sample Z_orig is then mapped through the scaler -> GP space
    before gp.predict. This fixes the StandardScaler mismatch issue.
    
    Parameters
    ----------
    X : np.ndarray
        Input parameters
    y : np.ndarray
        Target values
    bounds_orig : List[List[float]]
        Parameter bounds in original space
    kernel_kind : str, default="rbf"
        Kernel type
    ard : bool, default=True
        Use ARD kernel
    scaler : str or None, default="minmax"
        Scaler type
    gp_random_state : int, default=0
        Random state for GP
    N_sobol : int, default=4096
        Number of Sobol samples
    enable_sobol : bool, default=True
        Whether to compute Sobol indices
    length_scale_init : float or np.ndarray, default=1.0
        Initial length scale
        
    Returns
    -------
    tuple
        (GP model, Sobol indices, ARD length scales)
    """
    d = X.shape[1]

    # Build scaler and scale X for GP
    scaler_obj = _make_scaler(scaler)
    if scaler_obj is not None:
        X_scaled = scaler_obj.fit_transform(X)
    else:
        X_scaled = X.copy()

    # Build kernel with ARD
    kernel = build_kernel(
        kind=kernel_kind, ard=ard, d=d,
        length_scale_init=length_scale_init
    )

    gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True, random_state=gp_random_state)
    gp.fit(X_scaled, y)

    # Extract ARD length-scales (smaller => more sensitive)
    ard_ls = extract_lengthscales(gp.kernel_, d)

    # Optionally compute Sobol on the GP surrogate
    if enable_sobol:
        problem = {
            "num_vars": d,
            "names": [f"p{i}" for i in range(d)],
            "bounds": bounds_orig  # ORIGINAL space bounds
        }
        # 1) Sample in original space
        Z_orig = saltelli.sample(problem, N_sobol, calc_second_order=False)
        # 2) Transform into the scaled GP space
        if scaler_obj is not None:
            Z_scaled = scaler_obj.transform(Z_orig)
        else:
            Z_scaled = Z_orig
        # 3) Predict with GP
        y_hat = gp.predict(Z_scaled)
        # 4) Sobol indices
        Si = sobol.analyze(
            problem, y_hat, calc_second_order=False, conf_level=0.95,
            print_to_console=False, seed=gp_random_state
        )
    else:
        Si = None

    return gp, Si, ard_ls


def aggregate_table(
    param_names: List[str],
    MI: np.ndarray, dCor: np.ndarray,
    PermMean: np.ndarray, PermStd: np.ndarray,
    ARD_LS: np.ndarray,
    Si: Optional[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Build the consolidated sensitivity metrics table.
    
    Parameters
    ----------
    param_names : List[str]
        Parameter names
    MI : np.ndarray
        Mutual information values
    dCor : np.ndarray
        Distance correlation values
    PermMean : np.ndarray
        Permutation importance means
    PermStd : np.ndarray
        Permutation importance standard deviations
    ARD_LS : np.ndarray
        ARD length scales
    Si : dict or None
        Sobol indices (None if disabled)
        
    Returns
    -------
    pd.DataFrame
        Consolidated sensitivity metrics table
    """
    d = len(param_names)
    if Si is None:
        S1 = np.zeros(d); S1c = np.zeros(d)
        ST = np.zeros(d); STc = np.zeros(d)
    else:
        S1 = np.asarray(Si["S1"])
        S1c = np.asarray(Si["S1_conf"])
        ST = np.asarray(Si["ST"])
        STc = np.asarray(Si["ST_conf"])

    tbl = pd.DataFrame(
        {
            "MI": MI,
            "dCor": dCor,
            "PermMean": PermMean,
            "PermStd": PermStd,
            "ARD_LS": ARD_LS,
            "S1": S1, "S1_conf": S1c,
            "ST": ST, "ST_conf": STc,
        },
        index=param_names
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        inv_ls = 1.0 / tbl["ARD_LS"].to_numpy()
    tbl["1/ARD_LS"] = inv_ls

    # Aggregate ranking across available metrics; Sobol may be zeroed if disabled
    ranks = pd.DataFrame({
        "r_MI": tbl["MI"].rank(ascending=False),
        "r_dCor": tbl["dCor"].rank(ascending=False),
        "r_Perm": tbl["PermMean"].rank(ascending=False),
        "r_InvLS": tbl["1/ARD_LS"].rank(ascending=False),
        "r_ST": tbl["ST"].rank(ascending=False),
    }, index=tbl.index)
    tbl["AggRank"] = ranks.mean(axis=1)
    return tbl.sort_values("AggRank")
"""
Mock version of original gsa_pipeline.py for backward compatibility testing.

This file provides the same API as the original script but delegates
to the new mcpost implementation to ensure backward compatibility.
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple

# Import the new implementation
from mcpost.gsa import gsa_pipeline as new_gsa_pipeline, gsa_for_target as new_gsa_for_target


def gsa_pipeline(
    X: np.ndarray,
    Y: np.ndarray,
    param_names: Optional[List[str]] = None,
    feature_names: Optional[List[str]] = None,
    scaler: Optional[str] = "minmax",
    bounds: Optional[List[List[float]]] = None,
    bounds_pad_frac: float = 0.02,
    kernel_kind: str = "rbf",
    ard: bool = True,
    length_scale_init: float = 1.0,
    gp_random_state: int = 0,
    enable_perm: bool = True,
    enable_gp: bool = True,
    enable_sobol: bool = True,
    N_sobol: int = 4096,
    drop_const_atol: float = 0.0,
    make_pdp: bool = True,
    topk_pdp: int = 3,
    pdp_fig_prefix: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Original gsa_pipeline function signature.
    
    This delegates to the new implementation to ensure backward compatibility.
    """
    return new_gsa_pipeline(
        X=X, Y=Y,
        param_names=param_names,
        feature_names=feature_names,
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
        pdp_prefix=pdp_fig_prefix,  # Map old parameter name to new
    )


def gsa_for_target(
    X: np.ndarray,
    y: np.ndarray,
    param_names: Optional[List[str]] = None,
    scaler: Optional[str] = "minmax",
    bounds: Optional[List[List[float]]] = None,
    bounds_pad_frac: float = 0.02,
    kernel_kind: str = "rbf",
    ard: bool = True,
    length_scale_init: float = 1.0,
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
    Original gsa_for_target function signature.
    
    This delegates to the new implementation to ensure backward compatibility.
    """
    return new_gsa_for_target(
        X=X, y=y,
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
        pdp_fig_prefix=pdp_fig_prefix,
    )


# Additional functions that might have been in the original
def _screening_metrics(X, y, random_state=0, enable_perm=True):
    """Mock of original screening metrics function."""
    from mcpost.gsa.metrics import screening_metrics
    return screening_metrics(X, y, random_state=random_state, enable_perm=enable_perm)


def _default_param_names(d: int) -> List[str]:
    """Mock of original default parameter names function."""
    return [f"p{i}" for i in range(d)]
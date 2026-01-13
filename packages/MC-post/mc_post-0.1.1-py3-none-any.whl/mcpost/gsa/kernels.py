"""
GP kernel utilities for Global Sensitivity Analysis.

This module contains Gaussian Process kernel construction and utilities
for building kernels with ARD (Automatic Relevance Determination) support.
"""

from __future__ import annotations

import numpy as np
from typing import Tuple, Any

from sklearn.gaussian_process.kernels import (
    RBF, Matern, RationalQuadratic,
    WhiteKernel, ConstantKernel as C
)


def build_kernel(
    kind: str = "rbf",
    ard: bool = True,
    d: int = 1,
    length_scale_init: float | np.ndarray = 1.0,
    length_scale_bounds: Tuple[float, float] = (1e-2, 1e2),
    alpha_rq: float = 1.0,
    nu_matern: float = 1.5,
    constant_bounds: Tuple[float, float] = (1e-3, 1e3),
    noise_bounds: Tuple[float, float] = (1e-9, 1e-2),
    noise_init: float = 1e-6,
    constant_init: float = 1.0,
) -> Any:
    """
    Construct a GP kernel with ARD support where possible.

    Parameters
    ----------
    kind : str, default="rbf"
        Kernel type: 'rbf' | 'matern32' | 'matern52' | 'rq'
    ard : bool, default=True
        If True, use vector length-scales (per-dimension)
    d : int, default=1
        Input dimensionality
    length_scale_init : float or np.ndarray, default=1.0
        Initial length scale value(s)
    length_scale_bounds : tuple, default=(1e-2, 1e2)
        Bounds for length scale optimization
    alpha_rq : float, default=1.0
        Alpha parameter for RationalQuadratic kernel
    nu_matern : float, default=1.5
        Nu parameter for Matern kernel
    constant_bounds : tuple, default=(1e-3, 1e3)
        Bounds for constant kernel
    noise_bounds : tuple, default=(1e-9, 1e-2)
        Bounds for noise kernel
    noise_init : float, default=1e-6
        Initial noise level
    constant_init : float, default=1.0
        Initial constant value

    Returns
    -------
    kernel
        Constructed sklearn GP kernel
    """
    # length_scale_init can be scalar or vector; make vector for ARD
    if ard:
        if np.isscalar(length_scale_init):
            ls = np.ones(d) * float(length_scale_init)
        else:
            ls = np.asarray(length_scale_init, dtype=float)
            if ls.shape != (d,):
                raise ValueError(f"length_scale_init must have shape ({d},) for ARD=True.")
    else:
        ls = float(length_scale_init)

    if kind.lower() in ("rbf", "sqexp", "squared_exponential"):
        base = RBF(length_scale=ls, length_scale_bounds=length_scale_bounds)
    elif kind.lower() in ("matern32", "matern_32", "matern-32"):
        base = Matern(length_scale=ls, length_scale_bounds=length_scale_bounds, nu=1.5)
    elif kind.lower() in ("matern52", "matern_52", "matern-52"):
        base = Matern(length_scale=ls, length_scale_bounds=length_scale_bounds, nu=2.5)
    elif kind.lower() in ("rq", "rationalquadratic", "rational_quadratic"):
        # sklearn's RationalQuadratic kernel only accepts scalar length-scales.
        # When ARD was requested we quietly fall back to a scalar using the
        # geometric mean so that optimisation still receives a sensible scale.
        if ard:
            ls_scalar = float(np.exp(np.mean(np.log(ls))))
        else:
            ls_scalar = float(ls)
        base = RationalQuadratic(length_scale=ls_scalar, alpha=alpha_rq,
                                 length_scale_bounds=length_scale_bounds)
    else:
        raise ValueError(f"Unknown kernel kind='{kind}'.")

    kernel = (
        C(constant_init, constant_bounds) * base
        + WhiteKernel(noise_level=noise_init, noise_level_bounds=noise_bounds)
    )
    return kernel


def extract_lengthscales(kernel, d: int) -> np.ndarray:
    """
    Traverse a fitted kernel to recover per-dimension length-scales.

    Parameters
    ----------
    kernel
        Fitted sklearn GP kernel
    d : int
        Input dimensionality

    Returns
    -------
    np.ndarray
        Extracted length scales for each dimension
    """
    ls_collection = []

    def visit(k):
        if hasattr(k, "k1") and hasattr(k, "k2"):
            visit(k.k1)
            visit(k.k2)
        if hasattr(k, "length_scale"):
            try:
                raw = np.asarray(k.length_scale, dtype=float)
            except Exception:
                return
            arr = np.atleast_1d(raw)
            if arr.shape == (d,):
                ls_collection.append(arr)
            elif arr.size == 1:
                ls_collection.append(np.repeat(float(arr.item()), d))

    visit(kernel)

    if not ls_collection:
        return np.full(d, np.nan)

    ls_stack = np.vstack(ls_collection)
    with np.errstate(divide="ignore", invalid="ignore"):
        harmonic = ls_stack.shape[0] / np.nansum(1.0 / ls_stack, axis=0)
    return harmonic
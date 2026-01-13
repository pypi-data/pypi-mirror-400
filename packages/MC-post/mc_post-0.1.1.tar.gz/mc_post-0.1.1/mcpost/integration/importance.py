"""
Importance sampling utilities.

This module contains importance sampling techniques
refactored from the original mc_int.py script.
"""

import numpy as np
from scipy.stats import qmc


def qmc_integral_importance(N_samples, N_params, data_func, p_target, q_sample, bounds=None, method='sobol'):
    """
    QMC integral with explicit importance sampling.
    
    Performs quasi-Monte Carlo integration using importance sampling with
    a user-specified sampling distribution q_sample.

    Parameters
    ----------
    N_samples : int
        Number of QMC points to generate.
    N_params : int
        Dimension of the parameter space.
    data_func : callable
        Function f(theta) to integrate. Should accept array of shape 
        (N_samples, N_params) and return array of shape (N_samples, N_data).
    p_target : callable
        Target PDF p(theta). Should accept array of shape (N_samples, N_params)
        and return array of shape (N_samples,).
    q_sample : callable
        Sampling PDF q(theta) used for importance sampling. Should accept array 
        of shape (N_samples, N_params) and return array of shape (N_samples,).
    bounds : list of tuples, optional
        Parameter bounds as [(low1, high1), ..., (lowD, highD)].
        If None, uses unit hypercube [0,1]^d.
    method : {'sobol', 'halton'}, default='sobol'
        QMC sequence type.

    Returns
    -------
    dict
        Dictionary containing:
        - 'integral' : np.ndarray, shape (N_data,)
            Estimated integral of f(theta) over parameter space w.r.t p_target(theta).
        - 'samples' : np.ndarray, shape (N_samples, N_params)
            QMC sample points used.
        - 'function_values' : np.ndarray, shape (N_samples, N_data)
            Function values at sample points.
        - 'importance_weights' : np.ndarray, shape (N_samples,)
            Importance weights p_target/q_sample.
        - 'effective_sample_size' : float
            Effective sample size based on weight variance.
            
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.integration import qmc_integral_importance
    >>> 
    >>> # Define integrand and PDFs
    >>> def integrand(theta):
    ...     return theta[:, 0]**2 + theta[:, 1]**2
    >>> 
    >>> def target_pdf(theta):
    ...     return np.exp(-np.sum(theta**2, axis=1)) / np.pi
    >>> 
    >>> def sampling_pdf(theta):
    ...     return np.exp(-0.5 * np.sum(theta**2, axis=1)) / (2 * np.pi)
    >>> 
    >>> # Compute integral
    >>> result = qmc_integral_importance(
    ...     N_samples=2048,
    ...     N_params=2,
    ...     data_func=integrand,
    ...     p_target=target_pdf,
    ...     q_sample=sampling_pdf,
    ...     bounds=[(-3, 3), (-3, 3)]
    ... )
    >>> print(f"Integral: {result['integral']:.6f}")
    >>> print(f"Effective sample size: {result['effective_sample_size']:.1f}")
    
    Notes
    -----
    Importance sampling can significantly reduce variance when q_sample is chosen
    to be similar to |f(theta) * p_target(theta)|. The integral is computed as:
    
    .. math::
        \\int f(\\theta) p(\\theta) d\\theta \\approx V \\frac{1}{N} \\sum_{i=1}^N \\frac{p(\\theta_i)}{q(\\theta_i)} f(\\theta_i)
        
    where V is the volume of the integration domain.
    
    The effective sample size indicates how many independent samples the 
    importance-weighted samples are equivalent to. Values much smaller than
    N_samples indicate poor choice of q_sample.
    """
    # Default unit hypercube
    if bounds is None:
        bounds = [(0.0, 1.0)] * N_params
    bounds = np.array(bounds)
    lows = bounds[:,0]
    highs = bounds[:,1]

    # Generate QMC points in unit cube
    if method.lower() == 'sobol':
        sampler = qmc.Sobol(d=N_params, scramble=True)
        u = sampler.random(N_samples)
    elif method.lower() == 'halton':
        sampler = qmc.Halton(d=N_params, scramble=True)
        u = sampler.random(N_samples)
    else:
        raise ValueError("method must be 'sobol' or 'halton'")

    # Scale to bounds
    theta_unit = u
    theta = lows + (highs - lows) * theta_unit  # shape (N_samples, N_params)

    # Evaluate function
    data = np.asarray(data_func(theta))  # shape (N_samples, N_data)

    # Evaluate target PDF and sampling PDF
    p_vals = np.asarray(p_target(theta))
    q_vals = np.asarray(q_sample(theta))

    # Importance weights
    weights = p_vals / q_vals
    integral = np.mean(weights[:, None] * data, axis=0)  # weighted mean

    # Scale by volume of hypercube
    vol = np.prod(highs - lows)
    integral *= vol
    
    # Effective sample size
    normalized_weights = weights / np.sum(weights)
    eff_sample_size = 1.0 / np.sum(normalized_weights**2) if np.sum(normalized_weights**2) > 0 else N_samples

    return {
        'integral': integral,
        'samples': theta,
        'function_values': data,
        'importance_weights': weights,
        'effective_sample_size': eff_sample_size
    }
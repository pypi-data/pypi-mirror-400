"""
Monte Carlo integration methods.

This module contains standard Monte Carlo integration methods
refactored from the original mc_int.py script.
"""

import numpy as np
from scipy.stats import gaussian_kde


def monte_carlo_integral(params, data, p_target, q_sample=None):
    """
    Estimate integral of f(theta) over parameter space using Monte Carlo integration.
    
    Uses importance sampling with target distribution p_target. If the sampling 
    density q_sample is not provided, it is estimated from the samples using KDE.

    Parameters
    ----------
    params : np.ndarray, shape (N_samples, N_params)
        Sample points in the parameter space.
    data : np.ndarray, shape (N_samples, N_data)
        Function values at the sample points.
    p_target : callable
        Target probability density function p(theta), evaluated at each sample.
        Should accept array of shape (N_samples, N_params) and return array 
        of shape (N_samples,).
    q_sample : callable, optional
        Sampling probability density function q(theta), evaluated at each sample.
        Should accept array of shape (N_samples, N_params) and return array 
        of shape (N_samples,). If None, estimated via KDE from params.

    Returns
    -------
    dict
        Dictionary containing:
        - 'integral' : np.ndarray, shape (N_data,)
            Estimated integral over parameter space.
        - 'uncertainty' : np.ndarray, shape (N_data,)
            Estimated uncertainty (standard error) of the integral.
        - 'weights' : np.ndarray, shape (N_samples,)
            Importance weights used in the calculation.
        - 'effective_sample_size' : float
            Effective sample size based on weight variance.
            
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.integration import monte_carlo_integral
    >>> 
    >>> # Define target PDF (standard normal)
    >>> def target_pdf(theta):
    ...     return np.exp(-0.5 * np.sum(theta**2, axis=1)) / (2 * np.pi)
    >>> 
    >>> # Generate samples and function values
    >>> np.random.seed(42)
    >>> theta = np.random.normal(0, 1, (1000, 2))
    >>> f_vals = theta[:, 0] * np.sin(theta[:, 1])
    >>> 
    >>> # Compute integral
    >>> result = monte_carlo_integral(theta, f_vals, target_pdf)
    >>> print(f"Integral: {result['integral']:.6f}")
    >>> print(f"Uncertainty: {result['uncertainty']:.6f}")
    
    Notes
    -----
    The integral is computed as:
    
    .. math::
        \\int f(\\theta) p(\\theta) d\\theta \\approx \\sum_{i=1}^N w_i f(\\theta_i)
        
    where :math:`w_i = p(\\theta_i) / q(\\theta_i)` are the importance weights
    normalized to sum to 1.
    
    When q_sample is None, a Gaussian KDE is fitted to the parameter samples
    to estimate the sampling density.
    """
    params = np.asarray(params)
    data = np.asarray(data)
    N_samples = len(params)

    # Evaluate target PDF
    p_vals = np.asarray(p_target(params))
    
    # Evaluate or estimate sampling PDF
    if q_sample is None:
        kde = gaussian_kde(params.T)  # scipy expects shape (N_params, N_samples)
        q_vals = kde(params.T)
    else:
        q_vals = np.asarray(q_sample(params))
    
    # Importance weights
    weights = p_vals / q_vals
    weights /= np.sum(weights)  # normalize to sum to 1

    # Weighted sum
    integral = np.sum(weights[:, None] * data, axis=0)
    
    # Estimate uncertainty using weighted variance
    weighted_mean = integral
    weighted_var = np.sum(weights[:, None] * (data - weighted_mean)**2, axis=0)
    uncertainty = np.sqrt(weighted_var / N_samples)
    
    # Effective sample size
    eff_sample_size = 1.0 / np.sum(weights**2)
    
    return {
        'integral': integral,
        'uncertainty': uncertainty, 
        'weights': weights,
        'effective_sample_size': eff_sample_size
    }
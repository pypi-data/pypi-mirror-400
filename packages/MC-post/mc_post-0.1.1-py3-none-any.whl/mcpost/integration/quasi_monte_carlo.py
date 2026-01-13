"""
Quasi-Monte Carlo integration methods.

This module contains QMC integration methods
refactored from the original mc_int.py script.
"""

import numpy as np
from scipy.stats import qmc


def qmc_integral(N_samples, N_params, data_func, p_target, bounds=None, method='sobol'):
    """
    Estimate integral using quasi-Monte Carlo integration.
    
    Computes the integral of f(theta) over parameter space with target PDF 
    using quasi-Monte Carlo sampling for improved convergence over standard
    Monte Carlo methods.

    Parameters
    ----------
    N_samples : int
        Number of quasi-Monte Carlo points to generate.
    N_params : int
        Dimension of the parameter space.
    data_func : callable
        Function f(theta) that returns data array. Should accept array of shape 
        (N_samples, N_params) and return array of shape (N_samples, N_data).
    p_target : callable
        Target probability density function p(theta). Should accept array of shape
        (N_samples, N_params) and return array of shape (N_samples,).
    bounds : list of tuples, optional
        Parameter bounds as [(low1, high1), ..., (lowD, highD)] for each parameter. 
        If None, assumes unit hypercube [0,1]^d.
    method : {'sobol', 'halton'}, default='sobol'
        QMC sequence type to use.

    Returns
    -------
    dict
        Dictionary containing:
        - 'integral' : np.ndarray, shape (N_data,)
            Estimated integral of f(theta) over the parameter space w.r.t p_target(theta).
        - 'samples' : np.ndarray, shape (N_samples, N_params)
            QMC sample points used in the integration.
        - 'function_values' : np.ndarray, shape (N_samples, N_data)
            Function values at the sample points.
        - 'pdf_values' : np.ndarray, shape (N_samples,)
            Target PDF values at the sample points.
            
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.integration import qmc_integral
    >>> 
    >>> # Define integrand and target PDF
    >>> def integrand(theta):
    ...     return theta[:, 0] * np.sin(theta[:, 1])
    >>> 
    >>> def target_pdf(theta):
    ...     return np.exp(-0.5 * np.sum(theta**2, axis=1)) / (2 * np.pi)
    >>> 
    >>> # Compute integral over [-3, 3] x [-3, 3]
    >>> result = qmc_integral(
    ...     N_samples=4096,
    ...     N_params=2,
    ...     data_func=integrand,
    ...     p_target=target_pdf,
    ...     bounds=[(-3, 3), (-3, 3)]
    ... )
    >>> print(f"Integral: {result['integral']:.6f}")
    
    Notes
    -----
    QMC methods provide better convergence rates than standard Monte Carlo
    for smooth integrands, typically O(N^{-1}) vs O(N^{-1/2}).
    
    The integral is computed as:
    
    .. math::
        \\int f(\\theta) p(\\theta) d\\theta \\approx V \\frac{1}{N} \\sum_{i=1}^N f(\\theta_i) p(\\theta_i)
        
    where V is the volume of the integration domain and :math:`\\theta_i` are
    QMC points uniformly distributed in the domain.
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
    theta = lows + (highs - lows) * u  # shape (N_samples, N_params)

    # Evaluate function
    data = np.asarray(data_func(theta))  # shape (N_samples, N_data)

    # Evaluate target PDF
    p_vals = np.asarray(p_target(theta))  # shape (N_samples,)

    # Since QMC points are uniform in hypercube, weight by PDF and volume
    vol = np.prod(highs - lows)
    integral = vol * np.mean(data * p_vals[:, None], axis=0)

    return {
        'integral': integral,
        'samples': theta,
        'function_values': data,
        'pdf_values': p_vals
    }


def qmc_integral_auto(N_samples, N_params, data_func, p_target, q_sample=None, bounds=None, method='sobol'):
    """
    Fully automatic QMC integrator with optional importance sampling.
    
    Provides a high-level interface for quasi-Monte Carlo integration with
    automatic handling of importance sampling and bounds scaling.

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
    q_sample : callable, optional
        Sampling PDF q(theta) for importance sampling. If None, QMC points are 
        uniform in bounds and importance weights = p_target.
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
        - 'weights' : np.ndarray, shape (N_samples,)
            Importance weights used in integration.
        - 'effective_sample_size' : float
            Effective sample size based on weight variance.
            
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.integration import qmc_integral_auto
    >>> 
    >>> # Define integrand and PDFs
    >>> def integrand(theta):
    ...     return np.exp(theta[:, 0]) * np.cos(theta[:, 1])
    >>> 
    >>> def target_pdf(theta):
    ...     return np.exp(-0.5 * np.sum(theta**2, axis=1)) / (2 * np.pi)
    >>> 
    >>> def importance_pdf(theta):
    ...     return np.exp(-0.25 * np.sum(theta**2, axis=1)) / (4 * np.pi)
    >>> 
    >>> # Compute integral with importance sampling
    >>> result = qmc_integral_auto(
    ...     N_samples=4096,
    ...     N_params=2,
    ...     data_func=integrand,
    ...     p_target=target_pdf,
    ...     q_sample=importance_pdf,
    ...     bounds=[(-3, 3), (-3, 3)]
    ... )
    >>> print(f"Integral: {result['integral']:.6f}")
    >>> print(f"Effective sample size: {result['effective_sample_size']:.1f}")
    
    Notes
    -----
    When q_sample is provided, the method performs importance sampling:
    
    .. math::
        \\int f(\\theta) p(\\theta) d\\theta \\approx V \\sum_{i=1}^N w_i f(\\theta_i)
        
    where :math:`w_i = p(\\theta_i) / q(\\theta_i)` are normalized importance weights.
    
    Without importance sampling (q_sample=None), it reduces to standard QMC
    integration with uniform sampling in the specified bounds.
    """
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
    theta = lows + (highs - lows) * u  # shape (N_samples, N_params)

    # Evaluate function
    data = np.asarray(data_func(theta))  # shape (N_samples, N_data)

    # Evaluate target PDF
    p_vals = np.asarray(p_target(theta))

    if q_sample is None:
        # Uniform sampling in bounds: weights = target PDF
        weights = p_vals
    else:
        # Importance sampling
        q_vals = np.asarray(q_sample(theta))
        weights = p_vals / q_vals

    # Normalize weights and take weighted mean
    weights /= np.sum(weights)
    integral = np.sum(weights[:, None] * data, axis=0)

    # Scale by hypercube volume
    vol = np.prod(highs - lows)
    integral *= vol
    
    # Effective sample size
    eff_sample_size = 1.0 / np.sum(weights**2) if np.sum(weights**2) > 0 else N_samples

    return {
        'integral': integral,
        'samples': theta,
        'function_values': data,
        'weights': weights,
        'effective_sample_size': eff_sample_size
    }
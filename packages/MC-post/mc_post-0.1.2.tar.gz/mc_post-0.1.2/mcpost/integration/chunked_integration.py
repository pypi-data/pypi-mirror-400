"""
Chunked Monte Carlo integration for memory-efficient processing of large datasets.

This module provides chunked versions of Monte Carlo integration methods
that can handle large sample sets by processing them in memory-efficient chunks.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Dict, Any, Callable
import warnings

from mcpost.integration.monte_carlo import monte_carlo_integral
from mcpost.utils.chunked import (
    ChunkedIntegrationProcessor, suggest_chunking_strategy
)


def chunked_monte_carlo_integral(
    params: np.ndarray,
    data: np.ndarray,
    p_target: Callable,
    q_sample: Optional[Callable] = None,
    *,
    max_memory_mb: float = 1000.0,
    show_progress: bool = True,
    chunk_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Estimate integral using Monte Carlo with chunked processing for large datasets.
    
    This function automatically determines if chunking is needed based on memory
    constraints and falls back to the standard implementation for smaller datasets.
    
    Parameters
    ----------
    params : np.ndarray, shape (N_samples, N_params)
        Sample points in the parameter space
    data : np.ndarray, shape (N_samples, N_data)
        Function values at the sample points
    p_target : callable
        Target probability density function p(theta)
    q_sample : callable, optional
        Sampling probability density function q(theta).
        For chunked processing, this should be provided explicitly
        to avoid KDE estimation issues.
    max_memory_mb : float, default=1000.0
        Maximum memory usage in MB for chunked processing
    show_progress : bool, default=True
        Whether to show progress bars during chunked processing
    chunk_size : int, optional
        Fixed chunk size. If None, calculated automatically
        
    Returns
    -------
    dict
        Dictionary containing integration results - same as monte_carlo_integral
        
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.integration import chunked_monte_carlo_integral
    >>> 
    >>> # Define target PDF (standard normal)
    >>> def target_pdf(theta):
    ...     return np.exp(-0.5 * np.sum(theta**2, axis=1)) / (2 * np.pi)
    >>> 
    >>> # Define sampling PDF (uniform)
    >>> def sample_pdf(theta):
    ...     return np.ones(len(theta)) / 4  # Uniform on [-2, 2]^2
    >>> 
    >>> # Generate large sample set
    >>> np.random.seed(42)
    >>> theta = np.random.uniform(-2, 2, (100000, 2))  # Large dataset
    >>> f_vals = theta[:, 0] * np.sin(theta[:, 1])
    >>> 
    >>> # Compute integral with chunking
    >>> result = chunked_monte_carlo_integral(
    ...     theta, f_vals, target_pdf, sample_pdf,
    ...     max_memory_mb=500,
    ...     show_progress=True
    ... )
    >>> 
    >>> print(f"Integral: {result['integral']:.6f}")
    >>> print(f"Uncertainty: {result['uncertainty']:.6f}")
    >>> print(f"Effective sample size: {result['effective_sample_size']:.0f}")
    
    Notes
    -----
    - Automatically falls back to standard integration for datasets that fit in memory
    - For chunked processing, q_sample should be provided explicitly to avoid
      issues with KDE estimation across chunks
    - Results may have slightly different numerical values due to chunked aggregation
    """
    params = np.asarray(params)
    data = np.asarray(data)
    
    # Ensure data is 2D
    if data.ndim == 1:
        data = data[:, None]
    
    n_samples, n_params = params.shape
    n_data = data.shape[1]
    
    # Check if chunking is needed
    strategy = suggest_chunking_strategy(params, data, max_memory_mb)
    
    if not strategy["needs_chunking"]:
        # Use standard implementation
        if show_progress:
            print(f"Dataset fits in memory ({strategy['current_memory_mb']:.1f} MB). "
                  "Using standard Monte Carlo integration.")
        
        # Convert back to 1D if original data was 1D
        result = monte_carlo_integral(params, data.squeeze(), p_target, q_sample)
        return result
    
    # Use chunked processing
    if show_progress:
        print(f"Large dataset detected ({strategy['current_memory_mb']:.1f} MB). "
              f"Using chunked processing: {strategy['recommendation']}")
    
    # Warn if q_sample is not provided
    if q_sample is None:
        warnings.warn(
            "Chunked Monte Carlo integration without explicit q_sample may be "
            "less accurate due to KDE estimation across chunks. Consider "
            "providing q_sample explicitly for better results.",
            UserWarning
        )
    
    # Use chunked processor
    processor = ChunkedIntegrationProcessor(
        max_memory_mb=max_memory_mb,
        show_progress=show_progress,
        chunk_size=chunk_size
    )
    
    result = processor.process_monte_carlo_integral(params, data, p_target, q_sample)
    
    # Convert back to 1D if original data was 1D
    if result['integral'].shape == (1,):
        result['integral'] = result['integral'][0]
    if result['uncertainty'].shape == (1,):
        result['uncertainty'] = result['uncertainty'][0]
    
    # Add chunking metadata
    result['chunked_processing'] = True
    result['chunking_strategy'] = strategy
    
    return result


def chunked_qmc_integral(
    bounds: list,
    func: Callable,
    n_samples: int,
    method: str = "sobol",
    *,
    max_memory_mb: float = 1000.0,
    show_progress: bool = True,
    chunk_size: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Quasi-Monte Carlo integration with chunked processing for large sample sets.
    
    Parameters
    ----------
    bounds : list
        List of [low, high] bounds for each dimension
    func : callable
        Function to integrate
    n_samples : int
        Total number of samples to use
    method : str, default="sobol"
        QMC method: "sobol" or "halton"
    max_memory_mb : float, default=1000.0
        Maximum memory usage in MB
    show_progress : bool, default=True
        Whether to show progress bars
    chunk_size : int, optional
        Fixed chunk size. If None, calculated automatically
    **kwargs
        Additional arguments for the QMC method
        
    Returns
    -------
    dict
        Dictionary containing integration results
        
    Examples
    --------
    >>> import numpy as np
    >>> from mcpost.integration import chunked_qmc_integral
    >>> 
    >>> # Define function to integrate
    >>> def test_func(x):
    ...     return np.sum(x**2, axis=1)  # Sum of squares
    >>> 
    >>> # Integrate over unit hypercube
    >>> bounds = [[0, 1], [0, 1], [0, 1]]
    >>> 
    >>> result = chunked_qmc_integral(
    ...     bounds, test_func, n_samples=1000000,  # Large sample count
    ...     method="sobol",
    ...     max_memory_mb=500,
    ...     show_progress=True
    ... )
    >>> 
    >>> print(f"Integral: {result['integral']:.6f}")
    >>> print(f"Expected: {1.0:.6f}")  # Analytical result is 1.0
    """
    n_dims = len(bounds)
    
    # Estimate memory requirements for the full sample set
    # Rough estimate: 8 bytes per float64 * n_dims * n_samples * 2 (for params and function values)
    estimated_memory_mb = (8 * n_dims * n_samples * 2) / (1024 * 1024)
    
    if estimated_memory_mb <= max_memory_mb:
        # Use standard QMC implementation
        if show_progress:
            print(f"Sample set fits in memory ({estimated_memory_mb:.1f} MB). "
                  "Using standard QMC integration.")
        
        from mcpost.integration.quasi_monte_carlo import qmc_integral
        return qmc_integral(bounds, func, n_samples, method, **kwargs)
    
    # Use chunked processing
    if chunk_size is None:
        # Calculate chunk size based on memory constraint
        chunk_size = int((max_memory_mb * 1024 * 1024 * 0.8) / (8 * n_dims * 2))
        chunk_size = max(1000, min(chunk_size, n_samples))  # Reasonable bounds
    
    n_chunks = (n_samples + chunk_size - 1) // chunk_size
    
    if show_progress:
        print(f"Large sample set detected ({estimated_memory_mb:.1f} MB). "
              f"Using {n_chunks} chunks of size {chunk_size}.")
        
        from tqdm import tqdm
        pbar = tqdm(total=n_chunks, desc="QMC Integration", unit="chunks")
    else:
        pbar = None
    
    try:
        # Import QMC sampling functions
        if method.lower() == "sobol":
            from scipy.stats import qmc
            sampler = qmc.Sobol(d=n_dims, scramble=True)
        elif method.lower() == "halton":
            from scipy.stats import qmc
            sampler = qmc.Halton(d=n_dims, scramble=True)
        else:
            raise ValueError(f"Unknown QMC method: {method}")
        
        # Process in chunks
        integral_sum = 0.0
        total_processed = 0
        
        for i in range(n_chunks):
            # Determine chunk size for this iteration
            current_chunk_size = min(chunk_size, n_samples - total_processed)
            
            # Generate QMC samples for this chunk
            unit_samples = sampler.random(current_chunk_size)
            
            # Transform to actual bounds
            samples = np.zeros_like(unit_samples)
            for j, (low, high) in enumerate(bounds):
                samples[:, j] = low + (high - low) * unit_samples[:, j]
            
            # Evaluate function
            values = func(samples)
            
            # Accumulate integral (simple average for QMC)
            chunk_integral = np.mean(values)
            integral_sum += chunk_integral * current_chunk_size
            total_processed += current_chunk_size
            
            if pbar is not None:
                pbar.update(1)
        
        # Final integral estimate
        volume = np.prod([high - low for low, high in bounds])
        integral = (integral_sum / total_processed) * volume
        
        # Rough uncertainty estimate (QMC convergence is O(1/N))
        uncertainty = np.abs(integral) / np.sqrt(n_samples)
        
        result = {
            'integral': integral,
            'uncertainty': uncertainty,
            'n_samples': n_samples,
            'method': method,
            'chunked_processing': True,
            'n_chunks': n_chunks,
            'chunk_size': chunk_size
        }
        
    finally:
        if pbar is not None:
            pbar.close()
    
    return result
"""
Chunked processing utilities for memory-efficient analysis of large datasets.

This module provides utilities for processing large datasets in chunks to
reduce memory usage while maintaining computational accuracy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple, Callable, Iterator
import warnings
from tqdm import tqdm


def estimate_memory_usage(X: np.ndarray, Y: Optional[np.ndarray] = None) -> float:
    """
    Estimate memory usage in MB for arrays.
    
    Parameters
    ----------
    X : np.ndarray
        Input parameter array
    Y : np.ndarray, optional
        Target array
        
    Returns
    -------
    float
        Estimated memory usage in MB
    """
    memory_mb = X.nbytes / (1024 * 1024)
    if Y is not None:
        memory_mb += Y.nbytes / (1024 * 1024)
    return memory_mb


def calculate_optimal_chunk_size(
    n_samples: int,
    n_params: int,
    n_targets: int = 1,
    max_memory_mb: float = 1000.0,
    safety_factor: float = 0.8
) -> int:
    """
    Calculate optimal chunk size based on memory constraints.
    
    Parameters
    ----------
    n_samples : int
        Total number of samples
    n_params : int
        Number of parameters
    n_targets : int, default=1
        Number of target variables
    max_memory_mb : float, default=1000.0
        Maximum memory usage in MB
    safety_factor : float, default=0.8
        Safety factor to account for intermediate computations
        
    Returns
    -------
    int
        Optimal chunk size
    """
    # Estimate memory per sample (8 bytes per float64)
    bytes_per_sample = (n_params + n_targets) * 8
    # Account for intermediate computations (rough estimate)
    bytes_per_sample *= 3  # Factor for temporary arrays
    
    max_bytes = max_memory_mb * 1024 * 1024 * safety_factor
    chunk_size = int(max_bytes / bytes_per_sample)
    
    # Ensure reasonable bounds
    chunk_size = max(100, min(chunk_size, n_samples))
    
    return chunk_size


def chunk_array(
    arr: np.ndarray,
    chunk_size: int,
    axis: int = 0
) -> Iterator[Tuple[np.ndarray, slice]]:
    """
    Generate chunks of an array along specified axis.
    
    Parameters
    ----------
    arr : np.ndarray
        Array to chunk
    chunk_size : int
        Size of each chunk
    axis : int, default=0
        Axis along which to chunk
        
    Yields
    ------
    tuple
        (chunk_array, slice_object) for each chunk
    """
    n_total = arr.shape[axis]
    for start in range(0, n_total, chunk_size):
        end = min(start + chunk_size, n_total)
        slice_obj = slice(start, end)
        
        # Create slice tuple for the specified axis
        slices = [slice(None)] * arr.ndim
        slices[axis] = slice_obj
        
        yield arr[tuple(slices)], slice_obj


class ChunkedProcessor:
    """
    Base class for chunked processing operations.
    
    Provides common functionality for processing large datasets in chunks
    with progress tracking and memory management.
    """
    
    def __init__(
        self,
        max_memory_mb: float = 1000.0,
        show_progress: bool = True,
        chunk_size: Optional[int] = None
    ):
        """
        Initialize chunked processor.
        
        Parameters
        ----------
        max_memory_mb : float, default=1000.0
            Maximum memory usage in MB
        show_progress : bool, default=True
            Whether to show progress bars
        chunk_size : int, optional
            Fixed chunk size. If None, calculated automatically
        """
        self.max_memory_mb = max_memory_mb
        self.show_progress = show_progress
        self.chunk_size = chunk_size
        
    def _get_chunk_size(self, n_samples: int, n_params: int, n_targets: int = 1) -> int:
        """Get chunk size for processing."""
        if self.chunk_size is not None:
            return min(self.chunk_size, n_samples)
        
        return calculate_optimal_chunk_size(
            n_samples, n_params, n_targets, self.max_memory_mb
        )
    
    def _create_progress_bar(self, total: int, desc: str = "Processing") -> Optional[tqdm]:
        """Create progress bar if enabled."""
        if self.show_progress:
            return tqdm(total=total, desc=desc, unit="chunks")
        return None


class ChunkedGSAProcessor(ChunkedProcessor):
    """
    Chunked processor for GSA computations.
    
    Enables memory-efficient GSA analysis for large datasets by processing
    data in chunks and aggregating results appropriately.
    """
    
    def process_screening_metrics(
        self,
        X: np.ndarray,
        y: np.ndarray,
        metric_func: Callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process screening metrics (MI, dCor) in chunks.
        
        Parameters
        ----------
        X : np.ndarray
            Input parameters
        y : np.ndarray
            Target values
        metric_func : callable
            Function to compute metrics on chunks
        **kwargs
            Additional arguments for metric_func
            
        Returns
        -------
        dict
            Aggregated metrics results
        """
        n_samples, n_params = X.shape
        chunk_size = self._get_chunk_size(n_samples, n_params)
        
        if n_samples <= chunk_size:
            # No chunking needed
            return metric_func(X, y, **kwargs)
        
        # Process in chunks
        n_chunks = (n_samples + chunk_size - 1) // chunk_size
        pbar = self._create_progress_bar(n_chunks, "Computing screening metrics")
        
        chunk_results = []
        chunk_weights = []
        
        try:
            for X_chunk, slice_obj in chunk_array(X, chunk_size):
                y_chunk = y[slice_obj]
                
                # Compute metrics for this chunk
                result = metric_func(X_chunk, y_chunk, **kwargs)
                chunk_results.append(result)
                chunk_weights.append(len(X_chunk))
                
                if pbar is not None:
                    pbar.update(1)
                    
        finally:
            if pbar is not None:
                pbar.close()
        
        # Aggregate results
        return self._aggregate_screening_results(chunk_results, chunk_weights)
    
    def _aggregate_screening_results(
        self,
        chunk_results: List[Dict[str, Any]],
        chunk_weights: List[int]
    ) -> Dict[str, Any]:
        """
        Aggregate screening results from multiple chunks.
        
        For metrics like MI and dCor, we compute weighted averages.
        For models like RF, we use the largest chunk's model as representative.
        """
        total_weight = sum(chunk_weights)
        weights = np.array(chunk_weights) / total_weight
        
        # Aggregate MI and dCor as weighted averages, handling NaN values
        mi_values = np.array([result["mi"] for result in chunk_results])
        dcor_values = np.array([result["dcor"] for result in chunk_results])
        
        # Use nanmean for aggregation to handle NaN values from small chunks
        aggregated = {
            "MI": np.nanmean(mi_values, axis=0) if not np.isnan(mi_values).all() else mi_values[0],
            "dCor": np.nanmean(dcor_values, axis=0) if not np.isnan(dcor_values).all() else dcor_values[0],
        }
        
        # For permutation importance, aggregate if available
        if "PermMean" in chunk_results[0]:
            perm_mean = np.array([result["PermMean"] for result in chunk_results])
            perm_std = np.array([result["PermStd"] for result in chunk_results])
            
            aggregated["PermMean"] = np.average(perm_mean, axis=0, weights=weights)
            # For std, use pooled standard deviation formula
            aggregated["PermStd"] = np.sqrt(np.average(perm_std**2, axis=0, weights=weights))
        
        # Use the model from the largest chunk as representative
        largest_chunk_idx = np.argmax(chunk_weights)
        aggregated["rf_model"] = chunk_results[largest_chunk_idx]["rf_model"]
        
        # Include test data from largest chunk
        if "Xte" in chunk_results[largest_chunk_idx]:
            aggregated["Xte"] = chunk_results[largest_chunk_idx]["Xte"]
            aggregated["yte"] = chunk_results[largest_chunk_idx]["yte"]
        
        return aggregated


class ChunkedIntegrationProcessor(ChunkedProcessor):
    """
    Chunked processor for Monte Carlo integration.
    
    Enables memory-efficient integration for large sample sets by processing
    in chunks and properly aggregating the results.
    """
    
    def process_monte_carlo_integral(
        self,
        params: np.ndarray,
        data: np.ndarray,
        p_target: Callable,
        q_sample: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Process Monte Carlo integral in chunks.
        
        Parameters
        ----------
        params : np.ndarray
            Parameter samples
        data : np.ndarray
            Function values
        p_target : callable
            Target PDF
        q_sample : callable, optional
            Sampling PDF
            
        Returns
        -------
        dict
            Integration results
        """
        n_samples, n_params = params.shape
        n_data = data.shape[1] if data.ndim > 1 else 1
        
        chunk_size = self._get_chunk_size(n_samples, n_params, n_data)
        
        if n_samples <= chunk_size:
            # No chunking needed - use original function
            from mcpost.integration.monte_carlo import monte_carlo_integral
            return monte_carlo_integral(params, data, p_target, q_sample)
        
        # Process in chunks
        n_chunks = (n_samples + chunk_size - 1) // chunk_size
        pbar = self._create_progress_bar(n_chunks, "Computing MC integral")
        
        chunk_integrals = []
        chunk_weights = []
        all_weights = []
        
        try:
            for params_chunk, slice_obj in chunk_array(params, chunk_size):
                data_chunk = data[slice_obj]
                
                # Evaluate PDFs for this chunk
                p_vals = p_target(params_chunk)
                
                if q_sample is not None:
                    q_vals = q_sample(params_chunk)
                else:
                    # For chunked processing, we need to estimate q from all data
                    # This is a limitation - for now, require q_sample for chunked processing
                    warnings.warn(
                        "Chunked processing with KDE estimation of q_sample is not "
                        "recommended. Consider providing q_sample explicitly.",
                        UserWarning
                    )
                    from scipy.stats import gaussian_kde
                    kde = gaussian_kde(params.T)  # Use all data for KDE
                    q_vals = kde(params_chunk.T)
                
                # Compute weights for this chunk
                weights = p_vals / q_vals
                chunk_weight = np.sum(weights)
                
                # Weighted integral for this chunk
                if data_chunk.ndim == 1:
                    data_chunk = data_chunk[:, None]
                
                chunk_integral = np.sum(weights[:, None] * data_chunk, axis=0)
                
                chunk_integrals.append(chunk_integral)
                chunk_weights.append(chunk_weight)
                all_weights.extend(weights)
                
                if pbar is not None:
                    pbar.update(1)
                    
        finally:
            if pbar is not None:
                pbar.close()
        
        # Aggregate results
        total_weight = sum(chunk_weights)
        final_integral = sum(chunk_integrals) / total_weight
        
        # Estimate uncertainty (simplified)
        all_weights = np.array(all_weights)
        all_weights /= np.sum(all_weights)
        
        # Effective sample size
        eff_sample_size = 1.0 / np.sum(all_weights**2)
        
        # Rough uncertainty estimate
        uncertainty = np.std(final_integral) / np.sqrt(eff_sample_size)
        if np.isscalar(uncertainty):
            uncertainty = np.array([uncertainty])
        
        return {
            'integral': final_integral,
            'uncertainty': uncertainty,
            'weights': all_weights,
            'effective_sample_size': eff_sample_size
        }


def suggest_chunking_strategy(
    X: np.ndarray,
    Y: Optional[np.ndarray] = None,
    max_memory_mb: float = 1000.0
) -> Dict[str, Any]:
    """
    Suggest chunking strategy for given data.
    
    Parameters
    ----------
    X : np.ndarray
        Input parameter array
    Y : np.ndarray, optional
        Target array
    max_memory_mb : float, default=1000.0
        Maximum memory constraint in MB
        
    Returns
    -------
    dict
        Dictionary with chunking recommendations
    """
    n_samples, n_params = X.shape
    n_targets = Y.shape[1] if Y is not None and Y.ndim > 1 else 1
    
    current_memory = estimate_memory_usage(X, Y)
    
    if current_memory <= max_memory_mb:
        return {
            "needs_chunking": False,
            "current_memory_mb": current_memory,
            "recommendation": "No chunking needed - data fits in memory"
        }
    
    chunk_size = calculate_optimal_chunk_size(
        n_samples, n_params, n_targets, max_memory_mb
    )
    
    n_chunks = (n_samples + chunk_size - 1) // chunk_size
    memory_per_chunk = current_memory / n_chunks
    
    return {
        "needs_chunking": True,
        "current_memory_mb": current_memory,
        "max_memory_mb": max_memory_mb,
        "recommended_chunk_size": chunk_size,
        "n_chunks": n_chunks,
        "memory_per_chunk_mb": memory_per_chunk,
        "recommendation": f"Use {n_chunks} chunks of size {chunk_size} "
                         f"({memory_per_chunk:.1f} MB per chunk)"
    }
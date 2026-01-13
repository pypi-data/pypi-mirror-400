"""
Performance benchmarks for GSA methods.

This module provides benchmarking utilities to measure and compare
the performance of different GSA methods across various dataset sizes
and parameter configurations.
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
import psutil
import os
from dataclasses import dataclass
import warnings

from mcpost.gsa import gsa_for_target, chunked_gsa_for_target
from mcpost.gsa.base import BaseSensitivityMethod


@dataclass
class BenchmarkResult:
    """
    Container for benchmark results.
    
    Attributes
    ----------
    method_name : str
        Name of the benchmarked method
    dataset_size : tuple
        (n_samples, n_params) of the test dataset
    execution_time : float
        Total execution time in seconds
    memory_peak : float
        Peak memory usage in MB
    memory_baseline : float
        Baseline memory usage before execution in MB
    accuracy_metrics : Dict[str, float]
        Accuracy metrics (if ground truth available)
    metadata : Dict[str, Any]
        Additional benchmark metadata
    """
    method_name: str
    dataset_size: tuple
    execution_time: float
    memory_peak: float
    memory_baseline: float
    accuracy_metrics: Dict[str, float]
    metadata: Dict[str, Any]
    
    @property
    def memory_used(self) -> float:
        """Memory used during execution (peak - baseline)."""
        return self.memory_peak - self.memory_baseline
    
    @property
    def samples_per_second(self) -> float:
        """Processing rate in samples per second."""
        return self.dataset_size[0] / self.execution_time if self.execution_time > 0 else 0.0


class GSABenchmark:
    """
    Benchmark suite for GSA methods.
    
    Provides comprehensive benchmarking capabilities including performance
    measurement, memory profiling, and accuracy assessment.
    
    Examples
    --------
    >>> benchmark = GSABenchmark()
    >>> 
    >>> # Run standard benchmark suite
    >>> results = benchmark.run_standard_suite()
    >>> benchmark.print_summary(results)
    >>> 
    >>> # Benchmark custom method
    >>> def custom_gsa(X, y, **kwargs):
    ...     # Custom GSA implementation
    ...     return gsa_for_target(X, y, **kwargs)
    >>> 
    >>> result = benchmark.benchmark_method(
    ...     custom_gsa, "CustomGSA", n_samples=1000, n_params=10
    ... )
    >>> print(f"Execution time: {result.execution_time:.2f}s")
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize benchmark suite.
        
        Parameters
        ----------
        random_state : int, default=42
            Random seed for reproducible benchmarks
        """
        self.random_state = random_state
        np.random.seed(random_state)
        
    def generate_test_data(
        self, 
        n_samples: int, 
        n_params: int,
        function_type: str = "ishigami"
    ) -> tuple:
        """
        Generate synthetic test data for benchmarking.
        
        Parameters
        ----------
        n_samples : int
            Number of samples
        n_params : int
            Number of parameters
        function_type : str, default="ishigami"
            Type of test function: "ishigami", "linear", "polynomial", "sobol_g"
            
        Returns
        -------
        tuple
            (X, y, true_sensitivity) where true_sensitivity is known ground truth
        """
        np.random.seed(self.random_state)
        
        if function_type == "ishigami" and n_params >= 3:
            # Ishigami function (first 3 params matter, rest are noise)
            X = np.random.uniform(-np.pi, np.pi, (n_samples, n_params))
            y = (np.sin(X[:, 0]) + 
                 7 * np.sin(X[:, 1])**2 + 
                 0.1 * X[:, 2]**4 * np.sin(X[:, 0]))
            
            # Add noise from remaining parameters
            if n_params > 3:
                y += 0.01 * np.sum(X[:, 3:], axis=1)
            
            # True sensitivity ranking: x0 > x1 > x2 > others
            true_sensitivity = np.zeros(n_params)
            true_sensitivity[0] = 1.0  # Most important
            true_sensitivity[1] = 0.8  # Second most important
            true_sensitivity[2] = 0.3  # Third most important
            # Others remain 0
            
        elif function_type == "linear":
            # Linear function with known coefficients
            X = np.random.uniform(-1, 1, (n_samples, n_params))
            coeffs = np.random.exponential(1.0, n_params)
            coeffs = coeffs / np.sum(coeffs)  # Normalize
            y = X @ coeffs + 0.1 * np.random.normal(0, 1, n_samples)
            
            true_sensitivity = coeffs / np.max(coeffs)  # Normalized importance
            
        elif function_type == "polynomial":
            # Polynomial function
            X = np.random.uniform(-1, 1, (n_samples, n_params))
            y = (2 * X[:, 0]**2 + 
                 X[:, 1] + 
                 0.5 * X[:, 2]**3)
            
            if n_params > 3:
                y += 0.1 * np.sum(X[:, 3:], axis=1)
            
            true_sensitivity = np.zeros(n_params)
            true_sensitivity[0] = 1.0  # x0^2 term
            true_sensitivity[1] = 0.5  # x1 linear term
            true_sensitivity[2] = 0.3  # x2^3 term
            
        elif function_type == "sobol_g":
            # Sobol G-function
            X = np.random.uniform(0, 1, (n_samples, n_params))
            a = np.arange(n_params, dtype=float)  # Importance decreases with index
            
            y = np.ones(n_samples)
            for i in range(n_params):
                y *= (np.abs(4 * X[:, i] - 2) + a[i]) / (1 + a[i])
            
            # True sensitivity (approximate)
            true_sensitivity = 1.0 / (1 + a)
            true_sensitivity = true_sensitivity / np.max(true_sensitivity)
            
        else:
            raise ValueError(f"Unknown function type: {function_type}")
        
        return X, y, true_sensitivity
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    
    def benchmark_method(
        self,
        method_func: Callable,
        method_name: str,
        n_samples: int,
        n_params: int,
        function_type: str = "ishigami",
        **method_kwargs
    ) -> BenchmarkResult:
        """
        Benchmark a single GSA method.
        
        Parameters
        ----------
        method_func : callable
            GSA method to benchmark
        method_name : str
            Name of the method
        n_samples : int
            Number of samples in test dataset
        n_params : int
            Number of parameters in test dataset
        function_type : str, default="ishigami"
            Type of test function
        **method_kwargs
            Additional arguments for the method
            
        Returns
        -------
        BenchmarkResult
            Benchmark results
        """
        # Generate test data
        X, y, true_sensitivity = self.generate_test_data(
            n_samples, n_params, function_type
        )
        
        # Measure baseline memory
        memory_baseline = self.get_memory_usage()
        
        # Benchmark execution
        start_time = time.time()
        
        try:
            if hasattr(method_func, 'compute_sensitivity'):
                # Method is a class instance
                result = method_func.compute_sensitivity(X, y, **method_kwargs)
                sensitivity_values = result.sensitivity_values
            else:
                # Method is a function
                table, extras = method_func(X, y, **method_kwargs)
                sensitivity_values = table["MI"].values  # Use MI as default metric
                
        except Exception as e:
            warnings.warn(f"Method {method_name} failed: {str(e)}")
            return BenchmarkResult(
                method_name=method_name,
                dataset_size=(n_samples, n_params),
                execution_time=float('inf'),
                memory_peak=memory_baseline,
                memory_baseline=memory_baseline,
                accuracy_metrics={"error": float('inf')},
                metadata={"error": str(e)}
            )
        
        execution_time = time.time() - start_time
        memory_peak = self.get_memory_usage()
        
        # Compute accuracy metrics
        accuracy_metrics = self._compute_accuracy_metrics(
            sensitivity_values, true_sensitivity
        )
        
        return BenchmarkResult(
            method_name=method_name,
            dataset_size=(n_samples, n_params),
            execution_time=execution_time,
            memory_peak=memory_peak,
            memory_baseline=memory_baseline,
            accuracy_metrics=accuracy_metrics,
            metadata={
                "function_type": function_type,
                "method_kwargs": method_kwargs
            }
        )
    
    def _compute_accuracy_metrics(
        self, 
        computed_sensitivity: np.ndarray,
        true_sensitivity: np.ndarray
    ) -> Dict[str, float]:
        """Compute accuracy metrics comparing computed vs true sensitivity."""
        # Normalize both to [0, 1] range
        computed_norm = computed_sensitivity / np.max(computed_sensitivity) if np.max(computed_sensitivity) > 0 else computed_sensitivity
        true_norm = true_sensitivity / np.max(true_sensitivity) if np.max(true_sensitivity) > 0 else true_sensitivity
        
        # Mean squared error
        mse = np.mean((computed_norm - true_norm)**2)
        
        # Ranking correlation (Spearman)
        from scipy.stats import spearmanr
        rank_corr, _ = spearmanr(computed_sensitivity, true_sensitivity)
        rank_corr = 0.0 if np.isnan(rank_corr) else rank_corr
        
        # Top-k accuracy (fraction of top 3 parameters correctly identified)
        k = min(3, len(true_sensitivity))
        true_top_k = set(np.argsort(true_sensitivity)[-k:])
        computed_top_k = set(np.argsort(computed_sensitivity)[-k:])
        top_k_accuracy = len(true_top_k & computed_top_k) / k
        
        return {
            "mse": mse,
            "rank_correlation": rank_corr,
            "top_k_accuracy": top_k_accuracy
        }
    
    def run_scaling_benchmark(
        self,
        method_func: Callable,
        method_name: str,
        sample_sizes: List[int] = None,
        param_counts: List[int] = None,
        function_type: str = "ishigami"
    ) -> List[BenchmarkResult]:
        """
        Run scaling benchmark across different dataset sizes.
        
        Parameters
        ----------
        method_func : callable
            GSA method to benchmark
        method_name : str
            Name of the method
        sample_sizes : List[int], optional
            List of sample sizes to test
        param_counts : List[int], optional
            List of parameter counts to test
        function_type : str, default="ishigami"
            Type of test function
            
        Returns
        -------
        List[BenchmarkResult]
            List of benchmark results
        """
        if sample_sizes is None:
            sample_sizes = [100, 500, 1000, 2000, 5000]
        if param_counts is None:
            param_counts = [5, 10, 20, 50]
        
        results = []
        
        # Test scaling with sample size (fixed params)
        fixed_params = 10
        for n_samples in sample_sizes:
            result = self.benchmark_method(
                method_func, f"{method_name}_samples_{n_samples}",
                n_samples, fixed_params, function_type
            )
            results.append(result)
        
        # Test scaling with parameter count (fixed samples)
        fixed_samples = 1000
        for n_params in param_counts:
            result = self.benchmark_method(
                method_func, f"{method_name}_params_{n_params}",
                fixed_samples, n_params, function_type
            )
            results.append(result)
        
        return results
    
    def run_standard_suite(self) -> List[BenchmarkResult]:
        """
        Run standard benchmark suite comparing different GSA methods.
        
        Returns
        -------
        List[BenchmarkResult]
            Benchmark results for all methods
        """
        results = []
        
        # Standard test configuration
        n_samples = 1000
        n_params = 10
        
        # Test standard GSA
        def standard_gsa(X, y, **kwargs):
            return gsa_for_target(X, y, enable_sobol=False, make_pdp=False, **kwargs)
        
        result = self.benchmark_method(
            standard_gsa, "StandardGSA", n_samples, n_params
        )
        results.append(result)
        
        # Test chunked GSA
        def chunked_gsa(X, y, **kwargs):
            return chunked_gsa_for_target(
                X, y, max_memory_mb=100, show_progress=False,
                enable_sobol=False, make_pdp=False, **kwargs
            )
        
        result = self.benchmark_method(
            chunked_gsa, "ChunkedGSA", n_samples, n_params
        )
        results.append(result)
        
        # Test with different configurations
        configs = [
            {"enable_perm": False, "name_suffix": "_NoPerm"},
            {"enable_gp": False, "name_suffix": "_NoGP"},
            {"scaler": None, "name_suffix": "_NoScaling"}
        ]
        
        for config in configs:
            name_suffix = config.pop("name_suffix")
            result = self.benchmark_method(
                standard_gsa, f"StandardGSA{name_suffix}", 
                n_samples, n_params, **config
            )
            results.append(result)
        
        return results
    
    def compare_methods(
        self,
        methods: Dict[str, Callable],
        n_samples: int = 1000,
        n_params: int = 10,
        function_type: str = "ishigami"
    ) -> pd.DataFrame:
        """
        Compare multiple GSA methods side by side.
        
        Parameters
        ----------
        methods : Dict[str, Callable]
            Dictionary mapping method names to method functions
        n_samples : int, default=1000
            Number of samples in test dataset
        n_params : int, default=10
            Number of parameters in test dataset
        function_type : str, default="ishigami"
            Type of test function
            
        Returns
        -------
        pd.DataFrame
            Comparison results
        """
        results = []
        
        for method_name, method_func in methods.items():
            result = self.benchmark_method(
                method_func, method_name, n_samples, n_params, function_type
            )
            results.append(result)
        
        # Convert to DataFrame
        data = []
        for result in results:
            data.append({
                "Method": result.method_name,
                "Execution_Time_s": result.execution_time,
                "Memory_Used_MB": result.memory_used,
                "Samples_per_Second": result.samples_per_second,
                "MSE": result.accuracy_metrics.get("mse", np.nan),
                "Rank_Correlation": result.accuracy_metrics.get("rank_correlation", np.nan),
                "Top_K_Accuracy": result.accuracy_metrics.get("top_k_accuracy", np.nan)
            })
        
        df = pd.DataFrame(data)
        return df.sort_values("Execution_Time_s")
    
    def print_summary(self, results: List[BenchmarkResult]) -> None:
        """Print a summary of benchmark results."""
        print("GSA Benchmark Results")
        print("=" * 50)
        
        for result in results:
            print(f"\nMethod: {result.method_name}")
            print(f"Dataset: {result.dataset_size[0]} samples, {result.dataset_size[1]} params")
            print(f"Execution time: {result.execution_time:.3f}s")
            print(f"Memory used: {result.memory_used:.1f} MB")
            print(f"Processing rate: {result.samples_per_second:.0f} samples/s")
            
            if "mse" in result.accuracy_metrics:
                print(f"Accuracy - MSE: {result.accuracy_metrics['mse']:.4f}")
                print(f"Accuracy - Rank correlation: {result.accuracy_metrics['rank_correlation']:.3f}")
                print(f"Accuracy - Top-3 accuracy: {result.accuracy_metrics['top_k_accuracy']:.3f}")


def run_gsa_benchmarks():
    """Run comprehensive GSA benchmarks and save results."""
    benchmark = GSABenchmark()
    
    print("Running GSA benchmark suite...")
    
    # Run standard suite
    results = benchmark.run_standard_suite()
    benchmark.print_summary(results)
    
    # Save results to CSV
    data = []
    for result in results:
        row = {
            "method": result.method_name,
            "n_samples": result.dataset_size[0],
            "n_params": result.dataset_size[1],
            "execution_time": result.execution_time,
            "memory_used": result.memory_used,
            "samples_per_second": result.samples_per_second,
        }
        row.update(result.accuracy_metrics)
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv("gsa_benchmark_results.csv", index=False)
    print(f"\nResults saved to gsa_benchmark_results.csv")
    
    return results


if __name__ == "__main__":
    run_gsa_benchmarks()
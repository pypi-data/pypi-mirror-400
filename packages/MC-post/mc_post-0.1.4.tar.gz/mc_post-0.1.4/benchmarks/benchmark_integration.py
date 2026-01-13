"""
Performance benchmarks for Monte Carlo integration methods.

This module provides benchmarking utilities to measure and compare
the performance of different integration methods across various
problem dimensions and sample sizes.
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Tuple
import psutil
import os
from dataclasses import dataclass
import warnings

from mcpost.integration import monte_carlo_integral, qmc_integral
from mcpost.integration.chunked_integration import chunked_monte_carlo_integral
from mcpost.integration.base import BaseIntegrationMethod


@dataclass
class IntegrationBenchmarkResult:
    """
    Container for integration benchmark results.
    
    Attributes
    ----------
    method_name : str
        Name of the benchmarked method
    problem_config : Dict[str, Any]
        Problem configuration (dimensions, bounds, etc.)
    n_samples : int
        Number of samples used
    execution_time : float
        Total execution time in seconds
    memory_peak : float
        Peak memory usage in MB
    memory_baseline : float
        Baseline memory usage before execution in MB
    integral_estimate : float
        Computed integral estimate
    uncertainty : float
        Uncertainty estimate
    true_value : float
        True integral value (if known)
    metadata : Dict[str, Any]
        Additional benchmark metadata
    """
    method_name: str
    problem_config: Dict[str, Any]
    n_samples: int
    execution_time: float
    memory_peak: float
    memory_baseline: float
    integral_estimate: float
    uncertainty: float
    true_value: float
    metadata: Dict[str, Any]
    
    @property
    def memory_used(self) -> float:
        """Memory used during execution (peak - baseline)."""
        return self.memory_peak - self.memory_baseline
    
    @property
    def samples_per_second(self) -> float:
        """Processing rate in samples per second."""
        return self.n_samples / self.execution_time if self.execution_time > 0 else 0.0
    
    @property
    def absolute_error(self) -> float:
        """Absolute error compared to true value."""
        return abs(self.integral_estimate - self.true_value)
    
    @property
    def relative_error(self) -> float:
        """Relative error compared to true value."""
        if self.true_value != 0:
            return abs(self.integral_estimate - self.true_value) / abs(self.true_value)
        else:
            return abs(self.integral_estimate)
    
    @property
    def efficiency(self) -> float:
        """Efficiency metric: 1 / (relative_error^2 * execution_time)."""
        if self.relative_error > 0 and self.execution_time > 0:
            return 1.0 / (self.relative_error**2 * self.execution_time)
        else:
            return 0.0


class IntegrationBenchmark:
    """
    Benchmark suite for Monte Carlo integration methods.
    
    Provides comprehensive benchmarking capabilities including performance
    measurement, memory profiling, and accuracy assessment for various
    integration problems.
    
    Examples
    --------
    >>> benchmark = IntegrationBenchmark()
    >>> 
    >>> # Run standard benchmark suite
    >>> results = benchmark.run_standard_suite()
    >>> benchmark.print_summary(results)
    >>> 
    >>> # Benchmark custom method
    >>> def custom_integration(func, bounds, n_samples):
    ...     # Custom integration implementation
    ...     return monte_carlo_integral(params, data, p_target)
    >>> 
    >>> result = benchmark.benchmark_method(
    ...     custom_integration, "CustomMC", n_dims=3, n_samples=10000
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
    
    def get_test_problems(self) -> Dict[str, Dict[str, Any]]:
        """
        Get dictionary of standard test problems with known solutions.
        
        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary mapping problem names to problem configurations
        """
        problems = {
            "unit_hypercube": {
                "func": lambda x: np.ones(len(x)),
                "bounds": [(0, 1), (0, 1), (0, 1)],
                "true_value": 1.0,
                "description": "Integral of 1 over unit cube"
            },
            
            "quadratic": {
                "func": lambda x: np.sum(x**2, axis=1),
                "bounds": [(0, 1), (0, 1), (0, 1)],
                "true_value": 1.0,  # Integral of x^2 + y^2 + z^2 over [0,1]^3
                "description": "Sum of squares"
            },
            
            "gaussian": {
                "func": lambda x: np.exp(-0.5 * np.sum(x**2, axis=1)),
                "bounds": [(-3, 3), (-3, 3)],
                "true_value": 2 * np.pi,  # Approximate for 2D Gaussian
                "description": "2D Gaussian function"
            },
            
            "oscillatory": {
                "func": lambda x: np.cos(np.sum(x, axis=1)),
                "bounds": [(0, np.pi), (0, np.pi)],
                "true_value": 0.0,  # cos(x+y) integrated over [0,π]×[0,π]
                "description": "Oscillatory function"
            },
            
            "polynomial": {
                "func": lambda x: np.prod(x, axis=1),  # Product of coordinates
                "bounds": [(0, 1), (0, 1), (0, 1), (0, 1)],
                "true_value": 1.0 / (2**4),  # 1/16 for 4D unit cube
                "description": "Product of coordinates"
            },
            
            "peak": {
                "func": lambda x: np.exp(-100 * np.sum((x - 0.5)**2, axis=1)),
                "bounds": [(0, 1), (0, 1)],
                "true_value": np.pi / 100,  # Approximate for narrow Gaussian
                "description": "Sharp peak at center"
            }
        }
        
        return problems
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    
    def benchmark_method(
        self,
        method_func: Callable,
        method_name: str,
        problem_name: str = "quadratic",
        n_samples: int = 10000,
        **method_kwargs
    ) -> IntegrationBenchmarkResult:
        """
        Benchmark a single integration method on a test problem.
        
        Parameters
        ----------
        method_func : callable
            Integration method to benchmark
        method_name : str
            Name of the method
        problem_name : str, default="quadratic"
            Name of test problem
        n_samples : int, default=10000
            Number of samples to use
        **method_kwargs
            Additional arguments for the method
            
        Returns
        -------
        IntegrationBenchmarkResult
            Benchmark results
        """
        problems = self.get_test_problems()
        
        if problem_name not in problems:
            raise ValueError(f"Unknown problem: {problem_name}")
        
        problem = problems[problem_name]
        func = problem["func"]
        bounds = problem["bounds"]
        true_value = problem["true_value"]
        
        # Measure baseline memory
        memory_baseline = self.get_memory_usage()
        
        # Benchmark execution
        start_time = time.time()
        
        try:
            if hasattr(method_func, 'integrate'):
                # Method is a class instance
                result = method_func.integrate(func, bounds, n_samples, **method_kwargs)
                integral_estimate = result.integral
                uncertainty = result.uncertainty
            else:
                # Method is a function - need to adapt interface
                if "chunked" in method_name.lower():
                    # Chunked methods need different interface
                    # Generate samples and function values
                    np.random.seed(self.random_state)
                    n_dims = len(bounds)
                    params = np.random.random((n_samples, n_dims))
                    for i, (low, high) in enumerate(bounds):
                        params[:, i] = low + params[:, i] * (high - low)
                    
                    data = func(params)
                    
                    # Define target and sampling PDFs
                    volume = np.prod([high - low for low, high in bounds])
                    
                    def target_pdf(theta):
                        return np.ones(len(theta)) / volume
                    
                    def sample_pdf(theta):
                        return np.ones(len(theta)) / volume
                    
                    result = method_func(params, data, target_pdf, sample_pdf, **method_kwargs)
                    integral_estimate = result['integral']
                    uncertainty = result['uncertainty']
                else:
                    # Standard function interface
                    result = method_func(func, bounds, n_samples, **method_kwargs)
                    if isinstance(result, dict):
                        integral_estimate = result['integral']
                        uncertainty = result.get('uncertainty', 0.0)
                    else:
                        integral_estimate = result
                        uncertainty = 0.0
                        
        except Exception as e:
            warnings.warn(f"Method {method_name} failed: {str(e)}")
            return IntegrationBenchmarkResult(
                method_name=method_name,
                problem_config=problem,
                n_samples=n_samples,
                execution_time=float('inf'),
                memory_peak=memory_baseline,
                memory_baseline=memory_baseline,
                integral_estimate=float('nan'),
                uncertainty=float('inf'),
                true_value=true_value,
                metadata={"error": str(e)}
            )
        
        execution_time = time.time() - start_time
        memory_peak = self.get_memory_usage()
        
        return IntegrationBenchmarkResult(
            method_name=method_name,
            problem_config=problem,
            n_samples=n_samples,
            execution_time=execution_time,
            memory_peak=memory_peak,
            memory_baseline=memory_baseline,
            integral_estimate=float(integral_estimate),
            uncertainty=float(uncertainty),
            true_value=true_value,
            metadata={
                "problem_name": problem_name,
                "method_kwargs": method_kwargs
            }
        )
    
    def run_convergence_study(
        self,
        method_func: Callable,
        method_name: str,
        problem_name: str = "quadratic",
        sample_sizes: List[int] = None
    ) -> List[IntegrationBenchmarkResult]:
        """
        Study convergence behavior across different sample sizes.
        
        Parameters
        ----------
        method_func : callable
            Integration method to study
        method_name : str
            Name of the method
        problem_name : str, default="quadratic"
            Test problem name
        sample_sizes : List[int], optional
            List of sample sizes to test
            
        Returns
        -------
        List[IntegrationBenchmarkResult]
            Convergence study results
        """
        if sample_sizes is None:
            sample_sizes = [100, 500, 1000, 2000, 5000, 10000, 20000]
        
        results = []
        for n_samples in sample_sizes:
            result = self.benchmark_method(
                method_func, f"{method_name}_{n_samples}", 
                problem_name, n_samples
            )
            results.append(result)
        
        return results
    
    def run_dimension_scaling(
        self,
        method_func: Callable,
        method_name: str,
        dimensions: List[int] = None,
        n_samples: int = 10000
    ) -> List[IntegrationBenchmarkResult]:
        """
        Study scaling behavior across different problem dimensions.
        
        Parameters
        ----------
        method_func : callable
            Integration method to study
        method_name : str
            Name of the method
        dimensions : List[int], optional
            List of dimensions to test
        n_samples : int, default=10000
            Number of samples to use
            
        Returns
        -------
        List[IntegrationBenchmarkResult]
            Dimension scaling results
        """
        if dimensions is None:
            dimensions = [2, 3, 4, 5, 6, 8, 10]
        
        results = []
        
        for n_dims in dimensions:
            # Create n-dimensional quadratic problem
            def func(x):
                return np.sum(x**2, axis=1)
            
            bounds = [(0, 1) for _ in range(n_dims)]
            true_value = n_dims / 3.0  # Integral of sum(x_i^2) over [0,1]^n
            
            problem = {
                "func": func,
                "bounds": bounds,
                "true_value": true_value,
                "description": f"{n_dims}D quadratic"
            }
            
            # Measure baseline memory
            memory_baseline = self.get_memory_usage()
            
            # Benchmark execution
            start_time = time.time()
            
            try:
                if hasattr(method_func, 'integrate'):
                    result = method_func.integrate(func, bounds, n_samples)
                    integral_estimate = result.integral
                    uncertainty = result.uncertainty
                else:
                    result = method_func(func, bounds, n_samples)
                    if isinstance(result, dict):
                        integral_estimate = result['integral']
                        uncertainty = result.get('uncertainty', 0.0)
                    else:
                        integral_estimate = result
                        uncertainty = 0.0
                        
            except Exception as e:
                warnings.warn(f"Method {method_name} failed for {n_dims}D: {str(e)}")
                continue
            
            execution_time = time.time() - start_time
            memory_peak = self.get_memory_usage()
            
            benchmark_result = IntegrationBenchmarkResult(
                method_name=f"{method_name}_{n_dims}D",
                problem_config=problem,
                n_samples=n_samples,
                execution_time=execution_time,
                memory_peak=memory_peak,
                memory_baseline=memory_baseline,
                integral_estimate=float(integral_estimate),
                uncertainty=float(uncertainty),
                true_value=true_value,
                metadata={"n_dims": n_dims}
            )
            
            results.append(benchmark_result)
        
        return results
    
    def run_standard_suite(self) -> List[IntegrationBenchmarkResult]:
        """
        Run standard benchmark suite comparing different integration methods.
        
        Returns
        -------
        List[IntegrationBenchmarkResult]
            Benchmark results for all methods
        """
        results = []
        
        # Standard test configuration
        n_samples = 10000
        test_problems = ["quadratic", "gaussian", "oscillatory"]
        
        # Test standard Monte Carlo
        for problem in test_problems:
            result = self.benchmark_method(
                monte_carlo_integral, "StandardMC", problem, n_samples
            )
            results.append(result)
        
        # Test QMC (if available)
        try:
            for problem in test_problems:
                result = self.benchmark_method(
                    qmc_integral, "QMC", problem, n_samples
                )
                results.append(result)
        except Exception as e:
            warnings.warn(f"QMC benchmarking failed: {str(e)}")
        
        # Test chunked Monte Carlo
        for problem in test_problems:
            result = self.benchmark_method(
                chunked_monte_carlo_integral, "ChunkedMC", problem, n_samples,
                max_memory_mb=50, show_progress=False
            )
            results.append(result)
        
        return results
    
    def compare_methods(
        self,
        methods: Dict[str, Callable],
        problem_name: str = "quadratic",
        n_samples: int = 10000
    ) -> pd.DataFrame:
        """
        Compare multiple integration methods side by side.
        
        Parameters
        ----------
        methods : Dict[str, Callable]
            Dictionary mapping method names to method functions
        problem_name : str, default="quadratic"
            Test problem name
        n_samples : int, default=10000
            Number of samples to use
            
        Returns
        -------
        pd.DataFrame
            Comparison results
        """
        results = []
        
        for method_name, method_func in methods.items():
            result = self.benchmark_method(
                method_func, method_name, problem_name, n_samples
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
                "Integral_Estimate": result.integral_estimate,
                "True_Value": result.true_value,
                "Absolute_Error": result.absolute_error,
                "Relative_Error": result.relative_error,
                "Efficiency": result.efficiency
            })
        
        df = pd.DataFrame(data)
        return df.sort_values("Efficiency", ascending=False)
    
    def print_summary(self, results: List[IntegrationBenchmarkResult]) -> None:
        """Print a summary of benchmark results."""
        print("Integration Benchmark Results")
        print("=" * 60)
        
        for result in results:
            print(f"\nMethod: {result.method_name}")
            print(f"Problem: {result.metadata.get('problem_name', 'Unknown')}")
            print(f"Samples: {result.n_samples}")
            print(f"Execution time: {result.execution_time:.3f}s")
            print(f"Memory used: {result.memory_used:.1f} MB")
            print(f"Processing rate: {result.samples_per_second:.0f} samples/s")
            print(f"Integral estimate: {result.integral_estimate:.6f}")
            print(f"True value: {result.true_value:.6f}")
            print(f"Absolute error: {result.absolute_error:.6f}")
            print(f"Relative error: {result.relative_error:.2%}")
            print(f"Efficiency: {result.efficiency:.2e}")


def run_integration_benchmarks():
    """Run comprehensive integration benchmarks and save results."""
    benchmark = IntegrationBenchmark()
    
    print("Running integration benchmark suite...")
    
    # Run standard suite
    results = benchmark.run_standard_suite()
    benchmark.print_summary(results)
    
    # Save results to CSV
    data = []
    for result in results:
        row = {
            "method": result.method_name,
            "problem": result.metadata.get("problem_name", "Unknown"),
            "n_samples": result.n_samples,
            "execution_time": result.execution_time,
            "memory_used": result.memory_used,
            "samples_per_second": result.samples_per_second,
            "integral_estimate": result.integral_estimate,
            "true_value": result.true_value,
            "absolute_error": result.absolute_error,
            "relative_error": result.relative_error,
            "efficiency": result.efficiency
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv("integration_benchmark_results.csv", index=False)
    print(f"\nResults saved to integration_benchmark_results.csv")
    
    return results


if __name__ == "__main__":
    run_integration_benchmarks()
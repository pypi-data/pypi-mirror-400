"""
Profiling utilities for performance analysis and optimization.

This module provides tools for profiling MCPost functions to identify
performance bottlenecks and memory usage patterns.
"""

import time
import functools
import cProfile
import pstats
import io
from typing import Callable, Any, Dict, Optional, List
import psutil
import os
import numpy as np
from contextlib import contextmanager
from dataclasses import dataclass, field
import warnings


@dataclass
class ProfileResult:
    """
    Container for profiling results.
    
    Attributes
    ----------
    function_name : str
        Name of the profiled function
    execution_time : float
        Total execution time in seconds
    memory_peak : float
        Peak memory usage in MB
    memory_baseline : float
        Baseline memory usage in MB
    cpu_percent : float
        Average CPU usage percentage
    profile_stats : Optional[pstats.Stats]
        Detailed profiling statistics
    memory_timeline : List[float]
        Memory usage over time (if tracked)
    metadata : Dict[str, Any]
        Additional profiling metadata
    """
    function_name: str
    execution_time: float
    memory_peak: float
    memory_baseline: float
    cpu_percent: float
    profile_stats: Optional[pstats.Stats] = None
    memory_timeline: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def memory_used(self) -> float:
        """Memory used during execution (peak - baseline)."""
        return self.memory_peak - self.memory_baseline
    
    def print_summary(self) -> None:
        """Print a summary of profiling results."""
        print(f"Profile Summary: {self.function_name}")
        print("-" * 40)
        print(f"Execution time: {self.execution_time:.3f}s")
        print(f"Memory used: {self.memory_used:.1f} MB")
        print(f"Peak memory: {self.memory_peak:.1f} MB")
        print(f"CPU usage: {self.cpu_percent:.1f}%")
        
        if self.profile_stats:
            print("\nTop 10 functions by cumulative time:")
            self.profile_stats.sort_stats('cumulative').print_stats(10)
    
    def save_profile(self, filename: str) -> None:
        """Save detailed profile to file."""
        if self.profile_stats:
            self.profile_stats.dump_stats(filename)
            print(f"Profile saved to {filename}")
        else:
            warnings.warn("No profile statistics available to save")


class MemoryTracker:
    """
    Context manager for tracking memory usage over time.
    
    Examples
    --------
    >>> with MemoryTracker() as tracker:
    ...     # Your code here
    ...     result = some_computation()
    >>> 
    >>> print(f"Peak memory: {tracker.peak_memory:.1f} MB")
    >>> print(f"Memory timeline: {len(tracker.timeline)} measurements")
    """
    
    def __init__(self, interval: float = 0.1):
        """
        Initialize memory tracker.
        
        Parameters
        ----------
        interval : float, default=0.1
            Sampling interval in seconds
        """
        self.interval = interval
        self.baseline_memory = 0.0
        self.peak_memory = 0.0
        self.timeline = []
        self._tracking = False
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    
    def __enter__(self):
        """Start memory tracking."""
        self.baseline_memory = self.get_memory_usage()
        self.peak_memory = self.baseline_memory
        self.timeline = [self.baseline_memory]
        self._tracking = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop memory tracking."""
        self._tracking = False
        
    def update(self):
        """Update memory measurements."""
        if self._tracking:
            current_memory = self.get_memory_usage()
            self.timeline.append(current_memory)
            self.peak_memory = max(self.peak_memory, current_memory)
    
    @property
    def memory_used(self) -> float:
        """Total memory used (peak - baseline)."""
        return self.peak_memory - self.baseline_memory


@contextmanager
def profile_function(
    function_name: str = "Unknown",
    detailed: bool = True,
    track_memory: bool = True
):
    """
    Context manager for profiling function execution.
    
    Parameters
    ----------
    function_name : str, default="Unknown"
        Name of the function being profiled
    detailed : bool, default=True
        Whether to collect detailed cProfile statistics
    track_memory : bool, default=True
        Whether to track memory usage
        
    Yields
    ------
    ProfileResult
        Profiling results object
        
    Examples
    --------
    >>> with profile_function("my_computation") as prof:
    ...     result = expensive_computation()
    >>> 
    >>> prof.print_summary()
    >>> prof.save_profile("my_computation.prof")
    """
    # Initialize profiling
    start_time = time.time()
    
    if track_memory:
        memory_tracker = MemoryTracker()
        memory_tracker.__enter__()
        baseline_memory = memory_tracker.baseline_memory
    else:
        baseline_memory = 0.0
        memory_tracker = None
    
    # CPU profiling
    if detailed:
        profiler = cProfile.Profile()
        profiler.enable()
    else:
        profiler = None
    
    # CPU usage tracking
    process = psutil.Process(os.getpid())
    cpu_start = process.cpu_percent()
    
    try:
        # Create result object to yield
        result = ProfileResult(
            function_name=function_name,
            execution_time=0.0,
            memory_peak=baseline_memory,
            memory_baseline=baseline_memory,
            cpu_percent=0.0
        )
        
        yield result
        
    finally:
        # Stop profiling and collect results
        execution_time = time.time() - start_time
        
        if detailed and profiler:
            profiler.disable()
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s)
            result.profile_stats = ps
        
        if track_memory and memory_tracker:
            memory_tracker.__exit__(None, None, None)
            result.memory_peak = memory_tracker.peak_memory
            result.memory_timeline = memory_tracker.timeline
        
        cpu_end = process.cpu_percent()
        result.cpu_percent = (cpu_start + cpu_end) / 2
        
        # Update result object
        result.execution_time = execution_time


def profile_decorator(
    detailed: bool = True,
    track_memory: bool = True,
    print_results: bool = False
):
    """
    Decorator for profiling function calls.
    
    Parameters
    ----------
    detailed : bool, default=True
        Whether to collect detailed cProfile statistics
    track_memory : bool, default=True
        Whether to track memory usage
    print_results : bool, default=False
        Whether to automatically print results
        
    Returns
    -------
    callable
        Decorated function that returns (original_result, profile_result)
        
    Examples
    --------
    >>> @profile_decorator(print_results=True)
    ... def expensive_function(n):
    ...     return sum(i**2 for i in range(n))
    >>> 
    >>> result, profile = expensive_function(1000000)
    >>> print(f"Result: {result}")
    >>> print(f"Execution time: {profile.execution_time:.3f}s")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with profile_function(
                function_name=func.__name__,
                detailed=detailed,
                track_memory=track_memory
            ) as prof:
                result = func(*args, **kwargs)
            
            if print_results:
                prof.print_summary()
            
            return result, prof
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """
    Monitor for tracking performance across multiple function calls.
    
    Useful for identifying performance regressions and tracking
    improvements over time.
    
    Examples
    --------
    >>> monitor = PerformanceMonitor()
    >>> 
    >>> # Profile multiple calls
    >>> for i in range(10):
    ...     with monitor.profile_call("test_function") as prof:
    ...         result = test_function(data[i])
    >>> 
    >>> # Get statistics
    >>> stats = monitor.get_statistics("test_function")
    >>> print(f"Average time: {stats['mean_time']:.3f}s")
    >>> print(f"Memory usage: {stats['mean_memory']:.1f} MB")
    """
    
    def __init__(self):
        """Initialize performance monitor."""
        self.profiles: Dict[str, List[ProfileResult]] = {}
    
    @contextmanager
    def profile_call(self, function_name: str, **kwargs):
        """
        Profile a single function call.
        
        Parameters
        ----------
        function_name : str
            Name of the function
        **kwargs
            Additional arguments for profile_function
            
        Yields
        ------
        ProfileResult
            Profiling results
        """
        with profile_function(function_name, **kwargs) as prof:
            yield prof
        
        # Store result
        if function_name not in self.profiles:
            self.profiles[function_name] = []
        self.profiles[function_name].append(prof)
    
    def get_statistics(self, function_name: str) -> Dict[str, float]:
        """
        Get performance statistics for a function.
        
        Parameters
        ----------
        function_name : str
            Name of the function
            
        Returns
        -------
        Dict[str, float]
            Statistics dictionary
        """
        if function_name not in self.profiles:
            return {}
        
        profiles = self.profiles[function_name]
        
        times = [p.execution_time for p in profiles]
        memories = [p.memory_used for p in profiles]
        
        return {
            "count": len(profiles),
            "mean_time": np.mean(times),
            "std_time": np.std(times),
            "min_time": np.min(times),
            "max_time": np.max(times),
            "mean_memory": np.mean(memories),
            "std_memory": np.std(memories),
            "min_memory": np.min(memories),
            "max_memory": np.max(memories)
        }
    
    def print_summary(self) -> None:
        """Print summary of all monitored functions."""
        print("Performance Monitor Summary")
        print("=" * 50)
        
        for func_name in self.profiles:
            stats = self.get_statistics(func_name)
            print(f"\nFunction: {func_name}")
            print(f"Calls: {stats['count']}")
            print(f"Time: {stats['mean_time']:.3f}±{stats['std_time']:.3f}s")
            print(f"Memory: {stats['mean_memory']:.1f}±{stats['std_memory']:.1f} MB")
    
    def clear(self) -> None:
        """Clear all stored profiles."""
        self.profiles.clear()


def compare_implementations(
    implementations: Dict[str, Callable],
    test_args: tuple = (),
    test_kwargs: Dict[str, Any] = None,
    n_runs: int = 5
) -> Dict[str, Dict[str, float]]:
    """
    Compare performance of different implementations.
    
    Parameters
    ----------
    implementations : Dict[str, Callable]
        Dictionary mapping names to implementation functions
    test_args : tuple, default=()
        Arguments to pass to each implementation
    test_kwargs : Dict[str, Any], optional
        Keyword arguments to pass to each implementation
    n_runs : int, default=5
        Number of runs for each implementation
        
    Returns
    -------
    Dict[str, Dict[str, float]]
        Performance statistics for each implementation
        
    Examples
    --------
    >>> def impl1(data):
    ...     return np.sum(data**2)
    >>> 
    >>> def impl2(data):
    ...     return np.dot(data, data)
    >>> 
    >>> data = np.random.random(10000)
    >>> results = compare_implementations(
    ...     {"numpy_sum": impl1, "numpy_dot": impl2},
    ...     test_args=(data,)
    ... )
    >>> 
    >>> for name, stats in results.items():
    ...     print(f"{name}: {stats['mean_time']:.4f}s")
    """
    if test_kwargs is None:
        test_kwargs = {}
    
    monitor = PerformanceMonitor()
    results = {}
    
    for name, impl in implementations.items():
        print(f"Benchmarking {name}...")
        
        for run in range(n_runs):
            with monitor.profile_call(f"{name}_run_{run}"):
                try:
                    result = impl(*test_args, **test_kwargs)
                except Exception as e:
                    warnings.warn(f"Implementation {name} failed: {str(e)}")
                    break
        
        # Aggregate statistics across runs
        all_profiles = []
        for run in range(n_runs):
            run_name = f"{name}_run_{run}"
            if run_name in monitor.profiles:
                all_profiles.extend(monitor.profiles[run_name])
        
        if all_profiles:
            times = [p.execution_time for p in all_profiles]
            memories = [p.memory_used for p in all_profiles]
            
            results[name] = {
                "mean_time": np.mean(times),
                "std_time": np.std(times),
                "min_time": np.min(times),
                "max_time": np.max(times),
                "mean_memory": np.mean(memories),
                "std_memory": np.std(memories)
            }
    
    return results


def profile_gsa_pipeline(X, y, **kwargs):
    """
    Profile GSA pipeline execution with detailed breakdown.
    
    Parameters
    ----------
    X : np.ndarray
        Input parameters
    y : np.ndarray
        Target values
    **kwargs
        Arguments for GSA pipeline
        
    Returns
    -------
    tuple
        (gsa_result, profile_result)
    """
    from mcpost.gsa import gsa_for_target
    
    with profile_function("gsa_pipeline", detailed=True) as prof:
        result = gsa_for_target(X, y, **kwargs)
    
    return result, prof


def profile_integration(func, bounds, n_samples, **kwargs):
    """
    Profile integration execution with detailed breakdown.
    
    Parameters
    ----------
    func : callable
        Function to integrate
    bounds : list
        Integration bounds
    n_samples : int
        Number of samples
    **kwargs
        Arguments for integration method
        
    Returns
    -------
    tuple
        (integration_result, profile_result)
    """
    from mcpost.integration import monte_carlo_integral
    
    with profile_function("monte_carlo_integration", detailed=True) as prof:
        result = monte_carlo_integral(func, bounds, n_samples, **kwargs)
    
    return result, prof


# Convenience functions for common profiling tasks
def quick_profile(func: Callable, *args, **kwargs) -> ProfileResult:
    """
    Quick profiling of a function call.
    
    Parameters
    ----------
    func : callable
        Function to profile
    *args
        Function arguments
    **kwargs
        Function keyword arguments
        
    Returns
    -------
    ProfileResult
        Profiling results
    """
    with profile_function(func.__name__) as prof:
        result = func(*args, **kwargs)
    
    return prof


def memory_profile(func: Callable, *args, **kwargs) -> tuple:
    """
    Profile memory usage of a function call.
    
    Parameters
    ----------
    func : callable
        Function to profile
    *args
        Function arguments
    **kwargs
        Function keyword arguments
        
    Returns
    -------
    tuple
        (function_result, memory_used_mb)
    """
    with MemoryTracker() as tracker:
        result = func(*args, **kwargs)
    
    return result, tracker.memory_used
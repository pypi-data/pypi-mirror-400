#!/usr/bin/env python3
"""
Main benchmark runner script.

This script runs comprehensive benchmarks for both GSA and integration
methods, generating performance reports and saving results.
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.benchmark_gsa import GSABenchmark, run_gsa_benchmarks
from benchmarks.benchmark_integration import IntegrationBenchmark, run_integration_benchmarks


def run_all_benchmarks(output_dir: str = "benchmark_results"):
    """
    Run all benchmarks and save results.
    
    Parameters
    ----------
    output_dir : str, default="benchmark_results"
        Directory to save benchmark results
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("MCPost Performance Benchmark Suite")
    print("=" * 50)
    
    # Change to output directory
    original_dir = os.getcwd()
    os.chdir(output_dir)
    
    try:
        # Run GSA benchmarks
        print("\n1. Running GSA benchmarks...")
        gsa_results = run_gsa_benchmarks()
        
        # Run integration benchmarks
        print("\n2. Running integration benchmarks...")
        integration_results = run_integration_benchmarks()
        
        print(f"\nAll benchmarks completed!")
        print(f"Results saved in: {os.path.abspath('.')}")
        
    finally:
        # Return to original directory
        os.chdir(original_dir)
    
    return gsa_results, integration_results


def run_quick_benchmark():
    """Run a quick benchmark for basic performance check."""
    print("MCPost Quick Performance Check")
    print("=" * 40)
    
    # Quick GSA benchmark
    print("\nGSA Performance:")
    gsa_benchmark = GSABenchmark()
    
    # Test with small dataset
    from mcpost.gsa import gsa_for_target
    import numpy as np
    
    np.random.seed(42)
    X = np.random.uniform(-1, 1, (500, 5))
    y = 2*X[:, 0] + X[:, 1] + 0.1*np.random.normal(0, 1, 500)
    
    def quick_gsa(X, y, **kwargs):
        return gsa_for_target(X, y, enable_sobol=False, make_pdp=False, **kwargs)
    
    result = gsa_benchmark.benchmark_method(
        quick_gsa, "QuickGSA", 500, 5
    )
    
    print(f"  Execution time: {result.execution_time:.3f}s")
    print(f"  Memory used: {result.memory_used:.1f} MB")
    print(f"  Processing rate: {result.samples_per_second:.0f} samples/s")
    
    # Quick integration benchmark
    print("\nIntegration Performance:")
    integration_benchmark = IntegrationBenchmark()
    
    result = integration_benchmark.benchmark_method(
        lambda func, bounds, n_samples: {"integral": 0.5, "uncertainty": 0.01},
        "QuickIntegration", "quadratic", 1000
    )
    
    print(f"  Execution time: {result.execution_time:.3f}s")
    print(f"  Memory used: {result.memory_used:.1f} MB")
    print(f"  Processing rate: {result.samples_per_second:.0f} samples/s")


def main():
    """Main benchmark runner."""
    parser = argparse.ArgumentParser(
        description="MCPost Performance Benchmark Suite"
    )
    parser.add_argument(
        "--mode", 
        choices=["all", "gsa", "integration", "quick"],
        default="quick",
        help="Benchmark mode to run"
    )
    parser.add_argument(
        "--output-dir",
        default="benchmark_results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.mode == "quick":
        run_quick_benchmark()
    elif args.mode == "all":
        run_all_benchmarks(args.output_dir)
    elif args.mode == "gsa":
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
        run_gsa_benchmarks()
    elif args.mode == "integration":
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
        run_integration_benchmarks()


if __name__ == "__main__":
    main()
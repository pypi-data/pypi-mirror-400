#!/usr/bin/env python3
"""
Monte Carlo Integration Methods Comparison

This example compares different integration methods available in MCPost:
- Standard Monte Carlo
- Quasi-Monte Carlo (Sobol)
- Quasi-Monte Carlo (Halton)
- QMC with importance sampling
"""

import numpy as np
import time
from mcpost import (
    monte_carlo_integral, 
    qmc_integral, 
    qmc_integral_auto, 
    qmc_integral_importance
)


def gaussian_2d_integrand(theta):
    """
    Test integrand: f(x,y) = x * exp(-x^2 - y^2)
    
    Analytical solution over R^2: 0
    """
    x, y = theta[:, 0], theta[:, 1]
    return x * np.exp(-x**2 - y**2)


def target_pdf(theta):
    """Standard bivariate normal PDF."""
    return np.exp(-0.5 * np.sum(theta**2, axis=1)) / (2 * np.pi)


def importance_pdf(theta):
    """Importance sampling PDF (wider normal)."""
    return np.exp(-0.25 * np.sum(theta**2, axis=1)) / (4 * np.pi)


def run_integration_comparison():
    """Compare different integration methods."""
    print("MCPost Integration Methods Comparison")
    print("=" * 45)
    
    # Integration parameters
    n_samples = 8192
    bounds = [(-4, 4), (-4, 4)]
    n_runs = 5
    
    print(f"Integrand: f(x,y) = x * exp(-x^2 - y^2)")
    print(f"Domain: {bounds[0]} × {bounds[1]}")
    print(f"Analytical solution: 0.0")
    print(f"Number of samples: {n_samples}")
    print(f"Number of runs: {n_runs}")
    print()
    
    methods = []
    
    # Method 1: Standard Monte Carlo
    print("1. Standard Monte Carlo Integration")
    print("-" * 35)
    
    mc_results = []
    mc_times = []
    
    for run in range(n_runs):
        np.random.seed(42 + run)
        
        start_time = time.time()
        
        # Generate random samples
        theta_samples = np.random.uniform(
            [bounds[0][0], bounds[1][0]], 
            [bounds[0][1], bounds[1][1]], 
            (n_samples, 2)
        )
        f_values = gaussian_2d_integrand(theta_samples)
        
        # Use uniform PDF over the domain
        def uniform_pdf(theta):
            vol = (bounds[0][1] - bounds[0][0]) * (bounds[1][1] - bounds[1][0])
            return np.ones(len(theta)) / vol
        
        result = monte_carlo_integral(theta_samples, f_values, uniform_pdf)
        
        end_time = time.time()
        
        mc_results.append(result['integral'][0])
        mc_times.append(end_time - start_time)
        
        print(f"  Run {run+1}: {result['integral'][0]:.6f} "
              f"(uncertainty: {result['uncertainty'][0]:.6f}, "
              f"time: {mc_times[-1]:.3f}s)")
    
    mc_mean = np.mean(mc_results)
    mc_std = np.std(mc_results)
    mc_time_mean = np.mean(mc_times)
    
    print(f"  Average: {mc_mean:.6f} ± {mc_std:.6f} (time: {mc_time_mean:.3f}s)")
    methods.append(("Standard MC", mc_mean, mc_std, mc_time_mean))
    print()
    
    # Method 2: Quasi-Monte Carlo (Sobol)
    print("2. Quasi-Monte Carlo (Sobol)")
    print("-" * 30)
    
    qmc_sobol_results = []
    qmc_sobol_times = []
    
    for run in range(n_runs):
        start_time = time.time()
        
        result = qmc_integral(
            N_samples=n_samples,
            N_params=2,
            data_func=gaussian_2d_integrand,
            p_target=lambda theta: np.ones(len(theta)),  # Uniform weight
            bounds=bounds,
            method='sobol'
        )
        
        end_time = time.time()
        
        qmc_sobol_results.append(result['integral'][0])
        qmc_sobol_times.append(end_time - start_time)
        
        print(f"  Run {run+1}: {result['integral'][0]:.6f} "
              f"(time: {qmc_sobol_times[-1]:.3f}s)")
    
    qmc_sobol_mean = np.mean(qmc_sobol_results)
    qmc_sobol_std = np.std(qmc_sobol_results)
    qmc_sobol_time_mean = np.mean(qmc_sobol_times)
    
    print(f"  Average: {qmc_sobol_mean:.6f} ± {qmc_sobol_std:.6f} "
          f"(time: {qmc_sobol_time_mean:.3f}s)")
    methods.append(("QMC Sobol", qmc_sobol_mean, qmc_sobol_std, qmc_sobol_time_mean))
    print()
    
    # Method 3: Quasi-Monte Carlo (Halton)
    print("3. Quasi-Monte Carlo (Halton)")
    print("-" * 31)
    
    qmc_halton_results = []
    qmc_halton_times = []
    
    for run in range(n_runs):
        start_time = time.time()
        
        result = qmc_integral(
            N_samples=n_samples,
            N_params=2,
            data_func=gaussian_2d_integrand,
            p_target=lambda theta: np.ones(len(theta)),
            bounds=bounds,
            method='halton'
        )
        
        end_time = time.time()
        
        qmc_halton_results.append(result['integral'][0])
        qmc_halton_times.append(end_time - start_time)
        
        print(f"  Run {run+1}: {result['integral'][0]:.6f} "
              f"(time: {qmc_halton_times[-1]:.3f}s)")
    
    qmc_halton_mean = np.mean(qmc_halton_results)
    qmc_halton_std = np.std(qmc_halton_results)
    qmc_halton_time_mean = np.mean(qmc_halton_times)
    
    print(f"  Average: {qmc_halton_mean:.6f} ± {qmc_halton_std:.6f} "
          f"(time: {qmc_halton_time_mean:.3f}s)")
    methods.append(("QMC Halton", qmc_halton_mean, qmc_halton_std, qmc_halton_time_mean))
    print()
    
    # Method 4: QMC with importance sampling
    print("4. QMC with Importance Sampling")
    print("-" * 35)
    
    qmc_is_results = []
    qmc_is_times = []
    
    for run in range(n_runs):
        start_time = time.time()
        
        result = qmc_integral_importance(
            N_samples=n_samples,
            N_params=2,
            data_func=gaussian_2d_integrand,
            p_target=target_pdf,
            q_sample=importance_pdf,
            bounds=bounds,
            method='sobol'
        )
        
        end_time = time.time()
        
        qmc_is_results.append(result['integral'][0])
        qmc_is_times.append(end_time - start_time)
        
        print(f"  Run {run+1}: {result['integral'][0]:.6f} "
              f"(ESS: {result['effective_sample_size']:.0f}, "
              f"time: {qmc_is_times[-1]:.3f}s)")
    
    qmc_is_mean = np.mean(qmc_is_results)
    qmc_is_std = np.std(qmc_is_results)
    qmc_is_time_mean = np.mean(qmc_is_times)
    
    print(f"  Average: {qmc_is_mean:.6f} ± {qmc_is_std:.6f} "
          f"(time: {qmc_is_time_mean:.3f}s)")
    methods.append(("QMC + IS", qmc_is_mean, qmc_is_std, qmc_is_time_mean))
    print()
    
    # Summary comparison
    print("Summary Comparison")
    print("=" * 18)
    print(f"{'Method':<15} {'Mean':<10} {'Std Dev':<10} {'Time (s)':<10} {'Error':<10}")
    print("-" * 65)
    
    for name, mean, std, time_avg in methods:
        error = abs(mean - 0.0)  # True value is 0
        print(f"{name:<15} {mean:<10.6f} {std:<10.6f} {time_avg:<10.3f} {error:<10.6f}")
    
    print()
    print("Observations:")
    print("- QMC methods typically show lower variance than standard MC")
    print("- Sobol sequences often perform better than Halton for smooth integrands")
    print("- Importance sampling can reduce variance when well-chosen")
    print("- All methods converge to the analytical solution (0.0)")


if __name__ == "__main__":
    run_integration_comparison()
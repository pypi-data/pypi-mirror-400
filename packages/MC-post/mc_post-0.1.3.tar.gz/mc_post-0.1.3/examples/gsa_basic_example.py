#!/usr/bin/env python3
"""
Basic Global Sensitivity Analysis Example

This example demonstrates how to perform a comprehensive GSA analysis
using the MCPost package with the Ishigami function, a common benchmark
for sensitivity analysis methods.
"""

import numpy as np
import matplotlib.pyplot as plt
from mcpost import gsa_pipeline, plot_sensitivity_metrics

def ishigami_function(X, a=7, b=0.1):
    """
    Ishigami function: a common test function for sensitivity analysis.
    
    f(x1, x2, x3) = sin(x1) + a * sin(x2)^2 + b * x3^4 * sin(x1)
    
    Parameters
    ----------
    X : np.ndarray, shape (n_samples, 3)
        Input parameters in [-π, π]^3
    a : float, default=7
        First coefficient
    b : float, default=0.1
        Second coefficient
        
    Returns
    -------
    np.ndarray, shape (n_samples,)
        Function values
    """
    x1, x2, x3 = X[:, 0], X[:, 1], X[:, 2]
    return np.sin(x1) + a * np.sin(x2)**2 + b * x3**4 * np.sin(x1)


def main():
    """Run the GSA analysis example."""
    print("MCPost GSA Example: Ishigami Function Analysis")
    print("=" * 50)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate parameter samples
    n_samples = 2000
    print(f"Generating {n_samples} parameter samples...")
    
    # Parameters uniformly distributed in [-π, π]
    X = np.random.uniform(-np.pi, np.pi, (n_samples, 3))
    
    # Evaluate the Ishigami function
    print("Evaluating Ishigami function...")
    y = ishigami_function(X)
    Y = y.reshape(-1, 1)  # GSA expects 2D target array
    
    # Parameter and feature names
    param_names = ["x1", "x2", "x3"]
    feature_names = ["ishigami"]
    
    print("Running comprehensive GSA analysis...")
    print("This includes:")
    print("- Mutual Information (MI)")
    print("- Distance Correlation (dCor)")
    print("- Permutation Importance")
    print("- Gaussian Process surrogate with ARD")
    print("- Sobol' indices")
    print("- Partial Dependence Plots")
    
    # Run GSA pipeline
    results = gsa_pipeline(
        X, Y,
        param_names=param_names,
        feature_names=feature_names,
        scaler="minmax",
        enable_sobol=True,
        enable_gp=True,
        enable_perm=True,
        make_pdp=True,
        N_sobol=4096,
        topk_pdp=3
    )
    
    # Display results
    print("\nSensitivity Analysis Results:")
    print("-" * 30)
    sensitivity_table = results["results"]["ishigami"]["table"]
    print(sensitivity_table)
    
    # Theoretical Sobol indices for comparison
    print("\nTheoretical Sobol' indices (for comparison):")
    print("S1 (x1): 0.314")
    print("S2 (x2): 0.442") 
    print("S3 (x3): 0.000")
    print("ST1 (x1): 0.558")
    print("ST2 (x2): 0.442")
    print("ST3 (x3): 0.244")
    
    # Create sensitivity heatmap
    print("\nCreating sensitivity heatmap...")
    try:
        fig, ax = plot_sensitivity_metrics(
            sensitivity_table,
            title="Ishigami Function - Global Sensitivity Analysis"
        )
        plt.savefig("examples/ishigami_sensitivity_heatmap.png", dpi=150, bbox_inches='tight')
        print("Heatmap saved as 'examples/ishigami_sensitivity_heatmap.png'")
        plt.close()
    except ImportError:
        print("Matplotlib not available - skipping heatmap generation")
    
    # Print interpretation
    print("\nInterpretation:")
    print("- x2 shows highest sensitivity (expected from theoretical values)")
    print("- x1 shows moderate sensitivity with interaction effects")
    print("- x3 shows low main effect but contributes through interactions")
    print("- ARD length scales indicate relative parameter importance")
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
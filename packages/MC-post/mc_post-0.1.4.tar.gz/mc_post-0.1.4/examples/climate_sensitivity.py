#!/usr/bin/env python3
"""
Climate Model Parameter Sensitivity Analysis

This example demonstrates GSA applied to a simplified climate model
to identify which parameters most influence temperature predictions.
This showcases MCPost's application to environmental modeling.
"""

import numpy as np
from mcpost import gsa_pipeline, plot_sensitivity_metrics


def simplified_climate_model(params):
    """
    Simplified climate model for demonstration.
    
    This is a toy model that captures some basic climate dynamics
    for sensitivity analysis demonstration purposes.
    
    Parameters
    ----------
    params : np.ndarray, shape (n_samples, 8)
        Climate model parameters:
        - CO2_sensitivity: Climate sensitivity to CO2 doubling [1.5, 4.5] K
        - cloud_feedback: Cloud feedback parameter [-2, 1] W/m²/K
        - ocean_heat_capacity: Ocean heat capacity [0.5, 2.0] relative
        - aerosol_forcing: Aerosol forcing [-2, 0] W/m²
        - solar_constant: Solar constant variation [0.98, 1.02] relative
        - albedo: Surface albedo [0.1, 0.4]
        - water_vapor_feedback: Water vapor feedback [0.5, 1.5] relative
        - lapse_rate_feedback: Lapse rate feedback [-1, 1] W/m²/K
        
    Returns
    -------
    np.ndarray, shape (n_samples, 3)
        Model outputs:
        - global_temp_change: Global temperature change [K]
        - arctic_temp_change: Arctic temperature change [K] 
        - precipitation_change: Precipitation change [%]
    """
    n_samples = params.shape[0]
    
    # Extract parameters
    co2_sens = params[:, 0]
    cloud_fb = params[:, 1]
    ocean_hc = params[:, 2]
    aerosol = params[:, 3]
    solar = params[:, 4]
    albedo = params[:, 5]
    wv_fb = params[:, 6]
    lr_fb = params[:, 7]
    
    # Simplified climate physics
    # Base CO2 forcing (doubling from pre-industrial)
    co2_forcing = 3.7  # W/m²
    
    # Total radiative forcing
    total_forcing = (co2_forcing * solar + 
                    aerosol + 
                    0.5 * (albedo - 0.25))  # Albedo effect
    
    # Temperature response with feedbacks
    feedback_factor = (1 + cloud_fb * 0.1 + 
                      wv_fb * 0.3 + 
                      lr_fb * 0.1)
    
    # Global temperature change
    global_temp = (co2_sens * total_forcing / 3.7 * 
                  feedback_factor / ocean_hc)
    
    # Arctic amplification (2-4x global warming)
    arctic_amplification = 2.5 + 0.5 * (1 - albedo) + 0.3 * cloud_fb
    arctic_temp = global_temp * arctic_amplification
    
    # Precipitation change (roughly 2-3% per K of warming)
    precip_change = global_temp * (2.5 + 0.5 * wv_fb) + 0.1 * np.random.normal(0, 1, n_samples)
    
    # Add some nonlinear interactions
    global_temp += 0.1 * co2_sens * cloud_fb * wv_fb
    arctic_temp += 0.2 * global_temp * (1 - albedo)
    
    return np.column_stack([global_temp, arctic_temp, precip_change])


def main():
    """Run climate sensitivity analysis."""
    print("Climate Model Parameter Sensitivity Analysis")
    print("=" * 48)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Define parameter ranges (realistic climate model ranges)
    param_ranges = [
        [1.5, 4.5],    # CO2_sensitivity [K]
        [-2.0, 1.0],   # cloud_feedback [W/m²/K]
        [0.5, 2.0],    # ocean_heat_capacity [relative]
        [-2.0, 0.0],   # aerosol_forcing [W/m²]
        [0.98, 1.02],  # solar_constant [relative]
        [0.1, 0.4],    # albedo
        [0.5, 1.5],    # water_vapor_feedback [relative]
        [-1.0, 1.0],   # lapse_rate_feedback [W/m²/K]
    ]
    
    param_names = [
        "CO2_sensitivity",
        "cloud_feedback", 
        "ocean_heat_capacity",
        "aerosol_forcing",
        "solar_constant",
        "albedo",
        "water_vapor_feedback",
        "lapse_rate_feedback"
    ]
    
    feature_names = [
        "global_temp_change",
        "arctic_temp_change", 
        "precipitation_change"
    ]
    
    # Generate parameter samples (reduced for faster execution)
    n_samples = 500
    print(f"Generating {n_samples} parameter samples...")
    
    X = np.zeros((n_samples, len(param_ranges)))
    for i, (low, high) in enumerate(param_ranges):
        X[:, i] = np.random.uniform(low, high, n_samples)
    
    print("Running climate model simulations...")
    Y = simplified_climate_model(X)
    
    print(f"Model outputs shape: {Y.shape}")
    print(f"Global temperature range: [{Y[:, 0].min():.2f}, {Y[:, 0].max():.2f}] K")
    print(f"Arctic temperature range: [{Y[:, 1].min():.2f}, {Y[:, 1].max():.2f}] K")
    print(f"Precipitation change range: [{Y[:, 2].min():.2f}, {Y[:, 2].max():.2f}] %")
    print()
    
    # Run GSA for each climate variable
    print("Running Global Sensitivity Analysis...")
    print("This may take a few minutes for all climate variables...")
    
    results = gsa_pipeline(
        X, Y,
        param_names=param_names,
        feature_names=feature_names,
        scaler="minmax",
        enable_sobol=True,
        enable_gp=True,
        enable_perm=True,
        make_pdp=True,
        N_sobol=1024,  # Reduced for faster execution
        topk_pdp=3  # Show top 3 parameters
    )
    
    # Display results for each climate variable
    for feature in feature_names:
        print(f"\nSensitivity Analysis: {feature}")
        print("=" * (22 + len(feature)))
        
        table = results["results"][feature]["table"]
        print(table)
        
        # Create heatmap for this variable
        try:
            import matplotlib.pyplot as plt
            fig, ax = plot_sensitivity_metrics(
                table,
                title=f"Climate Sensitivity: {feature.replace('_', ' ').title()}"
            )
            filename = f"examples/climate_{feature}_sensitivity.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Sensitivity heatmap saved as '{filename}'")
            plt.close()
        except ImportError:
            print("Matplotlib not available - skipping heatmap generation")
    
    # Summary interpretation
    print("\n" + "=" * 60)
    print("CLIMATE SENSITIVITY ANALYSIS SUMMARY")
    print("=" * 60)
    
    print("\nKey Findings:")
    
    # Analyze global temperature sensitivity
    global_table = results["results"]["global_temp_change"]["table"]
    top_global_params = global_table.index[:3].tolist()
    
    print(f"\nGlobal Temperature Change - Most Influential Parameters:")
    for i, param in enumerate(top_global_params, 1):
        mi_score = global_table.loc[param, 'MI']
        print(f"  {i}. {param}: MI = {mi_score:.3f}")
    
    # Analyze arctic temperature sensitivity  
    arctic_table = results["results"]["arctic_temp_change"]["table"]
    top_arctic_params = arctic_table.index[:3].tolist()
    
    print(f"\nArctic Temperature Change - Most Influential Parameters:")
    for i, param in enumerate(top_arctic_params, 1):
        mi_score = arctic_table.loc[param, 'MI']
        print(f"  {i}. {param}: MI = {mi_score:.3f}")
    
    # Analyze precipitation sensitivity
    precip_table = results["results"]["precipitation_change"]["table"]
    top_precip_params = precip_table.index[:3].tolist()
    
    print(f"\nPrecipitation Change - Most Influential Parameters:")
    for i, param in enumerate(top_precip_params, 1):
        mi_score = precip_table.loc[param, 'MI']
        print(f"  {i}. {param}: MI = {mi_score:.3f}")
    
    print("\nInterpretation Guidelines:")
    print("- Higher MI (Mutual Information) indicates stronger parameter influence")
    print("- dCor (Distance Correlation) captures nonlinear relationships")
    print("- Sobol indices (Si, STi) show variance-based sensitivity")
    print("- ARD length scales (1/ARD_LS) indicate GP-based importance")
    print("- Parameters with high STi but low Si have interaction effects")
    
    print("\nClimate Model Insights:")
    print("- CO2 sensitivity typically dominates temperature responses")
    print("- Cloud feedback is crucial for temperature projections")
    print("- Ocean heat capacity affects transient climate response")
    print("- Arctic warming shows different sensitivities than global mean")
    print("- Precipitation changes depend on multiple interacting factors")
    
    print("\nAnalysis complete! Check generated plots for visual insights.")


if __name__ == "__main__":
    main()
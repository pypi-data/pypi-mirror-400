#!/usr/bin/env python3
"""
Financial Risk Analysis with MCPost

This example demonstrates using MCPost for financial risk assessment,
including portfolio sensitivity analysis and Value-at-Risk (VaR) computation
using Monte Carlo integration.
"""

import numpy as np
from mcpost import gsa_pipeline, qmc_integral_auto


def portfolio_model(params):
    """
    Simplified portfolio model for risk analysis.
    
    Parameters
    ----------
    params : np.ndarray, shape (n_samples, 6)
        Portfolio parameters:
        - stock_weight: Weight in stocks [0.3, 0.8]
        - bond_weight: Weight in bonds [0.1, 0.5] 
        - stock_volatility: Stock volatility [0.15, 0.35]
        - bond_volatility: Bond volatility [0.05, 0.15]
        - correlation: Stock-bond correlation [-0.3, 0.3]
        - market_shock: Market shock factor [-0.2, 0.2]
        
    Returns
    -------
    np.ndarray, shape (n_samples, 2)
        Portfolio metrics:
        - annual_return: Expected annual return [%]
        - portfolio_volatility: Portfolio volatility [%]
    """
    n_samples = params.shape[0]
    
    # Extract parameters
    w_stock = params[:, 0]
    w_bond = params[:, 1]
    vol_stock = params[:, 2]
    vol_bond = params[:, 3]
    correlation = params[:, 4]
    market_shock = params[:, 5]
    
    # Normalize weights
    total_weight = w_stock + w_bond
    w_stock = w_stock / total_weight
    w_bond = w_bond / total_weight
    
    # Expected returns (with market shock)
    base_stock_return = 0.08  # 8% base stock return
    base_bond_return = 0.03   # 3% base bond return
    
    stock_return = base_stock_return + market_shock
    bond_return = base_bond_return + 0.3 * market_shock  # Bonds less sensitive
    
    # Portfolio expected return
    portfolio_return = w_stock * stock_return + w_bond * bond_return
    
    # Portfolio volatility (with correlation)
    portfolio_var = (w_stock**2 * vol_stock**2 + 
                    w_bond**2 * vol_bond**2 + 
                    2 * w_stock * w_bond * correlation * vol_stock * vol_bond)
    
    portfolio_vol = np.sqrt(portfolio_var)
    
    # Convert to percentages
    annual_return = portfolio_return * 100
    portfolio_volatility = portfolio_vol * 100
    
    return np.column_stack([annual_return, portfolio_volatility])


def portfolio_loss_function(params):
    """Portfolio loss for VaR calculation (negative returns)."""
    portfolio_metrics = portfolio_model(params)
    annual_return = portfolio_metrics[:, 0] / 100  # Convert back to decimal
    portfolio_vol = portfolio_metrics[:, 1] / 100
    
    # Simulate 1-year portfolio loss (negative of return)
    # Assume normal distribution of returns
    random_returns = np.random.normal(annual_return, portfolio_vol)
    portfolio_loss = -random_returns  # Loss is negative return
    
    return portfolio_loss.reshape(-1, 1)


def main():
    """Run financial risk analysis."""
    print("Financial Portfolio Risk Analysis with MCPost")
    print("=" * 48)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Define parameter ranges
    param_ranges = [
        [0.3, 0.8],    # stock_weight
        [0.1, 0.5],    # bond_weight  
        [0.15, 0.35],  # stock_volatility
        [0.05, 0.15],  # bond_volatility
        [-0.3, 0.3],   # correlation
        [-0.2, 0.2],   # market_shock
    ]
    
    param_names = [
        "stock_weight",
        "bond_weight", 
        "stock_volatility",
        "bond_volatility",
        "correlation",
        "market_shock"
    ]
    
    feature_names = [
        "annual_return",
        "portfolio_volatility"
    ]
    
    # Generate parameter samples
    n_samples = 2500
    print(f"Generating {n_samples} portfolio scenarios...")
    
    X = np.zeros((n_samples, len(param_ranges)))
    for i, (low, high) in enumerate(param_ranges):
        X[:, i] = np.random.uniform(low, high, n_samples)
    
    # Evaluate portfolio model
    print("Computing portfolio metrics...")
    Y = portfolio_model(X)
    
    print(f"Return range: [{Y[:, 0].min():.2f}%, {Y[:, 0].max():.2f}%]")
    print(f"Volatility range: [{Y[:, 1].min():.2f}%, {Y[:, 1].max():.2f}%]")
    print()
    
    # Run GSA for portfolio metrics
    print("Running Global Sensitivity Analysis...")
    
    results = gsa_pipeline(
        X, Y,
        param_names=param_names,
        feature_names=feature_names,
        scaler="minmax",
        enable_sobol=True,
        enable_gp=True,
        enable_perm=True,
        make_pdp=False,  # Skip PDPs for this example
        N_sobol=4096
    )
    
    # Display sensitivity results
    for feature in feature_names:
        print(f"\nSensitivity Analysis: {feature}")
        print("=" * (22 + len(feature)))
        
        table = results["results"][feature]["table"]
        print(table)
        
        # Interpretation
        top_params = table.index[:3].tolist()
        print(f"\nTop 3 influential parameters for {feature}:")
        for i, param in enumerate(top_params, 1):
            mi_score = table.loc[param, 'MI']
            print(f"  {i}. {param}: MI = {mi_score:.3f}")
    
    # Value-at-Risk (VaR) calculation using Monte Carlo integration
    print("\n" + "=" * 50)
    print("VALUE-AT-RISK (VaR) CALCULATION")
    print("=" * 50)
    
    # Define uniform distribution over parameter space
    def uniform_pdf(theta):
        volume = 1.0
        for low, high in param_ranges:
            volume *= (high - low)
        return np.ones(len(theta)) / volume
    
    # VaR integrand: indicator function for losses > threshold
    def var_integrand(theta, threshold=0.05):  # 5% loss threshold
        """Probability of loss exceeding threshold."""
        losses = portfolio_loss_function(theta)
        return (losses > threshold).astype(float)
    
    # Compute VaR at different confidence levels
    confidence_levels = [0.90, 0.95, 0.99]
    
    print("Computing Value-at-Risk using QMC integration...")
    
    for conf_level in confidence_levels:
        # Find VaR threshold (loss level exceeded with probability 1-conf_level)
        target_prob = 1 - conf_level
        
        # Use binary search to find VaR threshold
        low_threshold, high_threshold = 0.0, 0.5
        tolerance = 1e-4
        
        for _ in range(20):  # Binary search iterations
            mid_threshold = (low_threshold + high_threshold) / 2
            
            # Compute probability of exceeding mid_threshold
            prob_result = qmc_integral_auto(
                N_samples=4096,
                N_params=len(param_ranges),
                data_func=lambda theta: var_integrand(theta, mid_threshold),
                p_target=uniform_pdf,
                bounds=param_ranges,
                method='sobol'
            )
            
            prob_exceed = prob_result['integral'][0]
            
            if abs(prob_exceed - target_prob) < tolerance:
                break
            elif prob_exceed > target_prob:
                low_threshold = mid_threshold
            else:
                high_threshold = mid_threshold
        
        var_estimate = mid_threshold
        print(f"VaR at {conf_level*100:.0f}% confidence: {var_estimate*100:.2f}% loss")
    
    # Expected Shortfall (Conditional VaR)
    print("\nComputing Expected Shortfall (CVaR)...")
    
    def cvar_integrand(theta, var_threshold=0.05):
        """Expected loss given loss > VaR threshold."""
        losses = portfolio_loss_function(theta)
        excess_losses = np.where(losses > var_threshold, losses, 0)
        return excess_losses
    
    # Compute CVaR at 95% confidence level
    var_95 = 0.05  # Approximate from above calculation
    
    cvar_result = qmc_integral_auto(
        N_samples=8192,
        N_params=len(param_ranges),
        data_func=lambda theta: cvar_integrand(theta, var_95),
        p_target=uniform_pdf,
        bounds=param_ranges
    )
    
    # Normalize by tail probability
    tail_prob_result = qmc_integral_auto(
        N_samples=4096,
        N_params=len(param_ranges),
        data_func=lambda theta: var_integrand(theta, var_95),
        p_target=uniform_pdf,
        bounds=param_ranges
    )
    
    cvar_95 = cvar_result['integral'][0] / tail_prob_result['integral'][0]
    print(f"CVaR at 95% confidence: {cvar_95*100:.2f}% loss")
    
    # Summary and interpretation
    print("\n" + "=" * 50)
    print("RISK ANALYSIS SUMMARY")
    print("=" * 50)
    
    print("\nKey Risk Factors (from GSA):")
    
    # Analyze return sensitivity
    return_table = results["results"]["annual_return"]["table"]
    print(f"\nPortfolio Return Drivers:")
    for i, param in enumerate(return_table.index[:3], 1):
        mi_score = return_table.loc[param, 'MI']
        print(f"  {i}. {param}: {mi_score:.3f}")
    
    # Analyze volatility sensitivity
    vol_table = results["results"]["portfolio_volatility"]["table"]
    print(f"\nPortfolio Volatility Drivers:")
    for i, param in enumerate(vol_table.index[:3], 1):
        mi_score = vol_table.loc[param, 'MI']
        print(f"  {i}. {param}: {mi_score:.3f}")
    
    print("\nRisk Management Insights:")
    print("- Asset allocation (stock/bond weights) significantly impacts both return and risk")
    print("- Stock volatility is a major driver of portfolio volatility")
    print("- Market shock affects returns more than volatility structure")
    print("- Correlation between assets influences portfolio risk diversification")
    
    print("\nVaR/CVaR Interpretation:")
    print("- VaR estimates the maximum expected loss at given confidence levels")
    print("- CVaR (Expected Shortfall) estimates average loss in worst-case scenarios")
    print("- These metrics help set risk limits and capital requirements")
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
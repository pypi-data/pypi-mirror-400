#!/usr/bin/env python3
"""
Financial Risk Analysis Example using MCPost

This example demonstrates how to use MCPost for Monte Carlo risk assessment
in financial modeling, including portfolio risk and Value at Risk (VaR) calculations.
"""

import numpy as np
import pandas as pd
from mcpost import monte_carlo_integral, gsa_for_target

def main():
    """Run financial risk analysis example."""
    print("Financial Risk Analysis with MCPost")
    print("=" * 50)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Define portfolio parameters
    n_assets = 3
    n_scenarios = 10000
    
    # Asset parameters (expected returns and volatilities)
    expected_returns = np.array([0.08, 0.12, 0.15])  # 8%, 12%, 15% annual returns
    volatilities = np.array([0.15, 0.20, 0.25])      # 15%, 20%, 25% annual volatility
    
    # Correlation matrix
    correlation_matrix = np.array([
        [1.0, 0.3, 0.2],
        [0.3, 1.0, 0.4],
        [0.2, 0.4, 1.0]
    ])
    
    # Portfolio weights (parameters for sensitivity analysis)
    weights = np.array([0.4, 0.35, 0.25])
    
    print(f"Portfolio composition:")
    print(f"Asset 1: {weights[0]:.1%} (Expected return: {expected_returns[0]:.1%}, Volatility: {volatilities[0]:.1%})")
    print(f"Asset 2: {weights[1]:.1%} (Expected return: {expected_returns[1]:.1%}, Volatility: {volatilities[1]:.1%})")
    print(f"Asset 3: {weights[2]:.1%} (Expected return: {expected_returns[2]:.1%}, Volatility: {volatilities[2]:.1%})")
    
    # Generate correlated asset returns
    print(f"\nGenerating {n_scenarios:,} Monte Carlo scenarios...")
    
    # Cholesky decomposition for correlated random variables
    L = np.linalg.cholesky(correlation_matrix)
    
    # Generate independent normal random variables
    independent_returns = np.random.normal(0, 1, (n_scenarios, n_assets))
    
    # Transform to correlated returns
    correlated_returns = independent_returns @ L.T
    
    # Scale by volatility and add expected returns
    asset_returns = expected_returns + correlated_returns * volatilities
    
    # Calculate portfolio returns
    portfolio_returns = np.sum(asset_returns * weights, axis=1)
    
    # Risk metrics
    portfolio_mean = np.mean(portfolio_returns)
    portfolio_std = np.std(portfolio_returns)
    var_95 = np.percentile(portfolio_returns, 5)  # 5th percentile (95% VaR)
    var_99 = np.percentile(portfolio_returns, 1)  # 1st percentile (99% VaR)
    
    print(f"\nPortfolio Risk Metrics:")
    print(f"Expected Return: {portfolio_mean:.2%}")
    print(f"Volatility (Std Dev): {portfolio_std:.2%}")
    print(f"95% VaR: {var_95:.2%} (5% chance of losing more than {-var_95:.2%})")
    print(f"99% VaR: {var_99:.2%} (1% chance of losing more than {-var_99:.2%})")
    
    # Sensitivity Analysis: How do weight changes affect portfolio risk?
    print(f"\nSensitivity Analysis: Weight Impact on Portfolio Risk")
    print("-" * 55)
    
    # Generate weight scenarios for sensitivity analysis
    n_sensitivity_scenarios = 1000
    weight_variations = np.random.dirichlet([10, 10, 10], n_sensitivity_scenarios)  # Dirichlet ensures weights sum to 1
    
    # Calculate portfolio metrics for each weight scenario
    portfolio_risks = []
    portfolio_expected_returns = []
    
    for weights_scenario in weight_variations:
        # Calculate expected return and risk for this weight scenario
        scenario_expected_return = np.sum(weights_scenario * expected_returns)
        
        # Portfolio variance calculation
        portfolio_variance = np.sum(
            weights_scenario[:, np.newaxis] * weights_scenario[np.newaxis, :] * 
            (volatilities[:, np.newaxis] * volatilities[np.newaxis, :] * correlation_matrix)
        )
        scenario_risk = np.sqrt(portfolio_variance)
        
        portfolio_expected_returns.append(scenario_expected_return)
        portfolio_risks.append(scenario_risk)
    
    # Convert to arrays for GSA
    X_weights = weight_variations
    y_risk = np.array(portfolio_risks)
    y_return = np.array(portfolio_expected_returns)
    
    # Perform GSA on portfolio risk
    print("Analyzing sensitivity of portfolio risk to asset weights...")
    risk_sensitivity = gsa_for_target(
        X_weights, 
        y_risk,
        param_names=['Weight_Asset1', 'Weight_Asset2', 'Weight_Asset3'],
        scaler='minmax',
        enable_perm=True,
        enable_gp=True,
        enable_sobol=True
    )
    
    print("\nRisk Sensitivity Results:")
    print(risk_sensitivity[['MI', 'dCor', 'Perm_Imp']].round(4))
    
    # Perform GSA on portfolio expected return
    print("\nAnalyzing sensitivity of portfolio return to asset weights...")
    return_sensitivity = gsa_for_target(
        X_weights, 
        y_return,
        param_names=['Weight_Asset1', 'Weight_Asset2', 'Weight_Asset3'],
        scaler='minmax',
        enable_perm=True,
        enable_gp=True,
        enable_sobol=True
    )
    
    print("\nReturn Sensitivity Results:")
    print(return_sensitivity[['MI', 'dCor', 'Perm_Imp']].round(4))
    
    # Monte Carlo Integration: Expected Shortfall (Conditional VaR)
    print(f"\nCalculating Expected Shortfall using Monte Carlo Integration...")
    
    def shortfall_integrand(returns):
        """Calculate shortfall for returns below VaR threshold."""
        var_threshold = var_95
        shortfall_mask = returns < var_threshold
        return np.where(shortfall_mask, returns, 0.0)
    
    def returns_pdf(returns):
        """Approximate PDF of portfolio returns (assuming normal)."""
        return (1 / (portfolio_std * np.sqrt(2 * np.pi))) * \
               np.exp(-0.5 * ((returns - portfolio_mean) / portfolio_std) ** 2)
    
    # Use a subset of scenarios for integration
    integration_scenarios = portfolio_returns[:5000]
    shortfall_values = shortfall_integrand(integration_scenarios)
    
    # Calculate expected shortfall using Monte Carlo integration
    mc_result = monte_carlo_integral(
        integration_scenarios.reshape(-1, 1),
        shortfall_values,
        lambda x: returns_pdf(x.flatten())
    )
    
    # Expected Shortfall is the conditional expectation given VaR breach
    prob_var_breach = np.mean(portfolio_returns < var_95)
    expected_shortfall = mc_result['integral'] / prob_var_breach if prob_var_breach > 0 else 0
    
    print(f"Expected Shortfall (95% CVaR): {expected_shortfall:.2%}")
    print(f"Monte Carlo Integration Uncertainty: ±{mc_result['uncertainty']:.4f}")
    
    # Summary
    print(f"\n" + "=" * 50)
    print("FINANCIAL RISK ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Portfolio Expected Return: {portfolio_mean:.2%}")
    print(f"Portfolio Risk (Volatility): {portfolio_std:.2%}")
    print(f"95% Value at Risk: {var_95:.2%}")
    print(f"99% Value at Risk: {var_99:.2%}")
    print(f"Expected Shortfall (95%): {expected_shortfall:.2%}")
    print(f"\nMost influential weight for risk: {risk_sensitivity.index[0]}")
    print(f"Most influential weight for return: {return_sensitivity.index[0]}")

if __name__ == "__main__":
    main()
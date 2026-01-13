"""
Monte Carlo Integration module.

This module provides various Monte Carlo and quasi-Monte Carlo integration
methods with importance sampling capabilities, chunked processing for large
datasets, and extensible base classes for custom methods.
"""

from mcpost.integration.monte_carlo import monte_carlo_integral
from mcpost.integration.quasi_monte_carlo import qmc_integral, qmc_integral_auto
from mcpost.integration.importance import qmc_integral_importance

# Extensible base classes and interfaces
from mcpost.integration.base import (
    BaseIntegrationMethod,
    MonteCarloMethod,
    QuasiMonteCarloMethod,
    ImportanceSamplingMethod,
    AdaptiveMethod,
    IntegrationResult,
    integration_registry,
    register_integration_method
)

# Chunked processing for large datasets
from mcpost.integration.chunked_integration import (
    chunked_monte_carlo_integral,
    chunked_qmc_integral
)

__all__ = [
    "monte_carlo_integral",
    "qmc_integral",
    "qmc_integral_auto", 
    "qmc_integral_importance",
    # Chunked processing
    "chunked_monte_carlo_integral",
    "chunked_qmc_integral",
    # Extension interfaces
    "BaseIntegrationMethod",
    "MonteCarloMethod", 
    "QuasiMonteCarloMethod",
    "ImportanceSamplingMethod",
    "AdaptiveMethod",
    "IntegrationResult",
    "integration_registry",
    "register_integration_method",
]
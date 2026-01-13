"""
MCPost: Monte Carlo Post-analysis Package

A comprehensive package for post-analysis of Monte Carlo samples, including
global sensitivity analysis (GSA) and Monte Carlo integration capabilities.
"""

from mcpost._version import __version__

# Core GSA functions
from mcpost.gsa import gsa_pipeline, gsa_for_target, sensitivity_table_to_latex

# Chunked processing functions for large datasets
from mcpost.gsa.chunked_pipeline import chunked_gsa_pipeline, chunked_gsa_for_target
from mcpost.integration.chunked_integration import chunked_monte_carlo_integral, chunked_qmc_integral

# Core integration functions  
from mcpost.integration import monte_carlo_integral, qmc_integral, qmc_integral_auto, qmc_integral_importance

# Extension interfaces
from mcpost.gsa.base import (
    BaseSensitivityMethod, VarianceBasedMethod, ModelBasedMethod, 
    GSAResult, gsa_registry, register_gsa_method
)
from mcpost.integration.base import (
    BaseIntegrationMethod, MonteCarloMethod, QuasiMonteCarloMethod,
    ImportanceSamplingMethod, AdaptiveMethod, IntegrationResult,
    integration_registry, register_integration_method
)

# Utility functions
from mcpost.utils import (
    validate_inputs, 
    configure_defaults, 
    GSAConfig, 
    IntegrationConfig,
    drop_constant_columns,
    infer_bounds_from_data
)

# Optional plotting functions (require matplotlib)
try:
    from mcpost.gsa import plot_sensitivity_metrics
    _HAS_PLOTTING = True
except ImportError:
    _HAS_PLOTTING = False
    plot_sensitivity_metrics = None

__all__ = [
    "__version__",
    # GSA functions
    "gsa_pipeline",
    "gsa_for_target", 
    "sensitivity_table_to_latex",
    # Chunked processing functions
    "chunked_gsa_pipeline",
    "chunked_gsa_for_target",
    "chunked_monte_carlo_integral",
    "chunked_qmc_integral",
    # Integration functions
    "monte_carlo_integral",
    "qmc_integral", 
    "qmc_integral_auto",
    "qmc_integral_importance",
    # Extension interfaces - GSA
    "BaseSensitivityMethod",
    "VarianceBasedMethod", 
    "ModelBasedMethod",
    "GSAResult",
    "gsa_registry",
    "register_gsa_method",
    # Extension interfaces - Integration
    "BaseIntegrationMethod",
    "MonteCarloMethod",
    "QuasiMonteCarloMethod", 
    "ImportanceSamplingMethod",
    "AdaptiveMethod",
    "IntegrationResult",
    "integration_registry",
    "register_integration_method",
    # Utilities
    "validate_inputs",
    "configure_defaults",
    "GSAConfig",
    "IntegrationConfig", 
    "drop_constant_columns",
    "infer_bounds_from_data",
]

# Add plotting function to __all__ only if available
if _HAS_PLOTTING:
    __all__.append("plot_sensitivity_metrics")
"""
Global Sensitivity Analysis (GSA) module.

This module provides comprehensive global sensitivity analysis capabilities
including multiple sensitivity metrics, Gaussian Process surrogates, 
visualization tools, and extensible base classes for custom methods.
"""

from mcpost.gsa.pipeline import gsa_pipeline, gsa_for_target
from mcpost.gsa.plotting import sensitivity_table_to_latex

# Extensible base classes and interfaces
from mcpost.gsa.base import (
    BaseSensitivityMethod,
    VarianceBasedMethod, 
    ModelBasedMethod,
    GSAResult,
    gsa_registry,
    register_gsa_method
)

# Chunked processing for large datasets
from mcpost.gsa.chunked_pipeline import chunked_gsa_for_target, chunked_gsa_pipeline

# Conditional import for plotting functions that require matplotlib
try:
    from mcpost.gsa.plotting import plot_sensitivity_metrics
    _HAS_PLOTTING = True
except ImportError:
    _HAS_PLOTTING = False
    plot_sensitivity_metrics = None

__all__ = [
    "gsa_pipeline",
    "gsa_for_target",
    "sensitivity_table_to_latex",
    # Chunked processing
    "chunked_gsa_for_target",
    "chunked_gsa_pipeline", 
    # Extension interfaces
    "BaseSensitivityMethod",
    "VarianceBasedMethod",
    "ModelBasedMethod", 
    "GSAResult",
    "gsa_registry",
    "register_gsa_method",
]

# Add plotting function to __all__ only if available
if _HAS_PLOTTING:
    __all__.append("plot_sensitivity_metrics")
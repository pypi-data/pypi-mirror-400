"""
Utilities module.

This module provides shared utility functions for data preprocessing,
input validation, configuration management, and chunked processing.
"""

from mcpost.utils.validation import validate_inputs
from mcpost.utils.config import configure_defaults, GSAConfig, IntegrationConfig
from mcpost.utils.data import drop_constant_columns, infer_bounds_from_data
from mcpost.utils.chunked import (
    suggest_chunking_strategy, 
    estimate_memory_usage,
    calculate_optimal_chunk_size,
    ChunkedGSAProcessor,
    ChunkedIntegrationProcessor
)
from mcpost.utils.profiling import (
    profile_function,
    profile_decorator,
    PerformanceMonitor,
    ProfileResult,
    MemoryTracker,
    quick_profile,
    memory_profile,
    compare_implementations
)

__all__ = [
    "validate_inputs",
    "configure_defaults",
    "GSAConfig",
    "IntegrationConfig",
    "drop_constant_columns",
    "infer_bounds_from_data",
    "suggest_chunking_strategy",
    "estimate_memory_usage", 
    "calculate_optimal_chunk_size",
    "ChunkedGSAProcessor",
    "ChunkedIntegrationProcessor",
    # Profiling utilities
    "profile_function",
    "profile_decorator", 
    "PerformanceMonitor",
    "ProfileResult",
    "MemoryTracker",
    "quick_profile",
    "memory_profile",
    "compare_implementations",
]
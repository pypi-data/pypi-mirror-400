"""
Pytest configuration and fixtures for MCPost tests.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import os
from pathlib import Path
from typing import Tuple, Dict, Any
import warnings

# Suppress warnings during testing
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    np.random.seed(42)
    n_samples, n_params = 100, 5
    X = np.random.random((n_samples, n_params))
    y = np.sin(6 * X[:, 0]) + 0.6 * X[:, 1]**2 + 0.1 * np.random.normal(size=n_samples)
    Y = y.reshape(-1, 1)
    return X, Y


@pytest.fixture
def large_sample_data():
    """Generate larger sample data for performance testing."""
    np.random.seed(42)
    n_samples, n_params = 1000, 10
    X = np.random.random((n_samples, n_params))
    y = (np.sin(6 * X[:, 0]) + 0.6 * X[:, 1]**2 + 
         0.3 * X[:, 2] * X[:, 3] + 0.1 * np.random.normal(size=n_samples))
    Y = y.reshape(-1, 1)
    return X, Y


@pytest.fixture
def multi_target_data():
    """Generate multi-target sample data for testing."""
    np.random.seed(42)
    n_samples, n_params, n_targets = 100, 5, 3
    X = np.random.random((n_samples, n_params))
    Y = np.zeros((n_samples, n_targets))
    Y[:, 0] = np.sin(6 * X[:, 0]) + 0.6 * X[:, 1]**2
    Y[:, 1] = np.cos(4 * X[:, 2]) + 0.4 * X[:, 3]
    Y[:, 2] = X[:, 0] * X[:, 1] + 0.2 * X[:, 4]**3
    Y += 0.1 * np.random.normal(size=Y.shape)
    return X, Y


@pytest.fixture
def integration_data():
    """Generate data for integration testing."""
    np.random.seed(42)
    n_samples = 1000
    # Parameters for a 2D integration problem
    params = np.random.uniform(-1, 1, (n_samples, 2))
    # Simple function: f(x,y) = x^2 + y^2
    data = params[:, 0]**2 + params[:, 1]**2
    return params, data


@pytest.fixture
def param_names():
    """Standard parameter names for testing."""
    return ['param_1', 'param_2', 'param_3', 'param_4', 'param_5']


@pytest.fixture
def feature_names():
    """Standard feature names for testing."""
    return ['feature_1', 'feature_2', 'feature_3']


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def package_root():
    """Get the package root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def gsa_config():
    """Standard GSA configuration for testing."""
    return {
        'scaler': 'minmax',
        'kernel': 'rbf',
        'n_sobol': 1024,
        'enable_perm': True,
        'enable_gp': True,
        'enable_sobol': True,
        'random_state': 42
    }


@pytest.fixture
def integration_config():
    """Standard integration configuration for testing."""
    return {
        'method': 'sobol',
        'n_samples': 1000,
        'random_state': 42
    }


@pytest.fixture(scope="session")
def numerical_tolerance():
    """Numerical tolerance for floating point comparisons."""
    return {
        'rtol': 1e-10,
        'atol': 1e-12
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "property: marks tests as property-based tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark property-based tests
        if "property" in item.nodeid or "test_properties" in item.nodeid:
            item.add_marker(pytest.mark.property)
        
        # Mark integration tests
        if "integration" in item.nodeid or "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests (default for most tests)
        if not any(marker.name in ["property", "integration", "slow"] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
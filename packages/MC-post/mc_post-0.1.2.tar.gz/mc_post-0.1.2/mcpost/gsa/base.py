"""
Base classes and interfaces for extensible GSA methods.

This module provides abstract base classes that enable users to extend
MCPost with custom sensitivity analysis methods while maintaining
consistent interfaces and integration with the existing pipeline.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass


@dataclass
class GSAResult:
    """
    Standard result container for GSA methods.
    
    Provides a consistent interface for all GSA method results,
    enabling interoperability between different sensitivity analysis approaches.
    
    Attributes
    ----------
    sensitivity_values : np.ndarray
        Array of sensitivity values for each parameter
    parameter_names : List[str]
        Names of the parameters
    method_name : str
        Name of the GSA method used
    metadata : Dict[str, Any]
        Additional method-specific information
    uncertainty : np.ndarray, optional
        Uncertainty estimates for sensitivity values
    rankings : np.ndarray, optional
        Parameter importance rankings
    """
    sensitivity_values: np.ndarray
    parameter_names: List[str]
    method_name: str
    metadata: Dict[str, Any]
    uncertainty: Optional[np.ndarray] = None
    rankings: Optional[np.ndarray] = None
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to a pandas DataFrame."""
        data = {
            'parameter': self.parameter_names,
            'sensitivity': self.sensitivity_values,
        }
        
        if self.uncertainty is not None:
            data['uncertainty'] = self.uncertainty
            
        if self.rankings is not None:
            data['rank'] = self.rankings
            
        df = pd.DataFrame(data)
        df.set_index('parameter', inplace=True)
        return df
    
    def get_top_parameters(self, n: int = 5) -> List[str]:
        """Get the top n most sensitive parameters."""
        if self.rankings is not None:
            sorted_indices = np.argsort(self.rankings)
        else:
            sorted_indices = np.argsort(self.sensitivity_values)[::-1]
        
        return [self.parameter_names[i] for i in sorted_indices[:n]]


class BaseSensitivityMethod(ABC):
    """
    Abstract base class for sensitivity analysis methods.
    
    This class defines the interface that all GSA methods must implement
    to be compatible with the MCPost pipeline. Custom methods should
    inherit from this class and implement the required abstract methods.
    
    Examples
    --------
    >>> class CustomGSAMethod(BaseSensitivityMethod):
    ...     def __init__(self, custom_param=1.0):
    ...         super().__init__()
    ...         self.custom_param = custom_param
    ...     
    ...     def compute_sensitivity(self, X, y, **kwargs):
    ...         # Custom sensitivity computation
    ...         sensitivity = np.var(X, axis=0) * self.custom_param
    ...         return GSAResult(
    ...             sensitivity_values=sensitivity,
    ...             parameter_names=[f"p{i}" for i in range(X.shape[1])],
    ...             method_name="CustomMethod",
    ...             metadata={"custom_param": self.custom_param}
    ...         )
    ...     
    ...     def validate_inputs(self, X, y):
    ...         if X.shape[0] != len(y):
    ...             raise ValueError("X and y must have same number of samples")
    >>> 
    >>> # Use custom method
    >>> method = CustomGSAMethod(custom_param=2.0)
    >>> X = np.random.random((100, 5))
    >>> y = np.sum(X, axis=1)
    >>> result = method.compute_sensitivity(X, y)
    >>> print(result.to_dataframe())
    """
    
    def __init__(self):
        """Initialize the sensitivity method."""
        self.name = self.__class__.__name__
        self.is_fitted = False
        
    @abstractmethod
    def compute_sensitivity(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        **kwargs
    ) -> GSAResult:
        """
        Compute sensitivity indices for the given data.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_parameters)
            Input parameter samples
        y : np.ndarray, shape (n_samples,)
            Output values
        **kwargs
            Method-specific parameters
            
        Returns
        -------
        GSAResult
            Sensitivity analysis results
        """
        pass
    
    def validate_inputs(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Validate input data.
        
        Parameters
        ----------
        X : np.ndarray
            Input parameters
        y : np.ndarray
            Output values
            
        Raises
        ------
        ValueError
            If inputs are invalid
        """
        if not isinstance(X, np.ndarray) or not isinstance(y, np.ndarray):
            raise TypeError("X and y must be numpy arrays")
            
        if X.ndim != 2:
            raise ValueError("X must be 2-dimensional")
            
        if y.ndim != 1:
            raise ValueError("y must be 1-dimensional")
            
        if X.shape[0] != len(y):
            raise ValueError("X and y must have the same number of samples")
            
        if X.shape[0] == 0:
            raise ValueError("Input arrays cannot be empty")
    
    def preprocess_data(
        self, 
        X: np.ndarray, 
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess input data before sensitivity analysis.
        
        Default implementation returns data unchanged. Override this method
        to implement custom preprocessing (scaling, transformation, etc.).
        
        Parameters
        ----------
        X : np.ndarray
            Input parameters
        y : np.ndarray
            Output values
            
        Returns
        -------
        tuple
            (preprocessed_X, preprocessed_y)
        """
        return X.copy(), y.copy()
    
    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> 'BaseSensitivityMethod':
        """
        Fit the sensitivity method to data.
        
        For methods that require training or parameter estimation.
        Default implementation does nothing.
        
        Parameters
        ----------
        X : np.ndarray
            Input parameters
        y : np.ndarray
            Output values
        **kwargs
            Method-specific parameters
            
        Returns
        -------
        self
            Fitted method instance
        """
        self.validate_inputs(X, y)
        self.is_fitted = True
        return self
    
    def __call__(self, X: np.ndarray, y: np.ndarray, **kwargs) -> GSAResult:
        """
        Convenience method to compute sensitivity.
        
        Equivalent to calling compute_sensitivity directly.
        """
        return self.compute_sensitivity(X, y, **kwargs)


class VarianceBasedMethod(BaseSensitivityMethod):
    """
    Base class for variance-based sensitivity methods.
    
    Provides common functionality for methods that decompose output variance
    into contributions from different input parameters (e.g., Sobol indices).
    """
    
    def __init__(self, n_bootstrap: int = 100):
        """
        Initialize variance-based method.
        
        Parameters
        ----------
        n_bootstrap : int, default=100
            Number of bootstrap samples for uncertainty estimation
        """
        super().__init__()
        self.n_bootstrap = n_bootstrap
    
    def estimate_total_variance(self, y: np.ndarray) -> float:
        """Estimate total output variance."""
        return np.var(y, ddof=1)
    
    def bootstrap_uncertainty(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        **kwargs
    ) -> np.ndarray:
        """
        Estimate uncertainty using bootstrap resampling.
        
        Parameters
        ----------
        X : np.ndarray
            Input parameters
        y : np.ndarray
            Output values
        **kwargs
            Method-specific parameters
            
        Returns
        -------
        np.ndarray
            Standard errors for sensitivity indices
        """
        n_samples = len(y)
        n_params = X.shape[1]
        bootstrap_results = np.zeros((self.n_bootstrap, n_params))
        
        for i in range(self.n_bootstrap):
            # Bootstrap sample
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_boot = X[indices]
            y_boot = y[indices]
            
            # Compute sensitivity for bootstrap sample
            result = self.compute_sensitivity(X_boot, y_boot, **kwargs)
            bootstrap_results[i] = result.sensitivity_values
        
        # Return standard errors
        return np.std(bootstrap_results, axis=0, ddof=1)


class ModelBasedMethod(BaseSensitivityMethod):
    """
    Base class for model-based sensitivity methods.
    
    Provides common functionality for methods that use surrogate models
    to estimate sensitivity (e.g., regression-based methods, GP-based methods).
    """
    
    def __init__(self, model=None):
        """
        Initialize model-based method.
        
        Parameters
        ----------
        model : object, optional
            Surrogate model instance. If None, a default model will be used.
        """
        super().__init__()
        self.model = model
        self.is_model_fitted = False
    
    @abstractmethod
    def fit_model(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Fit the surrogate model to data.
        
        Parameters
        ----------
        X : np.ndarray
            Input parameters
        y : np.ndarray
            Output values
        """
        pass
    
    @abstractmethod
    def predict_model(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the fitted model.
        
        Parameters
        ----------
        X : np.ndarray
            Input parameters
            
        Returns
        -------
        np.ndarray
            Model predictions
        """
        pass
    
    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> 'ModelBasedMethod':
        """Fit both the method and the underlying model."""
        super().fit(X, y, **kwargs)
        self.fit_model(X, y)
        self.is_model_fitted = True
        return self


class GSAMethodRegistry:
    """
    Registry for managing available GSA methods.
    
    Provides a centralized way to register, discover, and instantiate
    different sensitivity analysis methods.
    
    Examples
    --------
    >>> # Register a custom method
    >>> registry = GSAMethodRegistry()
    >>> registry.register('custom', CustomGSAMethod)
    >>> 
    >>> # List available methods
    >>> print(registry.list_methods())
    >>> 
    >>> # Create method instance
    >>> method = registry.create('custom', custom_param=2.0)
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._methods = {}
        self._register_builtin_methods()
    
    def _register_builtin_methods(self):
        """Register built-in GSA methods."""
        # Import and register built-in methods here
        # This would include existing methods like MI, dCor, etc.
        pass
    
    def register(
        self, 
        name: str, 
        method_class: type, 
        description: str = ""
    ) -> None:
        """
        Register a new GSA method.
        
        Parameters
        ----------
        name : str
            Method name identifier
        method_class : type
            Class implementing BaseSensitivityMethod
        description : str, optional
            Method description
        """
        if not issubclass(method_class, BaseSensitivityMethod):
            raise ValueError(
                f"Method class must inherit from BaseSensitivityMethod, "
                f"got {method_class}"
            )
        
        self._methods[name] = {
            'class': method_class,
            'description': description
        }
    
    def list_methods(self) -> List[str]:
        """List all registered method names."""
        return list(self._methods.keys())
    
    def get_method_info(self, name: str) -> Dict[str, Any]:
        """Get information about a registered method."""
        if name not in self._methods:
            raise ValueError(f"Method '{name}' not found in registry")
        return self._methods[name].copy()
    
    def create(self, name: str, **kwargs) -> BaseSensitivityMethod:
        """
        Create an instance of a registered method.
        
        Parameters
        ----------
        name : str
            Method name
        **kwargs
            Arguments to pass to method constructor
            
        Returns
        -------
        BaseSensitivityMethod
            Method instance
        """
        if name not in self._methods:
            raise ValueError(f"Method '{name}' not found in registry")
        
        method_class = self._methods[name]['class']
        return method_class(**kwargs)
    
    def is_registered(self, name: str) -> bool:
        """Check if a method is registered."""
        return name in self._methods


# Global registry instance
gsa_registry = GSAMethodRegistry()


def register_gsa_method(name: str, description: str = ""):
    """
    Decorator for registering GSA methods.
    
    Parameters
    ----------
    name : str
        Method name identifier
    description : str, optional
        Method description
        
    Examples
    --------
    >>> @register_gsa_method('my_method', 'Custom sensitivity method')
    ... class MyGSAMethod(BaseSensitivityMethod):
    ...     def compute_sensitivity(self, X, y, **kwargs):
    ...         # Implementation here
    ...         pass
    """
    def decorator(method_class):
        gsa_registry.register(name, method_class, description)
        return method_class
    return decorator
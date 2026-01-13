"""
Base classes and interfaces for extensible integration methods.

This module provides abstract base classes that enable users to extend
MCPost with custom Monte Carlo integration methods while maintaining
consistent interfaces and integration with the existing pipeline.
"""

from __future__ import annotations

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from dataclasses import dataclass
import warnings


@dataclass
class IntegrationResult:
    """
    Standard result container for integration methods.
    
    Provides a consistent interface for all integration method results,
    enabling interoperability between different numerical integration approaches.
    
    Attributes
    ----------
    integral : Union[float, np.ndarray]
        Estimated integral value(s)
    uncertainty : Union[float, np.ndarray]
        Uncertainty estimate(s)
    n_samples : int
        Number of samples used
    method_name : str
        Name of the integration method used
    metadata : Dict[str, Any]
        Additional method-specific information
    convergence_info : Dict[str, Any], optional
        Information about convergence behavior
    """
    integral: Union[float, np.ndarray]
    uncertainty: Union[float, np.ndarray]
    n_samples: int
    method_name: str
    metadata: Dict[str, Any]
    convergence_info: Optional[Dict[str, Any]] = None
    
    def relative_error(self) -> Union[float, np.ndarray]:
        """Compute relative uncertainty."""
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.abs(self.uncertainty / self.integral)
    
    def is_converged(self, tolerance: float = 0.01) -> bool:
        """Check if integration has converged within tolerance."""
        rel_err = self.relative_error()
        if np.isscalar(rel_err):
            return rel_err < tolerance
        else:
            return np.all(rel_err < tolerance)
    
    def summary(self) -> str:
        """Return a summary string of the integration results."""
        if np.isscalar(self.integral):
            return (f"{self.method_name}: I = {self.integral:.6f} ± {self.uncertainty:.6f} "
                   f"(n={self.n_samples}, rel_err={self.relative_error():.2%})")
        else:
            return (f"{self.method_name}: I = {self.integral} ± {self.uncertainty} "
                   f"(n={self.n_samples})")


class BaseIntegrationMethod(ABC):
    """
    Abstract base class for numerical integration methods.
    
    This class defines the interface that all integration methods must implement
    to be compatible with the MCPost pipeline. Custom methods should
    inherit from this class and implement the required abstract methods.
    
    Examples
    --------
    >>> class CustomIntegrationMethod(BaseIntegrationMethod):
    ...     def __init__(self, custom_param=1.0):
    ...         super().__init__()
    ...         self.custom_param = custom_param
    ...     
    ...     def integrate(self, func, bounds, n_samples=1000, **kwargs):
    ...         # Custom integration implementation
    ...         # Simple uniform sampling example
    ...         samples = self.generate_samples(bounds, n_samples)
    ...         values = func(samples)
    ...         volume = np.prod([b[1] - b[0] for b in bounds])
    ...         integral = np.mean(values) * volume
    ...         uncertainty = np.std(values) * volume / np.sqrt(n_samples)
    ...         
    ...         return IntegrationResult(
    ...             integral=integral,
    ...             uncertainty=uncertainty,
    ...             n_samples=n_samples,
    ...             method_name="CustomMethod",
    ...             metadata={"custom_param": self.custom_param}
    ...         )
    ...     
    ...     def generate_samples(self, bounds, n_samples):
    ...         # Generate uniform random samples
    ...         samples = np.random.random((n_samples, len(bounds)))
    ...         for i, (low, high) in enumerate(bounds):
    ...             samples[:, i] = low + (high - low) * samples[:, i]
    ...         return samples
    >>> 
    >>> # Use custom method
    >>> method = CustomIntegrationMethod(custom_param=2.0)
    >>> def test_func(x): return np.sum(x**2, axis=1)
    >>> bounds = [[0, 1], [0, 1]]
    >>> result = method.integrate(test_func, bounds, n_samples=10000)
    >>> print(result.summary())
    """
    
    def __init__(self):
        """Initialize the integration method."""
        self.name = self.__class__.__name__
        self.is_adaptive = False  # Whether method supports adaptive sampling
        
    @abstractmethod
    def integrate(
        self,
        func: Callable[[np.ndarray], Union[float, np.ndarray]],
        bounds: List[Tuple[float, float]],
        n_samples: int = 1000,
        **kwargs
    ) -> IntegrationResult:
        """
        Perform numerical integration.
        
        Parameters
        ----------
        func : callable
            Function to integrate. Should accept array of shape (n_samples, n_dims)
            and return array of shape (n_samples,) or (n_samples, n_outputs)
        bounds : List[Tuple[float, float]]
            Integration bounds [(low1, high1), (low2, high2), ...]
        n_samples : int, default=1000
            Number of samples to use
        **kwargs
            Method-specific parameters
            
        Returns
        -------
        IntegrationResult
            Integration results
        """
        pass
    
    def validate_inputs(
        self,
        func: Callable,
        bounds: List[Tuple[float, float]],
        n_samples: int
    ) -> None:
        """
        Validate integration inputs.
        
        Parameters
        ----------
        func : callable
            Function to integrate
        bounds : List[Tuple[float, float]]
            Integration bounds
        n_samples : int
            Number of samples
            
        Raises
        ------
        ValueError
            If inputs are invalid
        """
        if not callable(func):
            raise TypeError("func must be callable")
            
        if not isinstance(bounds, (list, tuple)):
            raise TypeError("bounds must be a list or tuple")
            
        if len(bounds) == 0:
            raise ValueError("bounds cannot be empty")
            
        for i, bound in enumerate(bounds):
            if not isinstance(bound, (list, tuple)) or len(bound) != 2:
                raise ValueError(f"bounds[{i}] must be a 2-element tuple (low, high)")
            
            low, high = bound
            if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
                raise TypeError(f"bounds[{i}] elements must be numeric")
                
            if low >= high:
                raise ValueError(f"bounds[{i}]: low ({low}) must be < high ({high})")
        
        if not isinstance(n_samples, int) or n_samples <= 0:
            raise ValueError("n_samples must be a positive integer")
    
    def estimate_volume(self, bounds: List[Tuple[float, float]]) -> float:
        """Estimate integration domain volume."""
        return np.prod([high - low for low, high in bounds])
    
    def __call__(
        self,
        func: Callable,
        bounds: List[Tuple[float, float]],
        n_samples: int = 1000,
        **kwargs
    ) -> IntegrationResult:
        """
        Convenience method to perform integration.
        
        Equivalent to calling integrate directly.
        """
        return self.integrate(func, bounds, n_samples, **kwargs)


class MonteCarloMethod(BaseIntegrationMethod):
    """
    Base class for Monte Carlo integration methods.
    
    Provides common functionality for methods that use random sampling
    to estimate integrals.
    """
    
    def __init__(self, random_state: Optional[int] = None):
        """
        Initialize Monte Carlo method.
        
        Parameters
        ----------
        random_state : int, optional
            Random seed for reproducibility
        """
        super().__init__()
        self.random_state = random_state
        if random_state is not None:
            np.random.seed(random_state)
    
    def generate_uniform_samples(
        self,
        bounds: List[Tuple[float, float]],
        n_samples: int
    ) -> np.ndarray:
        """
        Generate uniform random samples within bounds.
        
        Parameters
        ----------
        bounds : List[Tuple[float, float]]
            Integration bounds
        n_samples : int
            Number of samples
            
        Returns
        -------
        np.ndarray
            Random samples of shape (n_samples, n_dims)
        """
        n_dims = len(bounds)
        samples = np.random.random((n_samples, n_dims))
        
        for i, (low, high) in enumerate(bounds):
            samples[:, i] = low + (high - low) * samples[:, i]
            
        return samples
    
    def estimate_uncertainty(
        self,
        values: np.ndarray,
        volume: float
    ) -> Union[float, np.ndarray]:
        """
        Estimate integration uncertainty using sample variance.
        
        Parameters
        ----------
        values : np.ndarray
            Function evaluations
        volume : float
            Integration domain volume
            
        Returns
        -------
        Union[float, np.ndarray]
            Uncertainty estimate
        """
        n_samples = len(values)
        if values.ndim == 1:
            return np.std(values, ddof=1) * volume / np.sqrt(n_samples)
        else:
            return np.std(values, axis=0, ddof=1) * volume / np.sqrt(n_samples)


class QuasiMonteCarloMethod(BaseIntegrationMethod):
    """
    Base class for Quasi-Monte Carlo integration methods.
    
    Provides common functionality for methods that use low-discrepancy
    sequences for more efficient sampling.
    """
    
    def __init__(self, sequence_type: str = "sobol"):
        """
        Initialize QMC method.
        
        Parameters
        ----------
        sequence_type : str, default="sobol"
            Type of low-discrepancy sequence: "sobol", "halton", etc.
        """
        super().__init__()
        self.sequence_type = sequence_type
    
    @abstractmethod
    def generate_qmc_samples(
        self,
        bounds: List[Tuple[float, float]],
        n_samples: int
    ) -> np.ndarray:
        """
        Generate quasi-random samples using low-discrepancy sequence.
        
        Parameters
        ----------
        bounds : List[Tuple[float, float]]
            Integration bounds
        n_samples : int
            Number of samples
            
        Returns
        -------
        np.ndarray
            QMC samples of shape (n_samples, n_dims)
        """
        pass
    
    def estimate_qmc_uncertainty(
        self,
        values: np.ndarray,
        volume: float
    ) -> Union[float, np.ndarray]:
        """
        Estimate QMC integration uncertainty.
        
        QMC methods typically have O(1/N) convergence rather than O(1/sqrt(N)).
        This provides a rough uncertainty estimate.
        """
        n_samples = len(values)
        if values.ndim == 1:
            return np.std(values, ddof=1) * volume / n_samples
        else:
            return np.std(values, axis=0, ddof=1) * volume / n_samples


class ImportanceSamplingMethod(MonteCarloMethod):
    """
    Base class for importance sampling integration methods.
    
    Provides common functionality for methods that use importance sampling
    to reduce variance in Monte Carlo integration.
    """
    
    def __init__(
        self,
        proposal_dist: Optional[Callable] = None,
        random_state: Optional[int] = None
    ):
        """
        Initialize importance sampling method.
        
        Parameters
        ----------
        proposal_dist : callable, optional
            Proposal distribution for importance sampling
        random_state : int, optional
            Random seed for reproducibility
        """
        super().__init__(random_state)
        self.proposal_dist = proposal_dist
    
    @abstractmethod
    def compute_importance_weights(
        self,
        samples: np.ndarray,
        target_dist: Callable,
        proposal_dist: Callable
    ) -> np.ndarray:
        """
        Compute importance sampling weights.
        
        Parameters
        ----------
        samples : np.ndarray
            Sample points
        target_dist : callable
            Target distribution density
        proposal_dist : callable
            Proposal distribution density
            
        Returns
        -------
        np.ndarray
            Importance weights
        """
        pass
    
    def effective_sample_size(self, weights: np.ndarray) -> float:
        """
        Compute effective sample size from importance weights.
        
        Parameters
        ----------
        weights : np.ndarray
            Normalized importance weights
            
        Returns
        -------
        float
            Effective sample size
        """
        return 1.0 / np.sum(weights**2)


class AdaptiveMethod(BaseIntegrationMethod):
    """
    Base class for adaptive integration methods.
    
    Provides common functionality for methods that adaptively refine
    their sampling strategy based on function behavior.
    """
    
    def __init__(self, tolerance: float = 1e-3, max_iterations: int = 100):
        """
        Initialize adaptive method.
        
        Parameters
        ----------
        tolerance : float, default=1e-3
            Convergence tolerance
        max_iterations : int, default=100
            Maximum number of adaptive iterations
        """
        super().__init__()
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.is_adaptive = True
    
    @abstractmethod
    def adaptive_step(
        self,
        func: Callable,
        bounds: List[Tuple[float, float]],
        current_estimate: float,
        iteration: int,
        **kwargs
    ) -> Tuple[float, float, bool]:
        """
        Perform one adaptive refinement step.
        
        Parameters
        ----------
        func : callable
            Function to integrate
        bounds : List[Tuple[float, float]]
            Integration bounds
        current_estimate : float
            Current integral estimate
        iteration : int
            Current iteration number
        **kwargs
            Method-specific parameters
            
        Returns
        -------
        tuple
            (new_estimate, uncertainty, converged)
        """
        pass
    
    def check_convergence(
        self,
        estimate: float,
        uncertainty: float,
        iteration: int
    ) -> bool:
        """
        Check if adaptive integration has converged.
        
        Parameters
        ----------
        estimate : float
            Current integral estimate
        uncertainty : float
            Current uncertainty estimate
        iteration : int
            Current iteration number
            
        Returns
        -------
        bool
            True if converged
        """
        if iteration >= self.max_iterations:
            warnings.warn(
                f"Maximum iterations ({self.max_iterations}) reached without convergence",
                UserWarning
            )
            return True
        
        relative_error = abs(uncertainty / estimate) if estimate != 0 else uncertainty
        return relative_error < self.tolerance


class IntegrationMethodRegistry:
    """
    Registry for managing available integration methods.
    
    Provides a centralized way to register, discover, and instantiate
    different numerical integration methods.
    
    Examples
    --------
    >>> # Register a custom method
    >>> registry = IntegrationMethodRegistry()
    >>> registry.register('custom_mc', CustomIntegrationMethod)
    >>> 
    >>> # List available methods
    >>> print(registry.list_methods())
    >>> 
    >>> # Create method instance
    >>> method = registry.create('custom_mc', custom_param=2.0)
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._methods = {}
        self._register_builtin_methods()
    
    def _register_builtin_methods(self):
        """Register built-in integration methods."""
        # Import and register built-in methods here
        # This would include existing methods like standard MC, QMC, etc.
        pass
    
    def register(
        self,
        name: str,
        method_class: type,
        description: str = ""
    ) -> None:
        """
        Register a new integration method.
        
        Parameters
        ----------
        name : str
            Method name identifier
        method_class : type
            Class implementing BaseIntegrationMethod
        description : str, optional
            Method description
        """
        if not issubclass(method_class, BaseIntegrationMethod):
            raise ValueError(
                f"Method class must inherit from BaseIntegrationMethod, "
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
    
    def create(self, name: str, **kwargs) -> BaseIntegrationMethod:
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
        BaseIntegrationMethod
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
integration_registry = IntegrationMethodRegistry()


def register_integration_method(name: str, description: str = ""):
    """
    Decorator for registering integration methods.
    
    Parameters
    ----------
    name : str
        Method name identifier
    description : str, optional
        Method description
        
    Examples
    --------
    >>> @register_integration_method('my_mc', 'Custom Monte Carlo method')
    ... class MyMCMethod(MonteCarloMethod):
    ...     def integrate(self, func, bounds, n_samples=1000, **kwargs):
    ...         # Implementation here
    ...         pass
    """
    def decorator(method_class):
        integration_registry.register(name, method_class, description)
        return method_class
    return decorator
from typing import Any, Callable, Tuple, Optional
from abc import ABC, abstractmethod

from .backends import Backend


class NumericalScheme(ABC):
    @abstractmethod
    def step(
        self,
        backend: Backend,
        sde_drift: Callable,
        sde_diffusion: Callable,
        state: Any,
        dt: float,
        dW: Any
    ) -> Any:
        pass


class EulerScheme(NumericalScheme):
    def step(
        self,
        backend: Backend,
        sde_drift: Callable,
        sde_diffusion: Callable,
        state: Any,
        dt: float,
        dW: Any
    ) -> Any:
        drift = sde_drift(state) * dt
        diffusion = sde_diffusion(state) * dW
        return state + drift + diffusion


class HybridScheme(NumericalScheme):
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
    
    def step(
        self,
        backend: Backend,
        sde_drift: Callable,
        sde_diffusion: Callable,
        state: Any,
        dt: float,
        dW: Any
    ) -> Any:
        euler_step = EulerScheme().step(backend, sde_drift, sde_diffusion, state, dt, dW)
        
        drift_next = sde_drift(euler_step) * dt
        diffusion_current = sde_diffusion(state) * dW
        
        hybrid_step = state + self.alpha * sde_drift(state) * dt + (1 - self.alpha) * drift_next + diffusion_current
        
        return hybrid_step

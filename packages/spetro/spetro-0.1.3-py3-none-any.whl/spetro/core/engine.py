from typing import Union, Dict, Any, Optional, Tuple
import numpy as np
from abc import ABC, abstractmethod

from .backends import JAXBackend, TorchBackend, Backend
from .models import RoughVolatilityModel


class RoughVolatilityEngine:
    def __init__(
        self,
        backend: str = "jax",
        device: Optional[str] = None,
        precision: str = "float32"
    ):
        if backend not in ["jax", "torch"]:
            raise ValueError(f"unsupported backend: {backend}. supported: ['jax', 'torch']")
        
        if precision not in ["float32", "float64"]:
            raise ValueError(f"unsupported precision: {precision}. supported: ['float32', 'float64']")
        
        self.backend_name = backend
        self.device = device
        self.precision = precision
        
        try:
            if backend == "jax":
                self.backend = JAXBackend(device=device, precision=precision)
            elif backend == "torch":
                self.backend = TorchBackend(device=device, precision=precision)
        except ImportError as e:
            raise ImportError(f"backend '{backend}' not available. install required dependencies: {e}")
    
    def simulate(
        self,
        model: RoughVolatilityModel,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float = 100.0,
        key: Optional[Any] = None
    ) -> Tuple[Any, Any]:
        if n_paths <= 0:
            raise ValueError(f"n_paths must be positive, got {n_paths}")
        if n_steps <= 0:
            raise ValueError(f"n_steps must be positive, got {n_steps}")
        if T <= 0:
            raise ValueError(f"T must be positive, got {T}")
        if S0 <= 0:
            raise ValueError(f"S0 must be positive, got {S0}")
        
        return model.simulate(
            backend=self.backend,
            n_paths=n_paths,
            n_steps=n_steps,
            T=T,
            S0=S0,
            key=key
        )
    
    def price(
        self,
        model: RoughVolatilityModel,
        payoff_fn: callable,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float = 100.0,
        key: Optional[Any] = None,
        antithetic: bool = True
    ) -> Dict[str, float]:
        if antithetic and n_paths % 2 == 0:
            n_half = n_paths // 2
            S1, _ = model.simulate(self.backend, n_half, n_steps, T, S0, key, antithetic=False)
            S2, _ = model.simulate(self.backend, n_half, n_steps, T, S0, key, antithetic=True)
            if hasattr(self.backend, 'jnp'):
                S = self.backend.jnp.concatenate([S1, S2], axis=0)
            else:
                S = self.backend.torch.cat([S1, S2], dim=0)
            payoffs = payoff_fn(S)
        else:
            S, V = self.simulate(model, n_paths, n_steps, T, S0, key)
            payoffs = payoff_fn(S)
        
        price = self.backend.mean(payoffs)
        std_error = self.backend.std(payoffs) / self.backend.sqrt(n_paths)
        
        return {
            "price": float(price),
            "std_error": float(std_error),
            "paths": n_paths
        }
    
    def greeks(
        self,
        model: RoughVolatilityModel,
        payoff_fn: callable,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float = 100.0,
        key: Optional[Any] = None
    ) -> Dict[str, float]:
        def price_fn(s0):
            S, _ = model.simulate(self.backend, n_paths, n_steps, T, s0, key)
            return self.backend.mean(payoff_fn(S))
        
        grad_fn = self.backend.grad(price_fn)
        price = price_fn(S0)
        delta = grad_fn(S0)
        
        grad2_fn = self.backend.grad(grad_fn)
        gamma = grad2_fn(S0)
        
        return {
            "price": float(price),
            "delta": float(delta),
            "gamma": float(gamma)
        }

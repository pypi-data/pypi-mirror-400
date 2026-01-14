from typing import Any, Callable
import numpy as np


def european_call(K: float) -> Callable[[Any], Any]:
    if K <= 0:
        raise ValueError(f"strike K must be positive, got {K}")
    
    def payoff(S: Any) -> Any:
        try:
            import torch
            if isinstance(S, torch.Tensor):
                return torch.clamp(S[:, -1] - K, min=0.0)
        except ImportError:
            pass
        
        try:
            import jax.numpy as jnp
            if hasattr(S, 'shape') and hasattr(S, 'dtype'):
                return jnp.maximum(S[:, -1] - K, 0.0)
        except ImportError:
            pass
        
        return np.maximum(S[:, -1] - K, 0.0)
    return payoff


def european_put(K: float) -> Callable[[Any], Any]:
    if K <= 0:
        raise ValueError(f"strike K must be positive, got {K}")
    
    def payoff(S: Any) -> Any:
        try:
            import torch
            if isinstance(S, torch.Tensor):
                return torch.clamp(K - S[:, -1], min=0.0)
        except ImportError:
            pass
        
        try:
            import jax.numpy as jnp
            if hasattr(S, 'shape') and hasattr(S, 'dtype'):
                return jnp.maximum(K - S[:, -1], 0.0)
        except ImportError:
            pass
        
        return np.maximum(K - S[:, -1], 0.0)
    return payoff


def asian_call(K: float) -> Callable[[Any], Any]:
    if K <= 0:
        raise ValueError(f"strike K must be positive, got {K}")
    
    def payoff(S: Any) -> Any:
        try:
            import torch
            if isinstance(S, torch.Tensor):
                avg_price = torch.mean(S, dim=1)
                return torch.clamp(avg_price - K, min=0.0)
        except ImportError:
            pass
        
        try:
            import jax.numpy as jnp
            if hasattr(S, 'shape') and hasattr(S, 'dtype'):
                avg_price = jnp.mean(S, axis=1)
                return jnp.maximum(avg_price - K, 0.0)
        except ImportError:
            pass
        
        avg_price = np.mean(S, axis=1)
        return np.maximum(avg_price - K, 0.0)
    return payoff


def barrier_call(K: float, barrier: float, barrier_type: str = "up_and_out") -> Callable[[Any], Any]:
    def payoff(S: Any) -> Any:
        if barrier_type == "up_and_out":
            if hasattr(S, 'jnp') or hasattr(S, '__array__'):
                hit_barrier = np.any(S >= barrier, axis=1)
                call_payoff = np.maximum(S[:, -1] - K, 0.0)
                return call_payoff * (1 - hit_barrier)
            else:
                import torch
                hit_barrier = torch.any(S >= barrier, dim=1)
                call_payoff = torch.clamp(S[:, -1] - K, min=0.0)
                return call_payoff * (~hit_barrier).float()
        
        elif barrier_type == "down_and_out":
            if hasattr(S, 'jnp') or hasattr(S, '__array__'):
                hit_barrier = np.any(S <= barrier, axis=1)
                call_payoff = np.maximum(S[:, -1] - K, 0.0)
                return call_payoff * (1 - hit_barrier)
            else:
                import torch
                hit_barrier = torch.any(S <= barrier, dim=1)
                call_payoff = torch.clamp(S[:, -1] - K, min=0.0)
                return call_payoff * (~hit_barrier).float()
        
        else:
            raise ValueError(f"unsupported barrier type: {barrier_type}")
    
    return payoff


def basket_call(weights: list, K: float) -> Callable[[Any], Any]:
    if K <= 0:
        raise ValueError(f"strike K must be positive, got {K}")
    if not weights:
        raise ValueError("weights cannot be empty")
    
    def payoff(S: Any) -> Any:
        try:
            import torch
            if isinstance(S, torch.Tensor):
                basket_value = sum(w * S[:, -1] for w in weights)
                return torch.clamp(basket_value - K, min=0.0)
        except ImportError:
            pass
        
        try:
            import jax.numpy as jnp
            if hasattr(S, 'shape') and hasattr(S, 'dtype'):
                basket_value = sum(w * S[:, -1] for w in weights)
                return jnp.maximum(basket_value - K, 0.0)
        except ImportError:
            pass
        
        basket_value = sum(w * S[:, -1] for w in weights)
        return np.maximum(basket_value - K, 0.0)
    
    return payoff

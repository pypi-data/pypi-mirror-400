from typing import Any, Optional, Tuple, Dict
from abc import ABC, abstractmethod
import numpy as np

from .backends import Backend


class RoughVolatilityModel(ABC):
    @abstractmethod
    def simulate(
        self,
        backend: Backend,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float,
        key: Optional[Any] = None,
        antithetic: bool = False
    ) -> Tuple[Any, Any]:
        pass


class RoughBergomi(RoughVolatilityModel):
    def __init__(
        self,
        H: float = 0.07,
        eta: float = 1.9,
        rho: float = -0.9,
        xi: float = 0.235**2,
        r: float = 0.0
    ):
        self.H = H
        self.eta = eta
        self.rho = rho
        self.xi = xi
        self.r = r
        
        if not (0 < H < 0.5):
            raise ValueError("hurst parameter must be in (0, 0.5)")
    
    def simulate(
        self,
        backend: Backend,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float,
        key: Optional[Any] = None,
        antithetic: bool = False
    ) -> Tuple[Any, Any]:
        dt = T / n_steps
        
        if key is None:
            if hasattr(backend, 'random') and hasattr(backend.random, 'PRNGKey'):
                key = backend.random.PRNGKey(42)
            else:
                key = 42
        
        if hasattr(backend, 'random') and hasattr(backend.random, 'split'):
            k1, k2 = backend.random.split(key)
        else:
            k1, k2 = key, key + 1
        
        dW1 = backend.random_normal(k1, (n_paths, n_steps)) * backend.sqrt(dt)
        dW2 = backend.random_normal(k2, (n_paths, n_steps)) * backend.sqrt(dt)
        
        if antithetic:
            dW1 = -dW1
            dW2 = -dW2
        
        dB = self.rho * dW1 + backend.sqrt(1 - self.rho**2) * dW2
        
        t_grid = backend.array([i * dt for i in range(n_steps + 1)])
        
        Y = self._fractional_brownian_motion(backend, dW1, t_grid, self.H)
        
        V = backend.zeros((n_steps + 1, n_paths))
        if hasattr(V, 'at'):
            V = V.at[0].set(self.xi)
            for i in range(n_steps):
                vol_term = self.xi * backend.exp(self.eta * Y[:, i] - 0.5 * self.eta**2 * t_grid[i+1])
                V = V.at[i+1].set(vol_term)
        else:
            V[0] = self.xi
            for i in range(n_steps):
                vol_term = self.xi * backend.exp(self.eta * Y[:, i] - 0.5 * self.eta**2 * t_grid[i+1])
                V[i+1] = vol_term
        
        log_S = backend.zeros((n_paths, n_steps + 1))
        if hasattr(log_S, 'at'):
            log_S = log_S.at[:, 0].set(backend.log(S0))
        else:
            log_S[:, 0] = backend.log(S0)
        
        for i in range(n_steps):
            vol = backend.sqrt(V[i])
            drift = (self.r - 0.5 * V[i]) * dt
            diffusion = vol * dB[:, i]
            if hasattr(log_S, 'at'):
                log_S = log_S.at[:, i + 1].set(log_S[:, i] + drift + diffusion)
            else:
                log_S[:, i + 1] = log_S[:, i] + drift + diffusion
        
        S = backend.exp(log_S)
        
        return S, V
    
    def _fractional_brownian_motion(
        self, 
        backend: Backend, 
        dW: Any, 
        t_grid: Any, 
        H: float
    ) -> Any:
        n_paths, n_steps = dW.shape
        dt = t_grid[1] - t_grid[0]
        
        g = self._riemann_liouville_kernel(backend, t_grid[1:], H)
        
        if hasattr(backend, 'jnp'):
            g_rev = g[::-1]
            from jax import vmap
            def conv_path(path):
                return backend.jnp.convolve(path, g_rev, mode='valid')
            y = vmap(conv_path)(dW)
            return y
        else:
            g_rev = backend.torch.flip(g, dims=[0])
            dW_batched = dW.unsqueeze(1)
            kernel_batched = g_rev.unsqueeze(0).unsqueeze(0).unsqueeze(0)
            conv = backend.torch.conv1d(dW_batched, kernel_batched, padding=n_steps-1, groups=n_paths)
            y = conv.squeeze(1)[:, :n_steps]
            return y
    
    def _riemann_liouville_kernel(self, backend: Backend, t: Any, H: float) -> Any:
        def gamma_func(x):
            if hasattr(backend, 'jax'):
                from jax.scipy.special import gamma
                return gamma(x)
            else:
                return backend.torch.exp(backend.torch.lgamma(backend.array(x)))
        
        normalization = backend.sqrt(2 * H * gamma_func(1.5 - H) / gamma_func(H + 0.5))
        
        kernel = normalization * (t ** (H - 0.5))
        
        return kernel


class RoughHeston(RoughVolatilityModel):
    def __init__(
        self,
        H: float = 0.07,
        nu: float = 0.3,
        theta: float = 0.02,
        rho: float = -0.7,
        V0: float = 0.02,
        r: float = 0.0
    ):
        self.H = H
        self.nu = nu
        self.theta = theta
        self.rho = rho
        self.V0 = V0
        self.r = r
        
        if not (0 < H < 0.5):
            raise ValueError("hurst parameter must be in (0, 0.5)")
    
    def simulate(
        self,
        backend: Backend,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float,
        key: Optional[Any] = None,
        antithetic: bool = False
    ) -> Tuple[Any, Any]:
        dt = T / n_steps
        
        if key is None:
            if hasattr(backend, 'random') and hasattr(backend.random, 'PRNGKey'):
                key = backend.random.PRNGKey(42)
            else:
                key = 42
        
        if hasattr(backend, 'random') and hasattr(backend.random, 'split'):
            keys = backend.random.split(key, 3)
            k1, k2, k3 = keys[0], keys[1], keys[2]
        else:
            k1, k2, k3 = key, key + 1, key + 2
        
        dW1 = backend.random_normal(k1, (n_paths, n_steps)) * backend.sqrt(dt)
        dW2 = backend.random_normal(k2, (n_paths, n_steps)) * backend.sqrt(dt)
        dZ = backend.random_normal(k3, (n_paths, n_steps)) * backend.sqrt(dt)
        
        if antithetic:
            dW1 = -dW1
            dW2 = -dW2
            dZ = -dZ
        
        dB = self.rho * dW1 + backend.sqrt(1 - self.rho**2) * dW2
        
        V = backend.zeros((n_paths, n_steps + 1))
        S = backend.zeros((n_paths, n_steps + 1))
        
        V = backend.set_item(V, (slice(None), 0), backend.array([self.V0] * n_paths))
        S = backend.set_item(S, (slice(None), 0), backend.array([S0] * n_paths))
        
        t_grid = backend.array([i * dt for i in range(n_steps + 1)])
        Y = self._fractional_brownian_motion(backend, dZ, t_grid, self.H)
        
        for i in range(n_steps):
            v_curr = V[:, i]
            if hasattr(backend, 'jnp'):
                v_sqrt = backend.sqrt(backend.jnp.maximum(v_curr, backend.array(1e-8)))
            else:
                v_sqrt = backend.sqrt(backend.torch.clamp(v_curr, min=1e-8))
            
            rough_term = self.nu * backend.sqrt(2 * self.H) * Y[:, i] * backend.sqrt(dt)
            mean_reversion = self.theta * (self.V0 - v_curr) * dt
            v_next = v_curr + mean_reversion + rough_term
            if hasattr(backend, 'jnp'):
                v_next = backend.jnp.maximum(v_next, backend.array(0.0))
            else:
                v_next = backend.torch.clamp(v_next, min=0.0)
            
            V = backend.set_item(V, (slice(None), i + 1), v_next)
            
            drift = self.r * dt
            diffusion = v_sqrt * dB[:, i]
            s_next = S[:, i] * backend.exp(drift - 0.5 * v_curr * dt + diffusion)
            
            S = backend.set_item(S, (slice(None), i + 1), s_next)
        
        return S, V
    
    def _fractional_brownian_motion(
        self, 
        backend: Backend, 
        dW: Any, 
        t_grid: Any, 
        H: float
    ) -> Any:
        n_paths, n_steps = dW.shape
        dt = t_grid[1] - t_grid[0]
        
        g = self._riemann_liouville_kernel(backend, t_grid[1:], H)
        
        if hasattr(backend, 'jnp'):
            g_rev = g[::-1]
            from jax import vmap
            def conv_path(path):
                return backend.jnp.convolve(path, g_rev, mode='valid')
            y = vmap(conv_path)(dW)
            return y
        else:
            g_rev = backend.torch.flip(g, dims=[0])
            dW_batched = dW.unsqueeze(1)
            kernel_batched = g_rev.unsqueeze(0).unsqueeze(0).unsqueeze(0)
            conv = backend.torch.conv1d(dW_batched, kernel_batched, padding=n_steps-1, groups=n_paths)
            y = conv.squeeze(1)[:, :n_steps]
            return y
    
    def _riemann_liouville_kernel(self, backend: Backend, t: Any, H: float) -> Any:
        def gamma_func(x):
            if hasattr(backend, 'jax'):
                from jax.scipy.special import gamma
                return gamma(x)
            else:
                return backend.torch.exp(backend.torch.lgamma(backend.array(x)))
        
        normalization = backend.sqrt(2 * H * gamma_func(1.5 - H) / gamma_func(H + 0.5))
        
        kernel = normalization * (t ** (H - 0.5))
        
        return kernel

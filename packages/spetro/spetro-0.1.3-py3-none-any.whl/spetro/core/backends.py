from typing import Any, Optional, Union, Tuple
from abc import ABC, abstractmethod
import numpy as np


class Backend(ABC):
    @abstractmethod
    def array(self, data: Any) -> Any:
        pass
    
    @abstractmethod
    def zeros(self, shape: Tuple[int, ...]) -> Any:
        pass
    
    @abstractmethod
    def random_normal(self, key: Any, shape: Tuple[int, ...]) -> Any:
        pass
    
    @abstractmethod
    def exp(self, x: Any) -> Any:
        pass
    
    @abstractmethod
    def sqrt(self, x: Any) -> Any:
        pass
    
    @abstractmethod
    def log(self, x: Any) -> Any:
        pass
    
    @abstractmethod
    def cumsum(self, x: Any, axis: int = -1) -> Any:
        pass
    
    @abstractmethod
    def mean(self, x: Any, axis: Optional[int] = None) -> Any:
        pass
    
    @abstractmethod
    def std(self, x: Any, axis: Optional[int] = None) -> Any:
        pass
    
    @abstractmethod
    def grad(self, fn: callable) -> callable:
        pass
    
    @abstractmethod
    def set_item(self, arr: Any, idx: Any, val: Any) -> Any:
        pass


class JAXBackend(Backend):
    def __init__(self, device: Optional[str] = None, precision: str = "float32"):
        import jax
        import jax.numpy as jnp
        from jax import random, grad
        
        self.jax = jax
        self.jnp = jnp
        self.random = random
        self.grad_fn = grad
        
        if device:
            self.jax.config.update("jax_default_device", self.jax.devices(device)[0])
        
        self.dtype = jnp.float32 if precision == "float32" else jnp.float64
    
    def array(self, data: Any) -> Any:
        return self.jnp.array(data, dtype=self.dtype)
    
    def zeros(self, shape: Tuple[int, ...]) -> Any:
        return self.jnp.zeros(shape, dtype=self.dtype)
    
    def random_normal(self, key: Any, shape: Tuple[int, ...]) -> Any:
        return self.random.normal(key, shape, dtype=self.dtype)
    
    def exp(self, x: Any) -> Any:
        return self.jnp.exp(x)
    
    def sqrt(self, x: Any) -> Any:
        return self.jnp.sqrt(x)
    
    def log(self, x: Any) -> Any:
        return self.jnp.log(x)
    
    def cumsum(self, x: Any, axis: int = -1) -> Any:
        return self.jnp.cumsum(x, axis=axis)
    
    def mean(self, x: Any, axis: Optional[int] = None) -> Any:
        return self.jnp.mean(x, axis=axis)
    
    def std(self, x: Any, axis: Optional[int] = None) -> Any:
        return self.jnp.std(x, axis=axis)
    
    def grad(self, fn: callable) -> callable:
        return self.grad_fn(fn)
    
    def set_item(self, arr: Any, idx: Any, val: Any) -> Any:
        return arr.at[idx].set(val)


class TorchBackend(Backend):
    def __init__(self, device: Optional[str] = None, precision: str = "float32"):
        import torch
        
        self.torch = torch
        self.device_name = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.device_obj = torch.device(self.device_name)
        self.dtype = torch.float32 if precision == "float32" else torch.float64
    
    def array(self, data: Any) -> Any:
        return self.torch.tensor(data, dtype=self.dtype, device=self.device_obj)
    
    def zeros(self, shape: Tuple[int, ...]) -> Any:
        return self.torch.zeros(shape, dtype=self.dtype, device=self.device_obj)
    
    def random_normal(self, key: Any, shape: Tuple[int, ...]) -> Any:
        if key is not None:
            gen = self.torch.Generator(device=self.device_obj)
            gen.manual_seed(int(key))
            return self.torch.randn(shape, generator=gen, dtype=self.dtype, device=self.device_obj)
        return self.torch.randn(shape, dtype=self.dtype, device=self.device_obj)
    
    def exp(self, x: Any) -> Any:
        if not isinstance(x, self.torch.Tensor):
            x = self.array(x)
        return self.torch.exp(x)
    
    def sqrt(self, x: Any) -> Any:
        if not isinstance(x, self.torch.Tensor):
            x = self.array(x)
        return self.torch.sqrt(x)
    
    def log(self, x: Any) -> Any:
        if not isinstance(x, self.torch.Tensor):
            x = self.array(x)
        return self.torch.log(x)
    
    def cumsum(self, x: Any, axis: int = -1) -> Any:
        if not isinstance(x, self.torch.Tensor):
            x = self.array(x)
        return self.torch.cumsum(x, dim=axis)
    
    def mean(self, x: Any, axis: Optional[int] = None) -> Any:
        if not isinstance(x, self.torch.Tensor):
            x = self.array(x)
        if axis is None:
            return self.torch.mean(x)
        return self.torch.mean(x, dim=axis)
    
    def std(self, x: Any, axis: Optional[int] = None) -> Any:
        if not isinstance(x, self.torch.Tensor):
            x = self.array(x)
        if axis is None:
            return self.torch.std(x)
        return self.torch.std(x, dim=axis)
    
    def grad(self, fn: callable) -> callable:
        def grad_fn(x):
            if not isinstance(x, self.torch.Tensor):
                x_tensor = self.array(x)
            else:
                x_tensor = x
            x_tensor = x_tensor.clone().detach().requires_grad_(True)
            y = fn(x_tensor)
            return self.torch.autograd.grad(y, x_tensor, create_graph=True)[0]
        return grad_fn
    
    def set_item(self, arr: Any, idx: Any, val: Any) -> Any:
        arr[idx] = val
        return arr

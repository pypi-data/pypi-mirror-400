from typing import Dict, Any, Optional, Callable, Union
import numpy as np

from ..core.engine import RoughVolatilityEngine
from ..core.models import RoughVolatilityModel


class Pricer:
    def __init__(self, engine: RoughVolatilityEngine):
        self.engine = engine
    
    def price_european(
        self,
        model: RoughVolatilityModel,
        option_type: str,
        K: float,
        T: float,
        S0: float = 100.0,
        n_paths: int = 100000,
        n_steps: int = 252,
        antithetic: bool = True
    ) -> Dict[str, float]:
        from .payoffs import european_call, european_put
        
        if option_type.lower() == "call":
            payoff_fn = european_call(K)
        elif option_type.lower() == "put":
            payoff_fn = european_put(K)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
        
        return self.engine.price(
            model=model,
            payoff_fn=payoff_fn,
            n_paths=n_paths,
            n_steps=n_steps,
            T=T,
            S0=S0,
            antithetic=antithetic
        )
    
    def price_asian(
        self,
        model: RoughVolatilityModel,
        option_type: str,
        K: float,
        T: float,
        S0: float = 100.0,
        n_paths: int = 100000,
        n_steps: int = 252
    ) -> Dict[str, float]:
        from .payoffs import asian_call
        
        if option_type.lower() != "call":
            raise NotImplementedError("only asian call options supported")
        
        payoff_fn = asian_call(K)
        
        return self.engine.price(
            model=model,
            payoff_fn=payoff_fn,
            n_paths=n_paths,
            n_steps=n_steps,
            T=T,
            S0=S0,
            antithetic=False
        )
    
    def price_barrier(
        self,
        model: RoughVolatilityModel,
        K: float,
        barrier: float,
        barrier_type: str,
        T: float,
        S0: float = 100.0,
        n_paths: int = 100000,
        n_steps: int = 252
    ) -> Dict[str, float]:
        from .payoffs import barrier_call
        
        payoff_fn = barrier_call(K, barrier, barrier_type)
        
        return self.engine.price(
            model=model,
            payoff_fn=payoff_fn,
            n_paths=n_paths,
            n_steps=n_steps,
            T=T,
            S0=S0,
            antithetic=False
        )
    
    def price_custom(
        self,
        model: RoughVolatilityModel,
        payoff_fn: Callable[[Any], Any],
        T: float,
        S0: float = 100.0,
        n_paths: int = 100000,
        n_steps: int = 252,
        antithetic: bool = True
    ) -> Dict[str, float]:
        return self.engine.price(
            model=model,
            payoff_fn=payoff_fn,
            n_paths=n_paths,
            n_steps=n_steps,
            T=T,
            S0=S0,
            antithetic=antithetic
        )
    
    def greeks(
        self,
        model: RoughVolatilityModel,
        option_type: str,
        K: float,
        T: float,
        S0: float = 100.0,
        n_paths: int = 100000,
        n_steps: int = 252
    ) -> Dict[str, float]:
        from .payoffs import european_call, european_put
        
        if option_type.lower() == "call":
            payoff_fn = european_call(K)
        elif option_type.lower() == "put":
            payoff_fn = european_put(K)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
        
        return self.engine.greeks(
            model=model,
            payoff_fn=payoff_fn,
            n_paths=n_paths,
            n_steps=n_steps,
            T=T,
            S0=S0
        )

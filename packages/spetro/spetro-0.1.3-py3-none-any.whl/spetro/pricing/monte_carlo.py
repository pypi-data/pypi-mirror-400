from typing import Dict, Any, Optional, Callable, List, Tuple
import numpy as np

from ..core.engine import RoughVolatilityEngine
from ..core.models import RoughVolatilityModel


class MonteCarloPricer:
    def __init__(self, engine: RoughVolatilityEngine):
        self.engine = engine
    
    def price_portfolio(
        self,
        models: List[RoughVolatilityModel],
        payoff_fns: List[Callable[[Any], Any]],
        weights: List[float],
        T: float,
        S0: List[float],
        n_paths: int = 100000,
        n_steps: int = 252,
        correlations: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        n_assets = len(models)
        
        if correlations is None:
            correlations = np.eye(n_assets)
        
        if correlations is not None:
            if correlations.shape != (n_assets, n_assets):
                raise ValueError(f"correlations must be {n_assets}x{n_assets} matrix")
            if not np.allclose(correlations, correlations.T):
                raise ValueError("correlation matrix must be symmetric")
            if np.any(np.linalg.eigvals(correlations) < 0):
                raise ValueError("correlation matrix must be positive semi-definite")
            if not np.allclose(np.diag(correlations), 1.0):
                raise ValueError("correlation matrix diagonal must be 1.0")
            raise NotImplementedError("Portfolio correlations are not yet implemented. Models generate independent random numbers internally. Use correlations=None for independent pricing.")
        
        portfolio_value = 0.0
        individual_prices = []
        
        for i, (model, payoff_fn, weight, s0) in enumerate(zip(models, payoff_fns, weights, S0)):
            result = self.engine.price(
                model=model,
                payoff_fn=payoff_fn,
                n_paths=n_paths,
                n_steps=n_steps,
                T=T,
                S0=s0
            )
            
            individual_prices.append(result)
            portfolio_value += weight * result["price"]
        
        return {
            "portfolio_value": portfolio_value,
            "individual_prices": individual_prices,
            "weights": weights
        }
    
    def variance_reduction_price(
        self,
        model: RoughVolatilityModel,
        payoff_fn: Callable[[Any], Any],
        control_variate_fn: Optional[Callable[[Any], Any]],
        T: float,
        S0: float = 100.0,
        n_paths: int = 100000,
        n_steps: int = 252,
        beta: Optional[float] = None
    ) -> Dict[str, float]:
        S, V = self.engine.simulate(model, n_paths, n_steps, T, S0)
        
        main_payoffs = payoff_fn(S)
        
        if control_variate_fn is not None:
            control_payoffs = control_variate_fn(S)
            
            if beta is None:
                main_mean = self.engine.backend.mean(main_payoffs)
                control_mean = self.engine.backend.mean(control_payoffs)
                main_centered = main_payoffs - main_mean
                control_centered = control_payoffs - control_mean
                cov = self.engine.backend.mean(main_centered * control_centered)
                var_control = self.engine.backend.mean(control_centered ** 2)
                beta = cov / (var_control + 1e-10)
            else:
                control_mean = self.engine.backend.mean(control_payoffs)
            
            adjusted_payoffs = main_payoffs - beta * (control_payoffs - control_mean)
            
            price = self.engine.backend.mean(adjusted_payoffs)
            variance = self.engine.backend.mean((adjusted_payoffs - price)**2)
        else:
            price = self.engine.backend.mean(main_payoffs)
            variance = self.engine.backend.mean((main_payoffs - price)**2)
        
        std_error = self.engine.backend.sqrt(variance / n_paths)
        
        return {
            "price": float(price),
            "std_error": float(std_error),
            "variance_reduction": control_variate_fn is not None,
            "paths": n_paths
        }

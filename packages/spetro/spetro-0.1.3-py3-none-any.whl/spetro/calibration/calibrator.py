from typing import Dict, Any, List, Tuple, Optional, Callable
import numpy as np

from ..core.engine import RoughVolatilityEngine
from ..core.models import RoughVolatilityModel, RoughBergomi
from ..pricing.pricer import Pricer


class Calibrator:
    def __init__(self, engine: RoughVolatilityEngine):
        self.engine = engine
        self.pricer = Pricer(engine)
    
    def calibrate_to_surface(
        self,
        model_class: type,
        market_prices: Dict[Tuple[float, float], float],
        S0: float = 100.0,
        initial_params: Optional[Dict[str, float]] = None,
        bounds: Optional[Dict[str, Tuple[float, float]]] = None,
        optimizer: str = "adam",
        max_iter: int = 1000,
        tolerance: float = 1e-6,
        n_paths: int = 50000,
        n_steps: Optional[int] = None
    ) -> Dict[str, Any]:
        
        if initial_params is None:
            if model_class == RoughBergomi:
                initial_params = {"H": 0.07, "eta": 1.9, "rho": -0.9, "xi": 0.235**2}
            else:
                raise ValueError("initial_params required for custom model")
        
        if bounds is None:
            if model_class == RoughBergomi:
                bounds = {
                    "H": (0.01, 0.49),
                    "eta": (0.1, 5.0), 
                    "rho": (-0.99, 0.99),
                    "xi": (0.01, 1.0)
                }
            else:
                bounds = {k: (v * 0.1, v * 10) for k, v in initial_params.items()}
        
        def objective(params_array):
            if hasattr(params_array, '__array__') and not isinstance(params_array, np.ndarray):
                params_array = np.array(params_array)
            params_dict = dict(zip(initial_params.keys(), params_array))
            
            try:
                model = model_class(**params_dict)
            except:
                return 1e6
            
            total_error = 0.0
            n_options = 0
            
            for (K, T), market_price in market_prices.items():
                try:
                    steps = n_steps if n_steps is not None else max(50, int(T * 252))
                    result = self.pricer.price_european(
                        model=model,
                        option_type="call",
                        K=K,
                        T=T,
                        S0=S0,
                        n_paths=n_paths,
                        n_steps=steps
                    )
                    
                    model_price = result["price"]
                    error = (model_price - market_price) ** 2
                    total_error += error
                    n_options += 1
                    
                except:
                    total_error += 1e6
                    n_options += 1
            
            return total_error / max(n_options, 1)
        
        if optimizer == "adam":
            result = self._adam_optimize(
                objective, 
                list(initial_params.values()),
                bounds=list(bounds.values()),
                max_iter=max_iter,
                tolerance=tolerance
            )
        else:
            raise ValueError(f"unsupported optimizer: {optimizer}")
        
        optimal_params = dict(zip(initial_params.keys(), result["x"]))
        calibrated_model = model_class(**optimal_params)
        
        return {
            "model": calibrated_model,
            "parameters": optimal_params,
            "objective_value": result["fun"],
            "iterations": result["nit"],
            "success": result["success"]
        }
    
    def _adam_optimize(
        self,
        objective: Callable,
        x0: List[float],
        bounds: List[Tuple[float, float]],
        max_iter: int = 1000,
        tolerance: float = 1e-6,
        lr: float = 0.01,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8
    ) -> Dict[str, Any]:
        
        x = np.array(x0, dtype=np.float64)
        m = np.zeros_like(x)
        v = np.zeros_like(x)
        
        best_x = x.copy()
        best_f = objective(x)
        
        for t in range(1, max_iter + 1):
            f_current = objective(x)
            
            if f_current < best_f:
                best_f = f_current
                best_x = x.copy()
            
            if hasattr(self.engine.backend, 'grad'):
                grad = self._autodiff_gradient(objective, x)
            else:
                grad = self._numerical_gradient(objective, x)
            
            m = beta1 * m + (1 - beta1) * grad
            v = beta2 * v + (1 - beta2) * (grad ** 2)
            
            m_hat = m / (1 - beta1 ** t)
            v_hat = v / (1 - beta2 ** t)
            
            x_new = x - lr * m_hat / (np.sqrt(v_hat) + epsilon)
            
            for i, (lower, upper) in enumerate(bounds):
                x_new[i] = np.clip(x_new[i], lower, upper)
            
            if np.linalg.norm(x_new - x) < tolerance:
                break
                
            x = x_new
        
        return {
            "x": best_x,
            "fun": best_f,
            "nit": t,
            "success": best_f < 1e3
        }
    
    def _autodiff_gradient(self, f: Callable, x: np.ndarray) -> np.ndarray:
        x_backend = self.engine.backend.array(x)
        grad_fn = self.engine.backend.grad(f)
        grad_backend = grad_fn(x_backend)
        return np.array(grad_backend)
    
    def _numerical_gradient(self, f: Callable, x: np.ndarray, h: float = 1e-5) -> np.ndarray:
        grad = np.zeros_like(x)
        
        for i in range(len(x)):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += h
            x_minus[i] -= h
            
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
        
        return grad
    
    def validate_calibration(
        self,
        model: RoughVolatilityModel,
        market_prices: Dict[Tuple[float, float], float],
        S0: float = 100.0,
        n_paths: int = 100000,
        n_steps: Optional[int] = None
    ) -> Dict[str, Any]:
        
        results = {}
        total_error = 0.0
        
        for (K, T), market_price in market_prices.items():
            steps = n_steps if n_steps is not None else max(50, int(T * 252))
            model_result = self.pricer.price_european(
                model=model,
                option_type="call", 
                K=K,
                T=T,
                S0=S0,
                n_paths=n_paths,
                n_steps=steps
            )
            
            model_price = model_result["price"]
            error = abs(model_price - market_price)
            rel_error = error / market_price if market_price > 0 else float('inf')
            
            results[(K, T)] = {
                "market_price": market_price,
                "model_price": model_price,
                "absolute_error": error,
                "relative_error": rel_error
            }
            
            total_error += error
        
        return {
            "individual_results": results,
            "mean_absolute_error": total_error / len(market_prices),
            "max_relative_error": max(r["relative_error"] for r in results.values())
        }

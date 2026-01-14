from typing import Dict, Any, List, Tuple, Optional, Callable
import numpy as np


class Optimizer:
    def minimize(
        self,
        objective: Callable,
        x0: List[float],
        bounds: List[Tuple[float, float]],
        **kwargs
    ) -> Dict[str, Any]:
        raise NotImplementedError


class AdamOptimizer(Optimizer):
    def __init__(
        self,
        learning_rate: float = 0.01,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8
    ):
        self.lr = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
    
    def minimize(
        self,
        objective: Callable,
        x0: List[float],
        bounds: List[Tuple[float, float]],
        max_iter: int = 1000,
        tolerance: float = 1e-6
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
            
            grad = self._numerical_gradient(objective, x)
            
            m = self.beta1 * m + (1 - self.beta1) * grad
            v = self.beta2 * v + (1 - self.beta2) * (grad ** 2)
            
            m_hat = m / (1 - self.beta1 ** t)
            v_hat = v / (1 - self.beta2 ** t)
            
            x_new = x - self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)
            
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
    
    def _numerical_gradient(self, f: Callable, x: np.ndarray, h: float = 1e-5) -> np.ndarray:
        grad = np.zeros_like(x)
        
        for i in range(len(x)):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += h
            x_minus[i] -= h
            
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
        
        return grad


class LBFGSOptimizer(Optimizer):
    def minimize(
        self,
        objective: Callable,
        x0: List[float],
        bounds: List[Tuple[float, float]],
        max_iter: int = 1000,
        tolerance: float = 1e-6
    ) -> Dict[str, Any]:
        
        try:
            from scipy.optimize import minimize
            
            result = minimize(
                objective,
                x0,
                method='L-BFGS-B',
                bounds=bounds,
                options={'maxiter': max_iter, 'ftol': tolerance}
            )
            
            return {
                "x": result.x,
                "fun": result.fun,
                "nit": result.nit,
                "success": result.success
            }
            
        except ImportError:
            return AdamOptimizer().minimize(objective, x0, bounds, max_iter, tolerance)

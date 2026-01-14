from typing import List, Any, Optional
from abc import ABC, abstractmethod


class NeuralNetwork(ABC):
    @abstractmethod
    def forward(self, x: Any) -> Any:
        pass
    
    @abstractmethod
    def init_params(self, key: Any, input_shape: tuple) -> Any:
        pass


class PricingNetwork(NeuralNetwork):
    def __init__(self, hidden_dims: List[int] = [64, 128, 64, 32]):
        self.hidden_dims = hidden_dims
    
    def forward(self, x: Any) -> Any:
        raise NotImplementedError("implemented in surrogate.py")
    
    def init_params(self, key: Any, input_shape: tuple) -> Any:
        raise NotImplementedError("implemented in surrogate.py")


class CalibrationNetwork(NeuralNetwork):
    def __init__(self, output_dim: int, hidden_dims: List[int] = [128, 256, 128]):
        self.output_dim = output_dim
        self.hidden_dims = hidden_dims
    
    def forward(self, x: Any) -> Any:
        raise NotImplementedError("implemented in surrogate.py")
    
    def init_params(self, key: Any, input_shape: tuple) -> Any:
        raise NotImplementedError("implemented in surrogate.py")

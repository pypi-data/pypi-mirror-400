from typing import Dict, Any, List, Tuple, Optional, Union
import numpy as np

from ..core.engine import RoughVolatilityEngine
from ..core.models import RoughVolatilityModel
from ..pricing.pricer import Pricer


class NeuralSurrogate:
    def __init__(self, engine: RoughVolatilityEngine, backend: str = None):
        self.engine = engine
        self.backend_name = backend or engine.backend_name
        self.network = None
        self.is_trained = False
        
        if self.backend_name == "jax":
            self._init_jax_components()
        elif self.backend_name == "torch":
            self._init_torch_components()
    
    def _init_jax_components(self):
        import jax
        import jax.numpy as jnp
        import flax.linen as nn
        import optax
        
        self.jax = jax
        self.jnp = jnp
        self.nn = nn
        self.optax = optax
        
        class PricingMLP(nn.Module):
            features: List[int] = None
            
            def setup(self):
                if self.features is None:
                    self.features = [64, 128, 64, 32]
            
            @nn.compact
            def __call__(self, x):
                features = self.features if self.features is not None else [64, 128, 64, 32]
                for i, feat in enumerate(features):
                    x = nn.Dense(feat)(x)
                    if i < len(features) - 1:
                        x = nn.relu(x)
                x = nn.Dense(1)(x)
                return x.squeeze()
        
        self.network_class = PricingMLP
    
    def _init_torch_components(self):
        import torch
        import torch.nn as nn
        import torch.optim as optim
        
        self.torch = torch
        self.nn_torch = nn
        self.optim = optim
        
        class PricingMLP(nn.Module):
            def __init__(self, input_dim: int, hidden_dims: List[int] = None):
                super().__init__()
                if hidden_dims is None:
                    hidden_dims = [64, 128, 64, 32]
                layers = []
                prev_dim = input_dim
                
                for dim in hidden_dims:
                    layers.extend([
                        nn.Linear(prev_dim, dim),
                        nn.ReLU()
                    ])
                    prev_dim = dim
                
                layers.append(nn.Linear(prev_dim, 1))
                self.network = nn.Sequential(*layers)
            
            def forward(self, x):
                return self.network(x).squeeze()
        
        self.network_class = PricingMLP
    
    def generate_training_data(
        self,
        model: RoughVolatilityModel,
        param_ranges: Dict[str, Tuple[float, float]],
        option_configs: List[Dict[str, Any]],
        n_samples: int = 10000,
        n_paths: int = 50000
    ) -> Tuple[Any, Any]:
        
        pricer = Pricer(self.engine)
        X_data = []
        y_data = []
        
        for _ in range(n_samples):
            params = {}
            for param, (low, high) in param_ranges.items():
                params[param] = np.random.uniform(low, high)
            
            try:
                model_instance = type(model)(**params)
            except:
                continue
            
            for config in option_configs:
                try:
                    result = pricer.price_european(
                        model=model_instance,
                        option_type=config.get("option_type", "call"),
                        K=config["K"],
                        T=config["T"],
                        S0=config.get("S0", 100.0),
                        n_paths=n_paths,
                        n_steps=max(50, int(config["T"] * 252))
                    )
                    
                    features = list(params.values()) + [
                        config["K"], 
                        config["T"], 
                        config.get("S0", 100.0)
                    ]
                    
                    X_data.append(features)
                    y_data.append(result["price"])
                    
                except:
                    continue
        
        if self.backend_name == "jax":
            X = self.jnp.array(X_data)
            y = self.jnp.array(y_data)
        else:
            X = self.torch.tensor(X_data, dtype=self.torch.float32)
            y = self.torch.tensor(y_data, dtype=self.torch.float32)
        
        return X, y
    
    def train(
        self,
        X: Any,
        y: Any,
        validation_split: float = 0.2,
        epochs: int = 1000,
        learning_rate: float = 1e-3,
        batch_size: int = 512
    ) -> Dict[str, List[float]]:
        
        n_samples = X.shape[0]
        n_val = int(n_samples * validation_split)
        
        if self.backend_name == "jax":
            return self._train_jax(X, y, n_val, epochs, learning_rate, batch_size)
        else:
            return self._train_torch(X, y, n_val, epochs, learning_rate, batch_size)
    
    def _train_jax(self, X, y, n_val, epochs, learning_rate, batch_size):
        from jax import random
        
        key = random.PRNGKey(42)
        
        X_train, X_val = X[n_val:], X[:n_val]
        y_train, y_val = y[n_val:], y[:n_val]
        
        model = self.network_class()
        params = model.init(key, X_train[:1])
        
        optimizer = self.optax.adam(learning_rate)
        opt_state = optimizer.init(params)
        
        def loss_fn(params, X_batch, y_batch):
            pred = model.apply(params, X_batch)
            return self.jnp.mean((pred - y_batch) ** 2)
        
        def train_step(params, opt_state, X_batch, y_batch):
            loss, grads = self.jax.value_and_grad(loss_fn)(params, X_batch, y_batch)
            updates, opt_state = optimizer.update(grads, opt_state, params)
            params = self.optax.apply_updates(params, updates)
            return params, opt_state, loss
        
        train_losses = []
        val_losses = []
        
        for epoch in range(epochs):
            n_batches = len(X_train) // batch_size
            epoch_loss = 0.0
            
            for i in range(n_batches):
                start_idx = i * batch_size
                end_idx = start_idx + batch_size
                X_batch = X_train[start_idx:end_idx]
                y_batch = y_train[start_idx:end_idx]
                
                params, opt_state, batch_loss = train_step(params, opt_state, X_batch, y_batch)
                epoch_loss += batch_loss
            
            train_loss = epoch_loss / n_batches
            val_loss = loss_fn(params, X_val, y_val)
            
            train_losses.append(float(train_loss))
            val_losses.append(float(val_loss))
            
        
        self.network = model
        self.params = params
        self.is_trained = True
        
        return {"train_loss": train_losses, "val_loss": val_losses}
    
    def _train_torch(self, X, y, n_val, epochs, learning_rate, batch_size):
        X_train, X_val = X[n_val:], X[:n_val]
        y_train, y_val = y[n_val:], y[:n_val]
        
        model = self.network_class(input_dim=X.shape[1])
        optimizer = self.optim.Adam(model.parameters(), lr=learning_rate)
        criterion = self.nn_torch.MSELoss()
        
        train_losses = []
        val_losses = []
        
        for epoch in range(epochs):
            model.train()
            epoch_loss = 0.0
            n_batches = 0
            
            for i in range(0, len(X_train), batch_size):
                X_batch = X_train[i:i+batch_size]
                y_batch = y_train[i:i+batch_size]
                
                optimizer.zero_grad()
                pred = model(X_batch)
                loss = criterion(pred, y_batch)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                n_batches += 1
            
            model.eval()
            with self.torch.no_grad():
                val_pred = model(X_val)
                val_loss = criterion(val_pred, y_val)
            
            train_loss = epoch_loss / n_batches
            train_losses.append(train_loss)
            val_losses.append(val_loss.item())
            
        
        self.network = model
        self.is_trained = True
        
        return {"train_loss": train_losses, "val_loss": val_losses}
    
    def predict(self, features: Union[List[float], Any]) -> float:
        if not self.is_trained:
            raise ValueError("model not trained")
        
        if self.backend_name == "jax":
            if isinstance(features, list):
                features = self.jnp.array([features])
            pred = self.network.apply(self.params, features)
            return float(pred[0] if len(pred.shape) > 0 else pred)
        else:
            if isinstance(features, list):
                features = self.torch.tensor([features], dtype=self.torch.float32)
            self.network.eval()
            with self.torch.no_grad():
                pred = self.network(features)
            return float(pred[0] if len(pred.shape) > 0 else pred)

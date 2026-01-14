import pytest
import numpy as np
import spetro as sp


class TestNeuralSurrogate:
    def test_surrogate_creation_jax(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            surrogate = sp.NeuralSurrogate(engine)
            assert surrogate.engine == engine
            assert surrogate.backend_name == "jax"
        except ImportError:
            pytest.skip("jax not available")
    
    def test_surrogate_creation_torch(self):
        try:
            engine = sp.RoughVolatilityEngine("torch")
            surrogate = sp.NeuralSurrogate(engine)
            assert surrogate.engine == engine
            assert surrogate.backend_name == "torch"
        except ImportError:
            pytest.skip("torch not available")
    
    def test_training_data_generation(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            surrogate = sp.NeuralSurrogate(engine)
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            
            param_ranges = {
                "H": (0.05, 0.15),
                "eta": (1.0, 3.0),
                "rho": (-0.95, -0.5),
                "xi": (0.01, 0.1)
            }
            
            option_configs = [
                {"K": 100, "T": 0.25, "S0": 100},
                {"K": 105, "T": 0.5, "S0": 100}
            ]
            
            X, y = surrogate.generate_training_data(
                model=model,
                param_ranges=param_ranges,
                option_configs=option_configs,
                n_samples=100,
                n_paths=1000
            )
            
            assert X.shape[0] > 0
            assert y.shape[0] > 0
            assert X.shape[0] == y.shape[0]
        except ImportError:
            pytest.skip("jax not available")
    
    def test_training(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            surrogate = sp.NeuralSurrogate(engine)
            
            X = np.random.randn(100, 7)
            y = np.random.randn(100)
            
            if engine.backend_name == "jax":
                import jax.numpy as jnp
                X = jnp.array(X)
                y = jnp.array(y)
            
            history = surrogate.train(X, y, epochs=10, validation_split=0.2)
            
            assert "train_loss" in history
            assert "val_loss" in history
            assert len(history["train_loss"]) == 10
            assert surrogate.is_trained
        except ImportError:
            pytest.skip("jax not available")
    
    def test_prediction(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            surrogate = sp.NeuralSurrogate(engine)
            
            X = np.random.randn(50, 7)
            y = np.random.randn(50)
            
            if engine.backend_name == "jax":
                import jax.numpy as jnp
                X = jnp.array(X)
                y = jnp.array(y)
            
            surrogate.train(X, y, epochs=5)
            
            features = [0.07, 1.9, -0.9, 0.055, 100, 0.25, 100]
            prediction = surrogate.predict(features)
            
            assert isinstance(prediction, float)
        except ImportError:
            pytest.skip("jax not available")
    
    def test_prediction_not_trained(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            surrogate = sp.NeuralSurrogate(engine)
            
            with pytest.raises(ValueError):
                surrogate.predict([0.07, 1.9, -0.9, 0.055, 100, 0.25, 100])
        except ImportError:
            pytest.skip("jax not available")

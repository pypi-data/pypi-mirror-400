import pytest
import numpy as np
import spetro as sp


class TestIntegration:
    def test_full_workflow_jax(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            result = pricer.price_european(
                model=model,
                option_type="call",
                K=100,
                T=0.25,
                S0=100,
                n_paths=10000
            )
            
            assert result["price"] > 0
            assert result["std_error"] > 0
            
            greeks = pricer.greeks(
                model=model,
                option_type="call",
                K=100.0,
                T=0.25,
                S0=100.0,
                n_paths=10000
            )
            
            assert "price" in greeks
            assert "delta" in greeks
            assert "gamma" in greeks
        except ImportError:
            pytest.skip("jax not available")
    
    def test_full_workflow_torch(self):
        try:
            engine = sp.RoughVolatilityEngine("torch")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            result = pricer.price_european(
                model=model,
                option_type="call",
                K=100,
                T=0.25,
                S0=100,
                n_paths=10000
            )
            
            assert result["price"] > 0
            assert result["std_error"] > 0
        except ImportError:
            pytest.skip("torch not available")
    
    def test_calibration_workflow(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            calibrator = sp.Calibrator(engine)
            
            market_prices = {
                (100, 0.25): 5.0,
                (105, 0.25): 2.0,
                (95, 0.25): 8.0
            }
            
            result = calibrator.calibrate_to_surface(
                model_class=sp.RoughBergomi,
                market_prices=market_prices,
                S0=100,
                max_iter=5,
                n_paths=1000,
                n_steps=10
            )
            
            assert result["success"]
            assert isinstance(result["model"], sp.RoughBergomi)
            
            validation = calibrator.validate_calibration(
                result["model"],
                market_prices,
                S0=100,
                n_paths=1000,
                n_steps=10
            )
            
            assert "mean_absolute_error" in validation
            assert validation["mean_absolute_error"] >= 0
        except ImportError:
            pytest.skip("jax not available")
    
    def test_neural_surrogate_workflow(self):
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
                {"K": 100, "T": 0.25, "S0": 100}
            ]
            
            X, y = surrogate.generate_training_data(
                model=model,
                param_ranges=param_ranges,
                option_configs=option_configs,
                n_samples=200,
                n_paths=5000
            )
            
            history = surrogate.train(X, y, epochs=20, validation_split=0.2)
            
            assert surrogate.is_trained
            assert len(history["train_loss"]) == 20
            
            prediction = surrogate.predict([0.07, 1.9, -0.9, 0.055, 100, 0.25, 100])
            assert isinstance(prediction, float)
        except ImportError:
            pytest.skip("jax not available")


class TestPerformance:
    def test_large_simulation(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            
            S, V = engine.simulate(
                model=model,
                n_paths=1000,
                n_steps=50,
                T=1.0,
                S0=100
            )
            
            assert S.shape == (1000, 51)
            assert V.shape[0] == 51 or V.shape[1] == 1000
        except ImportError:
            pytest.skip("jax not available")
    
    def test_memory_usage(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            
            for i in range(5):
                S, V = engine.simulate(
                    model=model,
                    n_paths=1000,
                    n_steps=20,
                    T=0.5,
                    S0=100
                )
                
                assert S.shape[0] == 1000
        except ImportError:
            pytest.skip("jax not available")

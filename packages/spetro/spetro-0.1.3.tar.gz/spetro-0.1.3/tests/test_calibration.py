import pytest
import numpy as np
import spetro as sp


class TestCalibrator:
    def test_calibrator_creation(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            calibrator = sp.Calibrator(engine)
            assert calibrator.engine == engine
        except ImportError:
            pytest.skip("jax not available")
    
    def test_calibration_basic(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            calibrator = sp.Calibrator(engine)
            
            market_prices = {
                (100, 0.25): 5.0,
                (105, 0.25): 2.0
            }
            
            result = calibrator.calibrate_to_surface(
                model_class=sp.RoughBergomi,
                market_prices=market_prices,
                S0=100,
                max_iter=3,
                n_paths=1000,
                n_steps=10
            )
            
            assert "model" in result
            assert "parameters" in result
            assert "objective_value" in result
            assert isinstance(result["model"], sp.RoughBergomi)
        except ImportError:
            pytest.skip("jax not available")
    
    def test_validation(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            calibrator = sp.Calibrator(engine)
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            
            market_prices = {
                (100, 0.25): 5.0
            }
            
            result = calibrator.validate_calibration(model, market_prices, S0=100, n_paths=1000, n_steps=10)
            
            assert "individual_results" in result
            assert "mean_absolute_error" in result
        except ImportError:
            pytest.skip("jax not available")


class TestOptimizers:
    def test_adam_optimizer(self):
        from spetro.calibration.optimizers import AdamOptimizer
        
        optimizer = AdamOptimizer(learning_rate=0.01)
        
        def objective(x):
            return (x[0] - 2)**2 + (x[1] - 3)**2
        
        result = optimizer.minimize(
            objective,
            x0=[0.0, 0.0],
            bounds=[(-5, 5), (-5, 5)],
            max_iter=100
        )
        
        assert "x" in result
        assert "fun" in result
        assert len(result["x"]) == 2

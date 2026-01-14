import pytest
import numpy as np
import spetro as sp


class TestPricer:
    def test_european_call_pricing(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            result = pricer.price_european(
                model=model,
                option_type="call",
                K=100,
                T=1.0,
                S0=100,
                n_paths=1000
            )
            
            assert "price" in result
            assert "std_error" in result
            assert result["price"] > 0
            assert result["std_error"] > 0
        except ImportError:
            pytest.skip("jax not available")
    
    def test_european_put_pricing(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            result = pricer.price_european(
                model=model,
                option_type="put",
                K=100,
                T=1.0,
                S0=100,
                n_paths=1000
            )
            
            assert "price" in result
            assert result["price"] > 0
        except ImportError:
            pytest.skip("jax not available")
    
    def test_invalid_option_type(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            with pytest.raises(ValueError):
                pricer.price_european(model, "invalid", K=100, T=1.0)
        except ImportError:
            pytest.skip("jax not available")
    
    def test_asian_call_pricing(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            result = pricer.price_asian(
                model=model,
                option_type="call",
                K=100,
                T=1.0,
                n_paths=1000
            )
            
            assert "price" in result
            assert result["price"] > 0
        except ImportError:
            pytest.skip("jax not available")
    
    def test_barrier_option_pricing(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            result = pricer.price_barrier(
                model=model,
                K=100,
                barrier=120,
                barrier_type="up_and_out",
                T=1.0,
                n_paths=1000
            )
            
            assert "price" in result
            assert result["price"] >= 0
        except ImportError:
            pytest.skip("jax not available")


class TestPayoffs:
    def test_european_call_payoff(self):
        payoff_fn = sp.european_call(100)
        S = np.array([[90, 95, 105], [110, 115, 120]])
        
        payoffs = payoff_fn(S)
        expected = np.array([5, 20])
        
        np.testing.assert_array_equal(payoffs, expected)
    
    def test_european_put_payoff(self):
        payoff_fn = sp.european_put(100)
        S = np.array([[90, 95, 85], [110, 115, 95]])
        
        payoffs = payoff_fn(S)
        expected = np.array([15, 5])
        
        np.testing.assert_array_equal(payoffs, expected)

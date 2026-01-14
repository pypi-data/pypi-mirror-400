import pytest
import numpy as np
import spetro as sp


class TestEdgeCases:
    def test_hurst_boundary_values(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            
            with pytest.raises(ValueError):
                sp.RoughBergomi(H=0.0)
            
            with pytest.raises(ValueError):
                sp.RoughBergomi(H=0.5)
            
            with pytest.raises(ValueError):
                sp.RoughBergomi(H=-0.1)
            
            with pytest.raises(ValueError):
                sp.RoughBergomi(H=1.0)
        except ImportError:
            pytest.skip("jax not available")
    
    def test_zero_strike(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            pricer = sp.Pricer(engine)
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            
            with pytest.raises(ValueError):
                pricer.price_european(model, "call", K=0, T=0.25)
        except ImportError:
            pytest.skip("jax not available")
    
    def test_negative_parameters(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            
            with pytest.raises(ValueError):
                sp.RoughBergomi(H=0.07, eta=-1.0)
            
            with pytest.raises(ValueError):
                sp.RoughBergomi(H=0.07, xi=-0.1)
        except ImportError:
            pytest.skip("jax not available")
    
    def test_extreme_correlation(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            
            model1 = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.99, xi=0.055)
            model2 = sp.RoughBergomi(H=0.07, eta=1.9, rho=0.99, xi=0.055)
            
            S1, V1 = engine.simulate(model1, n_paths=1000, n_steps=50, T=0.25, S0=100)
            S2, V2 = engine.simulate(model2, n_paths=1000, n_steps=50, T=0.25, S0=100)
            
            assert S1.shape == (1000, 51)
            assert S2.shape == (1000, 51)
        except ImportError:
            pytest.skip("jax not available")
    
    def test_very_short_maturity(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            result = pricer.price_european(
                model=model,
                option_type="call",
                K=100,
                T=0.001,
                S0=100,
                n_paths=1000
            )
            
            assert result["price"] >= 0
        except ImportError:
            pytest.skip("jax not available")
    
    def test_very_long_maturity(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            result = pricer.price_european(
                model=model,
                option_type="call",
                K=100,
                T=10.0,
                S0=100,
                n_paths=1000
            )
            
            assert result["price"] >= 0
        except ImportError:
            pytest.skip("jax not available")
    
    def test_atm_options(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            call_result = pricer.price_european(
                model=model,
                option_type="call",
                K=100,
                T=0.25,
                S0=100,
                n_paths=1000
            )
            
            put_result = pricer.price_european(
                model=model,
                option_type="put",
                K=100,
                T=0.25,
                S0=100,
                n_paths=1000
            )
            
            assert call_result["price"] > 0
            assert put_result["price"] > 0
        except ImportError:
            pytest.skip("jax not available")
    
    def test_itm_otm_options(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            pricer = sp.Pricer(engine)
            
            itm_call = pricer.price_european(
                model=model,
                option_type="call",
                K=90,
                T=0.25,
                S0=100,
                n_paths=1000
            )
            
            otm_call = pricer.price_european(
                model=model,
                option_type="call",
                K=110,
                T=0.25,
                S0=100,
                n_paths=1000
            )
            
            assert itm_call["price"] > otm_call["price"]
        except ImportError:
            pytest.skip("jax not available")

import pytest
import numpy as np
import spetro as sp


class TestRoughVolatilityEngine:
    def test_engine_creation_jax(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            assert engine.backend_name == "jax"
        except ImportError:
            pytest.skip("jax not available")
    
    def test_engine_creation_torch(self):
        try:
            engine = sp.RoughVolatilityEngine("torch")
            assert engine.backend_name == "torch"
        except ImportError:
            pytest.skip("torch not available")
    
    def test_invalid_backend(self):
        with pytest.raises(ValueError):
            sp.RoughVolatilityEngine("invalid")


class TestRoughBergomi:
    def test_model_creation(self):
        model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
        assert model.H == 0.07
        assert model.eta == 1.9
        assert model.rho == -0.9
        assert model.xi == 0.055
    
    def test_invalid_hurst_parameter(self):
        with pytest.raises(ValueError):
            sp.RoughBergomi(H=0.6)
        
        with pytest.raises(ValueError):
            sp.RoughBergomi(H=-0.1)
    
    def test_simulation_shape(self):
        try:
            engine = sp.RoughVolatilityEngine("jax")
            model = sp.RoughBergomi(H=0.07, eta=1.9, rho=-0.9, xi=0.055)
            
            S, V = engine.simulate(model, n_paths=100, n_steps=50, T=1.0, S0=100.0)
            
            assert S.shape == (100, 51)
            assert V.shape[0] == 51 or V.shape[1] == 100
        except ImportError:
            pytest.skip("jax not available")


class TestRoughHeston:
    def test_model_creation(self):
        model = sp.RoughHeston(H=0.07, nu=0.3, theta=0.02, rho=-0.7, V0=0.02)
        assert model.H == 0.07
        assert model.nu == 0.3
        assert model.theta == 0.02
        assert model.rho == -0.7
        assert model.V0 == 0.02
    
    def test_invalid_hurst_parameter(self):
        with pytest.raises(ValueError):
            sp.RoughHeston(H=0.6)


class TestBackends:
    def test_jax_backend_operations(self):
        try:
            from spetro.core.backends import JAXBackend
            backend = JAXBackend()
            
            x = backend.array([1.0, 2.0, 3.0])
            assert backend.mean(x) is not None
            assert backend.std(x) is not None
        except ImportError:
            pytest.skip("jax not available")
    
    def test_torch_backend_operations(self):
        try:
            from spetro.core.backends import TorchBackend
            backend = TorchBackend()
            
            x = backend.array([1.0, 2.0, 3.0])
            assert backend.mean(x) is not None
            assert backend.std(x) is not None
        except ImportError:
            pytest.skip("torch not available")

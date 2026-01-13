"""Basic tests for unified simulation framework."""

import numpy as np
import pytest


class TestConstants:
    """Test constants module."""

    def test_physical_constants_exist(self):
        from sim.constants import PhysicalConstants

        pc = PhysicalConstants()
        assert pc.c == 299_792_458.0
        assert pc.G > 0
        assert 0 < pc.alpha < 1

    def test_cosmological_constants_exist(self):
        from sim.constants import CosmologicalConstants

        cc = CosmologicalConstants()
        assert cc.H0 > 0
        assert 0 < cc.Omega_m < 1
        assert abs(cc.k_over_alpha - 66) < 10


class TestQuantum:
    """Test quantum module."""

    def test_quantum_fabric_creation(self):
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=2)
        assert qf.n == 2
        assert abs(qf.get_coherence() - 1.0) < 1e-6

    def test_hadamard_gate(self):
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=1)
        qf.apply_hadamard(0)
        probs = qf.get_qubit_probabilities(0)
        assert abs(probs[0] - 0.5) < 0.01
        assert abs(probs[1] - 0.5) < 0.01

    def test_entanglement(self):
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=2)
        qf.apply_entanglement_operator([(0, 1)])
        entropy = qf.get_entanglement_entropy()
        assert entropy > 0


class TestCosmic:
    """Test cosmic module."""

    def test_body_creation(self):
        from sim.cosmic import Body

        body = Body(
            name="Test", mass=1e24, position=np.array([1e11, 0, 0]), velocity=np.array([0, 3e4, 0])
        )
        assert body.mass == 1e24
        assert np.allclose(body.position, [1e11, 0, 0])

    def test_presets_exist(self):
        from sim.cosmic import SystemPresets

        presets = SystemPresets()
        bodies = presets.create_earth_moon_system()
        assert len(bodies) == 2
        assert bodies[0].name == "Earth"
        assert bodies[1].name == "Moon"

    def test_nbody_simulator(self):
        from sim.cosmic import NBodySimulator, SystemPresets

        presets = SystemPresets()
        bodies = presets.create_earth_moon_system()
        sim = NBodySimulator(bodies)
        assert len(sim.bodies) == 2


class TestCoherence:
    """Test coherence module."""

    def test_coherence_model(self):
        from sim.coherence import CoherenceModel

        model = CoherenceModel()
        K, C, Total = model.evolve(N=12, alpha=0.66)
        assert len(K) == 12
        assert K[-1] > K[0]  # Coherence grows

    def test_growth_factor(self):
        from sim.coherence import CoherenceModel

        model = CoherenceModel()
        factor = model.growth_factor(alpha=0.66, N=12)
        assert factor > 1


class TestGenesis:
    """Test genesis module."""

    def test_parametric_resonance(self):
        from sim.genesis import ParametricResonance

        pr = ParametricResonance(inflaton_mass=1e13, coupling=1e-7)
        rate = pr.particle_production_rate(phi_amplitude=1e16, k=1.0)
        assert rate >= 0

    def test_leptogenesis(self):
        from sim.genesis import LeptogenesisModel

        model = LeptogenesisModel(M=1e10, Yukawa=1e-6, CP_violation=1e-6)
        result = model.solve_leptogenesis()
        assert "eta_B" in result


class TestHolographic:
    """Test holographic module."""

    def test_holographic_analysis(self):
        from sim.holographic import HolographicAnalysis

        analysis = HolographicAnalysis()
        results = analysis.analyze_all_models()
        assert "mean_k" in results
        assert abs(results["mean_k_over_alpha"] - 66) < 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

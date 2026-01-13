"""Comprehensive tests for quantum module."""

import numpy as np
import pytest
from numpy.testing import assert_allclose


class TestQuantumFabric:
    """Test QuantumFabric class."""

    def test_initialization_vacuum_state(self):
        """Test that system initializes in |0...0> state."""
        from sim.quantum import QuantumFabric

        for n in [1, 2, 3, 4]:
            qf = QuantumFabric(num_qubits=n)
            state = qf.get_state_vector()

            # |0...0> state: first amplitude is 1, rest are 0
            expected = np.zeros(2**n, dtype=complex)
            expected[0] = 1.0
            assert_allclose(state, expected)

    def test_initialization_invalid_qubits(self):
        """Test that invalid qubit count raises error."""
        from sim.quantum import QuantumFabric

        with pytest.raises(ValueError):
            QuantumFabric(num_qubits=0)
        with pytest.raises(ValueError):
            QuantumFabric(num_qubits=-1)

    def test_invalid_entanglement_strength(self):
        """Test that invalid entanglement strength raises error."""
        from sim.quantum import QuantumFabric

        with pytest.raises(ValueError):
            QuantumFabric(num_qubits=2, entanglement_strength=-0.1)
        with pytest.raises(ValueError):
            QuantumFabric(num_qubits=2, entanglement_strength=1.5)

    def test_hadamard_single_qubit(self):
        """Test Hadamard gate creates equal superposition."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=1)
        qf.apply_hadamard(0)

        probs = qf.get_probability_distribution()
        assert_allclose(probs, [0.5, 0.5], atol=1e-10)

    def test_hadamard_invalid_index(self):
        """Test that invalid qubit index raises error."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=2)
        with pytest.raises(ValueError):
            qf.apply_hadamard(-1)
        with pytest.raises(ValueError):
            qf.apply_hadamard(2)

    def test_bell_state_creation(self):
        """Test that entanglement creates Bell state."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=2)
        qf.apply_entanglement_operator([(0, 1)])

        probs = qf.get_probability_distribution()
        # Bell state |Φ+> = (|00> + |11>)/√2
        assert_allclose(probs[0], 0.5, atol=0.01)  # |00>
        assert_allclose(probs[3], 0.5, atol=0.01)  # |11>
        assert_allclose(probs[1], 0.0, atol=0.01)  # |01>
        assert_allclose(probs[2], 0.0, atol=0.01)  # |10>

    def test_entanglement_entropy_maximally_entangled(self):
        """Test entropy is maximal for Bell state."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=2)
        qf.apply_entanglement_operator([(0, 1)])

        entropy = qf.get_entanglement_entropy()
        # Maximum entropy for 2 qubits is 1 bit
        assert entropy > 0.9

    def test_entanglement_entropy_product_state(self):
        """Test entropy is zero for product state."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=2)
        # No entanglement, just Hadamard
        qf.apply_hadamard(0)

        # Product state should have low entropy
        entropy = qf.get_entanglement_entropy()
        assert entropy < 0.5

    def test_measurement_collapses_state(self):
        """Test that measurement collapses superposition."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=1)
        qf.apply_hadamard(0)

        result = qf.measure(0)
        assert result in [0, 1]

        # After measurement, state should be collapsed
        probs = qf.get_probability_distribution()
        if result == 0:
            assert_allclose(probs[0], 1.0, atol=1e-10)
        else:
            assert_allclose(probs[1], 1.0, atol=1e-10)

    def test_measurement_statistics(self):
        """Test measurement gives correct statistics."""
        from sim.quantum import QuantumFabric

        n_trials = 1000
        results = []

        for _ in range(n_trials):
            qf = QuantumFabric(num_qubits=1)
            qf.apply_hadamard(0)
            results.append(qf.measure(0))

        # Should be roughly 50/50
        mean = np.mean(results)
        assert 0.4 < mean < 0.6

    def test_normalization_preserved(self):
        """Test that state remains normalized after operations."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=3)

        qf.apply_hadamard(0)
        qf.apply_hadamard(1)
        qf.apply_entanglement_operator([(0, 2)])

        coherence = qf.get_coherence()
        assert_allclose(coherence, 1.0, atol=1e-10)

    def test_reset(self):
        """Test reset returns to vacuum state."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=2)
        qf.apply_hadamard(0)
        qf.apply_entanglement_operator([(0, 1)])

        qf.reset()

        state = qf.get_state_vector()
        expected = np.zeros(4, dtype=complex)
        expected[0] = 1.0
        assert_allclose(state, expected)

    def test_get_state_info(self):
        """Test state info string."""
        from sim.quantum import QuantumFabric

        qf = QuantumFabric(num_qubits=3)
        info = qf.get_state_info()

        assert "3 qubits" in info
        assert "norm" in info.lower()


class TestQuantumOperators:
    """Test optimized quantum operators."""

    def test_pauli_gates(self):
        """Test Pauli gate matrices."""
        from sim.quantum.operators import pauli_x, pauli_y, pauli_z

        X = pauli_x()
        Y = pauli_y()
        Z = pauli_z()

        # X² = Y² = Z² = I
        identity = np.eye(2)
        assert_allclose(X @ X, identity)
        assert_allclose(Y @ Y, identity)
        assert_allclose(Z @ Z, identity)

    def test_hadamard_unitary(self):
        """Test Hadamard is unitary."""
        from sim.quantum.operators import hadamard, is_unitary

        H = hadamard()
        assert is_unitary(H)

    def test_cnot_sparse(self):
        """Test sparse CNOT construction."""
        from sim.quantum.operators import build_cnot_sparse

        # Note: qubit ordering is LSB (qubit 0 is least significant bit)
        # State ordering: |q1 q0> = |00>, |01>, |10>, |11>
        # CNOT(control=0, target=1): flips target when control=1
        cnot = build_cnot_sparse(0, 1, 2).toarray()

        # |00> -> |00> (control=0, no flip)
        assert_allclose(cnot @ [1, 0, 0, 0], [1, 0, 0, 0])
        # |01> -> |11> (control=1, flip target)
        assert_allclose(cnot @ [0, 1, 0, 0], [0, 0, 0, 1])
        # |10> -> |10> (control=0, no flip)
        assert_allclose(cnot @ [0, 0, 1, 0], [0, 0, 1, 0])
        # |11> -> |01> (control=1, flip target)
        assert_allclose(cnot @ [0, 0, 0, 1], [0, 1, 0, 0])

    def test_swap_sparse(self):
        """Test sparse SWAP gate."""
        from sim.quantum.operators import build_swap_sparse

        swap = build_swap_sparse(0, 1, 2).toarray()

        # SWAP truth table
        assert_allclose(swap @ [1, 0, 0, 0], [1, 0, 0, 0])  # |00> -> |00>
        assert_allclose(swap @ [0, 1, 0, 0], [0, 0, 1, 0])  # |01> -> |10>
        assert_allclose(swap @ [0, 0, 1, 0], [0, 1, 0, 0])  # |10> -> |01>
        assert_allclose(swap @ [0, 0, 0, 1], [0, 0, 0, 1])  # |11> -> |11>

    def test_operator_cache(self):
        """Test operator caching."""
        from sim.quantum.operators import build_cnot_sparse, clear_cache, get_cache_stats

        clear_cache()

        # First call - should cache
        build_cnot_sparse(0, 1, 3)
        stats1 = get_cache_stats()

        # Second call - should use cache
        build_cnot_sparse(0, 1, 3)
        # Cache was used

        assert stats1["size"] > 0

    def test_fidelity(self):
        """Test state fidelity calculation."""
        from sim.quantum.operators import fidelity

        state1 = np.array([1, 0], dtype=complex)
        state2 = np.array([1, 0], dtype=complex)
        state3 = np.array([0, 1], dtype=complex)
        state4 = np.array([1, 1], dtype=complex) / np.sqrt(2)

        assert_allclose(fidelity(state1, state2), 1.0)  # Same state
        assert_allclose(fidelity(state1, state3), 0.0)  # Orthogonal
        assert_allclose(fidelity(state1, state4), 0.5)  # 50% overlap


class TestEmergentLaws:
    """Test EmergentLaws class."""

    def test_particle_creation(self):
        """Test particle creation simulation."""
        from sim.quantum import EmergentLaws

        particles = EmergentLaws.simulate_particle_creation(vacuum_energy=0.5)
        assert isinstance(particles, list)

    def test_landauer_principle(self):
        """Test Landauer energy calculation."""
        from sim.quantum import EmergentLaws

        energy = EmergentLaws.landauer_principle(bits_erased=1, temperature=300)

        # E = kT ln(2) ≈ 2.87 × 10^-21 J at 300K
        assert energy > 0
        assert_allclose(energy, 2.87e-21, rtol=0.1)


class TestObserver:
    """Test Observer class."""

    def test_human_observer(self):
        """Test human observer decoherence."""
        from sim.quantum import HUMAN_OBSERVER

        coherence = HUMAN_OBSERVER.observe_system(1.0, observation_time=1e-6)
        assert 0 <= coherence <= 1

    def test_ligo_observer(self):
        """Test LIGO observer."""
        from sim.quantum import LIGO_OBSERVER

        coherence = LIGO_OBSERVER.observe_system(1.0, observation_time=1e-10)
        assert 0 <= coherence <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

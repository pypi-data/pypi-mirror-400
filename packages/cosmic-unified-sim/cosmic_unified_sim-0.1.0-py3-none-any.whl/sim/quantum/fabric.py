"""
Quantum Fabric
==============

Multi-qubit quantum system with entanglement and measurement.
Supports GPU acceleration via CUDA, Vulkan, or OpenCL.
"""

import warnings
from typing import List, Optional, Tuple

import numpy as np

from sim.core.gpu import get_backend


class QuantumFabric:
    """
    Quantum system simulation with entanglement capabilities.

    Models a system of n qubits with:
    - State vector representation (2^n dimensional)
    - Entanglement operators (CNOT-like)
    - Hadamard gates for superposition
    - Projective measurements
    - Von Neumann entropy calculation

    Examples:
    ---------
    >>> from sim.quantum import QuantumFabric
    >>> qf = QuantumFabric(num_qubits=3)
    >>> qf.apply_entanglement_operator([(0, 1), (1, 2)])
    >>> result = qf.measure(0)
    >>> print(f"Measured qubit 0: {result}")
    """

    def __init__(
        self, num_qubits: int, entanglement_strength: float = 1.0, use_gpu: Optional[bool] = None
    ):
        """
        Initialize quantum system.

        Args:
            num_qubits: Number of qubits (system has 2^n states)
            entanglement_strength: Strength of entanglement (0.0 - 1.0)
            use_gpu: Force GPU (True), force CPU (False), or auto (None)

        Raises:
            ValueError: If parameters are invalid
        """
        if num_qubits <= 0:
            raise ValueError(f"num_qubits must be > 0, got {num_qubits}")
        if not 0.0 <= entanglement_strength <= 1.0:
            raise ValueError(
                f"entanglement_strength must be in [0, 1], got {entanglement_strength}"
            )

        self.n = num_qubits
        self.entanglement_strength = entanglement_strength
        self.backend = get_backend(use_gpu=use_gpu)
        self.xp = self.backend.get_array_module()
        self.state = self._initialize_vacuum_state()
        self._normalize_state()

    def _initialize_vacuum_state(self):
        """Initialize vacuum state |0>⊗n"""
        use_gpu_backend = hasattr(self.backend, "use_opencl") and self.backend.use_opencl
        if use_gpu_backend:
            state_cpu = np.zeros(2**self.n, dtype=complex)
            state_cpu[0] = 1.0
            return self.backend.to_gpu(state_cpu)
        else:
            state = self.backend.zeros(2**self.n, dtype=complex)
            state[0] = 1.0
            return state

    def _normalize_state(self) -> None:
        """Normalize quantum state."""
        norm = self.xp.linalg.norm(self.state)
        if norm > 1e-10:
            self.state = self.state / norm
        else:
            warnings.warn("State near zero, reinitializing")
            self.state = self._initialize_vacuum_state()

    def apply_hadamard(self, qubit_index: int):
        """
        Apply Hadamard gate to a qubit.

        Creates superposition: H|0> = (|0> + |1>)/√2

        Args:
            qubit_index: Index of qubit (0 to n-1)

        Returns:
            Updated state vector
        """
        if qubit_index < 0 or qubit_index >= self.n:
            raise ValueError(f"qubit_index must be in [0, {self.n-1}], got {qubit_index}")

        size = 2**self.n
        hadamard_matrix = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

        use_cpu = hasattr(self.backend, "use_opencl") and self.backend.use_opencl
        if use_cpu:
            operator_cpu = np.eye(size, dtype=complex)
        else:
            operator = self.xp.eye(size, dtype=complex)

        for i in range(size):
            for j in range(size):
                mask = ~(1 << qubit_index)
                if (i & mask) == (j & mask):
                    bit_i = (i >> qubit_index) & 1
                    bit_j = (j >> qubit_index) & 1
                    if use_cpu:
                        operator_cpu[i, j] = hadamard_matrix[bit_i, bit_j]
                    else:
                        operator[i, j] = hadamard_matrix[bit_i, bit_j]

        if use_cpu:
            operator = self.backend.asarray(operator_cpu)

        self.state = operator @ self.state
        self._normalize_state()
        return self.state

    def apply_entanglement_operator(
        self, qubit_pairs: List[Tuple[int, int]], use_hadamard: bool = True
    ):
        """
        Apply entanglement operators between qubit pairs.

        For Bell state creation: applies Hadamard on control qubit,
        then CNOT to create entanglement.

        Args:
            qubit_pairs: List of (control, target) qubit index pairs
            use_hadamard: Apply Hadamard before CNOT (for Bell states)

        Returns:
            Updated state vector
        """
        for i, j in qubit_pairs:
            if i < 0 or j < 0 or i >= self.n or j >= self.n:
                warnings.warn(f"Skipping invalid qubit pair: ({i}, {j})")
                continue
            if i == j:
                warnings.warn(f"Skipping pair with same indices: ({i}, {j})")
                continue

            if use_hadamard:
                self.apply_hadamard(i)

            operator = self._create_cnot_operator(i, j)
            self.state = operator @ self.state

        self._normalize_state()
        return self.state

    def _create_cnot_operator(self, control: int, target: int):
        """Create CNOT operator: CNOT|xy> = |x, y⊕x>"""
        size = 2**self.n
        use_cpu = hasattr(self.backend, "use_opencl") and self.backend.use_opencl

        if use_cpu:
            operator = np.zeros((size, size), dtype=complex)
        else:
            operator = self.backend.zeros((size, size), dtype=complex)

        for i in range(size):
            control_bit = (i >> control) & 1
            if control_bit == 1:
                j = i ^ (1 << target)
                if use_cpu:
                    operator[j, i] = 1.0
                else:
                    operator[j, i] = 1.0
            else:
                if use_cpu:
                    operator[i, i] = 1.0
                else:
                    operator[i, i] = 1.0

        # Apply partial entanglement via controlled rotation
        if self.entanglement_strength < 1.0:
            theta = np.pi * self.entanglement_strength
            if use_cpu:
                operator = np.eye(size, dtype=complex)
            else:
                operator = self.xp.eye(size, dtype=complex)

            for i in range(size):
                control_bit = (i >> control) & 1
                target_bit = (i >> target) & 1

                if control_bit == 1:
                    target_state = i ^ (1 << target)
                    c, s = np.cos(theta / 2), np.sin(theta / 2)
                    if target_bit == 0:
                        if use_cpu:
                            operator[i, i] = c
                            operator[target_state, i] = -s
                        else:
                            operator[i, i] = c
                            operator[target_state, i] = -s
                    else:
                        if use_cpu:
                            operator[i, i] = c
                            operator[target_state, i] = s
                        else:
                            operator[i, i] = c
                            operator[target_state, i] = s
                else:
                    if use_cpu:
                        operator[i, i] = 1.0
                    else:
                        operator[i, i] = 1.0

        if use_cpu:
            operator = self.backend.asarray(operator)

        return operator

    def measure(self, qubit_index: int) -> int:
        """
        Measure a qubit and collapse the state.

        Args:
            qubit_index: Index of qubit to measure

        Returns:
            Measurement result (0 or 1)
        """
        if qubit_index < 0 or qubit_index >= self.n:
            raise ValueError(f"qubit_index must be in [0, {self.n-1}], got {qubit_index}")

        use_gpu = hasattr(self.backend, "use_opencl") and self.backend.use_opencl
        state_cpu = self.backend.to_cpu(self.state) if use_gpu else self.state

        # Calculate probabilities
        prob_0, prob_1 = 0.0, 0.0
        for i in range(2**self.n):
            if (i >> qubit_index) & 1:
                prob_1 += float(np.abs(state_cpu[i]) ** 2)
            else:
                prob_0 += float(np.abs(state_cpu[i]) ** 2)

        # Collapse state
        result = np.random.choice([0, 1], p=[prob_0, prob_1])

        for i in range(2**self.n):
            if ((i >> qubit_index) & 1) != result:
                state_cpu[i] = 0.0

        if use_gpu:
            self.state = self.backend.to_gpu(state_cpu)
        else:
            self.state = state_cpu

        self._normalize_state()
        return result

    def get_probability_distribution(self) -> np.ndarray:
        """Get probability distribution over all basis states."""
        probs = self.xp.abs(self.state) ** 2
        return self.backend.to_cpu(probs)

    def get_qubit_probabilities(self, qubit_index: int) -> Tuple[float, float]:
        """Get probabilities for |0> and |1> states of a qubit."""
        use_gpu = hasattr(self.backend, "use_opencl") and self.backend.use_opencl
        state_cpu = self.backend.to_cpu(self.state) if use_gpu else self.state

        prob_0, prob_1 = 0.0, 0.0
        for i in range(2**self.n):
            if (i >> qubit_index) & 1:
                prob_1 += float(np.abs(state_cpu[i]) ** 2)
            else:
                prob_0 += float(np.abs(state_cpu[i]) ** 2)

        return (prob_0, prob_1)

    def get_entanglement_entropy(self) -> float:
        """
        Calculate von Neumann entropy as entanglement measure.

        Returns:
            Entanglement entropy normalized to [0, 1]
        """
        if self.n == 1:
            return 0.0

        if self.n == 2:
            # Full von Neumann entropy for 2 qubits
            rho = self.xp.outer(self.state, self.state.conj())
            rho_reduced = self.backend.zeros((2, 2), dtype=complex)

            for i in range(2):
                for j in range(2):
                    for k in range(2):
                        rho_reduced[i, j] += rho[i * 2 + k, j * 2 + k]

            eigenvals = self.xp.linalg.eigvals(rho_reduced)
            eigenvals = self.xp.real(eigenvals)
            eigenvals = eigenvals[eigenvals > 1e-10]

            entropy = -float(self.xp.sum(eigenvals * self.xp.log2(eigenvals + 1e-10)))
            return float(entropy)

        # For larger systems, calculate average entropy over pairs
        entropies = []
        for i in range(min(self.n, 5)):  # Limit computation
            for j in range(i + 1, min(self.n, 5)):
                prob_0, prob_1 = self.get_qubit_probabilities(i)
                if prob_0 > 1e-10 and prob_1 > 1e-10:
                    s = -prob_0 * np.log2(prob_0) - prob_1 * np.log2(prob_1)
                    entropies.append(s)

        return float(np.mean(entropies)) if entropies else 0.0

    def get_coherence(self) -> float:
        """Get coherence measure (sum of |amplitude|²)."""
        return float(self.xp.sum(self.xp.abs(self.state) ** 2))

    def get_state_vector(self) -> np.ndarray:
        """Get copy of state vector (on CPU)."""
        return self.backend.to_cpu(self.backend.copy(self.state))

    def get_state_info(self) -> str:
        """Get information about current state."""
        norm = self.xp.linalg.norm(self.state)
        coherence = self.get_coherence()
        return (
            f"System of {self.n} qubits, " f"state norm: {norm:.6f}, " f"coherence: {coherence:.6f}"
        )

    def reset(self) -> None:
        """Reset to vacuum state."""
        self.state = self._initialize_vacuum_state()
        self._normalize_state()

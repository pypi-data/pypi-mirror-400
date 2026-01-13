"""
Quantum Operators
=================

Optimized quantum gate operators using sparse matrices and caching.
"""

from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import sparse


class OperatorCache:
    """
    LRU cache for quantum operators.

    Caches gate matrices to avoid redundant computation.
    """

    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self._cache: Dict[str, np.ndarray] = {}
        self._access_order: List[str] = []

    def _make_key(self, gate: str, *args) -> str:
        """Create cache key from gate name and arguments."""
        return f"{gate}_{'-'.join(str(a) for a in args)}"

    def get(self, gate: str, *args) -> Optional[np.ndarray]:
        """Get cached operator."""
        key = self._make_key(gate, *args)
        if key in self._cache:
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None

    def put(self, gate: str, operator: np.ndarray, *args) -> None:
        """Cache an operator."""
        key = self._make_key(gate, *args)

        # Evict if full
        while len(self._cache) >= self.max_size:
            old_key = self._access_order.pop(0)
            del self._cache[old_key]

        self._cache[key] = operator
        self._access_order.append(key)

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._access_order.clear()

    def stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "memory_bytes": sum(op.nbytes for op in self._cache.values()),
        }


# Global operator cache
_operator_cache = OperatorCache()


# ============================================================================
# Single-Qubit Gates
# ============================================================================


@lru_cache(maxsize=32)
def pauli_x() -> np.ndarray:
    """Pauli-X (NOT) gate."""
    return np.array([[0, 1], [1, 0]], dtype=complex)


@lru_cache(maxsize=32)
def pauli_y() -> np.ndarray:
    """Pauli-Y gate."""
    return np.array([[0, -1j], [1j, 0]], dtype=complex)


@lru_cache(maxsize=32)
def pauli_z() -> np.ndarray:
    """Pauli-Z gate."""
    return np.array([[1, 0], [0, -1]], dtype=complex)


@lru_cache(maxsize=32)
def hadamard() -> np.ndarray:
    """Hadamard gate: H = (X + Z) / √2."""
    return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


@lru_cache(maxsize=32)
def phase(phi: float = np.pi / 2) -> np.ndarray:
    """Phase gate: S = diag(1, e^(iφ))."""
    return np.array([[1, 0], [0, np.exp(1j * phi)]], dtype=complex)


@lru_cache(maxsize=32)
def t_gate() -> np.ndarray:
    """T gate: T = diag(1, e^(iπ/4))."""
    return phase(np.pi / 4)


def rotation_x(theta: float) -> np.ndarray:
    """Rotation around X axis: Rx(θ) = exp(-iθX/2)."""
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)


def rotation_y(theta: float) -> np.ndarray:
    """Rotation around Y axis: Ry(θ) = exp(-iθY/2)."""
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def rotation_z(theta: float) -> np.ndarray:
    """Rotation around Z axis: Rz(θ) = exp(-iθZ/2)."""
    return np.array([[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex)


# ============================================================================
# Multi-Qubit Gate Construction (Optimized)
# ============================================================================


def expand_single_qubit_gate(
    gate: np.ndarray, qubit_index: int, num_qubits: int, use_sparse: bool = True
) -> sparse.csr_matrix:
    """
    Expand single-qubit gate to full Hilbert space.

    Uses tensor product: I ⊗ ... ⊗ G ⊗ ... ⊗ I

    Args:
        gate: 2x2 single-qubit gate
        qubit_index: Target qubit (0-indexed, qubit 0 is least significant)
        num_qubits: Total number of qubits
        use_sparse: Return sparse matrix

    Returns:
        2^n × 2^n matrix
    """
    # Check cache
    gate_hash = hash(gate.tobytes())
    cached = _operator_cache.get("expand", gate_hash, qubit_index, num_qubits)
    if cached is not None:
        return sparse.csr_matrix(cached) if use_sparse else cached

    # Build operator using tensor products
    eye2 = sparse.eye(2, format="csr")
    G = sparse.csr_matrix(gate)

    result = sparse.eye(1, format="csr")
    for i in range(num_qubits):
        if i == qubit_index:
            result = sparse.kron(G, result)
        else:
            result = sparse.kron(eye2, result)

    # Cache and return
    if not use_sparse:
        result = result.toarray()

    _operator_cache.put(
        "expand", result.toarray() if use_sparse else result, gate_hash, qubit_index, num_qubits
    )

    return result


def build_cnot_sparse(control: int, target: int, num_qubits: int) -> sparse.csr_matrix:
    """
    Build CNOT gate using sparse matrix.

    CNOT|x,y⟩ = |x, y⊕x⟩

    Args:
        control: Control qubit index
        target: Target qubit index
        num_qubits: Total number of qubits

    Returns:
        Sparse 2^n × 2^n CNOT matrix
    """
    # Check cache
    cached = _operator_cache.get("cnot", control, target, num_qubits)
    if cached is not None:
        return sparse.csr_matrix(cached)

    dim = 2**num_qubits

    # Build COO data for sparse matrix
    rows = []
    cols = []

    for i in range(dim):
        control_bit = (i >> control) & 1
        if control_bit == 1:
            # Flip target bit
            j = i ^ (1 << target)
        else:
            j = i
        rows.append(j)
        cols.append(i)

    data = np.ones(dim, dtype=complex)
    result = sparse.csr_matrix((data, (rows, cols)), shape=(dim, dim))

    # Cache
    _operator_cache.put("cnot", result.toarray(), control, target, num_qubits)

    return result


def build_cz_sparse(control: int, target: int, num_qubits: int) -> sparse.csr_matrix:
    """
    Build CZ (controlled-Z) gate using sparse matrix.

    CZ|x,y⟩ = (-1)^(xy)|x,y⟩

    Args:
        control: Control qubit index
        target: Target qubit index
        num_qubits: Total number of qubits

    Returns:
        Sparse CZ matrix
    """
    dim = 2**num_qubits

    data = []
    for i in range(dim):
        control_bit = (i >> control) & 1
        target_bit = (i >> target) & 1
        if control_bit == 1 and target_bit == 1:
            data.append(-1.0 + 0j)
        else:
            data.append(1.0 + 0j)

    return sparse.diags(data, format="csr")


def build_swap_sparse(qubit1: int, qubit2: int, num_qubits: int) -> sparse.csr_matrix:
    """
    Build SWAP gate using sparse matrix.

    SWAP|x,y⟩ = |y,x⟩

    Args:
        qubit1: First qubit index
        qubit2: Second qubit index
        num_qubits: Total number of qubits

    Returns:
        Sparse SWAP matrix
    """
    dim = 2**num_qubits

    rows = []
    cols = []

    for i in range(dim):
        bit1 = (i >> qubit1) & 1
        bit2 = (i >> qubit2) & 1

        # Swap the bits
        j = i
        j = (j & ~(1 << qubit1)) | (bit2 << qubit1)
        j = (j & ~(1 << qubit2)) | (bit1 << qubit2)

        rows.append(j)
        cols.append(i)

    data = np.ones(dim, dtype=complex)
    return sparse.csr_matrix((data, (rows, cols)), shape=(dim, dim))


def build_toffoli_sparse(
    control1: int, control2: int, target: int, num_qubits: int
) -> sparse.csr_matrix:
    """
    Build Toffoli (CCNOT) gate using sparse matrix.

    Toffoli|x,y,z⟩ = |x, y, z⊕(x∧y)⟩

    Args:
        control1: First control qubit
        control2: Second control qubit
        target: Target qubit
        num_qubits: Total number of qubits

    Returns:
        Sparse Toffoli matrix
    """
    dim = 2**num_qubits

    rows = []
    cols = []

    for i in range(dim):
        c1 = (i >> control1) & 1
        c2 = (i >> control2) & 1

        if c1 == 1 and c2 == 1:
            j = i ^ (1 << target)
        else:
            j = i

        rows.append(j)
        cols.append(i)

    data = np.ones(dim, dtype=complex)
    return sparse.csr_matrix((data, (rows, cols)), shape=(dim, dim))


def build_controlled_rotation(
    control: int, target: int, num_qubits: int, theta: float, axis: str = "z"
) -> sparse.csr_matrix:
    """
    Build controlled rotation gate.

    Args:
        control: Control qubit
        target: Target qubit
        num_qubits: Total qubits
        theta: Rotation angle
        axis: Rotation axis ('x', 'y', or 'z')

    Returns:
        Sparse controlled rotation matrix
    """
    dim = 2**num_qubits

    # Get rotation matrix
    if axis == "x":
        rot = rotation_x(theta)
    elif axis == "y":
        rot = rotation_y(theta)
    else:
        rot = rotation_z(theta)

    rows = []
    cols = []
    data = []

    for i in range(dim):
        control_bit = (i >> control) & 1

        if control_bit == 0:
            # Identity on this subspace
            rows.append(i)
            cols.append(i)
            data.append(1.0 + 0j)
        else:
            # Apply rotation on target
            target_bit = (i >> target) & 1

            for out_bit in [0, 1]:
                j = (i & ~(1 << target)) | (out_bit << target)
                coeff = rot[out_bit, target_bit]
                if abs(coeff) > 1e-15:
                    rows.append(j)
                    cols.append(i)
                    data.append(coeff)

    return sparse.csr_matrix((data, (rows, cols)), shape=(dim, dim))


# ============================================================================
# Utility Functions
# ============================================================================


def apply_sparse_operator(operator: sparse.spmatrix, state: np.ndarray) -> np.ndarray:
    """
    Apply sparse operator to state vector efficiently.

    Args:
        operator: Sparse operator matrix
        state: State vector

    Returns:
        New state vector
    """
    return operator @ state


def tensor_product(*operators) -> np.ndarray:
    """
    Compute tensor product of multiple operators.

    Args:
        *operators: Variable number of operators

    Returns:
        Tensor product
    """
    result = operators[0]
    for op in operators[1:]:
        result = np.kron(result, op)
    return result


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Compute commutator [A, B] = AB - BA."""
    return A @ B - B @ A


def anticommutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Compute anticommutator {A, B} = AB + BA."""
    return A @ B + B @ A


def is_unitary(operator: np.ndarray, tol: float = 1e-10) -> bool:
    """Check if operator is unitary: U†U = I."""
    dim = operator.shape[0]
    product = operator.conj().T @ operator
    return np.allclose(product, np.eye(dim), atol=tol)


def is_hermitian(operator: np.ndarray, tol: float = 1e-10) -> bool:
    """Check if operator is Hermitian: A† = A."""
    return np.allclose(operator, operator.conj().T, atol=tol)


def operator_norm(operator: np.ndarray) -> float:
    """Compute spectral norm of operator."""
    return np.linalg.norm(operator, ord=2)


def fidelity(state1: np.ndarray, state2: np.ndarray) -> float:
    """
    Compute fidelity between two pure states.

    F = |⟨ψ₁|ψ₂⟩|²
    """
    return abs(np.vdot(state1, state2)) ** 2


def trace_distance(rho1: np.ndarray, rho2: np.ndarray) -> float:
    """
    Compute trace distance between density matrices.

    D(ρ₁, ρ₂) = ½ Tr|ρ₁ - ρ₂|
    """
    diff = rho1 - rho2
    eigenvalues = np.linalg.eigvalsh(diff)
    return 0.5 * np.sum(np.abs(eigenvalues))


def partial_trace(rho: np.ndarray, dims: Tuple[int, ...], trace_out: int) -> np.ndarray:
    """
    Compute partial trace over specified subsystem.

    Args:
        rho: Density matrix
        dims: Dimensions of each subsystem
        trace_out: Index of subsystem to trace out

    Returns:
        Reduced density matrix
    """
    n_subsystems = len(dims)

    # Reshape to tensor
    rho_tensor = rho.reshape(dims + dims)

    # Axes to trace
    axis1 = trace_out
    axis2 = trace_out + n_subsystems

    # Trace
    result = np.trace(rho_tensor, axis1=axis1, axis2=axis2)

    # Remaining dimensions
    remaining_dims = [d for i, d in enumerate(dims) if i != trace_out]
    remaining_dim = int(np.prod(remaining_dims))

    return result.reshape(remaining_dim, remaining_dim)


def get_cache_stats() -> Dict[str, int]:
    """Get operator cache statistics."""
    return _operator_cache.stats()


def clear_cache() -> None:
    """Clear operator cache."""
    _operator_cache.clear()

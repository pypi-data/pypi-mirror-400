"""
Quantum Module
==============

Quantum mechanics simulation with entanglement and measurement.
"""

from .emergence import EmergentLaws
from .fabric import QuantumFabric
from .observer import ELECTRON_OBSERVER, HUMAN_OBSERVER, LIGO_OBSERVER, Observer
from .operators import (  # Single-qubit gates; Multi-qubit gates; Utilities
    anticommutator,
    build_cnot_sparse,
    build_controlled_rotation,
    build_cz_sparse,
    build_swap_sparse,
    build_toffoli_sparse,
    clear_cache,
    commutator,
    expand_single_qubit_gate,
    fidelity,
    get_cache_stats,
    hadamard,
    is_hermitian,
    is_unitary,
    operator_norm,
    partial_trace,
    pauli_x,
    pauli_y,
    pauli_z,
    phase,
    rotation_x,
    rotation_y,
    rotation_z,
    t_gate,
    tensor_product,
    trace_distance,
)

__all__ = [
    # Main classes
    "QuantumFabric",
    "EmergentLaws",
    "Observer",
    # Preset observers
    "HUMAN_OBSERVER",
    "LIGO_OBSERVER",
    "ELECTRON_OBSERVER",
    # Single-qubit gates
    "pauli_x",
    "pauli_y",
    "pauli_z",
    "hadamard",
    "phase",
    "t_gate",
    "rotation_x",
    "rotation_y",
    "rotation_z",
    # Multi-qubit gates
    "build_cnot_sparse",
    "build_cz_sparse",
    "build_swap_sparse",
    "build_toffoli_sparse",
    "build_controlled_rotation",
    "expand_single_qubit_gate",
    # Utilities
    "tensor_product",
    "commutator",
    "anticommutator",
    "is_unitary",
    "is_hermitian",
    "operator_norm",
    "fidelity",
    "trace_distance",
    "partial_trace",
    "get_cache_stats",
    "clear_cache",
]

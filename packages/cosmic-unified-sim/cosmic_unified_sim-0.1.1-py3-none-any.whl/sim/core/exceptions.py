"""
Custom Exceptions
=================

Domain-specific exceptions for the simulation framework.
"""

from typing import Any, Optional


class SimulationError(Exception):
    """Base exception for all simulation errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


class QuantumError(SimulationError):
    """Base exception for quantum simulation errors."""

    pass


class InvalidQubitIndexError(QuantumError):
    """Raised when qubit index is out of range."""

    def __init__(self, index: int, num_qubits: int):
        super().__init__(
            f"Qubit index {index} out of range for {num_qubits}-qubit system",
            {"index": index, "num_qubits": num_qubits, "valid_range": f"[0, {num_qubits - 1}]"},
        )
        self.index = index
        self.num_qubits = num_qubits


class InvalidQuantumStateError(QuantumError):
    """Raised when quantum state is invalid (e.g., not normalized)."""

    def __init__(self, reason: str, norm: Optional[float] = None):
        details = {"reason": reason}
        if norm is not None:
            details["norm"] = norm
        super().__init__(f"Invalid quantum state: {reason}", details)


class EntanglementError(QuantumError):
    """Raised when entanglement operation fails."""

    def __init__(self, message: str, qubit_pair: Optional[tuple] = None):
        details = {}
        if qubit_pair:
            details["qubit_pair"] = qubit_pair
        super().__init__(message, details)


class CosmicError(SimulationError):
    """Base exception for cosmic/N-body simulation errors."""

    pass


class NoBodiesError(CosmicError):
    """Raised when simulation has no bodies."""

    def __init__(self):
        super().__init__("No bodies in simulation system")


class InvalidBodyError(CosmicError):
    """Raised when body parameters are invalid."""

    def __init__(self, body_name: str, reason: str):
        super().__init__(
            f"Invalid body '{body_name}': {reason}", {"body_name": body_name, "reason": reason}
        )


class CollisionError(CosmicError):
    """Raised when bodies collide during simulation."""

    def __init__(self, body1: str, body2: str, distance: float):
        super().__init__(
            f"Collision detected between '{body1}' and '{body2}'",
            {"body1": body1, "body2": body2, "distance": distance},
        )


class IntegrationError(CosmicError):
    """Raised when numerical integration fails."""

    def __init__(self, message: str, time: Optional[float] = None):
        details = {}
        if time is not None:
            details["time"] = time
        super().__init__(f"Integration failed: {message}", details)


class CoherenceError(SimulationError):
    """Base exception for coherence simulation errors."""

    pass


class InvalidStageError(CoherenceError):
    """Raised when stage number is invalid."""

    def __init__(self, stage: int, max_stages: int):
        super().__init__(
            f"Invalid stage {stage}, must be in [0, {max_stages}]",
            {"stage": stage, "max_stages": max_stages},
        )


class GenesisError(SimulationError):
    """Base exception for matter genesis simulation errors."""

    pass


class PhysicsViolationError(GenesisError):
    """Raised when simulation violates physical constraints."""

    def __init__(self, constraint: str, value: Any, expected: str):
        super().__init__(
            f"Physics violation: {constraint}",
            {"constraint": constraint, "value": value, "expected": expected},
        )


class HolographicError(SimulationError):
    """Base exception for holographic analysis errors."""

    pass


class GPUError(SimulationError):
    """Base exception for GPU-related errors."""

    pass


class GPUNotAvailableError(GPUError):
    """Raised when GPU is requested but not available."""

    def __init__(self, requested_backend: Optional[str] = None):
        details = {}
        if requested_backend:
            details["requested_backend"] = requested_backend
        super().__init__("GPU acceleration not available", details)


class GPUMemoryError(GPUError):
    """Raised when GPU runs out of memory."""

    def __init__(self, required_bytes: int, available_bytes: int):
        super().__init__(
            "Insufficient GPU memory",
            {"required_mb": required_bytes / 1e6, "available_mb": available_bytes / 1e6},
        )


class ConfigurationError(SimulationError):
    """Raised when configuration is invalid."""

    def __init__(self, param: str, value: Any, reason: str):
        super().__init__(
            f"Invalid configuration for '{param}': {reason}",
            {"parameter": param, "value": value, "reason": reason},
        )


class CheckpointError(SimulationError):
    """Raised when checkpoint operations fail."""

    def __init__(self, operation: str, path: str, reason: str):
        super().__init__(
            f"Checkpoint {operation} failed: {reason}",
            {"operation": operation, "path": path, "reason": reason},
        )


class ValidationError(SimulationError):
    """Raised when input validation fails."""

    def __init__(self, param: str, value: Any, constraint: str):
        super().__init__(
            f"Validation failed for '{param}': {constraint}",
            {"parameter": param, "value": value, "constraint": constraint},
        )

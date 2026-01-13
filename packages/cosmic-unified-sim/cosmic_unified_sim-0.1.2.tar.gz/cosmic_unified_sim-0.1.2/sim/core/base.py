"""
Base Classes for Simulations
============================

Abstract base classes and common data structures for all simulation types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np


@dataclass
class SimulationResult:
    """
    Container for simulation results.

    Attributes:
        name: Name/identifier of the simulation
        times: Array of time points
        states: Dictionary of state arrays (key: variable name)
        parameters: Parameters used in simulation
        metadata: Additional metadata (timestamps, version, etc.)
        success: Whether simulation completed successfully
        message: Status/error message
    """

    name: str
    times: np.ndarray
    states: Dict[str, np.ndarray]
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    message: str = ""

    def __post_init__(self):
        """Add default metadata."""
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.now().isoformat()
        if "sim_version" not in self.metadata:
            from sim import __version__

            self.metadata["sim_version"] = __version__

    @property
    def n_steps(self) -> int:
        """Number of time steps."""
        return len(self.times)

    @property
    def duration(self) -> float:
        """Total simulation duration."""
        return float(self.times[-1] - self.times[0]) if len(self.times) > 1 else 0.0

    def get_state(self, name: str, time_index: int = -1) -> np.ndarray:
        """
        Get state variable at specific time.

        Args:
            name: Variable name
            time_index: Time index (default: -1 = final)

        Returns:
            State array at specified time
        """
        if name not in self.states:
            raise KeyError(f"State '{name}' not found. Available: {list(self.states.keys())}")
        return self.states[name][time_index]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "times": self.times.tolist(),
            "states": {k: v.tolist() for k, v in self.states.items()},
            "parameters": self.parameters,
            "metadata": self.metadata,
            "success": self.success,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationResult":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            times=np.array(data["times"]),
            states={k: np.array(v) for k, v in data["states"].items()},
            parameters=data.get("parameters", {}),
            metadata=data.get("metadata", {}),
            success=data.get("success", True),
            message=data.get("message", ""),
        )


class SimulationBase(ABC):
    """
    Abstract base class for all simulations.

    Provides common interface for:
    - Running simulations
    - Accessing results
    - Visualization hooks
    - Saving/loading state
    """

    def __init__(self, name: str = "simulation"):
        """
        Initialize simulation.

        Args:
            name: Simulation identifier
        """
        self.name = name
        self._result: Optional[SimulationResult] = None
        self._parameters: Dict[str, Any] = {}

    @property
    def result(self) -> Optional[SimulationResult]:
        """Get simulation result."""
        return self._result

    @property
    def parameters(self) -> Dict[str, Any]:
        """Get simulation parameters."""
        return self._parameters.copy()

    @abstractmethod
    def run(self, **kwargs) -> SimulationResult:
        """
        Run the simulation.

        Args:
            **kwargs: Simulation-specific parameters

        Returns:
            SimulationResult with times, states, and metadata
        """
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        Get current state of the simulation.

        Returns:
            Dictionary with current state variables
        """
        pass

    def set_parameters(self, **params) -> None:
        """
        Set simulation parameters.

        Args:
            **params: Parameter name-value pairs
        """
        self._parameters.update(params)

    def reset(self) -> None:
        """Reset simulation to initial state."""
        self._result = None

    def summary(self) -> str:
        """Get human-readable summary of simulation."""
        lines = [
            f"Simulation: {self.name}",
            f"Parameters: {self._parameters}",
        ]
        if self._result:
            lines.extend(
                [
                    f"Status: {'Success' if self._result.success else 'Failed'}",
                    f"Duration: {self._result.duration:.4g}",
                    f"Steps: {self._result.n_steps}",
                ]
            )
        else:
            lines.append("Status: Not run")
        return "\n".join(lines)

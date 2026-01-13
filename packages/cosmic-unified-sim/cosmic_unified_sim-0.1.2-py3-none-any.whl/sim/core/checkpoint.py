"""
Checkpoint System
=================

Save and restore simulation state for long-running computations.
"""

import gzip
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np

from .exceptions import CheckpointError
from .logging import get_logger

logger = get_logger("checkpoint")


@dataclass
class CheckpointMetadata:
    """Metadata for a checkpoint."""

    checkpoint_id: str
    simulation_name: str
    simulation_type: str
    created_at: str
    step: int
    time: float
    version: str
    parameters: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckpointMetadata":
        return cls(**data)


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy arrays."""

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return {
                "__numpy__": True,
                "dtype": str(obj.dtype),
                "shape": obj.shape,
                "data": obj.tolist(),
            }
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, complex):
            return {"__complex__": True, "real": obj.real, "imag": obj.imag}
        return super().default(obj)


def numpy_decoder(dct: dict) -> Any:
    """JSON decoder hook for numpy arrays."""
    if "__numpy__" in dct:
        return np.array(dct["data"], dtype=dct["dtype"]).reshape(dct["shape"])
    if "__complex__" in dct:
        return complex(dct["real"], dct["imag"])
    return dct


class CheckpointManager:
    """
    Manages checkpoints for simulations.

    Examples:
    ---------
    >>> manager = CheckpointManager("./checkpoints")
    >>> manager.save(sim, step=1000)
    >>> state = manager.load_latest("my_simulation")
    """

    def __init__(self, checkpoint_dir: Union[str, Path] = "./checkpoints"):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def _generate_id(self, name: str, step: int) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{name}_{step}_{timestamp}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"{name}_{step}_{short_hash}"

    def save(
        self,
        state: Dict[str, Any],
        name: str,
        simulation_type: str,
        step: int,
        time: float = 0.0,
        parameters: Optional[Dict[str, Any]] = None,
        compress: bool = True,
    ) -> Path:
        """
        Save a checkpoint.

        Args:
            state: Simulation state dictionary
            name: Simulation name
            simulation_type: Type of simulation (quantum, cosmic, etc.)
            step: Current step number
            time: Simulation time
            parameters: Simulation parameters
            compress: Use gzip compression

        Returns:
            Path to saved checkpoint
        """
        from sim import __version__

        checkpoint_id = self._generate_id(name, step)

        metadata = CheckpointMetadata(
            checkpoint_id=checkpoint_id,
            simulation_name=name,
            simulation_type=simulation_type,
            created_at=datetime.now().isoformat(),
            step=step,
            time=time,
            version=__version__,
            parameters=parameters or {},
        )

        checkpoint_data = {"metadata": metadata.to_dict(), "state": state}

        # Determine file path
        filename = f"{checkpoint_id}.json"
        if compress:
            filename += ".gz"
        filepath = self.checkpoint_dir / filename

        try:
            json_data = json.dumps(checkpoint_data, cls=NumpyEncoder, indent=2)

            if compress:
                with gzip.open(filepath, "wt", encoding="utf-8") as f:
                    f.write(json_data)
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(json_data)

            logger.info(f"Checkpoint saved: {filepath}")
            return filepath

        except Exception as e:
            raise CheckpointError("save", str(filepath), str(e))

    def load(self, checkpoint_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load a checkpoint from file.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            Dictionary with 'metadata' and 'state'
        """
        filepath = Path(checkpoint_path)

        if not filepath.exists():
            raise CheckpointError("load", str(filepath), "File not found")

        try:
            if filepath.suffix == ".gz" or str(filepath).endswith(".json.gz"):
                with gzip.open(filepath, "rt", encoding="utf-8") as f:
                    data = json.load(f, object_hook=numpy_decoder)
            else:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f, object_hook=numpy_decoder)

            logger.info(f"Checkpoint loaded: {filepath}")
            return data

        except Exception as e:
            raise CheckpointError("load", str(filepath), str(e))

    def load_latest(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load the latest checkpoint for a simulation.

        Args:
            name: Simulation name

        Returns:
            Checkpoint data or None if not found
        """
        checkpoints = self.list_checkpoints(name)
        if not checkpoints:
            return None

        # Sort by modification time, get latest
        latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
        return self.load(latest)

    def list_checkpoints(self, name: Optional[str] = None) -> list:
        """
        List available checkpoints.

        Args:
            name: Filter by simulation name (optional)

        Returns:
            List of checkpoint file paths
        """
        pattern = f"{name}_*.json*" if name else "*.json*"
        return sorted(self.checkpoint_dir.glob(pattern))

    def delete(self, checkpoint_path: Union[str, Path]) -> None:
        """Delete a checkpoint."""
        filepath = Path(checkpoint_path)
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Checkpoint deleted: {filepath}")

    def cleanup(self, name: str, keep_last: int = 5) -> int:
        """
        Clean up old checkpoints, keeping only the most recent.

        Args:
            name: Simulation name
            keep_last: Number of checkpoints to keep

        Returns:
            Number of checkpoints deleted
        """
        checkpoints = self.list_checkpoints(name)

        if len(checkpoints) <= keep_last:
            return 0

        # Sort by modification time
        checkpoints.sort(key=lambda p: p.stat().st_mtime)

        # Delete oldest
        to_delete = checkpoints[:-keep_last]
        for cp in to_delete:
            self.delete(cp)

        return len(to_delete)


# Convenience functions
_default_manager: Optional[CheckpointManager] = None


def get_checkpoint_manager(checkpoint_dir: str = "./checkpoints") -> CheckpointManager:
    """Get or create the default checkpoint manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = CheckpointManager(checkpoint_dir)
    return _default_manager


def save_checkpoint(
    state: Dict[str, Any], name: str, simulation_type: str, step: int, **kwargs
) -> Path:
    """Save a checkpoint using the default manager."""
    return get_checkpoint_manager().save(state, name, simulation_type, step, **kwargs)


def load_checkpoint(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a checkpoint using the default manager."""
    return get_checkpoint_manager().load(path)


def load_latest_checkpoint(name: str) -> Optional[Dict[str, Any]]:
    """Load the latest checkpoint for a simulation."""
    return get_checkpoint_manager().load_latest(name)

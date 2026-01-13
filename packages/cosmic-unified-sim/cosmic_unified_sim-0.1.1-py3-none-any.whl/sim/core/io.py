"""
Simulation I/O Utilities
========================

Save and load simulations, export data to various formats.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

import numpy as np

from .base import SimulationResult


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, complex):
            return {"real": obj.real, "imag": obj.imag}
        if isinstance(obj, np.complexfloating):
            return {"real": float(obj.real), "imag": float(obj.imag)}
        return super().default(obj)


class SimulationIO:
    """
    I/O utilities for simulation data.

    Supports:
    - JSON for state/config
    - CSV for trajectories/time series
    - NPZ for numpy arrays
    """

    @staticmethod
    def save_json(data: Dict[str, Any], filepath: Union[str, Path]) -> None:
        """
        Save dictionary to JSON file.

        Args:
            data: Dictionary to save
            filepath: Output file path
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, cls=NumpyEncoder, indent=2, ensure_ascii=False)

    @staticmethod
    def load_json(filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Load dictionary from JSON file.

        Args:
            filepath: Input file path

        Returns:
            Loaded dictionary
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_result(result: SimulationResult, filepath: Union[str, Path]) -> None:
        """
        Save SimulationResult to JSON.

        Args:
            result: SimulationResult to save
            filepath: Output file path
        """
        SimulationIO.save_json(result.to_dict(), filepath)

    @staticmethod
    def load_result(filepath: Union[str, Path]) -> SimulationResult:
        """
        Load SimulationResult from JSON.

        Args:
            filepath: Input file path

        Returns:
            SimulationResult object
        """
        data = SimulationIO.load_json(filepath)
        return SimulationResult.from_dict(data)

    @staticmethod
    def save_csv(
        data: Dict[str, np.ndarray], filepath: Union[str, Path], time_column: str = "time"
    ) -> None:
        """
        Save time series data to CSV.

        Args:
            data: Dictionary with arrays (must include time column)
            filepath: Output file path
            time_column: Name of time column
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Get column names with time first
        columns = [time_column] if time_column in data else []
        columns.extend(k for k in data.keys() if k != time_column)

        # Determine number of rows
        n_rows = len(data[columns[0]])

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            for i in range(n_rows):
                row = []
                for col in columns:
                    val = data[col][i]
                    if isinstance(val, np.ndarray):
                        row.append(str(val.tolist()))
                    else:
                        row.append(val)
                writer.writerow(row)

    @staticmethod
    def load_csv(filepath: Union[str, Path]) -> Dict[str, np.ndarray]:
        """
        Load time series data from CSV.

        Args:
            filepath: Input file path

        Returns:
            Dictionary with numpy arrays
        """
        data = {}
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

            columns = {h: [] for h in headers}
            for row in reader:
                for h, val in zip(headers, row):
                    try:
                        columns[h].append(float(val))
                    except ValueError:
                        columns[h].append(val)

            for h, vals in columns.items():
                try:
                    data[h] = np.array(vals, dtype=float)
                except ValueError:
                    data[h] = np.array(vals)

        return data

    @staticmethod
    def save_npz(
        data: Dict[str, np.ndarray], filepath: Union[str, Path], compressed: bool = True
    ) -> None:
        """
        Save arrays to NPZ format.

        Args:
            data: Dictionary of numpy arrays
            filepath: Output file path
            compressed: Use compression
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if compressed:
            np.savez_compressed(filepath, **data)
        else:
            np.savez(filepath, **data)

    @staticmethod
    def load_npz(filepath: Union[str, Path]) -> Dict[str, np.ndarray]:
        """
        Load arrays from NPZ format.

        Args:
            filepath: Input file path

        Returns:
            Dictionary of numpy arrays
        """
        with np.load(filepath) as data:
            return {k: data[k] for k in data.files}

    @staticmethod
    def export_trajectories(bodies: List[Any], filepath: Union[str, Path]) -> None:
        """
        Export body trajectories to CSV.

        Args:
            bodies: List of Body objects with trajectory attribute
            filepath: Output file path
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["body", "time_index", "x", "y", "z", "vx", "vy", "vz"])

            for body in bodies:
                if not hasattr(body, "trajectory") or body.trajectory is None:
                    continue
                for i, state in enumerate(body.trajectory):
                    pos = state[:3] if len(state) >= 3 else state
                    vel = state[3:6] if len(state) >= 6 else [0, 0, 0]
                    writer.writerow([body.name, i, *pos, *vel])

    @staticmethod
    def save_state(state_dict: Dict[str, Any], filepath: Union[str, Path]) -> None:
        """
        Save simulation state to JSON.

        Convenience method that adds metadata.

        Args:
            state_dict: State dictionary
            filepath: Output file path
        """
        state_with_meta = {
            "state": state_dict,
            "saved_at": datetime.now().isoformat(),
            "version": "1.0",
        }
        SimulationIO.save_json(state_with_meta, filepath)

    @staticmethod
    def load_state(filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Load simulation state from JSON.

        Args:
            filepath: Input file path

        Returns:
            State dictionary
        """
        data = SimulationIO.load_json(filepath)
        return data.get("state", data)

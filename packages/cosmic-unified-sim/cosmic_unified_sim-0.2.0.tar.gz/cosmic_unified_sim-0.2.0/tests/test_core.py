"""Tests for core module (base, config, checkpoint, logging)."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose


class TestSimulationResult:
    """Test SimulationResult dataclass."""

    def test_creation(self):
        """Test basic creation."""
        from sim.core.base import SimulationResult

        result = SimulationResult(
            name="test", times=np.array([0, 1, 2, 3, 4]), states={"x": np.array([0, 1, 4, 9, 16])}
        )

        assert result.name == "test"
        assert result.n_steps == 5
        assert result.duration == 4.0

    def test_get_state(self):
        """Test get_state method."""
        from sim.core.base import SimulationResult

        result = SimulationResult(
            name="test", times=np.array([0, 1, 2]), states={"x": np.array([10, 20, 30])}
        )

        assert result.get_state("x", 0) == 10
        assert result.get_state("x", -1) == 30

    def test_get_state_invalid_key(self):
        """Test get_state with invalid key."""
        from sim.core.base import SimulationResult

        result = SimulationResult(name="test", times=np.array([0]), states={"x": np.array([1])})

        with pytest.raises(KeyError):
            result.get_state("invalid")

    def test_to_dict_from_dict(self):
        """Test serialization round-trip."""
        from sim.core.base import SimulationResult

        original = SimulationResult(
            name="test",
            times=np.array([0.0, 1.0, 2.0]),
            states={"x": np.array([1.0, 2.0, 3.0])},
            parameters={"alpha": 0.5},
        )

        data = original.to_dict()
        restored = SimulationResult.from_dict(data)

        assert restored.name == original.name
        assert_allclose(restored.times, original.times)
        assert_allclose(restored.states["x"], original.states["x"])


class TestExceptions:
    """Test custom exceptions."""

    def test_simulation_error(self):
        """Test base SimulationError."""
        from sim.core.exceptions import SimulationError

        error = SimulationError("Something went wrong", {"key": "value"})
        assert "Something went wrong" in str(error)
        assert error.details["key"] == "value"

    def test_quantum_error(self):
        """Test QuantumError hierarchy."""
        from sim.core.exceptions import (
            InvalidQubitIndexError,
            QuantumError,
        )

        error = InvalidQubitIndexError(5, 3)
        assert "5" in str(error)
        assert "3" in str(error)
        assert isinstance(error, QuantumError)

    def test_cosmic_error(self):
        """Test CosmicError hierarchy."""
        from sim.core.exceptions import CollisionError, CosmicError, NoBodiesError

        error = NoBodiesError()
        assert "no bodies" in str(error).lower()

        collision = CollisionError("Earth", "Moon", 0.001)
        assert "Earth" in str(collision)
        assert isinstance(collision, CosmicError)


class TestConfig:
    """Test configuration system."""

    def test_default_config(self):
        """Test default configuration."""
        from sim.core.config import SimulationConfig

        config = SimulationConfig()

        assert config.quantum.num_qubits == 3
        assert config.cosmic.integrator == "rk45"
        assert config.logging.level == "INFO"

    def test_config_to_dict(self):
        """Test config serialization."""
        from sim.core.config import SimulationConfig

        config = SimulationConfig()
        data = config.to_dict()

        assert "quantum" in data
        assert "cosmic" in data
        assert data["quantum"]["num_qubits"] == 3

    def test_config_from_dict(self):
        """Test config deserialization."""
        from sim.core.config import SimulationConfig

        data = {"quantum": {"num_qubits": 5}, "cosmic": {"integrator": "verlet"}}

        config = SimulationConfig.from_dict(data)

        assert config.quantum.num_qubits == 5
        assert config.cosmic.integrator == "verlet"

    def test_config_save_load_json(self):
        """Test saving and loading JSON config."""
        from sim.core.config import SimulationConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"

            config = SimulationConfig()
            config.quantum.num_qubits = 7
            config.save(path)

            loaded = SimulationConfig.from_file(path)
            assert loaded.quantum.num_qubits == 7

    def test_config_validation(self):
        """Test config validation."""
        from sim.core.config import SimulationConfig
        from sim.core.exceptions import ConfigurationError

        config = SimulationConfig()
        config.quantum.num_qubits = 0

        with pytest.raises(ConfigurationError):
            config.validate()

    def test_global_config(self):
        """Test global config management."""
        from sim.core.config import SimulationConfig, get_config, reset_config, set_config

        reset_config()

        config = get_config()
        assert config.quantum.num_qubits == 3

        new_config = SimulationConfig()
        new_config.quantum.num_qubits = 10
        set_config(new_config)

        assert get_config().quantum.num_qubits == 10

        reset_config()


class TestCheckpoint:
    """Test checkpoint system."""

    def test_checkpoint_save_load(self):
        """Test basic save and load."""
        from sim.core.checkpoint import CheckpointManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(tmpdir)

            state = {"positions": np.array([[1, 2, 3], [4, 5, 6]]), "velocity": 42.0}

            path = manager.save(
                state=state, name="test_sim", simulation_type="cosmic", step=100, time=1000.0
            )

            assert path.exists()

            loaded = manager.load(path)
            assert_allclose(loaded["state"]["positions"], state["positions"])
            assert loaded["metadata"]["step"] == 100

    def test_checkpoint_compression(self):
        """Test compressed checkpoints."""
        from sim.core.checkpoint import CheckpointManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(tmpdir)

            state = {"data": np.random.rand(100, 100)}

            path = manager.save(
                state=state, name="test", simulation_type="test", step=1, compress=True
            )

            assert str(path).endswith(".gz")

            loaded = manager.load(path)
            assert_allclose(loaded["state"]["data"], state["data"])

    def test_checkpoint_list(self):
        """Test listing checkpoints."""
        from sim.core.checkpoint import CheckpointManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(tmpdir)

            for i in range(3):
                manager.save(state={"step": i}, name="test", simulation_type="test", step=i)

            checkpoints = manager.list_checkpoints("test")
            assert len(checkpoints) == 3

    def test_checkpoint_cleanup(self):
        """Test checkpoint cleanup."""
        import time

        from sim.core.checkpoint import CheckpointManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(tmpdir)

            for i in range(5):
                manager.save(state={"step": i}, name="test", simulation_type="test", step=i)
                # Windows filesystem has ~15ms timestamp resolution, need longer sleep
                time.sleep(0.2)

            deleted = manager.cleanup("test", keep_last=2)

            assert deleted == 3
            assert len(manager.list_checkpoints("test")) == 2

    def test_checkpoint_load_latest(self):
        """Test loading latest checkpoint."""
        import time

        from sim.core.checkpoint import CheckpointManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(tmpdir)

            for i in range(3):
                manager.save(state={"value": i}, name="test", simulation_type="test", step=i)
                # Windows filesystem has ~15ms timestamp resolution, need longer sleep
                time.sleep(0.2)

            latest = manager.load_latest("test")
            assert latest["state"]["value"] == 2


class TestLogging:
    """Test logging system."""

    def test_setup_logging(self):
        """Test logging setup."""
        import logging

        from sim.core.logging import logger, setup_logging

        setup_logging(level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_get_logger(self):
        """Test getting module logger."""
        from sim.core.logging import get_logger

        log = get_logger("test_module")
        assert log.name == "sim.test_module"

    def test_log_context(self):
        """Test log level context manager."""
        import logging

        from sim.core.logging import logger, silence

        original_level = logger.level

        with silence():
            assert logger.level > logging.CRITICAL

        assert logger.level == original_level


class TestProgress:
    """Test progress tracking."""

    def test_simple_progress(self):
        """Test simple progress bar."""
        from sim.core.progress import SimpleProgress

        pbar = SimpleProgress(total=100, desc="Test", disable=True)

        for i in range(100):
            pbar.update()

        pbar.close()

    def test_progress_tracker(self):
        """Test ProgressTracker."""
        from sim.core.progress import ProgressTracker

        with ProgressTracker(10, desc="Test", disable=True) as pbar:
            for i in range(10):
                pbar.update()
                info = pbar.get_info()
                assert info.current == i + 1

    def test_progress_iter(self):
        """Test progress_iter wrapper."""
        from sim.core.progress import progress_iter

        items = list(range(10))
        results = list(progress_iter(items, desc="Test", disable=True))

        assert results == items


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Configuration Management
========================

YAML-based configuration for simulations.
"""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Try to import YAML, fall back to JSON-only
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .exceptions import ConfigurationError
from .logging import get_logger

logger = get_logger("config")


@dataclass
class QuantumConfig:
    """Configuration for quantum simulations."""

    num_qubits: int = 3
    entanglement_strength: float = 1.0
    use_gpu: Optional[bool] = None
    preferred_backend: Optional[str] = None


@dataclass
class CosmicConfig:
    """Configuration for N-body simulations."""

    integrator: str = "rk45"  # rk45, verlet, leapfrog, yoshida
    rtol: float = 1e-8
    atol: float = 1e-10
    max_step: Optional[float] = None
    use_gpu: Optional[bool] = None
    collision_detection: bool = False
    softening_length: float = 0.0


@dataclass
class CoherenceConfig:
    """Configuration for coherence simulations."""

    num_stages: int = 12
    alpha: float = 0.66
    initial_coherence: float = 0.0


@dataclass
class GenesisConfig:
    """Configuration for matter genesis simulations."""

    inflaton_mass: float = 1e13
    coupling: float = 1e-7
    cp_violation: float = 1e-6
    total_time: float = 1000.0
    dt: float = 1.0


@dataclass
class VisualizationConfig:
    """Configuration for visualization."""

    style: str = "dark_background"
    figsize: tuple = (10, 8)
    dpi: int = 100
    save_format: str = "png"
    animation_fps: int = 30


@dataclass
class OutputConfig:
    """Configuration for output and checkpoints."""

    output_dir: str = "./output"
    checkpoint_dir: str = "./checkpoints"
    checkpoint_interval: int = 100
    save_trajectory: bool = True
    compress_checkpoints: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging."""

    level: str = "INFO"
    log_file: Optional[str] = None
    use_colors: bool = True
    verbose: bool = False


@dataclass
class SimulationConfig:
    """
    Master configuration for all simulations.

    Examples:
    ---------
    >>> config = SimulationConfig.from_yaml("config.yaml")
    >>> config.quantum.num_qubits = 5
    >>> config.save("my_config.yaml")
    """

    quantum: QuantumConfig = field(default_factory=QuantumConfig)
    cosmic: CosmicConfig = field(default_factory=CosmicConfig)
    coherence: CoherenceConfig = field(default_factory=CoherenceConfig)
    genesis: GenesisConfig = field(default_factory=GenesisConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "quantum": asdict(self.quantum),
            "cosmic": asdict(self.cosmic),
            "coherence": asdict(self.coherence),
            "genesis": asdict(self.genesis),
            "visualization": asdict(self.visualization),
            "output": asdict(self.output),
            "logging": asdict(self.logging),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        """Create from dictionary."""
        config = cls()

        if "quantum" in data:
            config.quantum = QuantumConfig(**data["quantum"])
        if "cosmic" in data:
            config.cosmic = CosmicConfig(**data["cosmic"])
        if "coherence" in data:
            config.coherence = CoherenceConfig(**data["coherence"])
        if "genesis" in data:
            config.genesis = GenesisConfig(**data["genesis"])
        if "visualization" in data:
            # Handle tuple conversion for figsize
            vis_data = data["visualization"].copy()
            if "figsize" in vis_data and isinstance(vis_data["figsize"], list):
                vis_data["figsize"] = tuple(vis_data["figsize"])
            config.visualization = VisualizationConfig(**vis_data)
        if "output" in data:
            config.output = OutputConfig(**data["output"])
        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])

        return config

    def save(self, path: Union[str, Path]) -> None:
        """
        Save configuration to file.

        Args:
            path: File path (.yaml, .yml, or .json)
        """
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = self.to_dict()

        if filepath.suffix in (".yaml", ".yml"):
            if not YAML_AVAILABLE:
                raise ConfigurationError(
                    "format",
                    "yaml",
                    "PyYAML not installed. Use 'pip install pyyaml' or save as .json",
                )
            with open(filepath, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        else:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

        logger.info(f"Configuration saved to {filepath}")

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "SimulationConfig":
        """
        Load configuration from file.

        Args:
            path: File path (.yaml, .yml, or .json)

        Returns:
            SimulationConfig instance
        """
        filepath = Path(path)

        if not filepath.exists():
            raise ConfigurationError("path", str(path), "File not found")

        with open(filepath, "r") as f:
            if filepath.suffix in (".yaml", ".yml"):
                if not YAML_AVAILABLE:
                    raise ConfigurationError(
                        "format", "yaml", "PyYAML not installed. Use 'pip install pyyaml'"
                    )
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        logger.info(f"Configuration loaded from {filepath}")
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "SimulationConfig":
        """Alias for from_file with YAML."""
        return cls.from_file(path)

    def validate(self) -> bool:
        """
        Validate configuration values.

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        # Quantum validation
        if self.quantum.num_qubits < 1:
            raise ConfigurationError("quantum.num_qubits", self.quantum.num_qubits, "Must be >= 1")
        if not 0 <= self.quantum.entanglement_strength <= 1:
            raise ConfigurationError(
                "quantum.entanglement_strength",
                self.quantum.entanglement_strength,
                "Must be in [0, 1]",
            )

        # Cosmic validation
        valid_integrators = ["rk45", "verlet", "leapfrog", "yoshida", "dop853"]
        if self.cosmic.integrator not in valid_integrators:
            raise ConfigurationError(
                "cosmic.integrator", self.cosmic.integrator, f"Must be one of {valid_integrators}"
            )

        # Coherence validation
        if self.coherence.num_stages < 1:
            raise ConfigurationError(
                "coherence.num_stages", self.coherence.num_stages, "Must be >= 1"
            )

        # Logging validation
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging.level.upper() not in valid_levels:
            raise ConfigurationError(
                "logging.level", self.logging.level, f"Must be one of {valid_levels}"
            )

        return True


# Global configuration instance
_global_config: Optional[SimulationConfig] = None


def get_config() -> SimulationConfig:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = SimulationConfig()
    return _global_config


def set_config(config: SimulationConfig) -> None:
    """Set the global configuration instance."""
    global _global_config
    config.validate()
    _global_config = config


def load_config(path: Union[str, Path]) -> SimulationConfig:
    """Load and set the global configuration from file."""
    config = SimulationConfig.from_file(path)
    set_config(config)
    return config


def reset_config() -> None:
    """Reset to default configuration."""
    global _global_config
    _global_config = SimulationConfig()


# Environment variable support
def config_from_env() -> SimulationConfig:
    """
    Create configuration from environment variables.

    Supported variables:
        SIM_QUANTUM_QUBITS, SIM_COSMIC_INTEGRATOR, SIM_LOG_LEVEL, etc.
    """
    config = SimulationConfig()

    # Quantum
    if "SIM_QUANTUM_QUBITS" in os.environ:
        config.quantum.num_qubits = int(os.environ["SIM_QUANTUM_QUBITS"])
    if "SIM_QUANTUM_GPU" in os.environ:
        config.quantum.use_gpu = os.environ["SIM_QUANTUM_GPU"].lower() == "true"

    # Cosmic
    if "SIM_COSMIC_INTEGRATOR" in os.environ:
        config.cosmic.integrator = os.environ["SIM_COSMIC_INTEGRATOR"]
    if "SIM_COSMIC_RTOL" in os.environ:
        config.cosmic.rtol = float(os.environ["SIM_COSMIC_RTOL"])

    # Logging
    if "SIM_LOG_LEVEL" in os.environ:
        config.logging.level = os.environ["SIM_LOG_LEVEL"]
    if "SIM_LOG_FILE" in os.environ:
        config.logging.log_file = os.environ["SIM_LOG_FILE"]

    # Output
    if "SIM_OUTPUT_DIR" in os.environ:
        config.output.output_dir = os.environ["SIM_OUTPUT_DIR"]
    if "SIM_CHECKPOINT_DIR" in os.environ:
        config.output.checkpoint_dir = os.environ["SIM_CHECKPOINT_DIR"]

    return config


# Generate example config file
def generate_example_config(path: Union[str, Path] = "sim_config.yaml") -> Path:
    """
    Generate an example configuration file.

    Args:
        path: Output file path

    Returns:
        Path to generated file
    """
    config = SimulationConfig()
    config.save(path)
    return Path(path)

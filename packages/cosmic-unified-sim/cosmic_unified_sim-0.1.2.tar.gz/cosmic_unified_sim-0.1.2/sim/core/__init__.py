"""
Core Module
===========

Base classes, utilities, and infrastructure for simulations.
"""

from .base import SimulationBase, SimulationResult
from .checkpoint import (
    CheckpointManager,
    CheckpointMetadata,
    get_checkpoint_manager,
    load_checkpoint,
    load_latest_checkpoint,
    save_checkpoint,
)
from .config import (
    CoherenceConfig,
    CosmicConfig,
    GenesisConfig,
    LoggingConfig,
    OutputConfig,
    QuantumConfig,
    SimulationConfig,
    VisualizationConfig,
    generate_example_config,
    get_config,
    load_config,
    reset_config,
    set_config,
)
from .exceptions import (
    CheckpointError,
    CoherenceError,
    CollisionError,
    ConfigurationError,
    CosmicError,
    EntanglementError,
    GenesisError,
    GPUError,
    GPUMemoryError,
    GPUNotAvailableError,
    HolographicError,
    IntegrationError,
    InvalidBodyError,
    InvalidQuantumStateError,
    InvalidQubitIndexError,
    InvalidStageError,
    NoBodiesError,
    PhysicsViolationError,
    QuantumError,
    SimulationError,
    ValidationError,
)
from .gpu import (
    GPU_AVAILABLE,
    GPUBackend,
    get_array_module,
    get_backend,
    get_gpu_info,
    list_available_backends,
)
from .logging import (
    critical,
    debug,
    error,
    get_logger,
    info,
    logger,
    setup_logging,
    silence,
    verbose,
    warning,
)
from .progress import (
    ProgressCallback,
    ProgressInfo,
    ProgressTracker,
    progress_iter,
)

__all__ = [
    # Base classes
    "SimulationBase",
    "SimulationResult",
    # Exceptions
    "SimulationError",
    "QuantumError",
    "InvalidQubitIndexError",
    "InvalidQuantumStateError",
    "EntanglementError",
    "CosmicError",
    "NoBodiesError",
    "InvalidBodyError",
    "CollisionError",
    "IntegrationError",
    "CoherenceError",
    "InvalidStageError",
    "GenesisError",
    "PhysicsViolationError",
    "HolographicError",
    "GPUError",
    "GPUNotAvailableError",
    "GPUMemoryError",
    "ConfigurationError",
    "CheckpointError",
    "ValidationError",
    # GPU
    "GPUBackend",
    "get_backend",
    "get_array_module",
    "GPU_AVAILABLE",
    "list_available_backends",
    "get_gpu_info",
    # Logging
    "logger",
    "setup_logging",
    "get_logger",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "silence",
    "verbose",
    # Checkpoint
    "CheckpointManager",
    "CheckpointMetadata",
    "get_checkpoint_manager",
    "save_checkpoint",
    "load_checkpoint",
    "load_latest_checkpoint",
    # Config
    "SimulationConfig",
    "QuantumConfig",
    "CosmicConfig",
    "CoherenceConfig",
    "GenesisConfig",
    "VisualizationConfig",
    "OutputConfig",
    "LoggingConfig",
    "get_config",
    "set_config",
    "load_config",
    "reset_config",
    "generate_example_config",
    # Progress
    "ProgressTracker",
    "ProgressCallback",
    "ProgressInfo",
    "progress_iter",
]

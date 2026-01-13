"""
Unified Cosmological Simulation Framework
==========================================

A comprehensive Python library for cosmological simulations combining:
- Quantum mechanics and emergence (quantum module)
- N-body celestial dynamics (cosmic module)
- Universe coherence evolution (coherence module)
- Matter genesis in early universe (genesis module)
- Holographic information analysis (holographic module)

Quick Start:
-----------
>>> from sim import QuantumFabric, NBodySimulator, CoherenceModel
>>> from sim.constants import PhysicalConstants, CosmologicalConstants

Author: Timur Isanov <tisanov@yahoo.com>
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Timur Isanov"

# Coherence module
from sim.coherence import (
    CoherenceModel,
    DepositionModel,
    UniverseSimulator,
)

# Core constants
from sim.constants import (
    FUTURE_STAGES,
    UNIVERSE_STAGES,
    CosmologicalConstants,
    PhysicalConstants,
)

# Cosmic N-body module
from sim.cosmic import (
    Body,
    CosmicCalculator,
    NBodySimulator,
    SystemPresets,
)

# Genesis module (matter creation)
from sim.genesis import (
    LeptogenesisModel,
    MatterGenesisSimulation,
    ParametricResonance,
    QuantumCreation,
)

# Holographic module
from sim.holographic import (
    HolographicAnalysis,
    UniverseFormulaReport,
)

# Quantum module
from sim.quantum import (
    ELECTRON_OBSERVER,
    HUMAN_OBSERVER,
    LIGO_OBSERVER,
    EmergentLaws,
    Observer,
    QuantumFabric,
)

# Visualization
from sim.visualization import (
    SimulationVisualizer,
    animate_simulation,
    plot_coherence_evolution,
    plot_quantum_state,
    plot_trajectories_3d,
)

__all__ = [
    # Version
    "__version__",
    # Constants
    "PhysicalConstants",
    "CosmologicalConstants",
    "UNIVERSE_STAGES",
    "FUTURE_STAGES",
    # Quantum
    "QuantumFabric",
    "EmergentLaws",
    "Observer",
    "HUMAN_OBSERVER",
    "LIGO_OBSERVER",
    "ELECTRON_OBSERVER",
    # Cosmic
    "Body",
    "NBodySimulator",
    "SystemPresets",
    "CosmicCalculator",
    # Coherence
    "CoherenceModel",
    "DepositionModel",
    "UniverseSimulator",
    # Genesis
    "ParametricResonance",
    "LeptogenesisModel",
    "QuantumCreation",
    "MatterGenesisSimulation",
    # Holographic
    "HolographicAnalysis",
    "UniverseFormulaReport",
    # Visualization
    "SimulationVisualizer",
    "plot_trajectories_3d",
    "plot_coherence_evolution",
    "plot_quantum_state",
    "animate_simulation",
]

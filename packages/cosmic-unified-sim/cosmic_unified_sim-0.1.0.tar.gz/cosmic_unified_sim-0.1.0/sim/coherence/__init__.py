"""
Coherence Module
================

Universe coherence evolution models based on recurrence relations.
"""

from .models import CoherenceModel, DepositionModel, SymmetryBreaking
from .simulator import UniverseSimulator

__all__ = [
    "CoherenceModel",
    "DepositionModel",
    "SymmetryBreaking",
    "UniverseSimulator",
]

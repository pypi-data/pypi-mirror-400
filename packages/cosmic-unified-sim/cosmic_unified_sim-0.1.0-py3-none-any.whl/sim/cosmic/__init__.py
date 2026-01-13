"""
Cosmic Module
=============

N-body gravitational simulations with multiple integration methods.
"""

from .body import Body
from .calculator import CosmicCalculator
from .integrators import (
    AdaptiveIntegrator,
    EulerIntegrator,
    ForestRuthIntegrator,
    Integrator,
    IntegratorState,
    LeapfrogIntegrator,
    VerletIntegrator,
    Yoshida4Integrator,
    Yoshida6Integrator,
    get_integrator,
    list_integrators,
)
from .nbody import NBodySimulator
from .presets import SystemPresets

__all__ = [
    # Main classes
    "Body",
    "NBodySimulator",
    "SystemPresets",
    "CosmicCalculator",
    # Integrators
    "Integrator",
    "IntegratorState",
    "EulerIntegrator",
    "VerletIntegrator",
    "LeapfrogIntegrator",
    "Yoshida4Integrator",
    "Yoshida6Integrator",
    "ForestRuthIntegrator",
    "AdaptiveIntegrator",
    "get_integrator",
    "list_integrators",
]

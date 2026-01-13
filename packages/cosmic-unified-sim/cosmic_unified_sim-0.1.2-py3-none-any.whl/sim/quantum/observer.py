"""
Observer Model
==============

Models observer-dependent decoherence in quantum systems.
"""

from typing import Union

import numpy as np


class Observer:
    """
    Observer with characteristic decoherence power.

    Models how different observers interact with quantum systems
    and cause decoherence. The decoherence rate depends on:
    - Mass: More massive observers interact more strongly
    - Temperature: Higher temperature increases decoherence
    - Complexity: More complex observers have more degrees of freedom

    Examples:
    ---------
    >>> from sim.quantum import Observer, HUMAN_OBSERVER
    >>> print(HUMAN_OBSERVER)
    Observer(mass=7.00e+01 kg, T=300.00 K, Γ=4.67e+01)
    >>> coherence = HUMAN_OBSERVER.observe_system(1.0, observation_time=1.0)
    >>> print(f"Remaining coherence: {coherence:.2e}")
    """

    def __init__(self, mass: float, temperature: float, complexity: float):
        """
        Initialize observer.

        Args:
            mass: Observer mass in kg
            temperature: Observer temperature in Kelvin
            complexity: Complexity measure (number of degrees of freedom)

        Raises:
            ValueError: If parameters are invalid
        """
        if mass < 0:
            raise ValueError(f"mass must be >= 0, got {mass}")
        if temperature < 0:
            raise ValueError(f"temperature must be >= 0, got {temperature}")
        if complexity < 0:
            raise ValueError(f"complexity must be >= 0, got {complexity}")

        self.mass = mass
        self.temperature = temperature
        self.complexity = complexity
        self.decoherence_power = self._calculate_decoherence_power()

    def _calculate_decoherence_power(self) -> float:
        """
        Calculate decoherence power Γ.

        Formula: Γ = ln(1 + |m × c / (T + ε)|)
        where m = mass, c = complexity, T = temperature

        Returns:
            Decoherence power Γ
        """
        base_power = self.mass * self.complexity
        if self.temperature > 0:
            base_power /= self.temperature + 1e-10
        return np.log(1 + abs(base_power))

    def observe_system(
        self, quantum_system: Union[float, np.ndarray], observation_time: float = 1.0
    ) -> Union[float, np.ndarray]:
        """
        Observer interacts with quantum system, causing decoherence.

        Coherence decays exponentially: coherence(t) = exp(-Γ × t)

        Args:
            quantum_system: Quantum system (number or array)
            observation_time: Observation duration

        Returns:
            System after decoherence

        Raises:
            ValueError: If observation_time < 0
        """
        if observation_time < 0:
            raise ValueError(f"observation_time must be >= 0, got {observation_time}")

        decoherence_rate = self.decoherence_power * observation_time
        coherence = np.exp(-decoherence_rate)
        return self._apply_decoherence(quantum_system, coherence)

    def _apply_decoherence(
        self, system: Union[float, np.ndarray], coherence_level: float
    ) -> Union[float, np.ndarray]:
        """Apply decoherence to system."""
        return system * coherence_level

    def get_decoherence_time(self, target_coherence: float = 0.01) -> float:
        """
        Calculate time for coherence to decay to target level.

        Args:
            target_coherence: Target coherence level (default 1%)

        Returns:
            Decoherence time
        """
        if target_coherence <= 0 or target_coherence >= 1:
            raise ValueError(f"target_coherence must be in (0, 1), got {target_coherence}")
        if self.decoherence_power <= 0:
            return float("inf")
        return -np.log(target_coherence) / self.decoherence_power

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Observer(mass={self.mass:.2e} kg, "
            f"T={self.temperature:.2f} K, "
            f"Γ={self.decoherence_power:.2e})"
        )

    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"Observer(mass={self.mass}, "
            f"temperature={self.temperature}, "
            f"complexity={self.complexity})"
        )


# Standard observers
HUMAN_OBSERVER = Observer(mass=70, temperature=300, complexity=1e15)
"""Human observer: ~70 kg, body temperature ~300 K, brain complexity ~10^15 synapses"""

LIGO_OBSERVER = Observer(mass=40, temperature=0.01, complexity=1e10)
"""LIGO detector: ~40 kg mirrors, cryogenic ~10 mK, ~10^10 modes"""

ELECTRON_OBSERVER = Observer(mass=9e-31, temperature=2.7, complexity=1)
"""Single electron: electron mass, CMB temperature, minimal complexity"""

QUANTUM_COMPUTER_OBSERVER = Observer(mass=1e-3, temperature=0.015, complexity=1e6)
"""Superconducting quantum computer: ~1g chip, ~15 mK, ~10^6 qubits/modes"""

COSMIC_OBSERVER = Observer(mass=1e42, temperature=2.7, complexity=1e80)
"""Observable universe: ~10^42 kg mass, CMB temperature, ~10^80 particles"""

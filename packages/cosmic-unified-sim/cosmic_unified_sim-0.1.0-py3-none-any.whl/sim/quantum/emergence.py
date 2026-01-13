"""
Emergent Physical Laws
======================

Models for emergent physical phenomena:
- Particle-antiparticle creation from vacuum
- Landauer's principle (information thermodynamics)
- Spacetime metric estimation from entanglement
"""

from typing import Any, Dict, List, Tuple, Union

import numpy as np

from sim.constants import PhysicalConstants


class EmergentLaws:
    """
    Static methods for modeling emergent physical phenomena.

    Demonstrates how macroscopic physical laws can emerge
    from microscopic quantum rules.

    Examples:
    ---------
    >>> from sim.quantum import EmergentLaws
    >>> particles = EmergentLaws.simulate_particle_creation(vacuum_energy=0.1)
    >>> print(f"Created {len(particles)} particle-antiparticle pairs")
    >>> energy = EmergentLaws.landauer_principle(bits_erased=100, temperature=300)
    >>> print(f"Minimum energy: {energy:.2e} J")
    """

    # Physical constants
    BOLTZMANN_CONSTANT = PhysicalConstants().k_B
    ELECTRON_MASS_MEV = PhysicalConstants().m_e * 1000  # Convert GeV to MeV

    @staticmethod
    def simulate_particle_creation(
        vacuum_energy: float = 0.1, time_steps: int = 100, particle_type: str = "electron"
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Simulate particle-antiparticle pair creation from vacuum fluctuations.

        Models quantum vacuum fluctuations that can produce
        particle-antiparticle pairs based on available energy.

        Args:
            vacuum_energy: Energy of vacuum fluctuations (dimensionless)
            time_steps: Number of time steps
            particle_type: Type of particle ('electron', 'photon')

        Returns:
            List of (particle, antiparticle) dictionary pairs

        Raises:
            ValueError: If parameters are invalid
        """
        if vacuum_energy < 0:
            raise ValueError(f"vacuum_energy must be >= 0, got {vacuum_energy}")
        if time_steps <= 0:
            raise ValueError(f"time_steps must be > 0, got {time_steps}")

        particles_created = []

        # Particle properties
        particle_properties = {
            "electron": {"charge": -1, "mass": EmergentLaws.ELECTRON_MASS_MEV},
            "positron": {"charge": +1, "mass": EmergentLaws.ELECTRON_MASS_MEV},
            "photon": {"charge": 0, "mass": 0.0},
            "quark": {"charge": +2 / 3, "mass": 2.2},  # Up quark mass in MeV
        }

        props = particle_properties.get(particle_type, particle_properties["electron"])

        for t in range(time_steps):
            # Creation probability decreases exponentially (energy conservation)
            creation_probability = vacuum_energy * np.exp(-t / 10)

            if np.random.random() < creation_probability:
                particle = {
                    "type": particle_type,
                    "charge": props["charge"],
                    "mass": props["mass"],
                    "momentum": np.random.randn(3) * vacuum_energy,
                    "created_at": t,
                }
                antiparticle = {
                    "type": f"anti-{particle_type}",
                    "charge": -props["charge"],
                    "mass": props["mass"],
                    "momentum": -particle["momentum"],  # Conservation of momentum
                    "created_at": t,
                }
                particles_created.append((particle, antiparticle))

        return particles_created

    @staticmethod
    def landauer_principle(bits_erased: Union[int, float], temperature: float) -> float:
        """
        Calculate minimum energy to erase information (Landauer's principle).

        E_min = k_B × T × ln(2) × bits

        This represents the fundamental thermodynamic cost of
        irreversible computation.

        Args:
            bits_erased: Number of bits erased
            temperature: System temperature in Kelvin

        Returns:
            Minimum energy in Joules

        Raises:
            ValueError: If parameters are invalid
        """
        if bits_erased < 0:
            raise ValueError(f"bits_erased must be >= 0, got {bits_erased}")
        if temperature < 0:
            raise ValueError(f"temperature must be >= 0, got {temperature}")

        return bits_erased * EmergentLaws.BOLTZMANN_CONSTANT * temperature * np.log(2)

    @staticmethod
    def estimate_metric_from_entanglement(
        entanglement_pattern: Union[np.ndarray, List],
    ) -> np.ndarray:
        """
        Estimate spacetime metric from entanglement patterns.

        Based on the idea that spacetime geometry emerges from
        quantum entanglement (ER=EPR conjecture, AdS/CFT).

        Args:
            entanglement_pattern: Matrix or array of entanglement correlations

        Returns:
            Estimated spacetime metric (symmetric matrix)
        """
        if isinstance(entanglement_pattern, list):
            entanglement_pattern = np.array(entanglement_pattern)

        if not isinstance(entanglement_pattern, np.ndarray):
            return np.eye(2)

        if entanglement_pattern.ndim == 1:
            if len(entanglement_pattern) < 2:
                return np.eye(2)
            pattern_2d = entanglement_pattern.reshape(-1, 1)
            metric = np.corrcoef(pattern_2d, rowvar=False)
        elif entanglement_pattern.ndim == 2:
            metric = np.corrcoef(entanglement_pattern)
        else:
            return np.eye(2)

        # Ensure symmetry
        metric = (metric + metric.T) / 2

        # Handle NaN values
        metric = np.nan_to_num(metric, nan=0.0)

        return metric

    @staticmethod
    def vacuum_fluctuation_energy(volume: float, temperature: float = 2.7) -> float:
        """
        Estimate vacuum fluctuation energy in a volume.

        Based on quantum field theory zero-point energy.

        Args:
            volume: Volume in m³
            temperature: Effective temperature in K (default: CMB temperature)

        Returns:
            Estimated vacuum energy in Joules
        """
        # Simplified model: E ~ k_B × T × (volume / λ³)
        # where λ is the thermal wavelength
        h = 6.626e-34  # Planck constant
        c = 3e8  # Speed of light
        k_B = EmergentLaws.BOLTZMANN_CONSTANT

        # Thermal wavelength
        lambda_T = h * c / (k_B * temperature) if temperature > 0 else 1e-3

        # Number of modes
        n_modes = volume / (lambda_T**3)

        return k_B * temperature * n_modes * 0.5

    @staticmethod
    def hawking_temperature(mass: float) -> float:
        """
        Calculate Hawking temperature of a black hole.

        T = ℏc³ / (8πGMk_B)

        Args:
            mass: Black hole mass in kg

        Returns:
            Hawking temperature in Kelvin
        """
        if mass <= 0:
            raise ValueError(f"mass must be > 0, got {mass}")

        pc = PhysicalConstants()
        return (pc.hbar * pc.c**3) / (8 * np.pi * pc.G * mass * pc.k_B)

    @staticmethod
    def unruh_temperature(acceleration: float) -> float:
        """
        Calculate Unruh temperature for accelerating observer.

        T = ℏa / (2πck_B)

        Args:
            acceleration: Proper acceleration in m/s²

        Returns:
            Unruh temperature in Kelvin
        """
        if acceleration < 0:
            raise ValueError(f"acceleration must be >= 0, got {acceleration}")

        pc = PhysicalConstants()
        return (pc.hbar * acceleration) / (2 * np.pi * pc.c * pc.k_B)

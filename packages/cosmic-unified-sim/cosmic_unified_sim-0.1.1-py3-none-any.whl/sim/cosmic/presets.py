"""
System Presets
==============

Predefined celestial systems for quick simulations.
"""

from typing import Any, Dict, List

import numpy as np

from .body import Body
from .calculator import CosmicCalculator


class SystemPresets:
    """
    Predefined celestial systems.

    Examples:
    ---------
    >>> from sim.cosmic import SystemPresets, NBodySimulator
    >>> presets = SystemPresets()
    >>> bodies = presets.create_solar_system()
    >>> sim = NBodySimulator(bodies)
    """

    def __init__(self):
        """Initialize with calculator."""
        self.calc = CosmicCalculator()

    def create_solar_system(self, include_outer_planets: bool = True) -> List[Body]:
        """
        Create Solar System bodies.

        Args:
            include_outer_planets: Include Jupiter, Saturn, Uranus, Neptune

        Returns:
            List of Body objects
        """
        bodies = []

        # Masses (kg)
        masses = {
            "Sun": 1.989e30,
            "Mercury": 3.301e23,
            "Venus": 4.867e24,
            "Earth": 5.972e24,
            "Mars": 6.417e23,
            "Jupiter": 1.898e27,
            "Saturn": 5.683e26,
            "Uranus": 8.681e25,
            "Neptune": 1.024e26,
        }

        # Distances from Sun (AU)
        distances_au = {
            "Mercury": 0.387,
            "Venus": 0.723,
            "Earth": 1.0,
            "Mars": 1.524,
            "Jupiter": 5.203,
            "Saturn": 9.537,
            "Uranus": 19.191,
            "Neptune": 30.069,
        }

        colors = {
            "Sun": "yellow",
            "Mercury": "gray",
            "Venus": "orange",
            "Earth": "blue",
            "Mars": "red",
            "Jupiter": "brown",
            "Saturn": "gold",
            "Uranus": "cyan",
            "Neptune": "navy",
        }

        # Sun at center
        bodies.append(
            Body(
                name="Sun",
                mass=masses["Sun"],
                position=np.array([0.0, 0.0, 0.0]),
                velocity=np.array([0.0, 0.0, 0.0]),
                radius=6.96e8,
                color="yellow",
            )
        )

        # Planets
        planet_list = ["Mercury", "Venus", "Earth", "Mars"]
        if include_outer_planets:
            planet_list.extend(["Jupiter", "Saturn", "Uranus", "Neptune"])

        for name in planet_list:
            r = distances_au[name] * self.calc.AU
            v = self.calc.orbital_velocity(masses["Sun"], r)

            bodies.append(
                Body(
                    name=name,
                    mass=masses[name],
                    position=np.array([r, 0.0, 0.0]),
                    velocity=np.array([0.0, v, 0.0]),
                    radius=r * 0.01,
                    color=colors[name],
                )
            )

        return bodies

    def create_binary_star_system(self, separation_au: float = 10.0) -> List[Body]:
        """
        Create binary star system.

        Args:
            separation_au: Separation between stars in AU

        Returns:
            List of Body objects
        """
        mass1 = 1.0 * self.calc.M_sun
        mass2 = 0.8 * self.calc.M_sun

        separation = separation_au * self.calc.AU
        total_mass = mass1 + mass2

        # Center of mass positions
        r1 = separation * mass2 / total_mass
        r2 = separation * mass1 / total_mass

        # Orbital velocities
        v1 = np.sqrt(self.calc.G * mass2 * separation / (total_mass * r1))
        v2 = np.sqrt(self.calc.G * mass1 * separation / (total_mass * r2))

        return [
            Body(
                name="Star 1",
                mass=mass1,
                position=np.array([-r1, 0.0, 0.0]),
                velocity=np.array([0.0, -v1, 0.0]),
                radius=6.96e8,
                color="yellow",
            ),
            Body(
                name="Star 2",
                mass=mass2,
                position=np.array([r2, 0.0, 0.0]),
                velocity=np.array([0.0, v2, 0.0]),
                radius=5.5e8,
                color="orange",
            ),
        ]

    def create_earth_moon_system(self) -> List[Body]:
        """
        Create Earth-Moon system.

        Returns:
            List of Body objects
        """
        mass_earth = 5.972e24
        mass_moon = 7.342e22
        r_moon = 3.844e8  # Mean lunar distance

        # Center of mass calculation
        total_mass = mass_earth + mass_moon
        r_earth_cm = r_moon * mass_moon / total_mass
        r_moon_cm = r_moon * mass_earth / total_mass

        # Orbital velocities
        v_earth = np.sqrt(self.calc.G * mass_moon / r_moon)
        v_moon = np.sqrt(self.calc.G * mass_earth / r_moon)

        return [
            Body(
                name="Earth",
                mass=mass_earth,
                position=np.array([-r_earth_cm, 0.0, 0.0]),
                velocity=np.array([0.0, -v_earth, 0.0]),
                radius=self.calc.R_earth,
                color="blue",
            ),
            Body(
                name="Moon",
                mass=mass_moon,
                position=np.array([r_moon_cm, 0.0, 0.0]),
                velocity=np.array([0.0, v_moon, 0.0]),
                radius=1.737e6,
                color="gray",
            ),
        ]

    def create_three_body_problem(self, config: str = "figure8") -> List[Body]:
        """
        Create classic three-body problem configurations.

        Args:
            config: Configuration name ('figure8', 'lagrange', 'euler')

        Returns:
            List of Body objects
        """
        if config == "figure8":
            # Famous figure-8 periodic orbit (Chenciner-Montgomery)
            # Positions and velocities for equal masses
            m = 1.0  # Unit mass
            scale = 1e11  # Scale factor
            v_scale = 3e4  # Velocity scale

            return [
                Body(
                    name="Body 1",
                    mass=m * 1e30,
                    position=np.array([-0.97000436, 0.24308753, 0.0]) * scale,
                    velocity=np.array([0.4662036850, 0.4323657300, 0.0]) * v_scale,
                    color="red",
                ),
                Body(
                    name="Body 2",
                    mass=m * 1e30,
                    position=np.array([0.97000436, -0.24308753, 0.0]) * scale,
                    velocity=np.array([0.4662036850, 0.4323657300, 0.0]) * v_scale,
                    color="blue",
                ),
                Body(
                    name="Body 3",
                    mass=m * 1e30,
                    position=np.array([0.0, 0.0, 0.0]) * scale,
                    velocity=np.array([-0.93240737, -0.86473146, 0.0]) * v_scale,
                    color="green",
                ),
            ]

        elif config == "lagrange":
            # Lagrange's equilateral triangle solution
            m = 1e30
            r = 1e11
            v = np.sqrt(self.calc.G * 3 * m / r) / 2

            angles = [0, 2 * np.pi / 3, 4 * np.pi / 3]

            bodies = []
            for i, angle in enumerate(angles):
                bodies.append(
                    Body(
                        name=f"Body {i+1}",
                        mass=m,
                        position=np.array([r * np.cos(angle), r * np.sin(angle), 0.0]),
                        velocity=np.array([-v * np.sin(angle), v * np.cos(angle), 0.0]),
                        color=["red", "blue", "green"][i],
                    )
                )
            return bodies

        else:
            raise ValueError(f"Unknown configuration: {config}")

    def create_custom_system(self, bodies_data: List[Dict[str, Any]]) -> List[Body]:
        """
        Create custom system from data dictionaries.

        Args:
            bodies_data: List of dicts with body parameters

        Returns:
            List of Body objects
        """
        return [Body(**data) for data in bodies_data]

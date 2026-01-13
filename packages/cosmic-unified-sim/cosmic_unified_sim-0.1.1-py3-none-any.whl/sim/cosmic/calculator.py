"""
Cosmic Calculator
=================

Physical constants and calculations for celestial mechanics.
"""

from typing import Tuple

import numpy as np

from sim.constants import PhysicalConstants


class CosmicCalculator:
    """
    Calculator for celestial mechanics with physical constants.

    Examples:
    ---------
    >>> from sim.cosmic import CosmicCalculator
    >>> calc = CosmicCalculator()
    >>> v = calc.orbital_velocity(calc.M_sun, calc.AU)
    >>> print(f"Earth orbital velocity: {v/1000:.1f} km/s")
    """

    def __init__(self):
        """Initialize with physical constants."""
        pc = PhysicalConstants()

        # Physical constants
        self.G = pc.G
        self.c = pc.c
        self.AU = pc.AU
        self.pc = pc.pc
        self.ly = pc.ly

        # Solar system
        self.M_sun = pc.M_sun
        self.R_sun = pc.R_sun
        self.M_earth = pc.M_earth
        self.R_earth = pc.R_earth

    def gravitational_force(self, m1: float, m2: float, r: float) -> float:
        """
        Newtonian gravitational force.

        F = GMm/r²

        Args:
            m1, m2: Masses in kg
            r: Distance in m

        Returns:
            Force in Newtons
        """
        return self.G * m1 * m2 / (r * r)

    def orbital_velocity(self, central_mass: float, distance: float) -> float:
        """
        Circular orbital velocity.

        v = √(GM/r)

        Args:
            central_mass: Central body mass in kg
            distance: Orbital radius in m

        Returns:
            Orbital velocity in m/s
        """
        return np.sqrt(self.G * central_mass / distance)

    def orbital_period(self, semi_major_axis: float, mass1: float, mass2: float) -> float:
        """
        Orbital period from Kepler's third law.

        T = 2π√(a³/G(M₁+M₂))

        Args:
            semi_major_axis: Semi-major axis in m
            mass1, mass2: Masses in kg

        Returns:
            Period in seconds
        """
        total_mass = mass1 + mass2
        return 2 * np.pi * np.sqrt(semi_major_axis**3 / (self.G * total_mass))

    def escape_velocity(self, mass: float, radius: float) -> float:
        """
        Escape velocity from surface.

        v_esc = √(2GM/r)

        Args:
            mass: Body mass in kg
            radius: Surface radius in m

        Returns:
            Escape velocity in m/s
        """
        return np.sqrt(2 * self.G * mass / radius)

    def hill_sphere_radius(
        self, m_primary: float, m_secondary: float, semi_major_axis: float
    ) -> float:
        """
        Hill sphere radius (gravitational influence).

        r_H ≈ a × (m/3M)^(1/3)

        Args:
            m_primary: Primary body mass (e.g., Sun)
            m_secondary: Secondary body mass (e.g., planet)
            semi_major_axis: Orbital semi-major axis

        Returns:
            Hill sphere radius in m
        """
        return semi_major_axis * (m_secondary / (3 * m_primary)) ** (1 / 3)

    def roche_limit(self, m_primary: float, r_primary: float, rho_secondary: float) -> float:
        """
        Roche limit (tidal disruption distance).

        d ≈ r × (2 × ρ_primary / ρ_secondary)^(1/3)

        Args:
            m_primary: Primary body mass
            r_primary: Primary body radius
            rho_secondary: Secondary body density

        Returns:
            Roche limit in m
        """
        rho_primary = m_primary / (4 / 3 * np.pi * r_primary**3)
        return r_primary * (2 * rho_primary / rho_secondary) ** (1 / 3)

    def parallax_distance(self, baseline: float, parallax_angle_rad: float) -> float:
        """
        Distance from parallax measurement.

        D = B / θ

        Args:
            baseline: Measurement baseline in m
            parallax_angle_rad: Parallax angle in radians

        Returns:
            Distance in m
        """
        return baseline / parallax_angle_rad

    def angular_size(self, physical_size: float, distance: float) -> float:
        """
        Angular size of an object.

        θ = R / D

        Args:
            physical_size: Physical size in m
            distance: Distance in m

        Returns:
            Angular size in radians
        """
        return physical_size / distance

    def spherical_to_cartesian(self, r: float, theta: float, phi: float) -> np.ndarray:
        """
        Convert spherical to Cartesian coordinates.

        Args:
            r: Radial distance
            theta: Polar angle (from z-axis)
            phi: Azimuthal angle (from x-axis)

        Returns:
            Cartesian [x, y, z]
        """
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return np.array([x, y, z])

    def cartesian_to_spherical(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """
        Convert Cartesian to spherical coordinates.

        Args:
            x, y, z: Cartesian coordinates

        Returns:
            Tuple (r, theta, phi)
        """
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = np.arccos(z / r) if r > 0 else 0
        phi = np.arctan2(y, x)
        return r, theta, phi

    def vis_viva_velocity(self, mass: float, r: float, a: float) -> float:
        """
        Orbital velocity at any point (vis-viva equation).

        v² = GM(2/r - 1/a)

        Args:
            mass: Central body mass
            r: Current distance
            a: Semi-major axis

        Returns:
            Velocity in m/s
        """
        return np.sqrt(self.G * mass * (2 / r - 1 / a))

    def synodic_period(self, T1: float, T2: float) -> float:
        """
        Synodic period between two orbits.

        1/T_syn = |1/T1 - 1/T2|

        Args:
            T1, T2: Orbital periods

        Returns:
            Synodic period
        """
        return 1 / abs(1 / T1 - 1 / T2)

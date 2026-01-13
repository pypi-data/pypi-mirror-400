"""
Fundamental Physical Constants
==============================

Physical constants for cosmological and quantum simulations.
Supports both SI units and natural units (ℏ = c = k_B = 1).
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PhysicalConstants:
    """
    Fundamental physical constants in SI units and natural units.

    SI Units:
        Mass: kg, Length: m, Time: s, Energy: J

    Natural Units (ℏ = c = k_B = 1):
        Energy: GeV, Length: GeV⁻¹, Time: GeV⁻¹

    Conversions:
        - 1 GeV⁻¹ ≈ 6.58 × 10⁻²⁵ s
        - 1 GeV⁻¹ ≈ 1.97 × 10⁻¹⁶ m
        - 1 K ≈ 8.62 × 10⁻¹⁴ GeV

    Examples:
    ---------
    >>> from sim.constants import PhysicalConstants
    >>> pc = PhysicalConstants()
    >>> print(f"Speed of light: {pc.c:.2e} m/s")
    Speed of light: 3.00e+08 m/s
    >>> print(f"Fine structure constant: 1/α = {1/pc.alpha:.2f}")
    Fine structure constant: 1/α = 137.04
    """

    # ==========================================================================
    # Fundamental Constants (SI Units)
    # ==========================================================================

    # Speed of light [m/s]
    c: float = 299_792_458.0

    # Gravitational constant [m³/(kg·s²)]
    G: float = 6.67430e-11

    # Planck constant [J·s]
    h: float = 6.62607015e-34

    # Reduced Planck constant ℏ = h/(2π) [J·s]
    hbar: float = 1.054571817e-34

    # Boltzmann constant [J/K]
    k_B: float = 1.380649e-23

    # Elementary charge [C]
    e: float = 1.602176634e-19

    # Vacuum permittivity [F/m]
    epsilon_0: float = 8.8541878128e-12

    # Vacuum permeability [H/m]
    mu_0: float = 1.25663706212e-6

    # ==========================================================================
    # Fine Structure Constant (dimensionless)
    # ==========================================================================

    # α = e²/(4πε₀ℏc) ≈ 1/137
    alpha: float = 0.0072973525693

    # ==========================================================================
    # Particle Masses (SI: kg, and GeV)
    # ==========================================================================

    # Electron mass [kg]
    m_e_kg: float = 9.1093837015e-31
    # Electron mass [GeV/c²]
    m_e: float = 0.000511

    # Proton mass [kg]
    m_p_kg: float = 1.67262192369e-27
    # Proton mass [GeV/c²]
    m_p: float = 0.938272

    # Neutron mass [GeV/c²]
    m_n: float = 0.939565

    # Muon mass [GeV/c²]
    m_mu: float = 0.105658

    # Tau mass [GeV/c²]
    m_tau: float = 1.77686

    # ==========================================================================
    # Quark Masses [GeV/c²] (current quark masses)
    # ==========================================================================

    m_up: float = 0.00216
    m_down: float = 0.00467
    m_strange: float = 0.0934
    m_charm: float = 1.27
    m_bottom: float = 4.18
    m_top: float = 172.76

    # ==========================================================================
    # Boson Masses [GeV/c²]
    # ==========================================================================

    m_W: float = 80.379  # W boson
    m_Z: float = 91.1876  # Z boson
    m_H: float = 125.10  # Higgs boson

    # ==========================================================================
    # Planck Units
    # ==========================================================================

    # Planck mass [kg]
    m_planck_kg: float = 2.176434e-8
    # Planck mass [GeV/c²]
    m_planck: float = 1.22093e19

    # Planck length [m]
    l_planck: float = 1.616255e-35

    # Planck time [s]
    t_planck: float = 5.391247e-44

    # Planck temperature [K]
    T_planck: float = 1.416784e32

    # ==========================================================================
    # Astronomical Constants (SI)
    # ==========================================================================

    # Astronomical Unit [m]
    AU: float = 1.495978707e11

    # Parsec [m]
    pc: float = 3.0856775814913673e16

    # Light year [m]
    ly: float = 9.4607304725808e15

    # Solar mass [kg]
    M_sun: float = 1.98892e30

    # Solar radius [m]
    R_sun: float = 6.96340e8

    # Earth mass [kg]
    M_earth: float = 5.97217e24

    # Earth radius [m]
    R_earth: float = 6.371e6

    # ==========================================================================
    # Conversion Factors
    # ==========================================================================

    # GeV to Joules
    GeV_to_J: float = 1.602176634e-10

    # GeV⁻¹ to seconds
    GeV_inv_to_s: float = 6.582119569e-25

    # GeV⁻¹ to meters
    GeV_inv_to_m: float = 1.9732696e-16

    # Kelvin to GeV
    K_to_GeV: float = 8.617333262e-14

    # ==========================================================================
    # Energy Scales [GeV]
    # ==========================================================================

    # Electroweak scale (Higgs VEV)
    v_EW: float = 246.22

    # QCD scale Λ_QCD
    Lambda_QCD: float = 0.217

    # GUT scale (approximate)
    E_GUT: float = 1e16

    # ==========================================================================
    # Coupling Constants at M_Z
    # ==========================================================================

    # Strong coupling αs(M_Z)
    alpha_s: float = 0.1179

    # Weak coupling αW
    alpha_W: float = 1.0 / 30.0

    # Weinberg angle sin²θ_W
    sin2_theta_W: float = 0.23122

    # ==========================================================================
    # Derived Properties
    # ==========================================================================

    @property
    def inverse_alpha(self) -> float:
        """1/α ≈ 137.036"""
        return 1.0 / self.alpha

    @property
    def delta_m_boson(self) -> float:
        """m_Z - m_W [GeV]"""
        return self.m_Z - self.m_W

    @property
    def G_natural(self) -> float:
        """Gravitational constant in natural units: G = 1/M_planck²"""
        return 1.0 / (self.m_planck**2)

    def to_natural_time(self, time_si: float) -> float:
        """Convert time from SI (seconds) to natural units (GeV⁻¹)"""
        return time_si / self.GeV_inv_to_s

    def to_si_time(self, time_natural: float) -> float:
        """Convert time from natural units (GeV⁻¹) to SI (seconds)"""
        return time_natural * self.GeV_inv_to_s

    def to_natural_length(self, length_si: float) -> float:
        """Convert length from SI (meters) to natural units (GeV⁻¹)"""
        return length_si / self.GeV_inv_to_m

    def to_si_length(self, length_natural: float) -> float:
        """Convert length from natural units (GeV⁻¹) to SI (meters)"""
        return length_natural * self.GeV_inv_to_m

    def to_natural_temperature(self, T_kelvin: float) -> float:
        """Convert temperature from Kelvin to GeV"""
        return T_kelvin * self.K_to_GeV

    def to_kelvin(self, T_gev: float) -> float:
        """Convert temperature from GeV to Kelvin"""
        return T_gev / self.K_to_GeV

    def orbital_velocity(self, central_mass: float, distance: float) -> float:
        """
        Circular orbital velocity.

        v = √(GM/r)

        Args:
            central_mass: Mass of central body [kg]
            distance: Orbital radius [m]

        Returns:
            Orbital velocity [m/s]
        """
        return np.sqrt(self.G * central_mass / distance)

    def orbital_period(self, semi_major_axis: float, mass1: float, mass2: float) -> float:
        """
        Orbital period from Kepler's third law.

        T = 2π√(a³/G(M₁+M₂))

        Args:
            semi_major_axis: Semi-major axis [m]
            mass1, mass2: Masses of both bodies [kg]

        Returns:
            Orbital period [s]
        """
        total_mass = mass1 + mass2
        return 2 * np.pi * np.sqrt(semi_major_axis**3 / (self.G * total_mass))

    def gravitational_force(self, m1: float, m2: float, r: float) -> float:
        """
        Newtonian gravitational force.

        F = GMm/r²

        Args:
            m1, m2: Masses [kg]
            r: Distance [m]

        Returns:
            Force [N]
        """
        return self.G * m1 * m2 / (r * r)

    def schwarzschild_radius(self, mass: float) -> float:
        """
        Schwarzschild radius of a mass.

        r_s = 2GM/c²

        Args:
            mass: Mass [kg]

        Returns:
            Schwarzschild radius [m]
        """
        return 2 * self.G * mass / (self.c * self.c)

    def summary(self) -> str:
        """Human-readable summary of key constants."""
        return f"""
Physical Constants Summary
==========================
Speed of light:         c = {self.c:.8e} m/s
Gravitational constant: G = {self.G:.5e} m³/(kg·s²)
Planck constant:        ℏ = {self.hbar:.8e} J·s
Boltzmann constant:     k_B = {self.k_B:.7e} J/K
Elementary charge:      e = {self.e:.9e} C

Fine Structure Constant:
  α = {self.alpha:.10f}
  1/α = {self.inverse_alpha:.4f}

Particle Masses [GeV/c²]:
  Electron: {self.m_e:.6f}
  Proton:   {self.m_p:.6f}
  W boson:  {self.m_W:.3f}
  Z boson:  {self.m_Z:.4f}
  Higgs:    {self.m_H:.2f}

Planck Units:
  M_Pl = {self.m_planck:.5e} GeV
  l_Pl = {self.l_planck:.6e} m
  t_Pl = {self.t_planck:.6e} s
"""


# Singleton instance for convenience
PHYSICAL_CONSTANTS = PhysicalConstants()

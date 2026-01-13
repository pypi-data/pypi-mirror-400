"""
Cosmological Constants and Universe Evolution Stages
====================================================

Cosmological parameters from Planck 2018 and other surveys,
plus universe evolution stages for coherence modeling.
"""

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np


@dataclass
class CosmologicalConstants:
    """
    Cosmological parameters and holographic physics constants.

    Contains measured values from Planck 2018, WMAP, and other surveys,
    as well as derived quantities for coherence and holographic analysis.

    Examples:
    ---------
    >>> from sim.constants import CosmologicalConstants
    >>> cosmo = CosmologicalConstants()
    >>> print(f"Hubble constant: H₀ = {cosmo.H0:.2f} km/s/Mpc")
    Hubble constant: H₀ = 67.36 km/s/Mpc
    >>> print(f"k/α ≈ {cosmo.k_over_alpha:.1f}")
    k/α ≈ 66.3
    """

    # ==========================================================================
    # Hubble Parameter
    # ==========================================================================

    # Hubble constant [km/s/Mpc] (Planck 2018)
    H0: float = 67.36
    # Uncertainty
    H0_error: float = 0.54

    # Hubble constant [s⁻¹]
    @property
    def H0_si(self) -> float:
        """H₀ in SI units [s⁻¹]"""
        return self.H0 * 1000 / 3.0856775814913673e22  # km/s/Mpc to s⁻¹

    # ==========================================================================
    # Density Parameters (Planck 2018)
    # ==========================================================================

    # Total matter density Ω_m
    Omega_m: float = 0.315
    Omega_m_error: float = 0.007

    # Baryonic matter density Ω_b
    Omega_b: float = 0.0493
    Omega_b_error: float = 0.0006

    # Dark matter density Ω_c = Ω_m - Ω_b
    @property
    def Omega_c(self) -> float:
        """Cold dark matter density"""
        return self.Omega_m - self.Omega_b

    # Dark energy density Ω_Λ
    Omega_lambda: float = 0.685
    Omega_lambda_error: float = 0.007

    # Radiation density Ω_r (including neutrinos)
    Omega_r: float = 9.236e-5

    # Curvature density Ω_k (approximately flat universe)
    Omega_k: float = 0.001
    Omega_k_error: float = 0.002

    # ==========================================================================
    # Primordial Perturbations (Planck 2018)
    # ==========================================================================

    # Scalar perturbation amplitude A_s at k = 0.05 Mpc⁻¹
    A_s: float = 2.100e-9
    A_s_error: float = 0.030e-9

    # Scalar spectral index n_s
    n_s: float = 0.9649
    n_s_error: float = 0.0042

    # Tensor-to-scalar ratio r (upper bound)
    r: float = 0.056  # 95% CL upper limit

    # ==========================================================================
    # Structure Formation
    # ==========================================================================

    # σ₈ - amplitude of matter fluctuations at 8 h⁻¹ Mpc
    sigma_8: float = 0.811
    sigma_8_error: float = 0.006

    # Optical depth to reionization τ
    tau: float = 0.054
    tau_error: float = 0.007

    # ==========================================================================
    # CMB Parameters
    # ==========================================================================

    # CMB temperature today [K]
    T_CMB: float = 2.7255
    T_CMB_error: float = 0.0006

    # CMB temperature in GeV
    @property
    def T_CMB_GeV(self) -> float:
        """CMB temperature in GeV"""
        return self.T_CMB * 8.617333262e-14

    # Redshift of recombination
    z_rec: float = 1089.80

    # Redshift of matter-radiation equality
    z_eq: float = 3387

    # ==========================================================================
    # Baryon-to-Photon Ratio
    # ==========================================================================

    # η = n_b/n_γ
    eta: float = 6.12e-10
    eta_error: float = 0.04e-10

    # ==========================================================================
    # Universe Age and Size
    # ==========================================================================

    # Age of universe [Gyr]
    t_universe: float = 13.787
    t_universe_error: float = 0.020

    # Age of universe [s]
    @property
    def t_universe_s(self) -> float:
        """Age of universe in seconds"""
        return self.t_universe * 1e9 * 365.25 * 24 * 3600

    # ==========================================================================
    # Fine Structure Constant (for holographic relations)
    # ==========================================================================

    alpha: float = 0.0072973525693
    alpha_error: float = 0.0000000011

    @property
    def inverse_alpha(self) -> float:
        """1/α ≈ 137"""
        return 1.0 / self.alpha

    # ==========================================================================
    # Holographic Parameter k
    # ==========================================================================

    # Observed holographic information ratio k = E_info/E_total
    k_observed: float = 0.483678
    k_error: float = 0.007725

    @property
    def k_over_alpha(self) -> float:
        """k/α ≈ 66 (key empirical relation)"""
        return self.k_observed / self.alpha

    # ==========================================================================
    # Boson Masses [GeV] (for alternative k formulas)
    # ==========================================================================

    m_Z: float = 91.1876
    m_W: float = 80.379

    @property
    def delta_m(self) -> float:
        """m_Z - m_W [GeV]"""
        return self.m_Z - self.m_W

    # ==========================================================================
    # k Formula Methods
    # ==========================================================================

    def k_formula_holographic(self) -> float:
        """
        Holographic formula for k.

        k = π × α × ln(1/A_s) / n_s

        This formula is fully dimensionless.

        Returns:
            Theoretical k value
        """
        return np.pi * self.alpha * np.log(1 / self.A_s) / self.n_s

    def k_formula_boson_mass(self, M_ref: float = 1.0) -> float:
        """
        k formula using boson mass difference.

        k = (49/8) × α × Δm / M_ref

        Args:
            M_ref: Reference mass scale [GeV]. Default 1 GeV.

        Returns:
            Theoretical k value
        """
        return (49 / 8) * self.alpha * self.delta_m / M_ref

    def k_formula_entropic(self) -> float:
        """
        Entropic formula for k.

        k = 66 × α

        Returns:
            k value from entropic formula
        """
        return 66.0 * self.alpha

    def k_formula_dark_energy(self) -> float:
        """
        k formula with dark energy correction.

        k = k_holographic × (1 - Ω_Λ)

        Returns:
            k value with dark energy correction
        """
        return self.k_formula_holographic() * (1 - self.Omega_lambda)

    def k_formula_information(self) -> float:
        """
        Information-theoretic formula for k.

        k = α × π × ln(10) / n_s

        Returns:
            k value from information formula
        """
        S_planck = np.pi * np.log(10)  # Planck entropy
        return self.alpha * S_planck / self.n_s

    def effective_alpha(self, scale: float = 100) -> float:
        """
        Effective α parameter for coherence model.

        α_eff = k / (scale × α)

        Args:
            scale: Scale factor (default 100)

        Returns:
            Effective α ≈ 0.66 for scale=100
        """
        return self.k_observed / (scale * self.alpha)

    def k_error_percent(self, formula: str = "holographic") -> float:
        """
        Relative error of k formula compared to observed value.

        Args:
            formula: One of "holographic", "boson_mass", "entropic",
                    "dark_energy", "information"

        Returns:
            Error in percent
        """
        formulas = {
            "holographic": self.k_formula_holographic,
            "boson_mass": self.k_formula_boson_mass,
            "entropic": self.k_formula_entropic,
            "dark_energy": self.k_formula_dark_energy,
            "information": self.k_formula_information,
        }
        k_theo = formulas.get(formula, self.k_formula_holographic)()
        return abs(self.k_observed - k_theo) / self.k_observed * 100

    # ==========================================================================
    # Uncertainties Dictionary
    # ==========================================================================

    uncertainties: Dict[str, float] = field(
        default_factory=lambda: {
            "H0": 0.54,
            "Omega_m": 0.007,
            "Omega_b": 0.0006,
            "Omega_lambda": 0.007,
            "A_s": 0.030e-9,
            "n_s": 0.0042,
            "sigma_8": 0.006,
            "tau": 0.007,
            "T_CMB": 0.0006,
            "t_universe": 0.020,
            "alpha": 0.0000000011,
            "k": 0.007725,
        }
    )

    def summary(self) -> str:
        """Human-readable summary of cosmological parameters."""
        return f"""
Cosmological Constants (Planck 2018)
====================================
Hubble Constant:
  H₀ = {self.H0:.2f} ± {self.H0_error:.2f} km/s/Mpc

Density Parameters:
  Ω_m = {self.Omega_m:.4f} (total matter)
  Ω_b = {self.Omega_b:.4f} (baryons)
  Ω_c = {self.Omega_c:.4f} (cold dark matter)
  Ω_Λ = {self.Omega_lambda:.4f} (dark energy)
  Ω_k = {self.Omega_k:.4f} (curvature)

Primordial Perturbations:
  A_s = {self.A_s:.3e} (scalar amplitude)
  n_s = {self.n_s:.4f} (spectral index)
  r < {self.r:.3f} (tensor-to-scalar ratio)

Structure Formation:
  σ₈ = {self.sigma_8:.3f}
  τ = {self.tau:.3f} (reionization optical depth)

CMB:
  T_CMB = {self.T_CMB:.4f} K
  z_rec = {self.z_rec:.1f} (recombination redshift)

Universe:
  Age = {self.t_universe:.3f} Gyr
  η = {self.eta:.2e} (baryon-to-photon ratio)

Holographic Relations:
  α = {self.alpha:.10f}
  1/α = {self.inverse_alpha:.4f}
  k = {self.k_observed:.6f}
  k/α = {self.k_over_alpha:.2f}

k Formulas Comparison:
  k (observed)    = {self.k_observed:.6f}
  k (holographic) = {self.k_formula_holographic():.6f} ({self.k_error_percent('holographic'):.1f}%)
  k (entropic)    = {self.k_formula_entropic():.6f} ({self.k_error_percent('entropic'):.1f}%)
  k (boson mass)  = {self.k_formula_boson_mass():.6f} ({self.k_error_percent('boson_mass'):.1f}%)
"""


# ==========================================================================
# Universe Evolution Stages
# ==========================================================================

UNIVERSE_STAGES: List[str] = [
    "Planck Epoch",  # 0: 0 - 10⁻⁴³ s
    "Inflation",  # 1: 10⁻³⁶ - 10⁻³² s
    "Quark-Gluon Plasma",  # 2: 10⁻¹² - 10⁻⁶ s
    "Nucleosynthesis",  # 3: 1 s - 3 min
    "Recombination",  # 4: ~380,000 years
    "Dark Ages",  # 5: 380,000 - 150M years
    "First Stars",  # 6: ~150-400M years
    "Galaxies",  # 7: ~400M - 1B years
    "Solar System",  # 8: ~9B years
    "Life",  # 9: ~10B years
    "Intelligence",  # 10: ~13.7B years
    "Now",  # 11: Present
]

UNIVERSE_STAGES_SHORT: List[str] = [
    "Planck",
    "Inflation",
    "QGP",
    "Nucleo",
    "Recomb",
    "Dark",
    "Stars",
    "Galaxies",
    "Solar",
    "Life",
    "Mind",
    "Now",
]

# Russian versions for backwards compatibility
UNIVERSE_STAGES_RU: List[str] = [
    "Планковская эпоха",
    "Инфляция",
    "Кварк-глюонная плазма",
    "Нуклеосинтез",
    "Рекомбинация",
    "Тёмные века",
    "Первые звёзды",
    "Галактики",
    "Солнечная система",
    "Жизнь",
    "Разум",
    "Сейчас",
]

# Hypothetical future evolution stages
FUTURE_STAGES: Dict[int, str] = {
    13: "Technosphere",
    14: "Cybersphere",
    15: "Noosphere",
    16: "Planetary Mind",
    17: "Solar Mind",
    18: "Galactic Mind",
    19: "Intergalactic Network",
    20: "Universal Mind",
    21: "Multiversal Links",
    22: "Transcendence",
    23: "Absolute Coherence",
    24: "Omega Point",
}

# Timeline of universe stages (approximate times)
UNIVERSE_TIMELINE: Dict[int, Dict[str, float]] = {
    0: {"t_start": 0, "t_end": 1e-43, "T_GeV": 1e19},
    1: {"t_start": 1e-36, "t_end": 1e-32, "T_GeV": 1e15},
    2: {"t_start": 1e-12, "t_end": 1e-6, "T_GeV": 0.2},
    3: {"t_start": 1, "t_end": 180, "T_GeV": 1e-3},
    4: {"t_start": 1.2e13, "t_end": 1.2e13, "T_GeV": 3e-13},
    5: {"t_start": 1.2e13, "t_end": 5e15, "T_GeV": 1e-13},
    6: {"t_start": 5e15, "t_end": 1.3e16, "T_GeV": 1e-14},
    7: {"t_start": 1.3e16, "t_end": 3e16, "T_GeV": 1e-14},
    8: {"t_start": 2.8e17, "t_end": 2.8e17, "T_GeV": 3e-14},
    9: {"t_start": 3.2e17, "t_end": 3.2e17, "T_GeV": 3e-14},
    10: {"t_start": 4.3e17, "t_end": 4.3e17, "T_GeV": 3e-14},
    11: {"t_start": 4.35e17, "t_end": 4.35e17, "T_GeV": 2.35e-13},
}


# Singleton instance for convenience
COSMOLOGICAL_CONSTANTS = CosmologicalConstants()

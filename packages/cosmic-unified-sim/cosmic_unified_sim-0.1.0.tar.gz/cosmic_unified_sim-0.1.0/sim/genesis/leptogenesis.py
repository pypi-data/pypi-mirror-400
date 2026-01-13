"""
Leptogenesis Model
==================

Baryogenesis through leptogenesis mechanism.
Heavy neutrino decays with CP violation.
"""

from typing import Dict, Tuple

import numpy as np
from scipy.integrate import solve_ivp


class LeptogenesisModel:
    """
    Leptogenesis via heavy right-handed neutrino decay.

    N → l + H (lepton + Higgs)
    N → l̄ + H̄ (antilepton + anti-Higgs)

    CP asymmetry ε leads to lepton asymmetry,
    converted to baryon asymmetry via sphalerons.

    Examples:
    ---------
    >>> from sim.genesis import LeptogenesisModel
    >>> model = LeptogenesisModel(M=1e10, Yukawa=1e-6, CP_violation=1e-6)
    >>> result = model.solve_leptogenesis()
    >>> print(f"Final baryon asymmetry: {result['eta_B']:.2e}")
    """

    def __init__(
        self,
        M: float = 1e10,  # GeV - heavy neutrino mass
        Yukawa: float = 1e-6,  # Yukawa coupling
        CP_violation: float = 1e-6,  # CP asymmetry ε
        g_star: float = 106.75,  # Effective degrees of freedom
    ):
        """
        Initialize leptogenesis model.

        Args:
            M: Heavy neutrino mass in GeV
            Yukawa: Yukawa coupling strength
            CP_violation: CP asymmetry parameter ε
            g_star: Effective relativistic degrees of freedom
        """
        self.M = M
        self.y = Yukawa
        self.epsilon = CP_violation
        self.g_star = g_star

        # Derived quantities
        self.Gamma = self._decay_width()
        self.M_Pl = 1.22e19  # Planck mass in GeV

    def _decay_width(self) -> float:
        """Calculate heavy neutrino decay width."""
        return self.y**2 * self.M / (8 * np.pi)

    def _equilibrium_density(self, z: float) -> float:
        """
        Equilibrium density of heavy neutrinos.

        n_eq/s ≈ (45/(2π⁴g*)) × z² × K_2(z)

        Args:
            z: M/T ratio

        Returns:
            Equilibrium density ratio
        """
        if z < 0.1:
            return 0.75  # Relativistic limit
        elif z > 10:
            return np.sqrt(np.pi / 2) * z**1.5 * np.exp(-z)
        else:
            # Interpolation
            return 0.75 * np.exp(-z)

    def _washout_rate(self, z: float) -> float:
        """
        Washout rate from inverse decays.

        Args:
            z: M/T ratio

        Returns:
            Washout parameter W
        """
        K = self.Gamma * self.M_Pl / (1.66 * np.sqrt(self.g_star) * self.M**2)
        return K * z * self._equilibrium_density(z)

    def boltzmann_equations(self, z: float, Y: np.ndarray) -> np.ndarray:
        """
        Boltzmann equations for leptogenesis.

        dY_N/dz = -(D + S)(Y_N - Y_N^eq)
        dY_L/dz = ε × D × (Y_N - Y_N^eq) - W × Y_L

        Args:
            z: M/T ratio
            Y: State vector [Y_N, Y_L]

        Returns:
            Derivatives [dY_N/dz, dY_L/dz]
        """
        Y_N, Y_L = Y
        Y_N_eq = self._equilibrium_density(z)

        # Decay parameter
        K = self.Gamma * self.M_Pl / (1.66 * np.sqrt(self.g_star) * self.M**2)
        D = K * z * Y_N_eq

        # Washout
        W = self._washout_rate(z)

        dY_N = -D * (Y_N - Y_N_eq) / Y_N_eq if Y_N_eq > 0 else 0
        dY_L = self.epsilon * D * (Y_N - Y_N_eq) / Y_N_eq - W * Y_L if Y_N_eq > 0 else 0

        return np.array([dY_N, dY_L])

    def solve_leptogenesis(
        self, z_span: Tuple[float, float] = (0.1, 100), n_points: int = 1000
    ) -> Dict:
        """
        Solve Boltzmann equations for leptogenesis.

        Args:
            z_span: Range of z = M/T
            n_points: Number of output points

        Returns:
            Dict with z, Y_N, Y_L, and final asymmetry
        """
        # Initial conditions: equilibrium N density, zero L asymmetry
        Y0 = [self._equilibrium_density(z_span[0]), 0.0]

        z_eval = np.linspace(z_span[0], z_span[1], n_points)

        sol = solve_ivp(
            self.boltzmann_equations, z_span, Y0, t_eval=z_eval, method="RK45", rtol=1e-8
        )

        Y_N = sol.y[0]
        Y_L = sol.y[1]

        # Convert lepton to baryon asymmetry via sphalerons
        # η_B = (28/79) × Y_L (for SM)
        sphaleron_factor = 28 / 79
        Y_B = sphaleron_factor * Y_L[-1]

        # Convert to baryon-to-photon ratio
        # η = n_B/n_γ ≈ 7.04 × Y_B
        eta_B = 7.04 * Y_B

        return {
            "z": sol.t,
            "Y_N": Y_N,
            "Y_L": Y_L,
            "Y_B_final": Y_B,
            "eta_B": eta_B,
            "eta_observed": 6.1e-10,
            "success": sol.success,
        }

    def scan_parameter_space(
        self,
        M_range: Tuple[float, float] = (1e8, 1e14),
        epsilon_range: Tuple[float, float] = (1e-8, 1e-4),
        n_points: int = 20,
    ) -> Dict:
        """
        Scan parameter space for successful leptogenesis.

        Args:
            M_range: Mass range in GeV
            epsilon_range: CP violation range
            n_points: Points per dimension

        Returns:
            Dict with parameter scan results
        """
        M_values = np.logspace(np.log10(M_range[0]), np.log10(M_range[1]), n_points)
        eps_values = np.logspace(np.log10(epsilon_range[0]), np.log10(epsilon_range[1]), n_points)

        results = np.zeros((n_points, n_points))

        original_M = self.M
        original_eps = self.epsilon

        for i, M in enumerate(M_values):
            for j, eps in enumerate(eps_values):
                self.M = M
                self.epsilon = eps
                self.Gamma = self._decay_width()

                try:
                    result = self.solve_leptogenesis()
                    results[i, j] = result["eta_B"]
                except Exception:
                    results[i, j] = 0.0

        # Restore original values
        self.M = original_M
        self.epsilon = original_eps
        self.Gamma = self._decay_width()

        return {
            "M": M_values,
            "epsilon": eps_values,
            "eta_B": results,
        }

"""
Parametric Resonance
====================

Post-inflation reheating via parametric resonance.
Based on Mathieu equation instability.
"""

from typing import Dict, Tuple

import numpy as np
from scipy.integrate import solve_ivp


class ParametricResonance:
    """
    Parametric resonance model for inflaton decay.

    After inflation, the inflaton field oscillates and decays
    to matter through parametric resonance instabilities.

    Mathieu equation: ẍ + (a - 2q cos(2t))x = 0

    Examples:
    ---------
    >>> from sim.genesis import ParametricResonance
    >>> pr = ParametricResonance(inflaton_mass=1e13, coupling=1e-7)
    >>> results = pr.simulate_resonance_bands()
    >>> rate = pr.particle_production_rate(phi_amplitude=1e16, k=1.0)
    """

    def __init__(
        self,
        inflaton_mass: float = 1e13,  # GeV
        coupling: float = 1e-7,  # dimensionless
        expansion_rate: float = 1e-5,  # GeV
    ):
        """
        Initialize parametric resonance model.

        Args:
            inflaton_mass: Inflaton mass in GeV
            coupling: Coupling to matter fields
            expansion_rate: Hubble parameter (damping)
        """
        self.m_phi = inflaton_mass
        self.g = coupling
        self.H = expansion_rate

    def mathieu_parameters(self, phi_amplitude: float, k: float) -> Tuple[float, float]:
        """
        Calculate Mathieu equation parameters a and q.

        a = (m² + k²) / m_φ²
        q = g² × φ₀² / (4 × m_φ²)

        Args:
            phi_amplitude: Inflaton amplitude
            k: Momentum of produced particles

        Returns:
            Tuple (a, q)
        """
        a = (self.m_phi**2 + k**2) / self.m_phi**2
        q = self.g**2 * phi_amplitude**2 / (4 * self.m_phi**2)
        return a, q

    def instability_bands(self, q_max: float = 10.0, n_points: int = 100) -> Dict[str, np.ndarray]:
        """
        Calculate instability bands of Mathieu equation.

        Args:
            q_max: Maximum q value
            n_points: Number of points

        Returns:
            Dict with q values and instability regions
        """
        q_values = np.linspace(0, q_max, n_points)

        # Approximate instability bands for first few resonances
        # Band n is centered at a ≈ n² with width ∝ q^n
        bands = []

        for n in range(1, 5):
            a_center = n**2
            width = 2 * q_values**n / (2 ** (2 * n - 1) * np.math.factorial(n - 1) ** 2)
            bands.append(
                {
                    "n": n,
                    "a_center": a_center,
                    "a_low": a_center - width,
                    "a_high": a_center + width,
                }
            )

        return {
            "q": q_values,
            "bands": bands,
        }

    def growth_exponent(self, a: float, q: float) -> float:
        """
        Calculate Floquet exponent (growth rate).

        In instability bands: n_k ∝ exp(2μ_k t)

        Args:
            a: Mathieu parameter a
            q: Mathieu parameter q

        Returns:
            Growth exponent μ
        """
        # Approximate formula for first instability band
        if abs(a - 1) < 2 * q:  # In first band
            return np.sqrt(q**2 - (a - 1) ** 2 / 4)
        return 0.0

    def particle_production_rate(self, phi_amplitude: float, k: float) -> float:
        """
        Calculate particle production rate.

        Args:
            phi_amplitude: Inflaton amplitude
            k: Particle momentum

        Returns:
            Production rate dn/dt
        """
        a, q = self.mathieu_parameters(phi_amplitude, k)
        mu = self.growth_exponent(a, q)

        # Rate with Hubble damping
        effective_rate = max(0, 2 * mu * self.m_phi - 3 * self.H)

        return effective_rate

    def simulate_resonance_bands(
        self, phi_amplitude: float = 1e16, k_max: float = 10.0, n_k: int = 100
    ) -> Dict[str, np.ndarray]:
        """
        Simulate resonance for range of momenta.

        Args:
            phi_amplitude: Inflaton amplitude
            k_max: Maximum momentum (in units of m_φ)
            n_k: Number of momentum points

        Returns:
            Dict with momenta, parameters, and growth rates
        """
        k_values = np.linspace(0.1, k_max, n_k) * self.m_phi

        a_values = np.zeros(n_k)
        q_values = np.zeros(n_k)
        mu_values = np.zeros(n_k)
        rate_values = np.zeros(n_k)

        for i, k in enumerate(k_values):
            a, q = self.mathieu_parameters(phi_amplitude, k)
            a_values[i] = a
            q_values[i] = q
            mu_values[i] = self.growth_exponent(a, q)
            rate_values[i] = self.particle_production_rate(phi_amplitude, k)

        return {
            "k": k_values,
            "a": a_values,
            "q": q_values,
            "mu": mu_values,
            "rate": rate_values,
        }

    def evolve_occupation(
        self, t_span: Tuple[float, float], phi_amplitude: float, k: float, n0: float = 0.5
    ) -> Dict[str, np.ndarray]:
        """
        Evolve particle occupation number.

        Args:
            t_span: Time interval (in units of m_φ⁻¹)
            phi_amplitude: Inflaton amplitude
            k: Particle momentum
            n0: Initial occupation

        Returns:
            Dict with time and occupation arrays
        """
        a, q = self.mathieu_parameters(phi_amplitude, k)

        def derivatives(t, y):
            # Simplified Mathieu dynamics
            x, v = y
            # Damped oscillator with parametric driving
            ax = -(a - 2 * q * np.cos(2 * t)) * x - 2 * self.H / self.m_phi * v
            return [v, ax]

        t_eval = np.linspace(t_span[0], t_span[1], 1000)
        sol = solve_ivp(derivatives, t_span, [np.sqrt(n0), 0], t_eval=t_eval, method="RK45")

        # Occupation number from amplitude
        n_k = sol.y[0] ** 2 + sol.y[1] ** 2

        return {
            "time": sol.t,
            "n_k": n_k,
            "amplitude": sol.y[0],
            "velocity": sol.y[1],
        }

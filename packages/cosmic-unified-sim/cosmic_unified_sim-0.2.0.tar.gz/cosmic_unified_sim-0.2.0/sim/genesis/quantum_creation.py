"""
Quantum Particle Creation
=========================

Particle creation from vacuum fluctuations in expanding spacetime.
Based on Bogoliubov transformation formalism.
"""

from typing import Dict, Tuple

import numpy as np
from scipy.integrate import solve_ivp


class QuantumCreation:
    """
    Quantum particle creation in expanding universe.

    Uses Bogoliubov coefficients to calculate particle production
    from vacuum fluctuations in time-dependent spacetime.

    Examples:
    ---------
    >>> from sim.genesis import QuantumCreation
    >>> qc = QuantumCreation(mass=0.1, expansion_rate=0.01)
    >>> results = qc.analyze_particle_creation()
    >>> print(f"Total particles: {results['n_total']:.2e}")
    """

    def __init__(
        self,
        mass: float = 0.1,  # Mass in units of expansion rate
        expansion_rate: float = 0.01,  # Hubble parameter
        scale_factor_init: float = 1.0,
    ):
        """
        Initialize quantum creation model.

        Args:
            mass: Particle mass
            expansion_rate: Hubble parameter H
            scale_factor_init: Initial scale factor
        """
        self.m = mass
        self.H = expansion_rate
        self.a0 = scale_factor_init

    def scale_factor(self, t: float) -> float:
        """Scale factor a(t) = a₀ × exp(Ht)."""
        return self.a0 * np.exp(self.H * t)

    def effective_frequency(self, k: float, t: float) -> float:
        """
        Effective frequency ω_k = √(k²/a² + m²).

        Args:
            k: Comoving momentum
            t: Time

        Returns:
            Effective frequency
        """
        a = self.scale_factor(t)
        return np.sqrt(k**2 / a**2 + self.m**2)

    def mode_equation(self, t: float, y: np.ndarray, k: float) -> np.ndarray:
        """
        Mode equation for quantum field.

        v̈_k + (ω_k² - ä/a) v_k = 0

        Args:
            t: Time
            y: State [v, v̇]
            k: Comoving momentum

        Returns:
            Derivatives [v̇, v̈]
        """
        v, vdot = y
        omega_k = self.effective_frequency(k, t)

        # ä/a = H² for de Sitter
        curvature = self.H**2

        vddot = -(omega_k**2 - curvature) * v

        return np.array([vdot, vddot])

    def bogoliubov_coefficients(
        self, k: float, t_span: Tuple[float, float] = (0, 10)
    ) -> Tuple[complex, complex]:
        """
        Calculate Bogoliubov coefficients α_k and β_k.

        The number of created particles is n_k = |β_k|²

        Args:
            k: Comoving momentum
            t_span: Time interval

        Returns:
            Tuple (alpha, beta)
        """
        # Initial conditions: positive frequency mode
        omega_i = self.effective_frequency(k, t_span[0])
        v0 = 1.0 / np.sqrt(2 * omega_i)
        vdot0 = -1j * omega_i * v0

        # Solve mode equation (real and imaginary parts)
        def real_mode(t, y):
            dy = self.mode_equation(t, y, k)
            return dy.real

        sol_re = solve_ivp(
            real_mode, t_span, [v0.real, vdot0.real], method="RK45", dense_output=True
        )

        sol_im = solve_ivp(
            real_mode, t_span, [v0.imag, vdot0.imag], method="RK45", dense_output=True
        )

        # Final mode function
        v_f = complex(sol_re.y[0, -1], sol_im.y[0, -1])
        vdot_f = complex(sol_re.y[1, -1], sol_im.y[1, -1])

        # Extract Bogoliubov coefficients
        omega_f = self.effective_frequency(k, t_span[1])

        alpha = np.sqrt(omega_f / 2) * v_f + 1j * vdot_f / np.sqrt(2 * omega_f)
        beta = np.sqrt(omega_f / 2) * v_f - 1j * vdot_f / np.sqrt(2 * omega_f)

        return alpha, beta

    def particle_spectrum(
        self,
        k_range: Tuple[float, float] = (0.1, 10),
        n_k: int = 50,
        t_span: Tuple[float, float] = (0, 10),
    ) -> Dict:
        """
        Calculate particle creation spectrum.

        Args:
            k_range: Momentum range
            n_k: Number of momentum points
            t_span: Time interval

        Returns:
            Dict with momenta and occupation numbers
        """
        k_values = np.linspace(k_range[0], k_range[1], n_k)
        n_values = np.zeros(n_k)

        for i, k in enumerate(k_values):
            try:
                alpha, beta = self.bogoliubov_coefficients(k, t_span)
                n_values[i] = np.abs(beta) ** 2
            except Exception:
                n_values[i] = 0.0

        return {
            "k": k_values,
            "n_k": n_values,
            "n_total": np.sum(n_values),
        }

    def analyze_particle_creation(
        self,
        t_span: Tuple[float, float] = (0, 20),
        k_range: Tuple[float, float] = (0.1, 10),
        n_k: int = 30,
    ) -> Dict:
        """
        Full analysis of particle creation.

        Args:
            t_span: Time interval
            k_range: Momentum range
            n_k: Number of momentum points

        Returns:
            Dict with spectrum, totals, and energy
        """
        # Calculate spectrum
        spectrum = self.particle_spectrum(k_range, n_k, t_span)

        # Energy density
        k_values = spectrum["k"]
        n_values = spectrum["n_k"]

        omega_f = np.array([self.effective_frequency(k, t_span[1]) for k in k_values])

        energy_density = np.sum(omega_f * n_values)

        # Characteristic momentum (peak of spectrum)
        k_peak = k_values[np.argmax(n_values)] if np.any(n_values > 0) else 0

        return {
            "k": k_values,
            "n_k": n_values,
            "n_total": spectrum["n_total"],
            "energy_density": energy_density,
            "k_peak": k_peak,
            "t_final": t_span[1],
            "H": self.H,
            "m": self.m,
        }

    def gravitational_particle_creation(self, m: float, H_inf: float) -> float:
        """
        Estimate particle creation during inflation.

        For m << H: n ∝ H³
        For m >> H: n ∝ exp(-πm/H)

        Args:
            m: Particle mass
            H_inf: Hubble rate during inflation

        Returns:
            Estimated number density
        """
        if m < H_inf:
            # Light particles: copious production
            return (H_inf / (2 * np.pi)) ** 3
        else:
            # Heavy particles: suppressed
            return (H_inf / (2 * np.pi)) ** 3 * np.exp(-np.pi * m / H_inf)

"""
Coherence Models
================

Mathematical models for universe coherence (complexity) evolution.
"""

from typing import Dict, Optional, Tuple

import numpy as np
from scipy.optimize import brentq

from sim.constants import CosmologicalConstants


class CoherenceModel:
    """
    Recurrence model for coherence growth.

    Core formula:
        K(n) = K₀ + α × Σ K(k)/(N-k)

    where α can be derived from fundamental constants.

    Examples:
    ---------
    >>> from sim.coherence import CoherenceModel
    >>> model = CoherenceModel()
    >>> K, C, Total = model.evolve(N=12, alpha=0.66)
    >>> print(f"Coherence growth: {K[-1]/K[0]:.2f}x")
    """

    def __init__(self, constants: Optional[CosmologicalConstants] = None):
        """
        Initialize model.

        Args:
            constants: Cosmological constants (uses defaults if None)
        """
        self.constants = constants or CosmologicalConstants()

    def evolve(
        self, N: int = 12, K0: float = 1.0, alpha: Optional[float] = None, gamma: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Evolve coherence through N stages.

        Args:
            N: Number of evolution stages
            K0: Initial coherence
            alpha: Deposition parameter (computed from constants if None)
            gamma: Realized coherence fraction (0 < γ < 1)

        Returns:
            K: Potential coherence at each stage
            C: Realized coherence (C = γ × K)
            Total: Cumulative coherence
        """
        if alpha is None:
            alpha = self.constants.effective_alpha()

        alpha = np.clip(alpha, 0.01, 0.99)

        K = np.zeros(N)
        C = np.zeros(N)
        Total = np.zeros(N)

        K[0] = K0

        # Recurrence relation
        for n in range(1, N):
            deposited_sum = sum(K[k] / (N - k) for k in range(n))
            K[n] = K0 + alpha * deposited_sum

        # Realized coherence
        for n in range(N):
            C[n] = gamma * K[n]
            Total[n] = np.sum(C[: n + 1])

        return K, C, Total

    def evolve_corrected(
        self, N: int = 12, K0: float = 1.0, alpha: Optional[float] = None, gamma: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Corrected model with stage normalization.

        Formula: K(n) = K₀ × (1 + α × Σ K(k)/max(1, N-k-1) / n)
        """
        if alpha is None:
            alpha = self.constants.effective_alpha()

        alpha = np.clip(alpha, 0.01, 0.99)

        K = np.zeros(N)
        C = np.zeros(N)
        Total = np.zeros(N)

        K[0] = K0

        for n in range(1, N):
            sum_term = 0
            for i in range(n):
                denominator = max(1, N - i - 1)
                sum_term += K[i] / denominator
            K[n] = K0 * (1 + alpha * sum_term / n)

        for n in range(N):
            C[n] = gamma * K[n]
            Total[n] = np.sum(C[: n + 1])

        return K, C, Total

    def evolve_quantum(
        self, N: int = 12, K0: float = 1.0, alpha: Optional[float] = None, gamma: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Quantum model with amplitude interference.
        """
        if alpha is None:
            alpha = self.constants.effective_alpha()

        alpha = np.clip(alpha, 0.01, 0.99)

        K = np.zeros(N)
        C = np.zeros(N)
        Total = np.zeros(N)

        K[0] = K0

        for n in range(1, N):
            amplitudes = []
            for i in range(n):
                amp = np.sqrt(K[i]) * np.exp(-((n - i) ** 2) / (2 * alpha**2))
                amplitudes.append(amp)

            total_amp = np.sum(np.array(amplitudes))
            K[n] = K0 + alpha * np.abs(total_amp) ** 2

        for n in range(N):
            C[n] = gamma * K[n]
            Total[n] = np.sum(C[: n + 1])

        return K, C, Total

    def evolve_with_dark_energy(
        self, N: int = 12, K0: float = 1.0, alpha: Optional[float] = None, gamma: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Model with dark energy suppression at late stages.
        """
        if alpha is None:
            alpha = self.constants.effective_alpha()

        alpha = np.clip(alpha, 0.01, 0.99)
        lambda_de = self.constants.Omega_lambda

        K = np.zeros(N)
        C = np.zeros(N)
        Total = np.zeros(N)

        K[0] = K0

        for n in range(1, N):
            sum_term = 0
            t_n = n / N

            for i in range(n):
                t_i = i / N
                dt = t_n - t_i
                if dt > 0:
                    de_factor = 1 - lambda_de * (t_i**3)
                    sum_term += K[i] * de_factor / dt

            K[n] = K0 + alpha * sum_term / n

        for n in range(N):
            C[n] = gamma * K[n]
            Total[n] = np.sum(C[: n + 1])

        return K, C, Total

    def find_optimal_alpha(self, target_growth: float, N: int = 12, K0: float = 1.0) -> float:
        """
        Find α for desired coherence growth.

        Args:
            target_growth: Desired K(N)/K(0) ratio
            N: Number of stages
            K0: Initial coherence

        Returns:
            Optimal α value
        """

        def objective(a):
            K, _, _ = self.evolve(N, K0, a)
            return K[-1] / K[0] - target_growth

        try:
            return brentq(objective, 0.01, 0.99)
        except ValueError:
            return 0.5

    def growth_factor(self, alpha: float, N: int = 12) -> float:
        """Calculate growth factor K(N)/K(0)."""
        K, _, _ = self.evolve(N, 1.0, alpha)
        return K[-1] / K[0]

    def information_content(self, K: np.ndarray) -> Dict:
        """
        Calculate information-theoretic properties.

        Args:
            K: Coherence array

        Returns:
            Dict with entropy, efficiency, info_rate, etc.
        """
        p = (K + 1e-10) / np.sum(K + 1e-10)

        entropy = -np.sum(p * np.log2(p))
        max_entropy = np.log2(len(K))
        info_hartley = np.log2(K + 1)
        info_rate = np.gradient(info_hartley)
        efficiency = entropy / max_entropy

        return {
            "entropy": entropy,
            "max_entropy": max_entropy,
            "efficiency": efficiency,
            "info_hartley": info_hartley,
            "info_rate": info_rate,
            "p": p,
        }

    def predict_future(
        self, current_stage: int = 12, total_stages: int = 24, alpha: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict future coherence evolution.

        Args:
            current_stage: Current stage (default 12)
            total_stages: Total stages to predict
            alpha: Deposition parameter

        Returns:
            K_future: Predicted coherence values
            stages: Stage numbers
        """
        if alpha is None:
            alpha = self.constants.effective_alpha()

        K_current, _, _ = self.evolve(current_stage + 1, alpha=alpha)
        K_now = K_current[-1]

        future_stages = total_stages - current_stage
        K_future = np.zeros(future_stages)
        stages = np.arange(current_stage + 1, total_stages + 1)

        for i in range(future_stages):
            t_ratio = (current_stage + i) / total_stages
            K_future[i] = (
                K_now * ((1 - current_stage / total_stages) / max(0.01, 1 - t_ratio)) ** alpha
            )

        return K_future, stages


class DepositionModel:
    """
    Deposition model with accumulation.

    Demonstrates potential accumulation through deposition.
    Analogy to cosmological coherence model.
    """

    def __init__(
        self,
        M0: float = 1.0,
        N: int = 10,
        alpha: float = 0.5,
        gamma: float = 0.3,
        beta: Optional[float] = None,
    ):
        """
        Initialize model.

        Args:
            M0: Initial resource amount
            N: Number of stages
            alpha: Deposition fraction (hidden potential)
            gamma: Realization fraction (used resource)
            beta: Losses (computed as 1 - α - γ if None)
        """
        self.M0 = M0
        self.N = N
        self.alpha = alpha
        self.gamma = gamma

        if beta is None:
            self.beta = 1 - alpha - gamma
        else:
            self.beta = beta
            total = alpha + beta + gamma
            if abs(total - 1) > 1e-10:
                self.alpha /= total
                self.beta /= total
                self.gamma /= total

    def calculate(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate deposition process.

        Returns:
            C: Concentration at each stage
            P: Realized resource at each stage
            m: Cumulative realization
        """
        C = np.zeros(self.N)
        P = np.zeros(self.N)
        m = np.zeros(self.N)

        C0 = self.M0 / self.N
        C[0] = C0

        for n in range(1, self.N):
            deposited_sum = sum(C[k] / (self.N - k) for k in range(n))
            C[n] = C0 + self.alpha * deposited_sum

        for n in range(self.N):
            P[n] = self.gamma * C[n]
            m[n] = np.sum(P[: n + 1])

        return C, P, m

    def efficiency(self) -> float:
        """Consumption efficiency (fraction of initial)."""
        _, _, m = self.calculate()
        return m[-1] / self.M0

    def amplification(self) -> float:
        """Amplification factor C(N)/C(0)."""
        C, _, _ = self.calculate()
        return C[-1] / C[0]


class SymmetryBreaking:
    """
    Spontaneous symmetry breaking model.

    Higgs-like potential: V(φ) = μ² × φ² + λ × φ⁴
    """

    @staticmethod
    def potential(phi: np.ndarray, mu2: float, lam: float = 0.25) -> np.ndarray:
        """
        Calculate potential V(φ).

        Args:
            phi: Field values
            mu2: Parameter μ² (positive = symmetric, negative = broken)
            lam: Self-coupling λ

        Returns:
            Potential values
        """
        return mu2 * phi**2 + lam * phi**4

    @staticmethod
    def phase_transition(
        phi_range: Tuple[float, float] = (-2, 2), n_points: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate potentials for both phases.

        Returns:
            phi: Field values
            V_symmetric: Potential in symmetric phase
            V_broken: Potential with broken symmetry
        """
        phi = np.linspace(phi_range[0], phi_range[1], n_points)
        V_symmetric = SymmetryBreaking.potential(phi, mu2=1.0)
        V_broken = SymmetryBreaking.potential(phi, mu2=-1.0)
        return phi, V_symmetric, V_broken

    @staticmethod
    def vacuum_expectation_value(mu2: float, lam: float = 0.25) -> float:
        """
        Calculate vacuum expectation value (VEV).

        v = √(-μ²/2λ) for μ² < 0

        Args:
            mu2: Parameter μ²
            lam: Self-coupling λ

        Returns:
            VEV (0 if μ² ≥ 0)
        """
        if mu2 >= 0:
            return 0.0
        return np.sqrt(-mu2 / (2 * lam))

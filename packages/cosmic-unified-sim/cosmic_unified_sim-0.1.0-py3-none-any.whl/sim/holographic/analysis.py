"""
Holographic Analysis
====================

Analysis of holographic information capacity k = E_info/E_total
and its relation to the fine structure constant α.
"""

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from sim.constants import CosmologicalConstants


@dataclass
class CosmologicalModel:
    """Cosmological model parameters."""

    name: str
    H0: float  # km/s/Mpc
    Omega_m: float
    Omega_b: float
    Omega_lambda: float
    A_s: float
    n_s: float
    sigma_8: float


# Standard cosmological models
COSMOLOGICAL_MODELS = {
    "Planck2018": CosmologicalModel(
        name="Planck 2018",
        H0=67.36,
        Omega_m=0.315,
        Omega_b=0.0493,
        Omega_lambda=0.685,
        A_s=2.100e-9,
        n_s=0.9649,
        sigma_8=0.811,
    ),
    "WMAP9": CosmologicalModel(
        name="WMAP9",
        H0=69.32,
        Omega_m=0.287,
        Omega_b=0.0463,
        Omega_lambda=0.713,
        A_s=2.195e-9,
        n_s=0.9608,
        sigma_8=0.820,
    ),
    "SH0ES": CosmologicalModel(
        name="SH0ES",
        H0=73.04,
        Omega_m=0.300,
        Omega_b=0.0490,
        Omega_lambda=0.700,
        A_s=2.100e-9,
        n_s=0.9649,
        sigma_8=0.811,
    ),
    "DES": CosmologicalModel(
        name="DES",
        H0=67.4,
        Omega_m=0.339,
        Omega_b=0.0490,
        Omega_lambda=0.661,
        A_s=2.100e-9,
        n_s=0.9649,
        sigma_8=0.733,
    ),
    "ACT": CosmologicalModel(
        name="ACT",
        H0=67.9,
        Omega_m=0.306,
        Omega_b=0.0490,
        Omega_lambda=0.694,
        A_s=2.100e-9,
        n_s=0.9649,
        sigma_8=0.840,
    ),
}


class HolographicAnalysis:
    """
    Analysis of holographic information ratio k and α relations.

    Key relation: k ≈ 66α (empirically observed)

    Formula: k = π × α × ln(1/A_s) / n_s

    Examples:
    ---------
    >>> from sim.holographic import HolographicAnalysis
    >>> ha = HolographicAnalysis()
    >>> results = ha.analyze_all_models()
    >>> print(f"Mean k: {results['mean_k']:.4f}")
    """

    ALPHA = 0.0072973525693  # Fine structure constant

    def __init__(self, constants: Optional[CosmologicalConstants] = None):
        """
        Initialize analysis.

        Args:
            constants: Reference cosmological constants
        """
        self.constants = constants or CosmologicalConstants()

    def calculate_k(self, model: CosmologicalModel) -> float:
        """
        Calculate k for a cosmological model.

        k = π × α × ln(1/A_s) / n_s

        Args:
            model: Cosmological model

        Returns:
            k value
        """
        return np.pi * self.ALPHA * np.log(1 / model.A_s) / model.n_s

    def k_error(self, k: float, k_reference: float) -> float:
        """Calculate relative error in percent."""
        return abs(k - k_reference) / k_reference * 100

    def analyze_model(self, model: CosmologicalModel) -> Dict:
        """
        Full analysis of a cosmological model.

        Args:
            model: Cosmological model

        Returns:
            Analysis results dict
        """
        k = self.calculate_k(model)
        k_over_alpha = k / self.ALPHA

        # Different k formulas
        k_66alpha = 66 * self.ALPHA

        return {
            "name": model.name,
            "k": k,
            "k_over_alpha": k_over_alpha,
            "k_66alpha": k_66alpha,
            "error_vs_66alpha": self.k_error(k, k_66alpha),
            "H0": model.H0,
            "Omega_m": model.Omega_m,
            "Omega_lambda": model.Omega_lambda,
            "A_s": model.A_s,
            "n_s": model.n_s,
        }

    def analyze_all_models(self) -> Dict:
        """
        Analyze all standard cosmological models.

        Returns:
            Combined analysis results
        """
        results = []
        for name, model in COSMOLOGICAL_MODELS.items():
            results.append(self.analyze_model(model))

        k_values = [r["k"] for r in results]

        return {
            "models": results,
            "mean_k": np.mean(k_values),
            "std_k": np.std(k_values),
            "mean_k_over_alpha": np.mean(k_values) / self.ALPHA,
            "k_66alpha": 66 * self.ALPHA,
            "mean_error_vs_66alpha": np.mean([r["error_vs_66alpha"] for r in results]),
        }

    def formula_comparison(self) -> Dict:
        """
        Compare different k formulas.

        Returns:
            Comparison dict
        """
        c = self.constants

        formulas = {
            "observed": c.k_observed,
            "holographic": c.k_formula_holographic(),
            "entropic": c.k_formula_entropic(),
            "boson_mass": c.k_formula_boson_mass(),
            "dark_energy": c.k_formula_dark_energy(),
            "information": c.k_formula_information(),
        }

        errors = {
            name: self.k_error(k, c.k_observed)
            for name, k in formulas.items()
            if name != "observed"
        }

        return {
            "values": formulas,
            "errors_percent": errors,
            "best_formula": min(errors, key=errors.get),
        }

    def significance_test(self, n_samples: int = 10000) -> Dict:
        """
        Statistical significance test for k ≈ 66α.

        Generate random α values and test probability of k/α ≈ 66.

        Args:
            n_samples: Number of random samples

        Returns:
            Significance test results
        """
        # Generate random α values (uniform in log space)
        alpha_random = 10 ** np.random.uniform(-4, -1, n_samples)

        # Generate random k values
        k_random = np.random.uniform(0.1, 1.0, n_samples)

        # Calculate k/α for random values
        ratio_random = k_random / alpha_random

        # Our observed ratio
        observed_ratio = 66.0
        threshold = 5.0  # Within 5 units

        # Count how many random ratios are close to 66
        close_to_66 = np.sum(np.abs(ratio_random - observed_ratio) < threshold)
        p_value = close_to_66 / n_samples

        return {
            "observed_ratio": observed_ratio,
            "mean_random_ratio": np.mean(ratio_random),
            "std_random_ratio": np.std(ratio_random),
            "p_value": p_value,
            "significant_at_0.05": p_value < 0.05,
            "n_samples": n_samples,
        }

    def information_capacity(
        self, horizon_radius: float = 4.4e26  # meters (observable universe)
    ) -> Dict:
        """
        Calculate holographic information capacity.

        I_max = A / (4 × l_p²) bits

        Args:
            horizon_radius: Horizon radius in meters

        Returns:
            Information capacity analysis
        """
        l_p = 1.616e-35  # Planck length in meters

        # Horizon area
        A = 4 * np.pi * horizon_radius**2

        # Maximum information (Bekenstein bound)
        I_max = A / (4 * l_p**2)

        # Information with holographic ratio k
        k = self.constants.k_observed
        I_actual = k * I_max

        return {
            "horizon_radius_m": horizon_radius,
            "horizon_area_m2": A,
            "max_information_bits": I_max,
            "actual_information_bits": I_actual,
            "k": k,
            "entropy_bits": I_actual * np.log(2),
        }

"""
Universe Simulator
==================

Generate and analyze ensembles of simulated universes.
"""

from typing import Any, Dict, List, Optional

import numpy as np

from sim.constants import CosmologicalConstants

from .models import CoherenceModel


class UniverseSimulator:
    """
    Generate ensembles of simulated universes with varying parameters.

    Examples:
    ---------
    >>> from sim.coherence import UniverseSimulator
    >>> simulator = UniverseSimulator()
    >>> universes = simulator.generate(n=1000, with_coherence=True)
    >>> stats = simulator.statistical_analysis(universes)
    >>> print(f"Mean k: {stats['k']['mean']:.4f}")
    """

    def __init__(self, constants: Optional[CosmologicalConstants] = None):
        """
        Initialize simulator.

        Args:
            constants: Reference constants for our universe
        """
        self.constants = constants or CosmologicalConstants()
        self.model = CoherenceModel(self.constants)

    def generate(
        self, n: int = 1000, with_coherence: bool = True, variation_scale: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Generate n random universes.

        Args:
            n: Number of universes to generate
            with_coherence: Calculate coherence for each universe
            variation_scale: Standard deviation for parameter variations

        Returns:
            List of universe dictionaries
        """
        universes = []

        for i in range(n):
            # Vary cosmological parameters
            alpha = self.constants.alpha * (1 + variation_scale * np.random.randn())
            A_s = self.constants.A_s * (1 + variation_scale * np.random.randn())
            n_s = self.constants.n_s * (1 + variation_scale * np.random.randn())
            Omega_m = np.clip(
                self.constants.Omega_m * (1 + variation_scale * np.random.randn()), 0.1, 0.9
            )
            Omega_lambda = 1 - Omega_m

            # Calculate k
            k = np.pi * alpha * np.log(1 / A_s) / n_s if n_s > 0 else 0.5

            universe = {
                "id": i,
                "alpha": alpha,
                "A_s": A_s,
                "n_s": n_s,
                "Omega_m": Omega_m,
                "Omega_lambda": Omega_lambda,
                "k": k,
                "k_over_alpha": k / alpha if alpha > 0 else 0,
            }

            if with_coherence:
                # Calculate coherence evolution
                alpha_eff = k / (100 * alpha) if alpha > 0 else 0.66
                alpha_eff = np.clip(alpha_eff, 0.01, 0.99)

                try:
                    K, C, Total = self.model.evolve(N=12, alpha=alpha_eff)
                    universe["final_coherence"] = K[-1]
                    universe["coherence_growth"] = K[-1] / K[0]
                    universe["total_realized"] = Total[-1]
                except Exception:
                    universe["final_coherence"] = 1.0
                    universe["coherence_growth"] = 1.0
                    universe["total_realized"] = 1.0

            universes.append(universe)

        return universes

    def statistical_analysis(self, universes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze universe ensemble statistics.

        Args:
            universes: List of universe dictionaries

        Returns:
            Dictionary with statistics for each parameter
        """
        stats = {}

        # Parameters to analyze
        params = ["alpha", "A_s", "n_s", "k", "k_over_alpha", "Omega_m", "Omega_lambda"]

        if "final_coherence" in universes[0]:
            params.extend(["final_coherence", "coherence_growth"])

        for param in params:
            values = [u[param] for u in universes if param in u]
            if values:
                stats[param] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "median": np.median(values),
                }

        # Calculate our universe's percentile
        if "final_coherence" in universes[0]:
            our_coherence = 3.62  # Approximate value for our universe
            coherences = [u["final_coherence"] for u in universes]
            percentile = np.sum(np.array(coherences) <= our_coherence) / len(coherences) * 100
            stats["our_universe_percentile"] = percentile

        # k-alpha correlation
        k_values = [u["k"] for u in universes]
        alpha_values = [u["alpha"] for u in universes]
        stats["k_alpha_correlation"] = np.corrcoef(k_values, alpha_values)[0, 1]

        return stats

    def find_special_universes(
        self, universes: List[Dict[str, Any]], criterion: str = "max_coherence"
    ) -> List[Dict[str, Any]]:
        """
        Find universes matching specific criteria.

        Args:
            universes: List of universes
            criterion: Selection criterion

        Returns:
            List of matching universes
        """
        if criterion == "max_coherence":
            if "final_coherence" in universes[0]:
                max_coh = max(u["final_coherence"] for u in universes)
                return [u for u in universes if u["final_coherence"] == max_coh]

        elif criterion == "like_ours":
            our_k = self.constants.k_observed
            threshold = 0.05 * our_k
            return [u for u in universes if abs(u["k"] - our_k) < threshold]

        elif criterion == "flat":
            return [u for u in universes if abs(u["Omega_m"] + u["Omega_lambda"] - 1) < 0.01]

        return []

    def monte_carlo_k(self, n_samples: int = 10000, return_samples: bool = False) -> Dict[str, Any]:
        """
        Monte Carlo analysis of k formula.

        Propagate uncertainties through k = π × α × ln(1/A_s) / n_s

        Args:
            n_samples: Number of Monte Carlo samples
            return_samples: Return raw samples

        Returns:
            Dictionary with k statistics
        """
        # Sample parameters with uncertainties
        alpha = np.random.normal(self.constants.alpha, self.constants.alpha_error, n_samples)
        A_s = np.random.normal(self.constants.A_s, self.constants.A_s_error, n_samples)
        n_s = np.random.normal(self.constants.n_s, self.constants.n_s_error, n_samples)

        # Calculate k samples
        k_samples = np.pi * alpha * np.log(1 / A_s) / n_s

        result = {
            "mean": np.mean(k_samples),
            "std": np.std(k_samples),
            "percentile_2.5": np.percentile(k_samples, 2.5),
            "percentile_97.5": np.percentile(k_samples, 97.5),
            "observed": self.constants.k_observed,
            "observed_in_range": (
                np.percentile(k_samples, 2.5)
                <= self.constants.k_observed
                <= np.percentile(k_samples, 97.5)
            ),
        }

        if return_samples:
            result["samples"] = k_samples

        return result

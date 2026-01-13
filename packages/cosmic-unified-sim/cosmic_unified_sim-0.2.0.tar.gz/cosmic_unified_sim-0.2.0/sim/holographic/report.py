"""
Universe Formula Report
=======================

Generate reports on holographic analysis results.
"""

from typing import Dict

from .analysis import COSMOLOGICAL_MODELS, HolographicAnalysis


class UniverseFormulaReport:
    """
    Generate comprehensive reports on k-alpha relation.

    Examples:
    ---------
    >>> from sim.holographic import UniverseFormulaReport
    >>> report = UniverseFormulaReport()
    >>> report.run_final_report()
    """

    def __init__(self):
        """Initialize report generator."""
        self.analysis = HolographicAnalysis()
        self.results = None

    def run_analysis(self) -> Dict:
        """Run full analysis and store results."""
        self.results = {
            "all_models": self.analysis.analyze_all_models(),
            "formula_comparison": self.analysis.formula_comparison(),
            "significance": self.analysis.significance_test(),
            "information": self.analysis.information_capacity(),
        }
        return self.results

    def create_executive_summary(self) -> str:
        """Create executive summary."""
        if self.results is None:
            self.run_analysis()

        r = self.results

        return f"""
EXECUTIVE SUMMARY: Holographic Information Ratio Analysis
=========================================================

KEY FINDING: k ≈ 66α (empirical relation)

Results across {len(COSMOLOGICAL_MODELS)} cosmological models:
- Mean k = {r['all_models']['mean_k']:.6f} ± {r['all_models']['std_k']:.6f}
- Mean k/α = {r['all_models']['mean_k_over_alpha']:.2f}
- Error vs 66α formula: {r['all_models']['mean_error_vs_66alpha']:.2f}%

Formula Comparison:
- Best formula: {r['formula_comparison']['best_formula']}
- Holographic: k = π × α × ln(1/A_s) / n_s

Statistical Significance:
- p-value: {r['significance']['p_value']:.3f}
- Significant at 0.05: {r['significance']['significant_at_0.05']}

Holographic Information:
- Maximum capacity: {r['information']['max_information_bits']:.2e} bits
- With k factor: {r['information']['actual_information_bits']:.2e} bits
"""

    def create_publication_template(self) -> str:
        """Create publication-ready text."""
        if self.results is None:
            self.run_analysis()

        return f"""
ABSTRACT
--------
We analyze the holographic information ratio k = E_info/E_total
across multiple cosmological datasets and find an empirical
relation k ≈ 66α, where α is the fine structure constant.

INTRODUCTION
------------
The holographic principle suggests that information in a region
scales with surface area rather than volume. We investigate whether
the information ratio k is related to fundamental constants.

METHODS
-------
We calculate k using the formula:
    k = π × α × ln(1/A_s) / n_s

where:
- α = 1/137 (fine structure constant)
- A_s = scalar perturbation amplitude
- n_s = spectral index

RESULTS
-------
Mean k across all models: {self.results['all_models']['mean_k']:.6f}
Standard deviation: {self.results['all_models']['std_k']:.6f}
k/α ratio: {self.results['all_models']['mean_k_over_alpha']:.2f}

CONCLUSIONS
-----------
The empirical relation k ≈ 66α has an error of
{self.results['all_models']['mean_error_vs_66alpha']:.2f}% and
p-value of {self.results['significance']['p_value']:.3f}.
"""

    def create_presentation_slides(self) -> str:
        """Create presentation-style summary."""
        if self.results is None:
            self.run_analysis()

        r = self.results

        return f"""
SLIDE 1: Title
==============
Holographic Information and the Fine Structure Constant
k ≈ 66α: Coincidence or Connection?

SLIDE 2: Key Results
====================
• Analyzed {len(COSMOLOGICAL_MODELS)} cosmological models
• Found: k = {r['all_models']['mean_k']:.4f} ± {r['all_models']['std_k']:.4f}
• Relation: k/α ≈ {r['all_models']['mean_k_over_alpha']:.1f}
• Error: {r['all_models']['mean_error_vs_66alpha']:.2f}%

SLIDE 3: The Formula
====================
k = π × α × ln(1/A_s) / n_s

Components:
• π = 3.14159...
• α = 1/137.036 (fine structure)
• A_s = 2.1×10⁻⁹ (scalar amplitude)
• n_s = 0.9649 (spectral index)

SLIDE 4: Statistical Test
=========================
• p-value = {r['significance']['p_value']:.3f}
• Significant at 5%: {r['significance']['significant_at_0.05']}
• Further investigation needed

SLIDE 5: Conclusions
====================
• Interesting numerical coincidence
• May hint at deeper physics
• Requires theoretical explanation
"""

    def create_checklist(self) -> str:
        """Create verification checklist."""
        if self.results is None:
            self.run_analysis()

        err = self.results["all_models"]["mean_error_vs_66alpha"]
        pval = self.results["significance"]["p_value"]
        std_k = self.results["all_models"]["std_k"]
        items = [
            f"[{'✓' if err < 5 else ' '}] Error < 5%",
            f"[{'✓' if pval < 0.3 else ' '}] p-value reasonable",
            f"[{'✓' if len(COSMOLOGICAL_MODELS) >= 3 else ' '}] Multiple models tested",
            f"[{'✓' if std_k < 0.05 else ' '}] Consistency across models",
        ]

        return "VERIFICATION CHECKLIST\n" + "=" * 20 + "\n" + "\n".join(items)

    def save_results(self, filepath: str) -> None:
        """Save results to file."""
        if self.results is None:
            self.run_analysis()

        with open(filepath, "w") as f:
            f.write(self.create_executive_summary())
            f.write("\n\n")
            f.write(self.create_publication_template())
            f.write("\n\n")
            f.write(self.create_checklist())

    def run_final_report(self) -> None:
        """Run and print full report."""
        self.run_analysis()

        print(self.create_executive_summary())
        print("\n" + "=" * 60 + "\n")
        print(self.create_presentation_slides())
        print("\n" + "=" * 60 + "\n")
        print(self.create_checklist())

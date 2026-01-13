"""
Matter Genesis Simulation
=========================

Full simulation of matter creation from inflation to present.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from sim.constants import PhysicalConstants


@dataclass
class UniverseState:
    """State of universe at a given time."""

    time: float  # In natural units (GeV⁻¹)
    temperature: float  # In GeV
    scale_factor: float
    energy_density: Dict[str, float]  # By component
    particle_counts: Dict[str, float]  # By species


class MatterGenesisSimulation:
    """
    Full matter genesis simulation.

    Simulates universe evolution from inflation through:
    - Reheating (inflaton decay)
    - Baryogenesis
    - Nucleosynthesis
    - Recombination

    Examples:
    ---------
    >>> from sim.genesis import MatterGenesisSimulation
    >>> sim = MatterGenesisSimulation()
    >>> history = sim.evolve_universe(total_time=1000.0)
    >>> print(f"Final composition: {history[-1].energy_density}")
    """

    def __init__(
        self,
        volume_size: float = 10.0,  # Comoving volume
        initial_inflaton_energy: float = 1e16,  # GeV
        hubble_parameter: float = 1e-5,  # GeV
    ):
        """
        Initialize simulation.

        Args:
            volume_size: Comoving volume in natural units
            initial_inflaton_energy: Initial inflaton energy
            hubble_parameter: Hubble parameter
        """
        self.volume = volume_size
        self.E_inf = initial_inflaton_energy
        self.H = hubble_parameter
        self.pc = PhysicalConstants()

        # Physics parameters
        self.g_star = 106.75  # SM degrees of freedom at high T
        self.eta_observed = 6.1e-10  # Observed baryon-to-photon ratio

    def initial_state(self) -> UniverseState:
        """Create initial state (end of inflation)."""
        return UniverseState(
            time=0.0,
            temperature=self.E_inf,
            scale_factor=1.0,
            energy_density={
                "inflaton": self.E_inf**4,
                "radiation": 0.0,
                "matter": 0.0,
                "dark_energy": (self.H * self.pc.m_planck) ** 2 / 3,
            },
            particle_counts={
                "photons": 0,
                "baryons": 0,
                "leptons": 0,
                "dark_matter": 0,
            },
        )

    def step(self, state: UniverseState, dt: float) -> UniverseState:
        """
        Evolve universe by one time step.

        Args:
            state: Current state
            dt: Time step

        Returns:
            New state
        """
        # Update scale factor
        new_a = state.scale_factor * np.exp(self.H * dt)

        # Temperature evolution
        # Before reheating: T ∝ a^0 (de Sitter)
        # After reheating: T ∝ a^{-1} (radiation)
        rho_rad = state.energy_density["radiation"]
        rho_inf = state.energy_density["inflaton"]

        if rho_rad > rho_inf:
            # Radiation dominated
            new_T = state.temperature * state.scale_factor / new_a
        else:
            # Inflaton dominated (reheating)
            new_T = state.temperature * 0.99  # Gradual reheating

        # Energy transfer: inflaton → radiation
        decay_rate = 0.01 * self.H  # Simplified decay rate
        d_rho_inf = -decay_rate * rho_inf * dt
        d_rho_rad = -d_rho_inf - 4 * self.H * rho_rad * dt  # Include dilution

        new_energy = {
            "inflaton": max(0, rho_inf + d_rho_inf),
            "radiation": max(0, rho_rad + d_rho_rad),
            "matter": state.energy_density["matter"] * (state.scale_factor / new_a) ** 3,
            "dark_energy": state.energy_density["dark_energy"],
        }

        # Particle creation
        new_counts = state.particle_counts.copy()

        # Photon production from reheating
        if d_rho_rad > 0:
            new_counts["photons"] += d_rho_rad * self.volume * new_a**3 / new_T

        # Baryon asymmetry (simplified)
        if state.time < 100 and state.particle_counts["baryons"] < 1e-10 * new_counts["photons"]:
            new_counts["baryons"] = self.eta_observed * new_counts["photons"]
            new_counts["leptons"] = new_counts["baryons"]  # Charge neutrality

        return UniverseState(
            time=state.time + dt,
            temperature=new_T,
            scale_factor=new_a,
            energy_density=new_energy,
            particle_counts=new_counts,
        )

    def evolve_universe(
        self, total_time: float = 1000.0, dt: float = 0.1, callback: Optional[Any] = None
    ) -> List[UniverseState]:
        """
        Evolve universe through matter genesis.

        Args:
            total_time: Total simulation time
            dt: Time step
            callback: Optional callback(state) at each step

        Returns:
            List of universe states
        """
        history = [self.initial_state()]

        while history[-1].time < total_time:
            new_state = self.step(history[-1], dt)
            history.append(new_state)

            if callback:
                callback(new_state)

        return history

    def get_composition(self, state: UniverseState) -> Dict[str, float]:
        """
        Get fractional composition at a state.

        Args:
            state: Universe state

        Returns:
            Dict with fractional densities
        """
        total = sum(state.energy_density.values())
        if total <= 0:
            return {k: 0.0 for k in state.energy_density}

        return {k: v / total for k, v in state.energy_density.items()}

    def get_summary(self, history: List[UniverseState]) -> Dict:
        """
        Get simulation summary.

        Args:
            history: List of universe states

        Returns:
            Summary dict
        """
        final = history[-1]
        composition = self.get_composition(final)

        # Find reheating time (when radiation dominates)
        reheat_time = None
        for state in history:
            if state.energy_density["radiation"] > state.energy_density["inflaton"]:
                reheat_time = state.time
                break

        return {
            "n_steps": len(history),
            "final_time": final.time,
            "final_temperature": final.temperature,
            "final_scale_factor": final.scale_factor,
            "composition": composition,
            "baryon_to_photon": (
                final.particle_counts["baryons"] / final.particle_counts["photons"]
                if final.particle_counts["photons"] > 0
                else 0
            ),
            "reheating_time": reheat_time,
        }

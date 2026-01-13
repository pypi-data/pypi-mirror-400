"""
N-Body Simulator
================

Full-scale gravitational N-body simulation.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
from scipy.integrate import solve_ivp

from .body import Body
from .calculator import CosmicCalculator


class NBodySimulator:
    """
    N-body gravitational simulation.

    Uses scipy.integrate.solve_ivp for high-precision numerical integration.

    Examples:
    ---------
    >>> from sim.cosmic import NBodySimulator, SystemPresets
    >>> presets = SystemPresets()
    >>> bodies = presets.create_earth_moon_system()
    >>> sim = NBodySimulator(bodies)
    >>> times, states = sim.simulate(
    ...     t_span=(0, 30*24*3600),  # 30 days
    ...     n_points=1000
    ... )
    >>> print(f"Total energy: {sim.get_total_energy():.2e} J")
    """

    def __init__(self, bodies: Optional[List[Body]] = None):
        """
        Initialize simulator.

        Args:
            bodies: List of celestial bodies
        """
        self.calc = CosmicCalculator()
        self.bodies = bodies if bodies is not None else []
        self.time = 0.0
        self.history: List[Dict[str, Any]] = []

    def add_body(self, body: Body) -> None:
        """Add a body to the system."""
        self.bodies.append(body)

    def remove_body(self, name: str) -> None:
        """Remove a body by name."""
        self.bodies = [b for b in self.bodies if b.name != name]

    def get_body(self, name: str) -> Optional[Body]:
        """Get body by name."""
        for body in self.bodies:
            if body.name == name:
                return body
        return None

    def _derivatives(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Calculate derivatives for N-body system.

        dy/dt = [velocities, accelerations]

        Args:
            t: Current time
            y: State vector [positions, velocities]

        Returns:
            Derivatives vector
        """
        n_bodies = len(self.bodies)
        n_dof = 3  # 3D space

        # Extract positions and velocities
        positions = y[: n_bodies * n_dof].reshape(n_bodies, n_dof)
        velocities = y[n_bodies * n_dof :].reshape(n_bodies, n_dof)

        # Calculate accelerations
        accelerations = np.zeros_like(positions)

        for i in range(n_bodies):
            for j in range(n_bodies):
                if i != j:
                    r_vec = positions[j] - positions[i]
                    r_mag = np.linalg.norm(r_vec)

                    if r_mag > 1e-10:  # Avoid singularity
                        accelerations[i] += self.calc.G * self.bodies[j].mass * r_vec / r_mag**3

        return np.concatenate([velocities.flatten(), accelerations.flatten()])

    def _update_bodies(self, y: np.ndarray) -> None:
        """Update body states from state vector."""
        n_bodies = len(self.bodies)
        n_dof = 3

        positions = y[: n_bodies * n_dof].reshape(n_bodies, n_dof)
        velocities = y[n_bodies * n_dof :].reshape(n_bodies, n_dof)

        for i, body in enumerate(self.bodies):
            body.position = positions[i].copy()
            body.velocity = velocities[i].copy()

    def simulate(
        self,
        t_span: Tuple[float, float],
        n_points: int = 1000,
        rtol: float = 1e-8,
        save_trajectory: bool = True,
        callback: Optional[Callable] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Run N-body simulation.

        Args:
            t_span: Time interval (t_start, t_end) in seconds
            n_points: Number of output points
            rtol: Relative tolerance for integrator
            save_trajectory: Save trajectory history
            callback: Optional callback(t, bodies) at each step

        Returns:
            Tuple (times, states) arrays

        Raises:
            ValueError: If no bodies in system
        """
        if len(self.bodies) == 0:
            raise ValueError("No bodies in system")

        # Build initial state [positions, velocities]
        positions = np.concatenate([b.position for b in self.bodies])
        velocities = np.concatenate([b.velocity for b in self.bodies])
        initial_state = np.concatenate([positions, velocities])

        # Clear trajectories
        if save_trajectory:
            for body in self.bodies:
                body.clear_trajectory()

        # Time points
        t_eval = np.linspace(t_span[0], t_span[1], n_points)

        # Integrate
        solution = solve_ivp(
            self._derivatives,
            t_span,
            initial_state,
            t_eval=t_eval,
            rtol=rtol,
            method="RK45",
            dense_output=True,
        )

        # Process results
        states = []
        for i, t in enumerate(t_eval):
            state_vector = solution.sol(t)
            self._update_bodies(state_vector)
            self.time = t

            if save_trajectory:
                for body in self.bodies:
                    body.add_to_trajectory()

            states.append(
                {"time": t, "bodies": {b.name: b.get_state().copy() for b in self.bodies}}
            )

            if callback:
                callback(t, self.bodies)

        self.history = states
        all_states = np.array([solution.sol(t) for t in t_eval]).T

        return t_eval, all_states

    def get_total_energy(self) -> float:
        """
        Calculate total system energy.

        Returns:
            Total energy (kinetic + potential) in Joules
        """
        # Kinetic energy
        kinetic = sum(body.get_kinetic_energy() for body in self.bodies)

        # Potential energy
        potential = 0.0
        for i, body1 in enumerate(self.bodies):
            for body2 in self.bodies[i + 1 :]:
                r = body1.get_distance_to(body2)
                if r > 1e-10:
                    potential -= self.calc.G * body1.mass * body2.mass / r

        return kinetic + potential

    def get_center_of_mass(self) -> np.ndarray:
        """
        Calculate center of mass position.

        Returns:
            Center of mass [x, y, z]
        """
        total_mass = sum(body.mass for body in self.bodies)
        if total_mass == 0:
            return np.zeros(3)

        com = np.zeros(3)
        for body in self.bodies:
            com += body.mass * body.position
        return com / total_mass

    def get_total_momentum(self) -> np.ndarray:
        """
        Calculate total momentum.

        Returns:
            Total momentum [px, py, pz]
        """
        momentum = np.zeros(3)
        for body in self.bodies:
            momentum += body.mass * body.velocity
        return momentum

    def get_total_angular_momentum(self) -> np.ndarray:
        """
        Calculate total angular momentum.

        Returns:
            Total angular momentum [Lx, Ly, Lz]
        """
        L = np.zeros(3)
        for body in self.bodies:
            L += body.get_angular_momentum()
        return L

    def reset(self) -> None:
        """Reset simulation state."""
        self.time = 0.0
        self.history = []
        for body in self.bodies:
            body.clear_trajectory()

    def get_energy_conservation(self) -> Tuple[float, float]:
        """
        Calculate energy conservation quality.

        Returns:
            Tuple (initial_energy, relative_change)
        """
        if len(self.history) < 2:
            return 0.0, 0.0

        # Recreate initial state
        initial_state = self.history[0]
        for name, state in initial_state["bodies"].items():
            body = self.get_body(name)
            if body:
                body.set_state(state)

        initial_energy = self.get_total_energy()

        # Current state
        final_state = self.history[-1]
        for name, state in final_state["bodies"].items():
            body = self.get_body(name)
            if body:
                body.set_state(state)

        final_energy = self.get_total_energy()

        if abs(initial_energy) > 1e-10:
            relative_change = (final_energy - initial_energy) / abs(initial_energy)
        else:
            relative_change = 0.0

        return initial_energy, relative_change

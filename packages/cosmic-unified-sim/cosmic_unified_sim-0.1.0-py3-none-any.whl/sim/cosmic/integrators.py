"""
Symplectic Integrators
======================

Energy-conserving integrators for N-body simulations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np


@dataclass
class IntegratorState:
    """State of the integrator."""

    positions: np.ndarray  # Shape: (n_bodies, 3)
    velocities: np.ndarray  # Shape: (n_bodies, 3)
    masses: np.ndarray  # Shape: (n_bodies,)
    time: float


class Integrator(ABC):
    """Abstract base class for integrators."""

    @abstractmethod
    def step(
        self,
        state: IntegratorState,
        dt: float,
        acceleration_func: Callable[[np.ndarray, np.ndarray], np.ndarray],
    ) -> IntegratorState:
        """
        Perform one integration step.

        Args:
            state: Current state
            dt: Time step
            acceleration_func: Function(positions, masses) -> accelerations

        Returns:
            New state
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Integrator name."""
        pass

    @property
    def order(self) -> int:
        """Order of accuracy."""
        return 1


class EulerIntegrator(Integrator):
    """
    Simple Euler integrator (first order).

    Not recommended for production - use for testing only.
    """

    @property
    def name(self) -> str:
        return "euler"

    @property
    def order(self) -> int:
        return 1

    def step(
        self, state: IntegratorState, dt: float, acceleration_func: Callable
    ) -> IntegratorState:
        acc = acceleration_func(state.positions, state.masses)

        new_positions = state.positions + state.velocities * dt
        new_velocities = state.velocities + acc * dt

        return IntegratorState(
            positions=new_positions,
            velocities=new_velocities,
            masses=state.masses,
            time=state.time + dt,
        )


class VerletIntegrator(Integrator):
    """
    Velocity Verlet integrator (second order, symplectic).

    Excellent energy conservation for gravitational systems.

    Algorithm:
        v(t + dt/2) = v(t) + a(t) * dt/2
        x(t + dt) = x(t) + v(t + dt/2) * dt
        a(t + dt) = F(x(t + dt)) / m
        v(t + dt) = v(t + dt/2) + a(t + dt) * dt/2
    """

    @property
    def name(self) -> str:
        return "verlet"

    @property
    def order(self) -> int:
        return 2

    def step(
        self, state: IntegratorState, dt: float, acceleration_func: Callable
    ) -> IntegratorState:
        # Current acceleration
        acc = acceleration_func(state.positions, state.masses)

        # Half-step velocity
        v_half = state.velocities + 0.5 * acc * dt

        # Full-step position
        new_positions = state.positions + v_half * dt

        # New acceleration
        new_acc = acceleration_func(new_positions, state.masses)

        # Full-step velocity
        new_velocities = v_half + 0.5 * new_acc * dt

        return IntegratorState(
            positions=new_positions,
            velocities=new_velocities,
            masses=state.masses,
            time=state.time + dt,
        )


class LeapfrogIntegrator(Integrator):
    """
    Leapfrog integrator (second order, symplectic).

    Equivalent to Verlet but with different structure.
    Positions and velocities are staggered by dt/2.

    Algorithm:
        x(t + dt) = x(t) + v(t + dt/2) * dt
        v(t + 3dt/2) = v(t + dt/2) + a(t + dt) * dt
    """

    def __init__(self):
        self._initialized = False
        self._v_half: Optional[np.ndarray] = None

    @property
    def name(self) -> str:
        return "leapfrog"

    @property
    def order(self) -> int:
        return 2

    def step(
        self, state: IntegratorState, dt: float, acceleration_func: Callable
    ) -> IntegratorState:
        if not self._initialized:
            # Initialize v_half = v - a*dt/2
            acc = acceleration_func(state.positions, state.masses)
            self._v_half = state.velocities - 0.5 * acc * dt
            self._initialized = True

        # v(t + dt/2)
        acc = acceleration_func(state.positions, state.masses)
        self._v_half = self._v_half + acc * dt

        # x(t + dt)
        new_positions = state.positions + self._v_half * dt

        # Synchronize velocity for output
        new_acc = acceleration_func(new_positions, state.masses)
        new_velocities = self._v_half + 0.5 * new_acc * dt

        return IntegratorState(
            positions=new_positions,
            velocities=new_velocities,
            masses=state.masses,
            time=state.time + dt,
        )

    def reset(self):
        """Reset integrator state."""
        self._initialized = False
        self._v_half = None


class Yoshida4Integrator(Integrator):
    """
    Fourth-order Yoshida integrator (symplectic).

    Higher accuracy while maintaining symplectic property.
    Uses carefully chosen coefficients for 4th order accuracy.

    Reference: Yoshida, H. (1990). "Construction of higher order
    symplectic integrators". Physics Letters A, 150(5-7), 262-268.
    """

    # Yoshida coefficients for 4th order
    _c = [
        1.0 / (2 * (2 - 2 ** (1 / 3))),
        (1 - 2 ** (1 / 3)) / (2 * (2 - 2 ** (1 / 3))),
        (1 - 2 ** (1 / 3)) / (2 * (2 - 2 ** (1 / 3))),
        1.0 / (2 * (2 - 2 ** (1 / 3))),
    ]
    _d = [
        1.0 / (2 - 2 ** (1 / 3)),
        -(2 ** (1 / 3)) / (2 - 2 ** (1 / 3)),
        1.0 / (2 - 2 ** (1 / 3)),
        0.0,
    ]

    @property
    def name(self) -> str:
        return "yoshida4"

    @property
    def order(self) -> int:
        return 4

    def step(
        self, state: IntegratorState, dt: float, acceleration_func: Callable
    ) -> IntegratorState:
        pos = state.positions.copy()
        vel = state.velocities.copy()

        for c, d in zip(self._c, self._d):
            # Position update
            pos = pos + c * vel * dt

            # Velocity update (if d != 0)
            if abs(d) > 1e-15:
                acc = acceleration_func(pos, state.masses)
                vel = vel + d * acc * dt

        return IntegratorState(
            positions=pos, velocities=vel, masses=state.masses, time=state.time + dt
        )


class Yoshida6Integrator(Integrator):
    """
    Sixth-order Yoshida integrator (symplectic).

    Even higher accuracy for demanding applications.
    """

    # Coefficients for 6th order (Yoshida solution A)
    _w = [
        0.78451361047755726382,
        0.23557321335935813369,
        -1.17767998417887100695,
        1.31518632068391121889,
    ]

    @property
    def name(self) -> str:
        return "yoshida6"

    @property
    def order(self) -> int:
        return 6

    def step(
        self, state: IntegratorState, dt: float, acceleration_func: Callable
    ) -> IntegratorState:
        # Build full coefficient sequence
        w0 = 1.0 - 2 * sum(self._w)
        w_full = self._w + [w0] + self._w[::-1]

        pos = state.positions.copy()
        vel = state.velocities.copy()

        for i, w in enumerate(w_full):
            # Alternate between position and velocity updates
            if i % 2 == 0:
                vel = vel + 0.5 * w * acceleration_func(pos, state.masses) * dt
            pos = pos + w * vel * dt
            if i % 2 == 0:
                vel = vel + 0.5 * w * acceleration_func(pos, state.masses) * dt

        return IntegratorState(
            positions=pos, velocities=vel, masses=state.masses, time=state.time + dt
        )


class ForestRuthIntegrator(Integrator):
    """
    Forest-Ruth integrator (fourth order, symplectic).

    Alternative 4th order symplectic integrator.

    Reference: Forest, E. & Ruth, R.D. (1990). "Fourth-order symplectic
    integration". Physica D, 43(1), 105-117.
    """

    _theta = 1.0 / (2 - 2 ** (1 / 3))

    @property
    def name(self) -> str:
        return "forest_ruth"

    @property
    def order(self) -> int:
        return 4

    def step(
        self, state: IntegratorState, dt: float, acceleration_func: Callable
    ) -> IntegratorState:
        theta = self._theta

        pos = state.positions.copy()
        vel = state.velocities.copy()

        # Step 1
        pos = pos + theta * dt / 2 * vel
        acc = acceleration_func(pos, state.masses)
        vel = vel + theta * dt * acc

        # Step 2
        pos = pos + (1 - theta) * dt / 2 * vel
        acc = acceleration_func(pos, state.masses)
        vel = vel + (1 - 2 * theta) * dt * acc

        # Step 3
        pos = pos + (1 - theta) * dt / 2 * vel
        acc = acceleration_func(pos, state.masses)
        vel = vel + theta * dt * acc

        # Step 4
        pos = pos + theta * dt / 2 * vel

        return IntegratorState(
            positions=pos, velocities=vel, masses=state.masses, time=state.time + dt
        )


class AdaptiveIntegrator(Integrator):
    """
    Adaptive time-stepping wrapper for any integrator.

    Uses error estimation to adjust step size.
    """

    def __init__(
        self,
        base_integrator: Integrator,
        tol: float = 1e-8,
        safety: float = 0.9,
        min_dt: float = 1e-10,
        max_dt: float = 1e6,
    ):
        self.base = base_integrator
        self.tol = tol
        self.safety = safety
        self.min_dt = min_dt
        self.max_dt = max_dt
        self._current_dt = None

    @property
    def name(self) -> str:
        return f"adaptive_{self.base.name}"

    @property
    def order(self) -> int:
        return self.base.order

    def step(
        self, state: IntegratorState, dt: float, acceleration_func: Callable
    ) -> IntegratorState:
        if self._current_dt is None:
            self._current_dt = dt

        # Take one full step
        full_state = self.base.step(state, self._current_dt, acceleration_func)

        # Take two half steps
        half_state = self.base.step(state, self._current_dt / 2, acceleration_func)
        half_state = self.base.step(half_state, self._current_dt / 2, acceleration_func)

        # Estimate error
        error = np.max(np.abs(full_state.positions - half_state.positions))

        # Adjust step size
        if error > 0:
            factor = self.safety * (self.tol / error) ** (1 / (self.base.order + 1))
            factor = max(0.1, min(factor, 10.0))
            self._current_dt = np.clip(self._current_dt * factor, self.min_dt, self.max_dt)

        # Return the more accurate result
        return half_state

    @property
    def current_dt(self) -> float:
        """Current adaptive time step."""
        return self._current_dt


# ============================================================================
# Factory Function
# ============================================================================

_INTEGRATORS = {
    "euler": EulerIntegrator,
    "verlet": VerletIntegrator,
    "leapfrog": LeapfrogIntegrator,
    "yoshida": Yoshida4Integrator,
    "yoshida4": Yoshida4Integrator,
    "yoshida6": Yoshida6Integrator,
    "forest_ruth": ForestRuthIntegrator,
}


def get_integrator(name: str, **kwargs) -> Integrator:
    """
    Get integrator by name.

    Args:
        name: Integrator name (euler, verlet, leapfrog, yoshida4, yoshida6, forest_ruth)
        **kwargs: Additional arguments for the integrator

    Returns:
        Integrator instance
    """
    name_lower = name.lower()

    if name_lower.startswith("adaptive_"):
        base_name = name_lower.replace("adaptive_", "")
        base = get_integrator(base_name)
        return AdaptiveIntegrator(base, **kwargs)

    if name_lower not in _INTEGRATORS:
        available = list(_INTEGRATORS.keys())
        raise ValueError(f"Unknown integrator '{name}'. Available: {available}")

    return _INTEGRATORS[name_lower]()


def list_integrators() -> List[str]:
    """List available integrators."""
    return list(_INTEGRATORS.keys()) + [f"adaptive_{name}" for name in _INTEGRATORS.keys()]

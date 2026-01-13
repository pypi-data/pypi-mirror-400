"""
Celestial Body
==============

Class for representing celestial bodies in N-body simulations.
"""

from typing import List

import numpy as np


class Body:
    """
    Celestial body with position, velocity, mass, and trajectory.

    Examples:
    ---------
    >>> from sim.cosmic import Body
    >>> earth = Body(
    ...     name="Earth",
    ...     mass=5.972e24,
    ...     position=np.array([1.5e11, 0, 0]),
    ...     velocity=np.array([0, 30000, 0]),
    ...     color='blue'
    ... )
    >>> print(f"Kinetic energy: {earth.get_kinetic_energy():.2e} J")
    """

    def __init__(
        self,
        name: str,
        mass: float,
        position: np.ndarray,
        velocity: np.ndarray,
        radius: float = 0.0,
        color: str = "blue",
    ):
        """
        Initialize celestial body.

        Args:
            name: Body name
            mass: Mass in kg
            position: Initial position [x, y, z] in m
            velocity: Initial velocity [vx, vy, vz] in m/s
            radius: Body radius in m (for visualization)
            color: Color for visualization
        """
        self.name = name
        self.mass = mass
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.radius = radius
        self.color = color

        # Trajectory history
        self.trajectory: List[np.ndarray] = []
        self.energy_history: List[float] = []

    def get_state(self) -> np.ndarray:
        """
        Get state vector [x, y, z, vx, vy, vz].

        Returns:
            State vector
        """
        return np.concatenate([self.position, self.velocity])

    def set_state(self, state: np.ndarray) -> None:
        """
        Set state from vector.

        Args:
            state: State vector [x, y, z, vx, vy, vz]
        """
        self.position = state[:3].copy()
        self.velocity = state[3:6].copy()

    def get_kinetic_energy(self) -> float:
        """
        Calculate kinetic energy.

        Returns:
            Kinetic energy in Joules
        """
        v_mag = np.linalg.norm(self.velocity)
        return 0.5 * self.mass * v_mag**2

    def get_distance_to(self, other: "Body") -> float:
        """
        Calculate distance to another body.

        Args:
            other: Another body

        Returns:
            Distance in meters
        """
        return np.linalg.norm(self.position - other.position)

    def get_angular_momentum(self) -> np.ndarray:
        """
        Calculate angular momentum L = r × p.

        Returns:
            Angular momentum vector [Lx, Ly, Lz]
        """
        return np.cross(self.position, self.mass * self.velocity)

    def add_to_trajectory(self) -> None:
        """Add current position to trajectory history."""
        self.trajectory.append(self.position.copy())

    def clear_trajectory(self) -> None:
        """Clear trajectory history."""
        self.trajectory = []
        self.energy_history = []

    def get_trajectory_array(self) -> np.ndarray:
        """
        Get trajectory as numpy array.

        Returns:
            Array of positions with shape (n_points, 3)
        """
        if len(self.trajectory) == 0:
            return np.array([]).reshape(0, 3)
        return np.array(self.trajectory)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Body({self.name}, mass={self.mass:.2e} kg, "
            f"pos={self.position}, vel={self.velocity})"
        )

    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"Body(name='{self.name}', mass={self.mass}, "
            f"position={self.position.tolist()}, "
            f"velocity={self.velocity.tolist()})"
        )

    def copy(self) -> "Body":
        """Create a copy of this body."""
        b = Body(
            name=self.name,
            mass=self.mass,
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            radius=self.radius,
            color=self.color,
        )
        b.trajectory = [p.copy() for p in self.trajectory]
        b.energy_history = self.energy_history.copy()
        return b

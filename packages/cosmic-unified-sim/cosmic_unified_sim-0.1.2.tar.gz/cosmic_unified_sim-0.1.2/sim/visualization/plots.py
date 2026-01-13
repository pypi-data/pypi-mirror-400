"""
Unified Visualization
=====================

Plotting functions for all simulation types.
"""

import warnings
from typing import Any, List, Optional, Tuple

import numpy as np

# Lazy matplotlib import
plt = None
Axes3D = None


def _import_matplotlib():
    """Lazy import of matplotlib."""
    global plt, Axes3D
    if plt is None:
        import matplotlib.pyplot as plt_module
        from mpl_toolkits.mplot3d import Axes3D as Axes3D_module

        plt = plt_module
        Axes3D = Axes3D_module


class SimulationVisualizer:
    """
    Unified visualization class for all simulation types.

    Examples:
    ---------
    >>> from sim.visualization import SimulationVisualizer
    >>> viz = SimulationVisualizer()
    >>> fig = viz.plot_nbody_3d(bodies)
    >>> fig = viz.plot_coherence(K, stages)
    """

    def __init__(self, style: str = "dark_background", figsize: Tuple[int, int] = (10, 8)):
        """
        Initialize visualizer.

        Args:
            style: Matplotlib style
            figsize: Default figure size
        """
        _import_matplotlib()
        self.style = style
        self.figsize = figsize

    def _setup_style(self):
        """Apply plotting style."""
        try:
            plt.style.use(self.style)
        except Exception:
            pass

    def plot_nbody_3d(
        self, bodies: List[Any], title: str = "N-Body Simulation", center_on_com: bool = True
    ):
        """
        Plot 3D trajectories of N-body simulation.

        Args:
            bodies: List of Body objects with trajectory
            title: Plot title
            center_on_com: Center on center of mass

        Returns:
            matplotlib Figure
        """
        self._setup_style()
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection="3d")

        # Calculate center of mass for centering
        if center_on_com:
            total_mass = sum(b.mass for b in bodies)
            com = np.zeros(3)
            for b in bodies:
                com += b.mass * b.position
            com /= total_mass if total_mass > 0 else 1
        else:
            com = np.zeros(3)

        # Plot trajectories
        max_dist = 0
        for body in bodies:
            traj = body.get_trajectory_array()
            if len(traj) > 0:
                # Center on COM
                traj_centered = traj - com
                ax.plot(
                    traj_centered[:, 0],
                    traj_centered[:, 1],
                    traj_centered[:, 2],
                    label=body.name,
                    color=body.color,
                    alpha=0.7,
                )
                # Current position
                pos = body.position - com
                ax.scatter(*pos, s=50, c=body.color, marker="o")
                max_dist = max(max_dist, np.max(np.abs(traj_centered)))

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(title)
        ax.legend(loc="upper left")

        # Equal aspect ratio
        if max_dist > 0:
            ax.set_xlim(-max_dist, max_dist)
            ax.set_ylim(-max_dist, max_dist)
            ax.set_zlim(-max_dist, max_dist)

        plt.tight_layout()
        return fig

    def plot_nbody_2d(self, bodies: List[Any], plane: str = "xy", title: str = "N-Body Projection"):
        """
        Plot 2D projection of trajectories.

        Args:
            bodies: List of Body objects
            plane: Projection plane ('xy', 'xz', 'yz')
            title: Plot title

        Returns:
            matplotlib Figure
        """
        self._setup_style()
        fig, ax = plt.subplots(figsize=self.figsize)

        idx = {"xy": (0, 1), "xz": (0, 2), "yz": (1, 2)}[plane]
        labels = {"xy": ("X", "Y"), "xz": ("X", "Z"), "yz": ("Y", "Z")}[plane]

        for body in bodies:
            traj = body.get_trajectory_array()
            if len(traj) > 0:
                ax.plot(
                    traj[:, idx[0]], traj[:, idx[1]], label=body.name, color=body.color, alpha=0.7
                )
                ax.scatter(
                    body.position[idx[0]], body.position[idx[1]], s=50, c=body.color, marker="o"
                )

        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        ax.set_title(title)
        ax.legend()
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_coherence(
        self, K: np.ndarray, stages: Optional[List[str]] = None, title: str = "Coherence Evolution"
    ):
        """
        Plot coherence evolution.

        Args:
            K: Coherence values
            stages: Stage names
            title: Plot title

        Returns:
            matplotlib Figure
        """
        self._setup_style()
        fig, ax = plt.subplots(figsize=self.figsize)

        n = len(K)
        x = np.arange(n)

        ax.bar(x, K, color="steelblue", alpha=0.7, edgecolor="navy")
        ax.plot(x, K, "o-", color="darkred", markersize=8)

        if stages and len(stages) == n:
            ax.set_xticks(x)
            ax.set_xticklabels(stages, rotation=45, ha="right")

        ax.set_xlabel("Stage")
        ax.set_ylabel("Coherence K(n)")
        ax.set_title(title)
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        return fig

    def plot_quantum_state(
        self, probabilities: np.ndarray, title: str = "Quantum State Distribution"
    ):
        """
        Plot quantum state probability distribution.

        Args:
            probabilities: Probability array
            title: Plot title

        Returns:
            matplotlib Figure
        """
        self._setup_style()
        fig, ax = plt.subplots(figsize=self.figsize)

        n = len(probabilities)
        x = np.arange(n)

        # Binary labels for basis states
        labels = [f"|{i:0{int(np.log2(n))}b}>" for i in range(n)] if n <= 16 else x

        ax.bar(x, probabilities, color="purple", alpha=0.7)

        if n <= 16:
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha="right")

        ax.set_xlabel("Basis State")
        ax.set_ylabel("Probability")
        ax.set_title(title)
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        return fig

    def plot_energy(
        self, times: np.ndarray, energies: np.ndarray, title: str = "Energy Conservation"
    ):
        """
        Plot energy vs time.

        Args:
            times: Time array
            energies: Energy array
            title: Plot title

        Returns:
            matplotlib Figure
        """
        self._setup_style()
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.plot(times, energies, "b-", linewidth=2)
        ax.axhline(energies[0], color="r", linestyle="--", alpha=0.5, label="Initial")

        relative_change = (energies - energies[0]) / abs(energies[0]) * 100

        ax2 = ax.twinx()
        ax2.plot(times, relative_change, "g-", alpha=0.5)
        ax2.set_ylabel("Relative Change (%)", color="g")

        ax.set_xlabel("Time")
        ax.set_ylabel("Total Energy", color="b")
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig


# Convenience functions


def plot_trajectories_3d(bodies: List[Any], **kwargs):
    """Plot 3D trajectories."""
    viz = SimulationVisualizer()
    return viz.plot_nbody_3d(bodies, **kwargs)


def plot_trajectories_2d(bodies: List[Any], **kwargs):
    """Plot 2D trajectory projection."""
    viz = SimulationVisualizer()
    return viz.plot_nbody_2d(bodies, **kwargs)


def plot_coherence_evolution(K: np.ndarray, **kwargs):
    """Plot coherence evolution."""
    viz = SimulationVisualizer()
    return viz.plot_coherence(K, **kwargs)


def plot_quantum_state(probabilities: np.ndarray, **kwargs):
    """Plot quantum state."""
    viz = SimulationVisualizer()
    return viz.plot_quantum_state(probabilities, **kwargs)


def plot_energy_conservation(times: np.ndarray, energies: np.ndarray, **kwargs):
    """Plot energy conservation."""
    viz = SimulationVisualizer()
    return viz.plot_energy(times, energies, **kwargs)


def animate_simulation(bodies: List[Any], interval: int = 50, save_path: Optional[str] = None):
    """
    Create animation of N-body simulation.

    Args:
        bodies: List of Body objects with trajectory
        interval: Animation interval in ms
        save_path: Path to save animation (optional)

    Returns:
        matplotlib Animation
    """
    _import_matplotlib()
    from matplotlib.animation import FuncAnimation

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Get trajectory data
    trajs = [b.get_trajectory_array() for b in bodies]
    n_frames = min(len(t) for t in trajs if len(t) > 0)

    if n_frames == 0:
        warnings.warn("No trajectory data for animation")
        return None

    # Initialize plot elements
    lines = []
    points = []
    for body in bodies:
        (line,) = ax.plot([], [], [], label=body.name, color=body.color, alpha=0.5)
        (point,) = ax.plot([], [], [], "o", color=body.color, markersize=8)
        lines.append(line)
        points.append(point)

    # Determine axis limits
    all_data = np.concatenate([t for t in trajs if len(t) > 0])
    max_range = np.max(np.abs(all_data)) * 1.1

    ax.set_xlim(-max_range, max_range)
    ax.set_ylim(-max_range, max_range)
    ax.set_zlim(-max_range, max_range)
    ax.legend()

    def update(frame):
        for i, (body, traj) in enumerate(zip(bodies, trajs)):
            if len(traj) > frame:
                lines[i].set_data(traj[:frame, 0], traj[:frame, 1])
                lines[i].set_3d_properties(traj[:frame, 2])
                points[i].set_data([traj[frame, 0]], [traj[frame, 1]])
                points[i].set_3d_properties([traj[frame, 2]])
        return lines + points

    anim = FuncAnimation(fig, update, frames=n_frames, interval=interval, blit=True)

    if save_path:
        anim.save(save_path, writer="pillow", fps=30)

    return anim

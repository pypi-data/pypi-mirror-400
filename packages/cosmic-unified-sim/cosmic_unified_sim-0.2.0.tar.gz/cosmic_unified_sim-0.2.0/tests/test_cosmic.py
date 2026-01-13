"""Comprehensive tests for cosmic module."""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal


class TestBody:
    """Test Body class."""

    def test_body_creation(self):
        """Test basic body creation."""
        from sim.cosmic import Body

        body = Body(
            name="Test", mass=1e24, position=np.array([1e11, 0, 0]), velocity=np.array([0, 3e4, 0])
        )

        assert body.name == "Test"
        assert body.mass == 1e24
        assert_array_equal(body.position, [1e11, 0, 0])
        assert_array_equal(body.velocity, [0, 3e4, 0])

    def test_body_kinetic_energy(self):
        """Test kinetic energy calculation."""
        from sim.cosmic import Body

        body = Body(
            name="Test",
            mass=2.0,  # 2 kg
            position=np.array([0, 0, 0]),
            velocity=np.array([3, 4, 0]),  # |v| = 5 m/s
        )

        # KE = 0.5 * m * v² = 0.5 * 2 * 25 = 25 J
        ke = body.get_kinetic_energy()
        assert_allclose(ke, 25.0)

    def test_body_distance(self):
        """Test distance calculation between bodies."""
        from sim.cosmic import Body

        body1 = Body("A", 1, np.array([0, 0, 0]), np.array([0, 0, 0]))
        body2 = Body("B", 1, np.array([3, 4, 0]), np.array([0, 0, 0]))

        dist = body1.get_distance_to(body2)
        assert_allclose(dist, 5.0)

    def test_body_trajectory(self):
        """Test trajectory recording."""
        from sim.cosmic import Body

        body = Body("Test", 1, np.array([0, 0, 0]), np.array([1, 0, 0]))

        # Add some trajectory points
        for i in range(5):
            body.position = np.array([float(i), 0, 0])
            body.add_to_trajectory()

        traj = body.get_trajectory_array()
        assert traj.shape == (5, 3)
        assert_array_equal(traj[:, 0], [0, 1, 2, 3, 4])

    def test_body_state(self):
        """Test state get/set."""
        from sim.cosmic import Body

        body = Body("Test", 1e24, np.array([1, 2, 3]), np.array([4, 5, 6]))

        state = body.get_state()
        # State is [x, y, z, vx, vy, vz]
        assert_allclose(state, [1, 2, 3, 4, 5, 6])

        new_state = np.array([10, 20, 30, 40, 50, 60])
        body.set_state(new_state)

        assert_allclose(body.position, [10, 20, 30])
        assert_allclose(body.velocity, [40, 50, 60])


class TestSystemPresets:
    """Test SystemPresets class."""

    def test_earth_moon_system(self):
        """Test Earth-Moon system creation."""
        from sim.cosmic import SystemPresets

        presets = SystemPresets()
        bodies = presets.create_earth_moon_system()

        assert len(bodies) == 2
        assert bodies[0].name == "Earth"
        assert bodies[1].name == "Moon"

        # Earth should be much more massive
        assert bodies[0].mass > bodies[1].mass * 10

    def test_solar_system_inner(self):
        """Test inner solar system creation."""
        from sim.cosmic import SystemPresets

        presets = SystemPresets()
        bodies = presets.create_solar_system(include_outer_planets=False)

        # Sun + Mercury, Venus, Earth, Mars
        assert len(bodies) >= 5
        assert bodies[0].name == "Sun"

    def test_solar_system_full(self):
        """Test full solar system creation."""
        from sim.cosmic import SystemPresets

        presets = SystemPresets()
        bodies = presets.create_solar_system(include_outer_planets=True)

        # Sun + all planets
        assert len(bodies) >= 9

    def test_binary_star_system(self):
        """Test binary star system creation."""
        from sim.cosmic import SystemPresets

        presets = SystemPresets()
        bodies = presets.create_binary_star_system()

        assert len(bodies) == 2

    def test_three_body_problem(self):
        """Test three-body problem preset."""
        from sim.cosmic import SystemPresets

        presets = SystemPresets()
        bodies = presets.create_three_body_problem()

        assert len(bodies) == 3


class TestNBodySimulator:
    """Test NBodySimulator class."""

    def test_simulator_creation(self):
        """Test simulator creation."""
        from sim.cosmic import NBodySimulator, SystemPresets

        presets = SystemPresets()
        bodies = presets.create_earth_moon_system()
        sim = NBodySimulator(bodies)

        assert len(sim.bodies) == 2

    def test_add_remove_body(self):
        """Test adding and removing bodies."""
        from sim.cosmic import Body, NBodySimulator

        sim = NBodySimulator()

        body1 = Body("A", 1e24, np.zeros(3), np.zeros(3))
        body2 = Body("B", 1e24, np.array([1e8, 0, 0]), np.zeros(3))

        sim.add_body(body1)
        sim.add_body(body2)
        assert len(sim.bodies) == 2

        sim.remove_body("A")
        assert len(sim.bodies) == 1
        assert sim.bodies[0].name == "B"

    def test_get_body(self):
        """Test getting body by name."""
        from sim.cosmic import NBodySimulator, SystemPresets

        presets = SystemPresets()
        bodies = presets.create_earth_moon_system()
        sim = NBodySimulator(bodies)

        earth = sim.get_body("Earth")
        assert earth is not None
        assert earth.name == "Earth"

        nonexistent = sim.get_body("Mars")
        assert nonexistent is None

    def test_simulation_empty(self):
        """Test simulation fails with no bodies."""
        from sim.cosmic import NBodySimulator

        sim = NBodySimulator()
        with pytest.raises(ValueError):
            sim.simulate(t_span=(0, 1000))

    def test_short_simulation(self):
        """Test short Earth-Moon simulation."""
        from sim.cosmic import NBodySimulator, SystemPresets

        presets = SystemPresets()
        bodies = presets.create_earth_moon_system()
        sim = NBodySimulator(bodies)

        # 1 day simulation
        t_span = (0, 24 * 3600)
        times, states = sim.simulate(t_span, n_points=100)

        assert len(times) == 100
        assert states.shape[1] == 100  # n_points columns

    def test_energy_conservation(self):
        """Test energy conservation in simulation."""
        from sim.cosmic import NBodySimulator, SystemPresets

        presets = SystemPresets()
        bodies = presets.create_earth_moon_system()
        sim = NBodySimulator(bodies)

        # 10 day simulation
        t_span = (0, 10 * 24 * 3600)
        times, states = sim.simulate(t_span, n_points=1000, rtol=1e-10)

        initial_e, relative_change = sim.get_energy_conservation()

        # Energy should be conserved to within 0.1%
        assert abs(relative_change) < 0.001

    def test_center_of_mass(self):
        """Test center of mass calculation."""
        from sim.cosmic import Body, NBodySimulator

        # Two equal masses
        body1 = Body("A", 1e24, np.array([0, 0, 0]), np.zeros(3))
        body2 = Body("B", 1e24, np.array([10, 0, 0]), np.zeros(3))

        sim = NBodySimulator([body1, body2])
        com = sim.get_center_of_mass()

        # COM should be at midpoint
        assert_allclose(com, [5, 0, 0])

    def test_total_momentum(self):
        """Test total momentum calculation."""
        from sim.cosmic import Body, NBodySimulator

        body1 = Body("A", 1e24, np.zeros(3), np.array([100, 0, 0]))
        body2 = Body("B", 1e24, np.zeros(3), np.array([-100, 0, 0]))

        sim = NBodySimulator([body1, body2])
        momentum = sim.get_total_momentum()

        # Equal and opposite momenta should sum to zero
        assert_allclose(momentum, [0, 0, 0], atol=1e-10)

    def test_reset(self):
        """Test simulator reset."""
        from sim.cosmic import NBodySimulator, SystemPresets

        presets = SystemPresets()
        bodies = presets.create_earth_moon_system()
        sim = NBodySimulator(bodies)

        sim.simulate(t_span=(0, 1000), n_points=10)
        assert len(sim.history) > 0

        sim.reset()
        assert len(sim.history) == 0


class TestIntegrators:
    """Test symplectic integrators."""

    def test_verlet_integrator(self):
        """Test Verlet integrator."""
        from sim.cosmic.integrators import VerletIntegrator

        integrator = VerletIntegrator()
        assert integrator.name == "verlet"
        assert integrator.order == 2

    def test_yoshida_integrator(self):
        """Test Yoshida integrator."""
        from sim.cosmic.integrators import Yoshida4Integrator

        integrator = Yoshida4Integrator()
        assert integrator.name == "yoshida4"
        assert integrator.order == 4

    def test_get_integrator(self):
        """Test integrator factory."""
        from sim.cosmic.integrators import get_integrator, list_integrators

        available = list_integrators()
        assert "verlet" in available
        assert "yoshida4" in available

        verlet = get_integrator("verlet")
        assert verlet.name == "verlet"

    def test_harmonic_oscillator(self):
        """Test integrator on harmonic oscillator (exact solution known)."""
        from sim.cosmic.integrators import IntegratorState, VerletIntegrator

        # Simple harmonic oscillator: a = -x
        def acceleration(positions, masses):
            return -positions

        # Initial: x=1, v=0 -> solution is x=cos(t)
        state = IntegratorState(
            positions=np.array([[1.0, 0, 0]]),
            velocities=np.array([[0.0, 0, 0]]),
            masses=np.array([1.0]),
            time=0.0,
        )

        integrator = VerletIntegrator()
        dt = 0.01

        # Integrate for 2π (one period)
        for _ in range(int(2 * np.pi / dt)):
            state = integrator.step(state, dt, acceleration)

        # Should be back near initial position
        assert_allclose(state.positions[0, 0], 1.0, atol=0.1)


class TestCosmicCalculator:
    """Test CosmicCalculator utility class."""

    def test_gravitational_constant(self):
        """Test G is correct."""
        from sim.cosmic import CosmicCalculator

        calc = CosmicCalculator()
        assert_allclose(calc.G, 6.67430e-11, rtol=1e-5)

    def test_orbital_velocity(self):
        """Test orbital velocity calculation."""
        from sim.cosmic import CosmicCalculator

        calc = CosmicCalculator()

        # Earth's orbital velocity around Sun
        M_sun = 1.989e30  # kg
        r = 1.496e11  # m (1 AU)

        v = calc.orbital_velocity(M_sun, r)

        # Should be about 30 km/s
        assert_allclose(v, 30000, rtol=0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

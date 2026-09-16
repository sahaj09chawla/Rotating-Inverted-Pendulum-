from math import pi

import pytest

from utils.config import ControllerConfig, PendulumConfig, HardwareConfig
from utils.controller import BalanceController, wrap_angle
from utils.limits import SteeringLimiter
from utils.model import State, acceleration

from utils.pid import PID

def test_pid_limit_output():
    pid = PID(10, 1, 0, output_limit=2, integral_limit=1)
    assert pid.update(1, 0, 0.01) == 2

def test_wrap_angle():
    assert abs(wrap_angle(3 * pi)) == pytest.approx(pi)

def test_controller_stops_outside_catch_range() :
    controller = BalanceController(ControllerConfig(catch_angle_rad=0.1))
    assert controller.update(0.2, 0.005) == 0


def test_model_returns_finite_accelerations():
    config = PendulumConfig(
        pendulum_mass=0.05,
        pendulum_com=0.1,
        pendulum_inertia=0.001,
        arm_length=0.1,
        arm_inertia=0.002,
    )
    alpha_ddot, theta_ddot = acceleration(State(0, 0.1, 0, 0), 0.01, config)
    assert isinstance(alpha_ddot, float)
    assert isinstance(theta_ddot, float)

def test_steering_limiter_stops_only_outward_motion_at_each_lock():
    limiter = SteeringLimiter(pi / 2)
    assert limiter.apply(1.0, pi / 2) == 0.0
    assert limiter.apply(-1.0, pi / 2) == -1.0
    assert limiter.apply(-1.0, -pi / 2) == 0.0
    assert limiter.apply(1.0, -pi / 2) == 1.0


def test_default_steering_limit_is_135_degrees_per_side():
    assert HardwareConfig().motor_angle_limit_rad == pytest.approx(3 * pi / 4)
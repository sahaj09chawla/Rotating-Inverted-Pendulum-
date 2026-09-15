from math import pi

import pytest

from utils.config import ControllerConfig, PendulumConfig
from utils.controller import BalanceController, wrap_angle
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
    alpha_ddot, theta_ddot = acceleration(State(0, 0.1, 0, 0), 0.01, PendulumConfig())
    assert isinstance(alpha_ddot, float)
    assert isinstance(theta_ddot, float)
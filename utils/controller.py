from math import atan2, cos, sin

from .config import ControllerConfig
from .pid import PID

def wrap_angle(angle_rad):
    return atan2(sin(angle_rad), cos(angle_rad))

class BalanceController:
    def __init__(self, controller_config: ControllerConfig):
        self.controller_config = controller_config
        self.pid = PID(kp=controller_config.kp,
                       ki=controller_config.ki,
                       kd=controller_config.kd,
                       output_limit=controller_config.output_limit,
                       integral_limit=controller_config.integral_limit,
                       derivative_filter=controller_config.derivative_filter
                   )

    def update(self, pendulum_angle_rad, dt):
        error_measurement = wrap_angle(pendulum_angle_rad - self.controller_config.upright_angle_rad)
        if(abs(error_measurement) > self.controller_config.catch_angle_rad):
            self.pid.reset()
            return 0.0

        return self.pid.update(0.0, error_measurement, dt)



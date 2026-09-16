from math import cos, sin

from .config import PendulumConfig

class State:
    def __init__(self, theta= 0.0, alpha_dot=0.0, theta_dot=0.0, alpha=0.0):
        self.alpha = alpha
        self.theta = theta
        self.alpha_dot = theta
        self.theta_dot = theta_dot

#fix this
def acceleration(state: State, arm_torque, pendulum_config: PendulumConfig):
    mass, pendulum_length ,arm_length = pendulum_config.pendulum_mass, pendulum_config.pendulum_com, pendulum_config.arm_length
    pendulum_inertia, arm_inertia = pendulum_config.pendulum_pivot_inertia, pendulum_config.arm_inertia
    cosine, sine = cos(state.theta), sin(state.theta)
    arm_effective_inertia= arm_inertia + mass * arm_length ** 2 + mass * pendulum_length ** 2 * sine ** 2
    coupling_inertia = mass * pendulum_length * arm_length * cosine
    pendulum_effective_inertia = pendulum_inertia
    arm_dynamics = 2.0 * mass * arm_length ** 2 + mass * pendulum_length ** 2 * sine * cosine * state.alpha_dot * state.theta_dot + mass * pendulum_length * arm_length * sine * state.theta_dot ** 2 + pendulum_config.pendulum_damping * state.theta_dot
    pendulum_dynamics = -mass * pendulum_length ** 2 * sine * cosine * state.alpha_dot ** 2 - mass * pendulum_config.gravity * pendulum_length * sine + pendulum_config.pendulum_damping * state.theta_dot
    determinant = arm_effective_inertia * pendulum_effective_inertia - coupling_inertia * coupling_inertia

    if abs(determinant) < 1e-12:
        print("singular dynamic matrix; check physical parameters")

    arm_net_torque, pendulum_net_torque = arm_torque - arm_dynamics, pendulum_dynamics

    return ((arm_net_torque * pendulum_effective_inertia - coupling_inertia * pendulum_net_torque) / determinant, (arm_effective_inertia * pendulum_net_torque - coupling_inertia * arm_net_torque) / determinant)
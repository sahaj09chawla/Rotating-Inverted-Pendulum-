from math import pi

class HardwareConfig:
    def __init__(
        self,
        stepper_pin=23,
        direction_pin=24,
        enable_pin=25,
        encoder_a_pin=17,
        encoder_b_pin=18,
        hall_effect_sensor_pin=22,
        encoder_pulses_per_revolution=600,
        encoder_decode_multiplier=4,
        stepper_full_step_per_revolution=200,
        microsteps=16,
        steps_pulse=4,
        max_step_rate=1_500.0,
        hall_active_level=0,
        hall_debounce=0.050,
        motor_angle_limit_rad=135.0 * pi / 180.0,
    ):
        self.stepper_pin = stepper_pin
        self.direction_pin = direction_pin
        self.enable_pin = enable_pin
        self.encoder_a_pin = encoder_a_pin
        self.encoder_b_pin = encoder_b_pin
        self.hall_effect_sensor_pin = hall_effect_sensor_pin
        self.encoder_pulses_per_revolution = encoder_pulses_per_revolution
        self.encoder_decode_multiplier = encoder_decode_multiplier
        self.stepper_full_step_per_revolution = stepper_full_step_per_revolution
        self.microsteps = microsteps
        self.steps_pulse = steps_pulse
        self.max_step_rate = max_step_rate
        self.hall_active_level = hall_active_level
        self.hall_debounce = hall_debounce
        self.motor_angle_limit_rad = motor_angle_limit_rad


    @property
    def encoder_counts_per_revolution(self):
        return self.encoder_pulses_per_revolution * self.encoder_decode_multiplier

    @property
    def motor_steps_per_revolution(self):
        return self.stepper_full_step_per_revolution * self.microsteps

class PendulumConfig:
    def __init__(
        self,
        pendulum_mass=0.0,
        pendulum_com=0.0,
        pendulum_inertia=0.0,
        arm_length=0.0,
        arm_inertia=0.0,
        gravity=9.80665,
        pendulum_damping=0.0008,
        arm_damping=0.0004,
    ):
        self.pendulum_mass = pendulum_mass
        self.pendulum_com = pendulum_com
        self.pendulum_inertia = pendulum_inertia
        self.arm_length = arm_length
        self.arm_inertia = arm_inertia
        self.gravity = gravity
        self.pendulum_damping = pendulum_damping
        self.arm_damping = arm_damping

    @property
    def pendulum_pivot_inertia(self):
        return self.pendulum_inertia + self.pendulum_mass * self.pendulum_com**2

class ControllerConfig:
    def __init__(
        self,
        sample_period=0.005,
        upright_angle_rad=0.0,
        kp=0.0,
        ki=0.0,
        kd=0.0,
        output_limit=0.0,
        integral_limit=0.20,
        derivative_filter=0.020,
        catch_angle_rad=20.0 * pi / 180.0,
        enable_after_homing=True,
    ):
        self.sample_period = sample_period
        self.upright_angle_rad = upright_angle_rad
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limit = output_limit
        self.integral_limit = integral_limit
        self.derivative_filter = derivative_filter
        self.catch_angle_rad = catch_angle_rad
        self.enable_after_homing = enable_after_homing

class AppConfig:
    def __init__(self, hardware=None, pendulum=None, controller=None):
        if hardware is not None:
            self.hardware = hardware
        else:
            self.hardware = HardwareConfig()

        if pendulum is not None:
            self.pendulum = pendulum
        else:
            self.pendulum = PendulumConfig()

        if controller is not None:
            self.controller = controller
        else:
            self.controller = ControllerConfig()




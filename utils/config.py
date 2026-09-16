from dataclasses import dataclass, field
from math import pi

@dataclass(frozen=True)
class HardwareConfig:
    #BCM GPIO and electrical limits for the A4998 and the 600 P/R encoder
    stepper_pin = 23
    direction_pin = 24
    enable_pin = 25 #Set the ENABLE pin in the A4998 to active low
    encoder_a_pin =  17
    encoder_b_pin = 18
    hall_effect_sensor_pin = 22 #KY-024 D0 output
    encoder_pulses_per_revolution =  600
    encoder_decode_multiplier = 4 # x4 quadrature = 2400 counts/rev
    stepper_full_step_per_revolution = 200
    microsteps = 16
    steps_pulse = 4 #A4998 needs less than or equal 1 microsecond high pulse
    max_step_rate = 1_500.0 #This value will be changed and will be tuned upwards
    hall_active_level = 0
    hall_debounce = 0.050
    motor_angle_limit = 135.0 * pi / 180.0

    @property
    def encoder_counts_per_revolution(self):
        return self.encoder_pulses_per_revolution * self.encoder_decode_multiplier

    @property
    def motor_steps_per_revolution(self):
        return self.stepper_full_step_per_revolution * self.microsteps

@dataclass(frozen=True)
class PendulumConfig:
    pendulum_mass = 0.0000
    pendulum_com = 0.000 #Pivot to pendulum centre of mass
    pendulum_inertia = 0.00000 #about its center of mass
    arm_length = 0.0000 #Base axis to pendulum pivot
    arm_inertia =  0.0000 #Rotor + arm about vertical axis
    gravity =  9.80665
    pendulum_damping = 0.0008
    arm_damping = 0.0004

    @property
    def pendulum_pivot_inertia(self):
        return self.pendulum_inertia + self.pendulum_mass * self.pendulum_com**2

@dataclass(frozen=True)
class ControllerConfig:
    sample_period = 0.005 #200 Hz control loop
    upright_angle_rad = 0.0
    kp  = 0.0
    ki = 0.0
    kd= 0.0
    output_limit_rad = 0.0 #arm velocity
    integral_limit= 0.20
    derivative_filter_tau = 0.020
    catch_angle_rad = 20.0 * pi / 180.0
    enable_after_homing = True

@dataclass(frozen=True)
class AppConfig:
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    pendulum: PendulumConfig = field(default_factory=PendulumConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)




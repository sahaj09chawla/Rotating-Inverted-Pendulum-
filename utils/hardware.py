import threading
import time
from math import pi
from .config import HardwareConfig
from .limits import SteeringLimiter

import pigpio

class QuadratureEncoder:
    TRANSITIONS = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, -1, 0)

    def __init__(self, pi_handle, pin_a, pin_b, counts_per_revolution):
        self.pi_handle, self.pin_a, self.pin_b = pi_handle, pin_a, pin_b
        self.counts_per_revolution = counts_per_revolution
        self.count = 0
        self.lock = threading.Lock()

        self.pi_handle.set_mode(self.pin_a, pigpio.INPUT)
        self.pi_handle.set_mode(self.pin_b, pigpio.INPUT)
        self.pi_handle.set_pull_up_down(self.pin_a, pigpio.PUD_UP)
        self.pi_handle.set_pull_up_down(self.pin_b, pigpio.PUD_UP)

        self.state = (self.pi_handle.read(self.pin_a) << 1) | self.pi_handle.read(self.pin_b)

        self.callback_a = self.pi_handle.callback(self.pin_a, pigpio.EITHER_EDGE, self.edge)
        self.callback_b = self.pi_handle.callback(self.pin_b, pigpio.EITHER_EDGE, self.edge)

        self.callback = (self.callback_a, self.callback_b)


    def edge(self, pin, level, tick):
        new_state = (self.pi_handle.read(self.pin_a) << 1 | self.pi_handle.read(self.pin_b))
        with self.lock:
            self.count += self.TRANSITIONS[(self.state << 2) | new_state]
            self.state = new_state

    @property
    def angle_rad(self):
        with self.lock:
            return self.count * 2.0 * pi / self.counts_per_revolution

    def zero(self):
        with self.lock:
            self.count = 0

    def close(self):
        for callback in self.callback:
            callback.cancel()

class A4998Stepper:
    def __init__(self, pi_handle, hardware_config: HardwareConfig, position_encoder=None):
        self.pi_handle, self.hardware_config = pi_handle, hardware_config
        for pin in (hardware_config.stepper_pin, hardware_config.direction_pin):
            self.pi_handle.set_mode(pin, pigpio.OUTPUT)
        if hardware_config.enable_pin is not None:
            self.pi_handle.set_mode(hardware_config.enable_pin, pigpio.OUTPUT)
            self.pi_handle.write(hardware_config.enable_pin, 1)

        self.rate_hz = 0.0
        self.request_velocity = 0.0
        self.position_encoder = position_encoder
        self.steering_limiter = SteeringLimiter(hardware_config.motor_angle_limit)
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def limit_velocity(self, velocity):
        if self.position_encoder is None:
            return velocity
        return self.steering_limiter.apply(velocity, self.position_encoder.angle_rad)

    def set_active_velocity_locked(self, velocity):
        velocity = self.limit_velocity(velocity)
        rate = abs(velocity) * self.hardware_config.motor_steps_per_revolution / (2.0 * pi)
        if velocity:
            self.pi_handle.write(self.hardware_config.direction_pin, int(velocity >0))
        self.rate_hz = min(rate, self.hardware_config.max_step_rate)
        if self.hardware_config.enable_pin is not None:
            if self.rate_hz:
                self.pi_handle.write(self.hardware_config.enable_pin, 0)
            else:
                self.pi_handle.write(self.hardware_config.enable_pin, 1)

    def set_velocity(self, velocity):
        with self.lock:
            self.request_velocity = velocity
            self.set_active_velocity_locked(velocity)

    def run(self):
        while not self.stop.is_set():
            with self.lock:
                rate = self.rate_hz
            if rate <= 0:
                self.stop.wait(0.002)
                continue
            period  = 1.0 / rate
            self.pi_handle.write(self.hardware_config.stepper_pin, 1)
            time.sleep(self.hardware_config.steps_pulse / 1_000_000)
            self.pi_handle.write(self.hardware_config.stepper_pin, 0)
            self.stop.wait(max(0.0, period - self.hardware_config.steps_pulse / 1_000_000))

    def close(self):
        self.set_velocity(0.0)
        self.stop.set()
        self.thread.join(timeout=1)
        if self.hardware_config.enable_pin is not None:
            self.pi_handle.write(self.hardware_config.enable_pin, 1)

class HallReference:
    def __init__(self, pi_handle, pin, active_level, debounce, encoder: QuadratureEncoder):
        self.pi_handle, self.pin = pi_handle, pin
        self.active, self.debounce = active_level, debounce
        self.encoder = encoder
        self.last_event = 0.0
        self._referenced = pi_handle.read(self.pin) == active_level
        self._lock = threading.Lock()
        if self.referenced:
            encoder.zero()
        self.callback = pi_handle.callback(self.pin, pigpio.EITHER_EDGE, self.edge)

    def edge(self, pin, level, tick):
        now = time.monotonic()
        if level == self.active and now - self.last_event >= self.debounce:
            self.last_event = now
            self.encoder.zero()
            with self._lock:
                self._referenced = True

    @property
    def referenced(self):
        with self._lock:
            return self.referenced

    def close(self):
        self.callback.cancel()

def connect(hardware_config: HardwareConfig):
    pi_handle = pigpio.pi()
    if not pi_handle.connected:
        print("Cannot connect to pigpiod; run: sudo systemct1 enable --now pigpiod")
    for pin in (hardware_config.encoder_a_pin, hardware_config.encoder_b_pin, hardware_config.hall_effect_sensor_pin):
        pi_handle.set_mode(pin, pigpio.INPUT)
        pi_handle.set_pull_up_down(pin, pigpio.PUD_UP)
    encoder = QuadratureEncoder(pi_handle, hardware_config.encoder_a_pin, hardware_config.encoder_b_pin, hardware_config.encoder_counts_per_revolution)

    hall_reference  = HallReference(pi_handle, hardware_config.hall_effect_sensor_pin, hardware_config.hall_active_level, hardware_config.hall_debounce, encoder)
    motor = A4998Stepper(pi_handle, hardware_config, position_encoder=encoder)
    return pi_handle, encoder, motor, hall_reference

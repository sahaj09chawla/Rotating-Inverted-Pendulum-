import threading
import time
from math import pi
from .config import HardwareConfig
from .limits import SteeringLimiter
from gpiozero import DigitalInputDevice, DigitalOutputDevice

class QuadratureEncoder:
    TRANSITIONS = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, -1, 0)

    def __init__(self, pi_handle, pin_a, pin_b, counts_per_revolution):
        self.pin_a = DigitalInputDevice(pin_a, pull_up=True)
        self.pin_b = DigitalInputDevice(pin_b, pull_up=True)
        self.counts_per_revolution = counts_per_revolution
        self.count = 0
        self.lock = threading.Lock()
        self.state = self._read_state()

        self.pin_a.when_changed = self.edge
        self.pin_b.when_changed = self.edge

    def _read_state(self):
        return (int(self.pin_a.value) << 1) | int(self.pin_b.value)


    def edge(self):
        new_state = self._read_state()
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
        self.pin_a.when_changed = None
        self.pin_b.when_changed = None
        self.pin_a.close()
        self.pin_b.close()

class A4998Stepper:
    def __init__(self, hardware_config: HardwareConfig, position_encoder=None):
        self.hardware_config = hardware_config
        self.step_pin = DigitalOutputDevice(hardware_config.stepper_pin, initial_value=False)
        self.direction_pin = DigitalOutputDevice(hardware_config.direction_pin, initial_value=False)
        self.enable_pin = (
            DigitalOutputDevice(hardware_config.enable_pin, initial_value=True)
            if hardware_config.enable_pin is not None
            else None
        )

        self.rate_hz = 0.0
        self.request_velocity = 0.0
        self.position_encoder = position_encoder
        self.steering_limiter = SteeringLimiter(hardware_config.motor_angle_limit_rad)
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
            self.direction_pin.value = int(velocity > 0)
        self.rate_hz = min(rate, self.hardware_config.max_step_rate)
        if self.enable_pin is not None:
            self.enable_pin.value = int(not self.rate_hz)

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
            self.step_pin.on()
            time.sleep(self.hardware_config.steps_pulse / 1_000_000)
            self.step_pin.off()
            self.stop.wait(max(0.0, period - self.hardware_config.steps_pulse / 1_000_000))

    def close(self):
        self.set_velocity(0.0)
        self.stop.set()
        self.thread.join(timeout=1)
        if self.enable_pin is not None:
            self.enable_pin.on()
            self.enable_pin.close()
        self.step_pin.close()
        self.direction_pin.close()

class HallReference:
    def __init__(self, pin, active_level, debounce, encoder: QuadratureEncoder):
        self.pin = DigitalInputDevice(pin, pull_up=True)
        self.active, self.debounce = active_level, debounce
        self.encoder = encoder
        self.last_event = 0.0
        self._referenced = int(self.pin.value) == active_level
        self._lock = threading.Lock()
        if self.referenced:
            encoder.zero()
        self.pin.when_changed = self.edge

    def edge(self):
        now = time.monotonic()
        if int(self.pin.value) == self.active and now - self.last_event >= self.debounce:
            self.last_event = now
            self.encoder.zero()
            with self._lock:
                self._referenced = True

    @property
    def referenced(self):
        with self._lock:
            return self._referenced

    def close(self):
        self.pin.when_changed = None
        self.pin.close()

def connect(hardware_config: HardwareConfig):
    encoder = QuadratureEncoder(hardware_config.encoder_a_pin, hardware_config.encoder_b_pin, hardware_config.encoder_counts_per_revolution)

    hall_reference  = HallReference(hardware_config.hall_effect_sensor_pin, hardware_config.hall_active_level, hardware_config.hall_debounce, encoder)
    motor = A4998Stepper(hardware_config, position_encoder=encoder)
    return encoder, motor, hall_reference

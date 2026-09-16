import signal
import time
from utils.config import AppConfig
from utils.controller import BalanceController
from utils.hardware import connect

def main():
    app_config = AppConfig()
    controller = BalanceController(app_config.controller)
    pi_handle, encoder, motor, hall_reference = connect(app_config.hardware)
    running = True

    def stop(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    last = time.monotonic()
    print("Controller Started, The Hall Effect Sensor establish zero for motor,limited to the configured travel on either side. Ctrl-C stops motor")
    try:
        while running:
            now = time.monotonic()
            dt = now - last
            if dt >= app_config.controller.sample_period:
                last = now
                if app_config.controller.enable_after_homing and not hall_reference:
                    motor.set_velocity(0.0)

                else:
                    motor.set_velocity(controller.update(encoder.angle_rad, dt))
            else:
                time.sleep(0.0005)

    finally:
        motor.close()
        hall_reference.close()
        encoder.close()
        pi_handle.close()

if __name__ == '__main__':
    main()



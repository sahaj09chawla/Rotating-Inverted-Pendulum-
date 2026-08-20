import sys
import time
import config
from RpiMotorLib import  RpiMotorLib
from RpiMotorLib.rpi_emergency_stop import EmergencyStop

stepper_motor = RpiMotorLib.A4988Nema(config.DIRECTION, config.STEP, config.GPIO_PINS, "A4988")
estop = EmergencyStop(gpio_pins=26, stop_callable=stepper_motor.motor_stop, verbose=True)


GPIO_PINS = (14, 15, 25)
DIRECTION = 24
STEP = 23

steps_per_rev = 200
max_speed = 1200
current_angle = 0.0
range_angle = 200.0
degrees_per_step = 360.0 /steps_per_rev
speed = 0.0
homing_speed = 2000.0
direction = False
step_count = 0
episode_done = 0
homing = False
hall_sensor_debounce = 0
hall_sensor_centering = False

time_step = 5.0
theta_dot = 0.0
old_theta = 0.0

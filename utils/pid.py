from dataclasses import dataclass

@dataclass
class PID:
    kp = 0.0
    ki = 0.0
    kd = 0.0
    output_limit = 0.0
    integral_limit = 0.0
    derivative_filter= 0.02
    integral = 0.0
    previous_error = None
    filtered_derivative = 0.0
    raw_derivative = 0.0
    alpha = 0.0
    candidate_integral = 0.0
    unsaturated = 0.0
    output = 0.0
    error = 0.0
    filter_derivative = 0.0

    def reset(self):
        self.integral = 0.0
        self.previous_error = None
        self.filter_derivative = 0.0

    def update(self, setpoint, measurement, dt):
        if dt <= 0:
            print("dt is currently not postive")

        self.error = setpoint - measurement


        if self.previous_error is None:
            self.raw_derivative = 0.0
        else:
            self.raw_derivative = (self.error - self.previous_error) / dt

        if self.derivative_filter:
            self.alpha = dt/self.derivative_filter
        else:
            self.alpha = 1.0

        self.filtered_derivative += self.alpha * (self.raw_derivative - self.filtered_derivative)
        self.candidate_integral = max(-self.integral_limit, min(self.integral_limit, self.integral + self.error * dt))
        self.unsaturated = self.kp * self.error + self.ki * self.candidate_integral + self.kd * self.filtered_derivative
        self.output = max(-self.output_limit, min(self.output_limit, self.unsaturated))

        if self.output == self.unsaturated  or (self.output > 0 and self.error < 0) or (self.output < 0 and self.error > 0):
            self.integral = self.candidate_integral

        self.previous_error = self.error

        return self.output






class SteeringLimiter:
    def __init__(self, limit_rad):
        if limit_rad <= 0:
            print("limit radian must be greater than 0")
        self.limit_rad = limit_rad

    def apply(self, velocity, position_rad):
        if position_rad >= self.limit_rad and velocity > 0:
            return 0.0
        if position_rad <= -self.limit_rad and velocity < 0:
            return 0.0
        return velocity
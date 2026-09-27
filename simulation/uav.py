import math

from scenarios.gc1_config import MAX_SPEED_MPS, MAX_FLIGHT_TIME_S


class UAV:
    def __init__(self, uav_id, x, y, speed=MAX_SPEED_MPS, battery=MAX_FLIGHT_TIME_S):
        self.id = uav_id
        self.x = float(x)
        self.y = float(y)
        self.speed = min(float(speed), MAX_SPEED_MPS)
        self.battery = float(battery)
        self.flight_time_used = 0.0
        self.status = "ACTIVE"
        self.communication_status = True
        self.current_task = None
        self.phase = "LAUNCH"
        self.detected_poi = False
        self.path = []
        self.path_index = 0
        self.altitude_m = 50.0
        self.failure_reason = None

    def distance_to(self, x, y):
        return math.hypot(self.x - x, self.y - y)

    def assign_task(self, task_id):
        self.current_task = task_id
        self.phase = "TO_POI"
        self.detected_poi = False

    def clear_task(self):
        self.current_task = None
        self.phase = "IDLE"
        self.detected_poi = False
        self.path = []
        self.path_index = 0

    def move_to_position(self, x, y, dt_seconds):
        if self.status != "ACTIVE":
            return False
        distance = self.distance_to(x, y)
        if distance <= 0.0001:
            return False
        travel = min(self.speed * dt_seconds, distance)
        ratio = travel / distance
        self.x += (x - self.x) * ratio
        self.y += (y - self.y) * ratio
        self.flight_time_used += dt_seconds
        self.battery = max(0.0, MAX_FLIGHT_TIME_S - self.flight_time_used)
        if self.flight_time_used >= MAX_FLIGHT_TIME_S:
            self.fail("FLIGHT_TIME_LIMIT")
        return True

    def move_towards(self, x, y, dt_seconds):
        return self.move_to_position(x, y, dt_seconds)

    def fail(self, reason="TECHNICAL_FAILURE"):
        self.status = "FAILED"
        self.failure_reason = reason

    def is_available(self):
        return self.status == "ACTIVE" and self.current_task is None

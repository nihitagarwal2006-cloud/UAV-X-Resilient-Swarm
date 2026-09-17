class UAV:

    def __init__(self, uav_id, x, y, speed=5, battery=100):
        self.id = uav_id
        self.x = x
        self.y = y
        self.speed = speed
        self.battery = battery

        self.status = "ACTIVE"
        self.current_task = None

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.battery -= 1

    def assign_task(self, task_id):
        self.current_task = task_id

    def complete_task(self):
        self.current_task = None

    def fail(self):
        self.status = "FAILED"

    def is_available(self):
        return self.status == "ACTIVE" and self.current_task is None
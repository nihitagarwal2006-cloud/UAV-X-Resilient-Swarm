class UAV:

    def __init__(self, uav_id, x, y, speed=5, battery=100):
        self.id = uav_id
        self.x = x
        self.y = y
        self.speed = speed
        self.battery = battery

        self.status = "ACTIVE"
        self.current_task = None
        self.path = []
        self.path_index = 0

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.battery -= 1

    def assign_task(self, task_id):
        self.current_task = task_id

    def complete_task(self):
        self.current_task = None
        self.path = []
        self.path_index = 0

    def set_path(self, path):
        self.path = path
        self.path_index = 1

    def move_one_step(self):

        if self.path_index >= len(self.path):
            return False

        x, y = self.path[self.path_index]

        self.move_to(x, y)

        self.path_index += 1

        return True

    def fail(self):
        self.status = "FAILED"

    def is_available(self):
        return self.status == "ACTIVE" and self.current_task is None
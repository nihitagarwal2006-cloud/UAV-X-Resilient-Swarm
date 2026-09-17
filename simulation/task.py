class Task:

    def __init__(self, task_id, x, y, priority="MEDIUM"):
        self.id = task_id
        self.x = x
        self.y = y
        self.priority = priority

        self.status = "UNASSIGNED"
        self.assigned_uav = None

    def assign(self, uav_id):
        self.assigned_uav = uav_id
        self.status = "ASSIGNED"

    def complete(self):
        self.status = "COMPLETED"
        self.assigned_uav = None

    def cancel(self):
        self.status = "CANCELLED"
        self.assigned_uav = None
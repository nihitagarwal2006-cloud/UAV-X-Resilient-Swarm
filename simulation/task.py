class Task:
    PRIORITY_WEIGHT = {"HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}

    def __init__(self, task_id, x, y, priority="MEDIUM"):
        self.id = task_id
        self.x = float(x)
        self.y = float(y)
        self.priority = priority
        self.priority_weight = self.PRIORITY_WEIGHT.get(str(priority).upper(), 1.0)
        self.status = "UNASSIGNED"
        self.assigned_uav = None
        self.detected = False
        self.reported = False
        self.recovery_pending = False

    def assign(self, uav_id):
        self.assigned_uav = uav_id
        self.status = "ASSIGNED"

    def mark_detected(self):
        self.detected = True
        self.status = "DETECTED"

    def mark_reported(self):
        self.reported = True
        self.status = "REPORTED"

    def complete(self):
        self.status = "COMPLETED"
        self.assigned_uav = None

    def cancel(self):
        self.status = "CANCELLED"
        self.assigned_uav = None

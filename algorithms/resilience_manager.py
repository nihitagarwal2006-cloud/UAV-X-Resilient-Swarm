from algorithms.recovery import RecoveryManager


class ResilienceManager:
    def __init__(self):
        self.recovery = RecoveryManager()

    def recover(self, uavs, failed_uav_id, task, connections=None):
        replacement = self.recovery.find_replacement(
            uavs, failed_uav_id, task, connections
        )
        if replacement is None:
            return None
        replacement.assign_task(task.id)
        task.assign(replacement.id)
        return replacement

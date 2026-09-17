import math

from algorithms.path_planning import AStarPlanner


class RecoveryManager:

    def __init__(self):
        self.path_planner = AStarPlanner(20, 20)

    def distance(self, uav, task):
        dx = uav.x - task.x
        dy = uav.y - task.y
        return math.sqrt(dx * dx + dy * dy)

    def find_replacement(self, uavs, failed_uav_id, task):

        candidates = [
            uav for uav in uavs
            if uav.id != failed_uav_id
            and uav.is_available()
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda uav: self.distance(uav, task)
        )

    def recover_task(self, uavs, failed_uav_id, task, obstacles=None):

        if obstacles is None:
            obstacles = []

        replacement = self.find_replacement(
            uavs,
            failed_uav_id,
            task
        )

        if replacement is None:
            return None

        replacement.assign_task(task.id)
        task.assign(replacement.id)

        path = self.path_planner.plan(
            (replacement.x, replacement.y),
            (task.x, task.y),
            obstacles
        )

        replacement.set_path(path)

        return replacement
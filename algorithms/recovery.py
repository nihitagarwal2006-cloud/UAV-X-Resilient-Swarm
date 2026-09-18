import math

from algorithms.path_planning import AStarPlanner


class RecoveryManager:

    def __init__(self):
        self.path_planner = AStarPlanner(20, 20)

    def distance(self, uav, task):
        dx = uav.x - task.x
        dy = uav.y - task.y

        return math.sqrt(dx * dx + dy * dy)

    def find_replacement(
        self,
        uavs,
        failed_uav_id,
        task,
        connections=None
    ):

        candidates = [
            uav for uav in uavs
            if uav.id != failed_uav_id
            and uav.is_available()
        ]

        if connections is not None:

            connected_candidates = []

            for uav in candidates:

                for node_id, neighbors in connections.items():

                    if node_id == failed_uav_id:
                        continue

                    if uav.id in neighbors:
                        connected_candidates.append(uav)
                        break

            if connected_candidates:
                candidates = connected_candidates

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda uav: self.distance(uav, task)
        )

    def recover_task(
        self,
        uavs,
        failed_uav_id,
        task,
        obstacles=None,
        connections=None
    ):

        if obstacles is None:
            obstacles = []

        replacement = self.find_replacement(
            uavs,
            failed_uav_id,
            task,
            connections
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

        if not path:
            replacement.complete_task()
            task.status = "UNASSIGNED"
            task.assigned_uav = None
            return None

        replacement.set_path(path)

        return replacement
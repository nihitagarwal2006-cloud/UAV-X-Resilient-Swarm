import math


PRIORITY_WEIGHT = {
    "HIGH": 3.0,
    "MEDIUM": 2.0,
    "LOW": 1.0,
}


class TaskAllocator:
    """Priority-aware autonomous task allocation."""

    @staticmethod
    def distance(uav, task):
        return math.hypot(uav.x - task.x, uav.y - task.y)

    @staticmethod
    def priority_weight(task):
        return PRIORITY_WEIGHT.get(str(task.priority).upper(), 1.0)

    def allocate(self, uavs, tasks):
        assignments = {}
        waiting = [t for t in tasks if t.status == "UNASSIGNED"]
        waiting.sort(key=lambda t: (-self.priority_weight(t), t.id))

        for task in waiting:
            available = [u for u in uavs if u.is_available()]
            if not available:
                break

            # Lower score is better: distance is balanced against task priority.
            selected = min(
                available,
                key=lambda u: self.distance(u, task) / self.priority_weight(task),
            )
            selected.assign_task(task.id)
            task.assign(selected.id)
            assignments[task.id] = selected.id

        return assignments

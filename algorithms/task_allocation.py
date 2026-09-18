import math


class TaskAllocator:

    def distance(self, uav, task):
        dx = uav.x - task.x
        dy = uav.y - task.y

        return math.sqrt(dx * dx + dy * dy)

    def allocate(self, uavs, tasks):

        assignments = {}

        for task in tasks:

            available_uavs = [
                uav for uav in uavs
                if uav.is_available()
            ]

            if not available_uavs:
                break

            selected_uav = min(
                available_uavs,
                key=lambda uav: self.distance(uav, task)
            )

            selected_uav.assign_task(task.id)
            task.assign(selected_uav.id)

            assignments[task.id] = selected_uav.id

        return assignments
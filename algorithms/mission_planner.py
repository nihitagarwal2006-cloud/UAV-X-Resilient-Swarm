from algorithms.task_allocation import TaskAllocator
from algorithms.path_planning import AStarPlanner


class MissionPlanner:

    def __init__(self):
        self.allocator = TaskAllocator()
        self.path_planner = AStarPlanner(20, 20)

    def plan_mission(self, uavs, tasks, obstacles):

        assignments = self.allocator.allocate(uavs, tasks)

        mission = {}

        for task in tasks:

            if task.id not in assignments:
                continue

            uav_id = assignments[task.id]

            uav = next(
                uav for uav in uavs
                if uav.id == uav_id
            )

            start = (uav.x, uav.y)
            goal = (task.x, task.y)

            path = self.path_planner.plan(
                start,
                goal,
                obstacles
            )

            mission[task.id] = {
                "uav": uav.id,
                "path": path
            }

        return mission
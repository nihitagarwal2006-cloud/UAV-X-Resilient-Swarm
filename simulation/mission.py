from algorithms.mission_planner import MissionPlanner
from algorithms.resilience_manager import ResilienceManager


class Mission:

    def __init__(self, uavs, tasks, obstacles=None):
        self.uavs = uavs
        self.tasks = tasks
        self.obstacles = obstacles or []

        self.planner = MissionPlanner()
        self.resilience = ResilienceManager()

        self.step_count = 0

    def start(self):

        mission = self.planner.plan_mission(
            self.uavs,
            self.tasks,
            self.obstacles
        )

        for task_id, data in mission.items():

            uav = next(
                uav for uav in self.uavs
                if uav.id == data["uav"]
            )

            uav.set_path(data["path"])

        print("MISSION STARTED")

    def step(self):

        self.step_count += 1

        for uav in self.uavs:

            if uav.status != "ACTIVE":
                continue

            if uav.path_index >= len(uav.path):
                continue

            uav.move_one_step()

            print(
                f"UAV {uav.id} -> "
                f"({uav.x}, {uav.y})"
            )

            if uav.path_index >= len(uav.path):

                task = next(
                    (
                        task for task in self.tasks
                        if task.assigned_uav == uav.id
                    ),
                    None
                )

                if task:

                    task.complete()
                    uav.complete_task()

                    print(
                        f"Task {task.id} completed by "
                        f"UAV {uav.id}"
                    )

    def fail_uav(self, uav_id):

        uav = next(
            (
                uav for uav in self.uavs
                if uav.id == uav_id
            ),
            None
        )

        if uav is None:
            return

        if uav.status != "ACTIVE":
            return

        uav.fail()

        print(
            f"UAV {uav_id} FAILED "
            f"at mission step {self.step_count}"
        )

        replacement = self.resilience.handle_failure(
            self.uavs,
            uav_id,
            self.tasks,
            self.obstacles
        )

        if replacement:

            print(
                f"Recovery: UAV {replacement.id} "
                f"taking over the task"
            )

        else:

            print(
                "Recovery failed: "
                "no replacement UAV available"
            )

    def is_complete(self):

        return all(
            task.status == "COMPLETED"
            for task in self.tasks
        )
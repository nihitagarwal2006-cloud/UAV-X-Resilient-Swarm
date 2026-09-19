class MissionMetrics:

    def __init__(self):

        self.total_tasks = 0
        self.completed_tasks = 0

        self.uav_failures = 0
        self.recovery_events = 0
        self.communication_failures = 0

        self.mission_steps = 0

        self.failed_uavs = []
        self.recovered_tasks = []

    # =====================================
    # MISSION
    # =====================================

    def initialize(self, tasks):

        self.total_tasks = len(tasks)

    def update_task_status(self, tasks):

        self.total_tasks = len(tasks)

        self.completed_tasks = sum(
            task.status == "COMPLETED"
            for task in tasks
        )

    # =====================================
    # UAV FAILURE
    # =====================================

    def record_uav_failure(self, uav_id):

        self.uav_failures += 1

        if uav_id not in self.failed_uavs:

            self.failed_uavs.append(uav_id)

    # =====================================
    # RECOVERY
    # =====================================

    def record_recovery(
        self,
        task_id,
        replacement_uav_id
    ):

        self.recovery_events += 1

        self.recovered_tasks.append(
            {
                "task_id": task_id,
                "uav_id": replacement_uav_id
            }
        )

    # =====================================
    # COMMUNICATION FAILURE
    # =====================================

    def record_communication_failure(
        self,
        uav_id
    ):

        self.communication_failures += 1

    # =====================================
    # SIMULATION STEP
    # =====================================

    def update_step(self, step):

        self.mission_steps = step

    # =====================================
    # SUMMARY
    # =====================================

    def get_summary(self):

        completion_rate = 0

        if self.total_tasks > 0:

            completion_rate = (
                self.completed_tasks
                / self.total_tasks
            ) * 100

        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "completion_rate": completion_rate,
            "uav_failures": self.uav_failures,
            "recovery_events": self.recovery_events,
            "communication_failures":
                self.communication_failures,
            "mission_steps": self.mission_steps,
            "failed_uavs":
                self.failed_uavs,
            "recovered_tasks":
                self.recovered_tasks
        }

    # =====================================
    # PRINT SUMMARY
    # =====================================

    def print_summary(self):

        summary = self.get_summary()

        print("\n========================================")
        print("MISSION METRICS")
        print("========================================")

        print(
            f"Total Tasks: "
            f"{summary['total_tasks']}"
        )

        print(
            f"Completed Tasks: "
            f"{summary['completed_tasks']}"
        )

        print(
            f"Completion Rate: "
            f"{summary['completion_rate']:.1f}%"
        )

        print(
            f"UAV Failures: "
            f"{summary['uav_failures']}"
        )

        print(
            f"Recovery Events: "
            f"{summary['recovery_events']}"
        )

        print(
            f"Communication Failures: "
            f"{summary['communication_failures']}"
        )

        print(
            f"Mission Steps: "
            f"{summary['mission_steps']}"
        )

        print(
            "========================================"
        )
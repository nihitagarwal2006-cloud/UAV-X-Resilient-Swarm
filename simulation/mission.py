from algorithms.mission_planner import MissionPlanner
from algorithms.resilience_manager import ResilienceManager
from communication.network import CommunicationNetwork
from communication.heartbeat import HeartbeatMonitor
from communication.uav_state import UAVState
from simulation.metrics import MissionMetrics


class Mission:

    def __init__(
        self,
        uavs,
        tasks,
        obstacles=None,
        failure_simulator=None
    ):

        self.uavs = uavs
        self.tasks = tasks
        self.obstacles = obstacles or []

        self.planner = MissionPlanner()
        self.resilience = ResilienceManager()

        self.network = CommunicationNetwork(
            communication_range=6
        )

        self.connections = {}

        self.step_count = 0

        self.heartbeat_monitor = HeartbeatMonitor(
            timeout=3
        )

        self.failure_simulator = failure_simulator

        self.uav_states = {
            uav.id: UAVState(uav.id)
            for uav in self.uavs
        }

        # =====================================
        # MISSION METRICS
        # =====================================

        self.metrics = MissionMetrics()

        self.metrics.initialize(
            self.tasks
        )

        self.communication_failures_recorded = set()

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

            if data["path"]:
                uav.set_path(
                    data["path"]
                )

        self.connections = (
            self.network.update_connections(
                [
                    uav
                    for uav in self.uavs
                    if uav.status == "ACTIVE"
                ]
            )
        )

        self.metrics.update_task_status(
            self.tasks
        )

        print("MISSION STARTED")

        print(
            "\nINITIAL COMMUNICATION NETWORK:"
        )

        print(self.connections)

    def add_task(self, task):

        print(
            f"\nNEW TASK CREATED: "
            f"Task {task.id} "
            f"at ({task.x}, {task.y})"
        )

        self.tasks.append(task)

        mission = self.planner.plan_mission(
            self.uavs,
            [task],
            self.obstacles
        )

        if task.id not in mission:

            print(
                f"No available UAV for "
                f"Task {task.id}"
            )

            self.tasks.remove(task)

            return False

        data = mission[task.id]

        uav = next(
            uav for uav in self.uavs
            if uav.id == data["uav"]
        )

        path = data["path"]

        if not path:

            print(
                f"No valid path found for "
                f"Task {task.id}"
            )

            task.status = "UNASSIGNED"
            task.assigned_uav = None

            self.tasks.remove(task)

            return False

        # =====================================
        # TASK ALREADY AT UAV LOCATION
        # =====================================

        if len(path) == 1:

            task.complete()

            print(
                f"Task {task.id} completed "
                f"immediately by UAV {uav.id}"
            )

            self.metrics.update_task_status(
                self.tasks
            )

            self.connections = (
                self.network.update_connections(
                    [
                        active_uav
                        for active_uav in self.uavs
                        if active_uav.status == "ACTIVE"
                    ]
                )
            )

            return True

        # =====================================
        # NORMAL TASK ASSIGNMENT
        # =====================================

        uav.set_path(path)

        print(
            f"Task {task.id} assigned to "
            f"UAV {uav.id}"
        )

        print(
            f"UAV {uav.id} travelling to "
            f"({task.x}, {task.y})"
        )

        self.metrics.update_task_status(
            self.tasks
        )

        self.connections = (
            self.network.update_connections(
                [
                    active_uav
                    for active_uav in self.uavs
                    if active_uav.status == "ACTIVE"
                ]
            )
        )

        return True

    def step(self):

        self.step_count += 1

        self.metrics.update_step(
            self.step_count
        )

        # =====================================
        # UPDATE HEARTBEATS
        # =====================================

        for uav in self.uavs:

            if uav.status == "ACTIVE":

                state = self.uav_states[
                    uav.id
                ]

                if state.communication_status:

                    state.update_heartbeat(
                        self.step_count
                    )

        print(
            f"Heartbeat check at step "
            f"{self.step_count}"
        )

        # =====================================
        # RECORD COMMUNICATION FAILURES
        # =====================================

        for uav in self.uavs:

            state = self.uav_states[
                uav.id
            ]

            if (
                not state.communication_status
                and
                uav.id
                not in self.communication_failures_recorded
            ):

                self.metrics.record_communication_failure(
                    uav.id
                )

                self.communication_failures_recorded.add(
                    uav.id
                )

        # =====================================
        # HEARTBEAT TIMEOUT
        # =====================================

        active_states = [
            self.uav_states[uav.id]
            for uav in self.uavs
            if uav.status == "ACTIVE"
        ]

        failed_uavs = (
            self.heartbeat_monitor.check(
                active_states,
                self.step_count
            )
        )

        for uav_id in failed_uavs:

            print(
                f"Heartbeat timeout detected "
                f"for UAV {uav_id}"
            )

            self.fail_uav(
                uav_id
            )

        # =====================================
        # TECHNICAL FAILURE
        # =====================================

        if self.failure_simulator:

            for uav in self.uavs:

                if uav.status != "ACTIVE":
                    continue

                if self.failure_simulator.check_failure(
                    self.step_count,
                    uav
                ):

                    self.fail_uav(
                        uav.id
                    )

        old_connections = (
            self.connections.copy()
        )

        # =====================================
        # MOVE ACTIVE UAVs
        # =====================================

        for uav in self.uavs:

            if uav.status != "ACTIVE":
                continue

            if uav.path_index >= len(
                uav.path
            ):
                continue

            uav.move_one_step()

            print(
                f"UAV {uav.id} -> "
                f"({uav.x}, {uav.y})"
            )

            if (
                uav.path_index
                >= len(uav.path)
            ):

                task = next(
                    (
                        task
                        for task in self.tasks
                        if task.assigned_uav
                        == uav.id
                    ),
                    None
                )

                if task:

                    task.complete()

                    uav.complete_task()

                    print(
                        f"Task {task.id} "
                        f"completed by "
                        f"UAV {uav.id}"
                    )

        # =====================================
        # UPDATE METRICS
        # =====================================

        self.metrics.update_task_status(
            self.tasks
        )

        # =====================================
        # UPDATE COMMUNICATION NETWORK
        # =====================================

        self.connections = (
            self.network.update_connections(
                [
                    uav
                    for uav in self.uavs
                    if uav.status == "ACTIVE"
                ]
            )
        )

        lost_links, new_links = (
            self.network.get_link_changes(
                old_connections
            )
        )

        if lost_links:

            print(
                f"Communication links lost: "
                f"{lost_links}"
            )

        if new_links:

            print(
                f"Communication links restored: "
                f"{new_links}"
            )

    def fail_uav(self, uav_id):

        uav = next(
            (
                uav
                for uav in self.uavs
                if uav.id == uav_id
            ),
            None
        )

        if uav is None:
            return

        if uav.status != "ACTIVE":
            return

        uav.fail()

        # =====================================
        # RECORD UAV FAILURE
        # =====================================

        self.metrics.record_uav_failure(
            uav_id
        )

        print(
            f"\nUAV {uav_id} FAILED "
            f"at mission step "
            f"{self.step_count}"
        )

        self.connections = (
            self.network.update_connections(
                [
                    uav
                    for uav in self.uavs
                    if uav.status == "ACTIVE"
                ]
            )
        )

        # =====================================
        # RESILIENCE / RECOVERY
        # =====================================

        replacement = (
            self.resilience.handle_failure(
                self.uavs,
                uav_id,
                self.tasks,
                self.obstacles,
                self.connections
            )
        )

        if replacement:

            recovered_task = next(
                (
                    task
                    for task in self.tasks
                    if task.assigned_uav
                    == replacement.id
                    and task.status
                    == "ASSIGNED"
                ),
                None
            )

            if recovered_task:

                self.metrics.record_recovery(
                    recovered_task.id,
                    replacement.id
                )

            print(
                f"Recovery: UAV "
                f"{replacement.id} "
                f"taking over the task"
            )

        else:

            print(
                "Recovery failed: "
                "no suitable replacement "
                "UAV available"
            )

        self.metrics.update_task_status(
            self.tasks
        )

    def is_complete(self):

        return (
            len(self.tasks) > 0
            and
            all(
                task.status
                == "COMPLETED"
                for task in self.tasks
            )
        )

    def get_metrics(self):

        self.metrics.update_task_status(
            self.tasks
        )

        self.metrics.update_step(
            self.step_count
        )

        return self.metrics.get_summary()
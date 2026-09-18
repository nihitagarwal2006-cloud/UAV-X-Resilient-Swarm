from algorithms.mission_planner import MissionPlanner
from algorithms.resilience_manager import ResilienceManager
from communication.network import CommunicationNetwork
from communication.heartbeat import HeartbeatMonitor
from communication.uav_state import UAVState


class Mission:

    def __init__(self, uavs, tasks, obstacles=None):

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
            timeout=2
        )

        self.uav_states = {
            uav.id: UAVState(uav.id)
            for uav in self.uavs
        }

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

        self.connections = self.network.update_connections(
            self.uavs
        )

        print("MISSION STARTED")

        print("\nINITIAL COMMUNICATION NETWORK:")
        print(self.connections)

    def step(self):

        self.step_count += 1

        # -----------------------------
        # HEARTBEAT UPDATE
        # -----------------------------

        for uav in self.uavs:

            if uav.status != "ACTIVE":
                continue

            state = self.uav_states[uav.id]

            # Heartbeat only works when
            # communication is available.
            if state.communication_status:

                state.update_heartbeat(
                    self.step_count
                )

        print(
            f"Heartbeat check at step "
            f"{self.step_count}"
        )

        # -----------------------------
        # FAILURE DETECTION
        # -----------------------------

        active_states = [
            self.uav_states[uav.id]
            for uav in self.uavs
            if uav.status == "ACTIVE"
        ]

        failed_uavs = self.heartbeat_monitor.check(
            active_states,
            self.step_count
        )

        for uav_id in failed_uavs:

            print(
                f"Heartbeat timeout detected for "
                f"UAV {uav_id}"
            )

            self.fail_uav(uav_id)

        # -----------------------------
        # UAV MOVEMENT
        # -----------------------------

        old_connections = self.connections.copy()

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

            # -------------------------
            # TASK COMPLETION
            # -------------------------

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

        # -----------------------------
        # UPDATE NETWORK
        # -----------------------------

        self.connections = self.network.update_connections(
            self.uavs
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
            f"\nUAV {uav_id} FAILED "
            f"at mission step {self.step_count}"
        )

        # Remove failed UAV from
        # active communication network.
        self.connections = self.network.update_connections(
            [
                uav
                for uav in self.uavs
                if uav.status == "ACTIVE"
            ]
        )

        replacement = self.resilience.handle_failure(
            self.uavs,
            uav_id,
            self.tasks,
            self.obstacles,
            self.connections
        )

        if replacement:

            print(
                f"Recovery: UAV {replacement.id} "
                f"taking over the task"
            )

        else:

            print(
                "Recovery failed: "
                "no suitable replacement UAV available"
            )

    def is_complete(self):

        return all(
            task.status == "COMPLETED"
            for task in self.tasks
        )
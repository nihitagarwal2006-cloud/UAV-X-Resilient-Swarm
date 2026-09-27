import math

from algorithms.task_allocation import TaskAllocator
from algorithms.resilience_manager import ResilienceManager
from communication.network import CommunicationNetwork
from communication.uav_state import UAVState
from communication.heartbeat import HeartbeatMonitor
from simulation.metrics import MissionMetrics
from scenarios.gc1_config import (
    COMMUNICATION_RANGE_M,
    MAX_SPEED_MPS,
    SIMULATION_DT_S,
    MIN_UAV_SEPARATION_M,
    OPERATIONAL_CENTER_X_M,
    OPERATIONAL_CENTER_Y_M,
    failure_events,
)


class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


class Mission:
    """GC1 mission engine: POI survey, GCS reporting, resilient multi-hop links,
    priority-aware allocation, relay-role assignment, failure recovery and safety.
    """

    def __init__(self, uavs, tasks, scenario="GC1_MULTIPLE_FAILURE"):
        self.uavs = uavs
        self.tasks = tasks
        self.scenario = scenario
        self.center = Point(OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M)
        self.network = CommunicationNetwork(COMMUNICATION_RANGE_M)
        self.heartbeat = HeartbeatMonitor(timeout_steps=3)
        self.resilience = ResilienceManager()
        self.allocator = TaskAllocator()
        self.metrics = MissionMetrics()
        self.states = {u.id: UAVState(u.id) for u in uavs}
        self.step_count = 0
        self.events = []
        self.failure_events = failure_events(scenario)
        self.processed_failure_events = set()
        self.connections = {}
        self.center_reachable = set()
        self.relay_uavs = set()
        self.started = False
        self._last_relay_set = set()
        self._last_connections = {}

    def log(self, message):
        self.events.append(message)
        if len(self.events) > 100:
            self.events.pop(0)
        print(message)

    def start(self):
        self.started = True
        self.metrics.update(self.tasks, self.step_count)
        self._allocate_waiting_tasks()
        self._update_network()
        self.log("GC1 MISSION STARTED")
        self.log("Operational centre: (-75 m, 500 m)")
        self.log("Arena: 1000 m x 1000 m | POIs: 10")

    def _update_network(self):
        active = [u for u in self.uavs if u.status == "ACTIVE" and u.communication_status]
        old_connections = self.connections
        self.connections = self.network.update_connections(active)
        self.center_reachable = self.network.connected_to_center(active, self.center)
        self.relay_uavs = self.network.allocate_relays(active, self.center)

        if self._last_connections and self.connections != old_connections:
            self.metrics.network_reconfigurations += 1
        if self.relay_uavs != self._last_relay_set:
            if self.relay_uavs:
                self.metrics.relay_allocations += 1
                self.log("RELAY ROLE UPDATE: " + ", ".join(f"UAV {i}" for i in sorted(self.relay_uavs)))
            self._last_relay_set = set(self.relay_uavs)

        self._last_connections = {k: list(v) for k, v in self.connections.items()}

    def _allocate_waiting_tasks(self):
        waiting = [t for t in self.tasks if t.status == "UNASSIGNED"]
        if not waiting:
            return
        assignments = self.allocator.allocate(self.uavs, waiting)
        for task_id, uav_id in assignments.items():
            task = next(t for t in self.tasks if t.id == task_id)
            if task.recovery_pending:
                self.metrics.record_recovery(task.id, uav_id)
                task.recovery_pending = False
                self.log(f"RECOVERY: POI {task.id:02d} reassigned to UAV {uav_id}")
            else:
                self.log(
                    f"POI {task_id:02d} assigned to UAV {uav_id} "
                    f"[{task.priority} priority]"
                )

    def _task_for_uav(self, uav_id):
        return next((t for t in self.tasks if t.assigned_uav == uav_id), None)

    @staticmethod
    def _distance(a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    def _safe_position(self, uav, nx, ny):
        # The official scenario has a common launch/return point. Separation is
        # enforced once UAVs are airborne rather than penalising co-location at GCS.
        if math.hypot(nx - self.center.x, ny - self.center.y) <= 1.0:
            return True
        for other in self.uavs:
            if other.id == uav.id or other.status != "ACTIVE":
                continue
            if math.hypot(nx - other.x, ny - other.y) < MIN_UAV_SEPARATION_M:
                return False
        return True

    def _record_separation(self):
        airborne = [
            u for u in self.uavs
            if u.status == "ACTIVE" and math.hypot(u.x - self.center.x, u.y - self.center.y) > 1.0
        ]
        for i, a in enumerate(airborne):
            for b in airborne[i + 1:]:
                d = math.hypot(a.x - b.x, a.y - b.y)
                self.metrics.minimum_separation_m = min(self.metrics.minimum_separation_m, d)
                if d < MIN_UAV_SEPARATION_M:
                    self.metrics.separation_violations += 1
                    self.metrics.collision_count += 1

    def _predicted_position(self, uav, target_x, target_y):
        distance = uav.distance_to(target_x, target_y)
        if distance <= 1.0:
            return target_x, target_y
        travel = min(MAX_SPEED_MPS * SIMULATION_DT_S, distance)
        ratio = travel / distance
        return (
            uav.x + (target_x - uav.x) * ratio,
            uav.y + (target_y - uav.y) * ratio,
        )

    def _move_to(self, uav, target_x, target_y):
        nx, ny = self._predicted_position(uav, target_x, target_y)
        if self._safe_position(uav, nx, ny):
            uav.move_to_position(target_x, target_y, SIMULATION_DT_S)
            return True

        dx = target_x - uav.x
        dy = target_y - uav.y
        length = max(math.hypot(dx, dy), 1.0)
        px, py = -dy / length, dx / length
        travel = min(MAX_SPEED_MPS * SIMULATION_DT_S, length)

        for offset in (25.0, -25.0, 50.0, -50.0, 75.0, -75.0):
            cx = uav.x + dx / length * travel + px * offset
            cy = uav.y + dy / length * travel + py * offset
            if target_x == self.center.x and target_y == self.center.y:
                cx = max(self.center.x, cx)
                cy = max(0.0, min(1000.0, cy))
            else:
                cx = max(0.0, min(1000.0, cx))
                cy = max(0.0, min(1000.0, cy))
            actual_x, actual_y = self._predicted_position(uav, cx, cy)
            if self._safe_position(uav, actual_x, actual_y):
                uav.move_to_position(cx, cy, SIMULATION_DT_S)
                return True

        self.log(f"SAFETY HOLD: UAV {uav.id} waiting for 20 m clearance")
        return False

    def _inject_events(self):
        for event in self.failure_events:
            key = ("TECH", event["uav_id"], event["step"])
            if self.step_count == event["step"] and key not in self.processed_failure_events:
                self.processed_failure_events.add(key)
                self.fail_uav(event["uav_id"], "TECHNICAL_FAILURE")

        if self.scenario == "GC1_COMMUNICATION_FAILURE" and self.step_count == 15:
            self.set_communication_failure(2)
        elif self.scenario == "GC1_MULTIPLE_FAILURE" and self.step_count == 20:
            self.set_communication_failure(2)

    def set_communication_failure(self, uav_id):
        state = self.states.get(uav_id)
        if not state or not state.communication_status:
            return
        state.set_communication(False)
        self.metrics.record_communication_failure()
        self.metrics.communication_downtime_steps += 1
        self.log(f"COMMUNICATION LOSS: UAV {uav_id} at step {self.step_count}")
        self._update_network()

    def fail_uav(self, uav_id, reason="TECHNICAL_FAILURE"):
        uav = next((u for u in self.uavs if u.id == uav_id), None)
        if not uav or uav.status != "ACTIVE":
            return
        affected = self._task_for_uav(uav_id)
        uav.fail(reason)
        self.metrics.record_failure(uav_id)
        self.log(f"UAV {uav_id} FAILED at step {self.step_count} ({reason})")
        self._update_network()

        if affected:
            replacement = self.resilience.recover(self.uavs, uav_id, affected, self.connections)
            if replacement:
                self.metrics.record_recovery(affected.id, replacement.id)
                self.log(f"RECOVERY: POI {affected.id:02d} reassigned UAV {replacement.id}")
            else:
                affected.status = "UNASSIGNED"
                affected.assigned_uav = None
                affected.recovery_pending = True
                self.log(f"RECOVERY WAITING: POI {affected.id:02d} has no available UAV")
        self._update_network()

    def _record_communication_metrics(self):
        active_all = [u for u in self.uavs if u.status == "ACTIVE"]
        if not active_all:
            return
        # Periodic telemetry packet: one status packet per active UAV every 5 steps.
        if self.step_count % 5 != 0:
            return
        reachable_count = 0
        for uav in active_all:
            delivered, hops, latency = self.network.packet_delivery(uav.id)
            self.metrics.record_packet(delivered, latency)
            if delivered:
                reachable_count += 1
        self.metrics.connectivity_samples += len(active_all)
        self.metrics.connected_samples += reachable_count
        if reachable_count < len(active_all):
            self.metrics.communication_downtime_steps += 1

    def step(self):
        if not self.started or self.is_complete():
            return

        self.step_count += 1
        self._inject_events()

        for uav in self.uavs:
            if uav.status == "ACTIVE" and uav.communication_status:
                self.states[uav.id].update_heartbeat(self.step_count)

        self._update_network()
        self._record_communication_metrics()

        timed_out = self.heartbeat.check(
            [self.states[u.id] for u in self.uavs if u.status == "ACTIVE"],
            self.step_count,
        )
        for uav_id in timed_out:
            self.fail_uav(uav_id, "COMMUNICATION_TIMEOUT")

        for uav in self.uavs:
            if uav.status != "ACTIVE" or uav.current_task is None:
                continue

            task = self._task_for_uav(uav.id)
            if task is None:
                uav.clear_task()
                continue

            if uav.phase == "TO_POI":
                self._move_to(uav, task.x, task.y)
                if uav.distance_to(task.x, task.y) <= 1.0:
                    task.mark_detected()
                    uav.detected_poi = True
                    uav.phase = "TO_CENTER"
                    self.log(f"POI {task.id:02d} DETECTED by UAV {uav.id}")

            elif uav.phase == "TO_CENTER":
                self._move_to(uav, self.center.x, self.center.y)
                if uav.distance_to(self.center.x, self.center.y) <= 1.0:
                    self._update_network()
                    if uav.id in self.center_reachable:
                        task.mark_reported()
                        task.complete()
                        uav.clear_task()
                        self.log(f"POI {task.id:02d} REPORTED to centre by UAV {uav.id}")
                    else:
                        self.log(f"REPORT WAITING: UAV {uav.id} has no resilient link to centre")

        self._record_separation()
        self._allocate_waiting_tasks()
        self._update_network()
        self.metrics.update(self.tasks, self.step_count)

    def is_complete(self):
        return bool(self.tasks) and all(t.status == "COMPLETED" for t in self.tasks)

    def summary(self):
        self.metrics.update(self.tasks, self.step_count)
        return self.metrics.summary()

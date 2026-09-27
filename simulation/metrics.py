class MissionMetrics:
    def __init__(self):
        self.total_tasks = 0
        self.completed_tasks = 0
        self.detected_pois = 0
        self.reported_pois = 0
        self.uav_failures = 0
        self.recovery_events = 0
        self.communication_failures = 0
        self.mission_steps = 0
        self.failed_uavs = []
        self.recovered_tasks = []
        self.packets_sent = 0
        self.packets_delivered = 0
        self.total_latency_ms = 0.0
        self.communication_downtime_steps = 0
        self.connectivity_samples = 0
        self.connected_samples = 0
        self.relay_allocations = 0
        self.network_reconfigurations = 0
        self.collision_count = 0
        self.minimum_separation_m = float("inf")
        self.separation_violations = 0
        self.priority_weighted_score = 0.0
        self.priority_weighted_total = 0.0

    def update(self, tasks, step):
        self.total_tasks = len(tasks)
        self.completed_tasks = sum(t.status == "COMPLETED" for t in tasks)
        self.detected_pois = sum(t.detected for t in tasks)
        self.reported_pois = sum(t.reported for t in tasks)
        self.mission_steps = step
        self.priority_weighted_total = sum(getattr(t, "priority_weight", 1.0) for t in tasks)
        self.priority_weighted_score = sum(
            getattr(t, "priority_weight", 1.0) for t in tasks if t.status == "COMPLETED"
        )

    def record_failure(self, uav_id):
        self.uav_failures += 1
        if uav_id not in self.failed_uavs:
            self.failed_uavs.append(uav_id)

    def record_recovery(self, task_id, uav_id):
        self.recovery_events += 1
        self.recovered_tasks.append({"task_id": task_id, "uav_id": uav_id})

    def record_communication_failure(self):
        self.communication_failures += 1

    def record_packet(self, delivered, latency_ms=0.0):
        self.packets_sent += 1
        if delivered:
            self.packets_delivered += 1
            self.total_latency_ms += latency_ms

    def summary(self):
        rate = 100.0 * self.completed_tasks / self.total_tasks if self.total_tasks else 0.0
        pdr = 100.0 * self.packets_delivered / self.packets_sent if self.packets_sent else 0.0
        avg_latency = self.total_latency_ms / self.packets_delivered if self.packets_delivered else 0.0
        connectivity = (
            100.0 * self.connected_samples / self.connectivity_samples
            if self.connectivity_samples else 0.0
        )
        weighted = (
            100.0 * self.priority_weighted_score / self.priority_weighted_total
            if self.priority_weighted_total else 0.0
        )
        minimum_sep = 0.0 if self.minimum_separation_m == float("inf") else self.minimum_separation_m
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "completion_rate": rate,
            "detected_pois": self.detected_pois,
            "reported_pois": self.reported_pois,
            "priority_weighted_score": weighted,
            "uav_failures": self.uav_failures,
            "recovery_events": self.recovery_events,
            "communication_failures": self.communication_failures,
            "packets_sent": self.packets_sent,
            "packets_delivered": self.packets_delivered,
            "packet_delivery_ratio": pdr,
            "average_packet_latency_ms": avg_latency,
            "connectivity_availability": connectivity,
            "communication_downtime_steps": self.communication_downtime_steps,
            "relay_allocations": self.relay_allocations,
            "network_reconfigurations": self.network_reconfigurations,
            "collision_count": self.collision_count,
            "minimum_separation_m": minimum_sep,
            "separation_violations": self.separation_violations,
            "mission_steps": self.mission_steps,
            "failed_uavs": self.failed_uavs,
            "recovered_tasks": self.recovered_tasks,
        }

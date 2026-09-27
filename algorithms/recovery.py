import math


class RecoveryManager:
    def distance(self, uav, task):
        return math.hypot(uav.x - task.x, uav.y - task.y)

    def find_replacement(self, uavs, failed_uav_id, task, connections=None):
        candidates = [
            u for u in uavs
            if u.id != failed_uav_id and u.is_available()
        ]
        if not candidates:
            return None
        if connections:
            connected = [u for u in candidates if u.id in connections.get(failed_uav_id, [])]
            if connected:
                candidates = connected
        return min(candidates, key=lambda u: self.distance(u, task))

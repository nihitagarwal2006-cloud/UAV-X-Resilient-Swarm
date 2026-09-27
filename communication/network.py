import math
from collections import deque


class CommunicationNetwork:
    """Range-limited aerial network with multi-hop GCS reachability."""

    def __init__(self, communication_range=100.0):
        self.communication_range = float(communication_range)
        self.connections = {}
        self.paths_to_center = {}
        self.hop_counts = {}
        self.relay_uavs = set()

    @staticmethod
    def distance(a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    def update_connections(self, uavs):
        active = [u for u in uavs if u.status == "ACTIVE" and u.communication_status]
        self.connections = {u.id: [] for u in active}
        for i, a in enumerate(active):
            for b in active[i + 1:]:
                if self.distance(a, b) <= self.communication_range:
                    self.connections[a.id].append(b.id)
                    self.connections[b.id].append(a.id)
        return self.connections

    def paths_from_center(self, uavs, center):
        """Build shortest multi-hop paths from the GCS to every reachable UAV."""
        active = [u for u in uavs if u.status == "ACTIVE" and u.communication_status]
        nodes = {u.id: u for u in active}
        self.paths_to_center = {}
        self.hop_counts = {}
        queue = deque()

        for u in active:
            if self.distance(u, center) <= self.communication_range:
                self.paths_to_center[u.id] = [u.id]
                self.hop_counts[u.id] = 1
                queue.append(u.id)

        while queue:
            current = queue.popleft()
            for neighbor in self.connections.get(current, []):
                if neighbor in nodes and neighbor not in self.paths_to_center:
                    self.paths_to_center[neighbor] = [neighbor] + self.paths_to_center[current]
                    self.hop_counts[neighbor] = self.hop_counts[current] + 1
                    queue.append(neighbor)

        return self.paths_to_center

    def connected_to_center(self, uavs, center):
        self.paths_from_center(uavs, center)
        return set(self.paths_to_center)

    def allocate_relays(self, uavs, center):
        """Assign relay roles to UAVs that bridge the GCS and remote peers."""
        relay_ids = set()
        active = [u for u in uavs if u.status == "ACTIVE" and u.communication_status]
        by_id = {u.id: u for u in active}
        direct_to_center = {
            u.id for u in active if self.distance(u, center) <= self.communication_range
        }
        for u in active:
            if u.id not in direct_to_center:
                continue
            for neighbor in self.connections.get(u.id, []):
                if neighbor in by_id and neighbor not in direct_to_center:
                    relay_ids.add(u.id)
                    break
        for path in self.paths_to_center.values():
            if len(path) > 2:
                relay_ids.update(path[1:-1])
        self.relay_uavs = relay_ids
        return relay_ids

    def packet_delivery(self, uav_id):
        """Return (delivered, hop_count, latency_ms) for a GCS packet."""
        if uav_id not in self.paths_to_center:
            return False, 0, 0.0
        hops = self.hop_counts.get(uav_id, 0)
        # POC communication assumption: 20 ms per aerial hop.
        return True, hops, float(hops * 20.0)

import math


class CommunicationNetwork:

    def __init__(self, communication_range=150):
        self.communication_range = communication_range
        self.connections = {}

    def distance(self, uav1, uav2):
        dx = uav1.x - uav2.x
        dy = uav1.y - uav2.y
        return math.sqrt(dx * dx + dy * dy)

    def update_connections(self, uavs):

        new_connections = {}

        for uav in uavs:
            new_connections[uav.id] = []

        for i in range(len(uavs)):
            for j in range(i + 1, len(uavs)):

                distance = self.distance(uavs[i], uavs[j])

                if distance <= self.communication_range:
                    new_connections[uavs[i].id].append(uavs[j].id)
                    new_connections[uavs[j].id].append(uavs[i].id)

        self.connections = new_connections

        return self.connections

    def get_connected_uavs(self, uav_id):
        return self.connections.get(uav_id, [])

    def get_link_changes(self, old_connections):

        lost_links = []
        new_links = []

        for uav_id, old_neighbors in old_connections.items():

            current_neighbors = self.connections.get(uav_id, [])

            for neighbor in old_neighbors:
                if neighbor not in current_neighbors:
                    link = tuple(sorted((uav_id, neighbor)))

                    if link not in lost_links:
                        lost_links.append(link)

            for neighbor in current_neighbors:
                if neighbor not in old_neighbors:
                    link = tuple(sorted((uav_id, neighbor)))

                    if link not in new_links:
                        new_links.append(link)

        return lost_links, new_links
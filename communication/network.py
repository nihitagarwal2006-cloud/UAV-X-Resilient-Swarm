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

        self.connections = {}

        for uav in uavs:
            self.connections[uav.id] = []

        for i in range(len(uavs)):
            for j in range(i + 1, len(uavs)):

                distance = self.distance(uavs[i], uavs[j])

                if distance <= self.communication_range:

                    self.connections[uavs[i].id].append(uavs[j].id)
                    self.connections[uavs[j].id].append(uavs[i].id)

        return self.connections
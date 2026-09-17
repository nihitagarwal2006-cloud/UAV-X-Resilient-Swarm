class UAVState:

    def __init__(self, uav_id):
        self.uav_id = uav_id
        self.communication_status = True
        self.last_heartbeat = 0
        self.connected_uavs = []

    def update_heartbeat(self, time):
        self.last_heartbeat = time

    def set_communication(self, status):
        self.communication_status = status
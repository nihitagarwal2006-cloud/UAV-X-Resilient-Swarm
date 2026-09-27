class UAVState:
    def __init__(self, uav_id):
        self.uav_id = uav_id
        self.communication_status = True
        self.last_heartbeat = 0

    def update_heartbeat(self, step):
        self.last_heartbeat = step

    def set_communication(self, status):
        self.communication_status = bool(status)

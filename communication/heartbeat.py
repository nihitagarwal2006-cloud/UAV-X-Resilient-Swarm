class HeartbeatMonitor:

    def __init__(self, timeout=5):
        self.timeout = timeout

    def check(self, uav_states, current_time):

        failed_uavs = []

        for state in uav_states:

            if current_time - state.last_heartbeat > self.timeout:
                failed_uavs.append(state.uav_id)

        return failed_uavs
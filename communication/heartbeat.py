class HeartbeatMonitor:
    def __init__(self, timeout_steps=3):
        self.timeout_steps = timeout_steps

    def check(self, states, current_step):
        return [
            state.uav_id
            for state in states
            if state.communication_status
            and current_step - state.last_heartbeat > self.timeout_steps
        ]

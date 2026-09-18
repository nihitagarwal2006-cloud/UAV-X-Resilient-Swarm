class FailureSimulator:

    def __init__(self, failure_step=None, uav_id=None):
        self.failure_step = failure_step
        self.uav_id = uav_id
        self.failed = False

    def check_failure(self, current_step, uav):

        if (
            self.failure_step is not None
            and current_step == self.failure_step
            and uav.id == self.uav_id
            and not self.failed
            and uav.status == "ACTIVE"
        ):

            self.failed = True

            print(
                f"\nTECHNICAL FAILURE DETECTED: "
                f"UAV {uav.id} at step {current_step}\n"
            )

            return True

        return False
class FailureSimulator:

    def __init__(
        self,
        failure_step=None,
        uav_id=None,
        failures=None
    ):

        self.failure_step = failure_step
        self.uav_id = uav_id

        # Support multiple configured failures
        if failures is not None:
            self.failures = failures
        elif failure_step is not None and uav_id is not None:
            self.failures = [
                {
                    "uav_id": uav_id,
                    "step": failure_step
                }
            ]
        else:
            self.failures = []

        self.failed_uavs = set()

    def check_failure(self, current_step, uav):

        if uav.status != "ACTIVE":
            return False

        for failure in self.failures:

            failure_uav_id = failure["uav_id"]
            failure_step = failure["step"]

            if (
                current_step == failure_step
                and uav.id == failure_uav_id
                and uav.id not in self.failed_uavs
            ):

                self.failed_uavs.add(uav.id)

                print(
                    f"\nTECHNICAL FAILURE DETECTED: "
                    f"UAV {uav.id} "
                    f"at step {current_step}\n"
                )

                return True

        return False

    def get_failed_uavs(self):

        return list(self.failed_uavs)
class FailureSimulator:

    def __init__(self, failure_step):
        self.failure_step = failure_step
        self.failed = False

    def check_failure(self, current_step, uav):

        if (
            current_step == self.failure_step
            and not self.failed
            and uav.status == "ACTIVE"
        ):
            uav.fail()
            self.failed = True

            print(f"\nUAV {uav.id} FAILED at step {current_step}!\n")

            return True

        return False
from algorithms.recovery import RecoveryManager


class ResilienceManager:

    def __init__(self):
        self.recovery = RecoveryManager()

    def handle_failure(self, uavs, failed_uav_id, tasks, obstacles=None):

        for task in tasks:

            if task.assigned_uav == failed_uav_id:
                print(
                    f"Task {task.id} affected by "
                    f"UAV {failed_uav_id} failure"
                )

                replacement = self.recovery.recover_task(
                    uavs,
                    failed_uav_id,
                    task,
                    obstacles
                )

                if replacement:

                    print(
                        f"Task {task.id} reassigned to "
                        f"UAV {replacement.id}"
                    )

                    return replacement

                print(
                    f"No replacement UAV available "
                    f"for Task {task.id}"
                )

        return None
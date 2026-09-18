from simulation.uav import UAV
from simulation.task import Task
from simulation.mission import Mission


# Available scenarios:
# NORMAL
# COMMUNICATION_FAILURE
# TECHNICAL_FAILURE

SCENARIO = "NORMAL"


uavs = [
    UAV(1, 1, 1),
    UAV(2, 10, 2),
    UAV(3, 15, 15),
    UAV(4, 5, 15)
]

tasks = [
    Task(1, 8, 8),
    Task(2, 18, 3),
    Task(3, 12, 18)
]


mission = Mission(uavs, tasks)

mission.start()


while not mission.is_complete():

    # Communication failure scenario
    if (
        SCENARIO == "COMMUNICATION_FAILURE"
        and mission.step_count == 4
    ):
        mission.uav_states[2].set_communication(False)

        print("\nUAV 2 COMMUNICATION LOST")

    # Technical failure scenario
    if (
        SCENARIO == "TECHNICAL_FAILURE"
        and mission.step_count == 6
    ):
        print("\nTECHNICAL ISSUE DETECTED IN UAV 2")
        mission.fail_uav(2)

    mission.step()


print("\nMISSION COMPLETE")

print("\nFINAL TASK STATUS:")

for task in tasks:
    print(
        f"Task {task.id}: "
        f"{task.status}"
    )


print("\nFINAL UAV STATUS:")

for uav in uavs:
    print(
        f"UAV {uav.id}: "
        f"{uav.status}"
    )
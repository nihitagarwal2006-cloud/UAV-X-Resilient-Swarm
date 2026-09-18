from simulation.uav import UAV
from simulation.task import Task
from simulation.mission import Mission


# ==============================
# SCENARIO CONFIGURATION
# ==============================

FAILURE_MODE = "communication"
FAILURE_UAV_ID = 2
FAILURE_STEP = 4


# ==============================
# UAVs
# ==============================

uavs = [
    UAV(1, 1, 1),
    UAV(2, 10, 2),
    UAV(3, 15, 15),
    UAV(4, 5, 15)
]


# ==============================
# Tasks
# ==============================

tasks = [
    Task(1, 8, 8),
    Task(2, 18, 3),
    Task(3, 12, 18)
]


# ==============================
# Start Mission
# ==============================

mission = Mission(uavs, tasks)

mission.start()


# ==============================
# Simulation Loop
# ==============================

while not mission.is_complete():

    # --------------------------------
    # Simulate technical issue
    # --------------------------------

    if mission.step_count == FAILURE_STEP:

        if FAILURE_MODE == "communication":

            mission.uav_states[
                FAILURE_UAV_ID
            ].set_communication(False)

            print(
                f"\nUAV {FAILURE_UAV_ID} "
                f"COMMUNICATION LOST"
            )

        elif FAILURE_MODE == "uav_failure":

            mission.fail_uav(
                FAILURE_UAV_ID
            )

    # --------------------------------
    # Run next simulation step
    # --------------------------------

    mission.step()


# ==============================
# Final Results
# ==============================

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
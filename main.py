from simulation.uav import UAV
from simulation.task import Task
from simulation.mission import Mission
from simulation.failure import FailureSimulator


# ============================================================
# SCENARIO CONFIGURATION
# ============================================================
#
# NORMAL
#   -> No failures
#
# TECHNICAL_FAILURE
#   -> Selected UAV experiences a technical failure
#
# COMMUNICATION_FAILURE
#   -> Selected UAV loses communication
#
SCENARIO = "TECHNICAL_FAILURE"

# Used only for failure scenarios
FAILURE_UAV_ID = 2
FAILURE_STEP = 6


# ============================================================
# UAV SWARM
# ============================================================

uavs = [
    UAV(1, 1, 1),
    UAV(2, 10, 2),
    UAV(3, 15, 15),
    UAV(4, 5, 15)
]


# ============================================================
# MISSION TASKS
# ============================================================

tasks = [
    Task(1, 8, 8),
    Task(2, 18, 3),
    Task(3, 12, 18)
]


# ============================================================
# FAILURE CONFIGURATION
# ============================================================

failure_simulator = None

if SCENARIO == "TECHNICAL_FAILURE":

    failure_simulator = FailureSimulator(
        failure_step=FAILURE_STEP,
        uav_id=FAILURE_UAV_ID
    )


# ============================================================
# CREATE MISSION
# ============================================================

mission = Mission(
    uavs,
    tasks,
    failure_simulator=failure_simulator
)


# ============================================================
# START MISSION
# ============================================================

mission.start()


# ============================================================
# RUN SIMULATION
# ============================================================

MAX_STEPS = 1000

while not mission.is_complete():

    # --------------------------------------------------------
    # Communication failure scenario
    # --------------------------------------------------------

    if (
        SCENARIO == "COMMUNICATION_FAILURE"
        and mission.step_count == FAILURE_STEP
    ):

        mission.uav_states[FAILURE_UAV_ID].set_communication(False)

        print(
            f"\nCOMMUNICATION FAILURE: "
            f"UAV {FAILURE_UAV_ID} communication lost\n"
        )

    # --------------------------------------------------------
    # Execute one simulation step
    # --------------------------------------------------------

    mission.step()

    # --------------------------------------------------------
    # Safety protection against infinite simulation
    # --------------------------------------------------------

    if mission.step_count >= MAX_STEPS:

        print(
            "\nMISSION STOPPED: "
            "Maximum simulation steps reached."
        )

        break


# ============================================================
# FINAL RESULTS
# ============================================================

if mission.is_complete():

    print("\nMISSION COMPLETE")

else:

    print("\nMISSION INCOMPLETE")


# ============================================================
# FINAL TASK STATUS
# ============================================================

print("\nFINAL TASK STATUS:")

for task in tasks:

    print(
        f"Task {task.id}: "
        f"{task.status}"
    )


# ============================================================
# FINAL UAV STATUS
# ============================================================

print("\nFINAL UAV STATUS:")

for uav in uavs:

    print(
        f"UAV {uav.id}: "
        f"{uav.status}"
    )

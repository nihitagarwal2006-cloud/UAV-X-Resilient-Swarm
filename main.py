from simulation.uav import UAV
from simulation.task import Task
from simulation.mission import Mission
from simulation.failure import FailureSimulator
from scenarios.config import ScenarioConfig


# ============================================================
# SCENARIO CONFIGURATION
# ============================================================

SCENARIO = ScenarioConfig.MULTIPLE_FAILURE

scenario = ScenarioConfig(SCENARIO)


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


technical_failures = (
    scenario.get_technical_failures()
)


if technical_failures:

    failure_simulator = FailureSimulator(
        failures=technical_failures
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

print("\n========================================")
print("UAV-X RESILIENT SWARM SIMULATOR")
print("========================================")

print(
    f"SCENARIO: {scenario.scenario}"
)

if technical_failures:

    print("\nTECHNICAL FAILURE EVENTS:")

    for failure in technical_failures:

        print(
            f"  UAV {failure['uav_id']} "
            f"-> Step {failure['step']}"
        )


communication_failures = (
    scenario.get_communication_failures()
)


if communication_failures:

    print("\nCOMMUNICATION FAILURE EVENTS:")

    for failure in communication_failures:

        print(
            f"  UAV {failure['uav_id']} "
            f"-> Step {failure['step']}"
        )


print("\n========================================\n")


mission.start()


# ============================================================
# RUN SIMULATION
# ============================================================

MAX_STEPS = 1000

while not mission.is_complete():

    # --------------------------------------------------------
    # Communication failure scenario
    # --------------------------------------------------------

    for failure in communication_failures:

        if (
            mission.step_count
            == failure["step"]
        ):

            uav_id = failure["uav_id"]

            if (
                uav_id in mission.uav_states
                and
                mission.uav_states[
                    uav_id
                ].communication_status
            ):

                mission.uav_states[
                    uav_id
                ].set_communication(False)

                print(
                    f"\nCOMMUNICATION FAILURE: "
                    f"UAV {uav_id} "
                    f"communication lost "
                    f"at step "
                    f"{mission.step_count}\n"
                )


    # --------------------------------------------------------
    # Execute one simulation step
    # --------------------------------------------------------

    mission.step()


    # --------------------------------------------------------
    # Safety protection
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

print("\n========================================")
print("FINAL RESULTS")
print("========================================")


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


# ============================================================
# FAILURE SUMMARY
# ============================================================

if failure_simulator:

    print("\nFAILED UAVs:")

    failed_uavs = (
        failure_simulator.get_failed_uavs()
    )

    if failed_uavs:

        for uav_id in failed_uavs:

            print(
                f"  UAV {uav_id}"
            )

    else:

        print("  None")


print("\n========================================")
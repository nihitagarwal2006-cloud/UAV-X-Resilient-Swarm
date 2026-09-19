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
    UAV(4, 5, 15),
    UAV(5, 18, 18)
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

technical_failures = (
    scenario.get_technical_failures()
)

communication_failures = (
    scenario.get_communication_failures()
)


# ============================================================
# FAILURE SIMULATOR
# ============================================================

failure_simulator = None

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
# STARTUP INFORMATION
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


if communication_failures:

    print("\nCOMMUNICATION FAILURE EVENTS:")

    for failure in communication_failures:

        print(
            f"  UAV {failure['uav_id']} "
            f"-> Step {failure['step']}"
        )


print(
    "\n========================================\n"
)


# ============================================================
# START MISSION
# ============================================================

mission.start()


# ============================================================
# SIMULATION LOOP
# ============================================================

MAX_STEPS = 1000

while not mission.is_complete():

    # --------------------------------------------------------
    # Communication failure injection
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
    # Execute mission step
    # --------------------------------------------------------

    mission.step()


    # --------------------------------------------------------
    # Safety limit
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
# FAILED UAVS
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


# ============================================================
# MISSION METRICS
# ============================================================

metrics = mission.get_metrics()

print("\n========================================")
print("MISSION METRICS")
print("========================================")

print(
    f"Total Tasks: "
    f"{metrics['total_tasks']}"
)

print(
    f"Completed Tasks: "
    f"{metrics['completed_tasks']}"
)

print(
    f"Completion Rate: "
    f"{metrics['completion_rate']:.1f}%"
)

print(
    f"UAV Failures: "
    f"{metrics['uav_failures']}"
)

print(
    f"Recovery Events: "
    f"{metrics['recovery_events']}"
)

print(
    f"Communication Failures: "
    f"{metrics['communication_failures']}"
)

print(
    f"Mission Steps: "
    f"{metrics['mission_steps']}"
)

print(
    f"Failed UAVs: "
    f"{metrics['failed_uavs']}"
)

print(
    f"Recovered Tasks: "
    f"{metrics['recovered_tasks']}"
)

print(
    "========================================"
)
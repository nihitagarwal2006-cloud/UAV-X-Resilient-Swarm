from simulation.uav import UAV
from simulation.task import Task
from simulation.mission import Mission


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

    # Simulate communication failure of UAV 2
    if mission.step_count == 4:
        mission.uav_states[2].set_communication(False)

        print(
            "\nUAV 2 communication LOST"
        )

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
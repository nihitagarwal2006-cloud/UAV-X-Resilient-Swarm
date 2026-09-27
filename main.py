import random

from scenarios.config import ScenarioConfig
from scenarios.gc1_config import DEFAULT_POI_COUNT, RANDOM_SEED, ARENA_WIDTH_M, ARENA_HEIGHT_M, OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M
from simulation.uav import UAV
from simulation.task import Task
from simulation.mission import Mission


def build_mission(scenario=ScenarioConfig.MULTIPLE_FAILURE, poi_count=DEFAULT_POI_COUNT):
    random.seed(RANDOM_SEED)
    uavs = [
        UAV(1, OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M),
        UAV(2, OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M),
        UAV(3, OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M),
        UAV(4, OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M),
        UAV(5, OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M),
    ]
    points = []
    while len(points) < min(poi_count, 10):
        point = (random.randint(40, 960), random.randint(40, 960))
        if all((point[0]-x)**2 + (point[1]-y)**2 >= 80**2 for x, y in points):
            points.append(point)
    tasks = [Task(i + 1, x, y, "HIGH") for i, (x, y) in enumerate(points)]
    mission = Mission(uavs, tasks, scenario=scenario)
    mission.start()
    return mission, uavs, tasks


def main():
    scenario = ScenarioConfig.MULTIPLE_FAILURE
    mission, uavs, tasks = build_mission(scenario)
    print("\n========================================")
    print("UAV-X RESILIENT SWARM — GC1 POC")
    print("========================================")
    print(f"Scenario: {scenario}")
    print(f"Arena: {ARENA_WIDTH_M:.0f} m x {ARENA_HEIGHT_M:.0f} m")
    print(f"Operational centre: ({OPERATIONAL_CENTER_X_M:.0f}, {OPERATIONAL_CENTER_Y_M:.0f}) m")
    print("Communication range: 100 m")
    print("Max speed: 5 m/s")
    print("Max flight time: 20 min")
    print("POIs: 10")
    print("========================================\n")

    while not mission.is_complete() and mission.step_count < 240:
        mission.step()

    result = mission.summary()
    print("\n========================================")
    print("FINAL RESULTS")
    print("========================================")
    print("MISSION COMPLETE" if mission.is_complete() else "MISSION INCOMPLETE")
    for task in tasks:
        print(f"POI {task.id:02d}: {task.status}")
    for uav in uavs:
        print(f"UAV {uav.id}: {uav.status} | {uav.phase} | {uav.x:.1f},{uav.y:.1f}")
    print("\nMETRICS")
    for key, value in result.items():
        print(f"{key}: {value}")
    print("\nGC1 SAFETY / COMMUNICATION CHECK")
    print(f"Packet delivery ratio: {result['packet_delivery_ratio']:.1f}%")
    print(f"Average packet latency: {result['average_packet_latency_ms']:.1f} ms")
    print(f"Relay allocations: {result['relay_allocations']}")
    print(f"Network reconfigurations: {result['network_reconfigurations']}")
    print(f"Minimum separation: {result['minimum_separation_m']:.1f} m")
    print(f"Separation violations: {result['separation_violations']}")
    print(f"Collision count: {result['collision_count']}")


if __name__ == "__main__":
    main()

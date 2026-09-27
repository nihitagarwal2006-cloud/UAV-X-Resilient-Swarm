"""Official-style GC1 scenario parameters for the UAV-X proof of concept."""

ARENA_WIDTH_M = 1000.0
ARENA_HEIGHT_M = 1000.0
OPERATIONAL_CENTER_X_M = -75.0
OPERATIONAL_CENTER_Y_M = 500.0
COMMUNICATION_RANGE_M = 100.0
MAX_SPEED_MPS = 5.0
MAX_FLIGHT_TIME_S = 20 * 60
SIMULATION_DT_S = 5.0
MIN_UAV_SEPARATION_M = 20.0
MAX_ALTITUDE_M = 100.0
MAX_POIS = 10
DEFAULT_POI_COUNT = 10
RANDOM_SEED = 2026

SCENARIOS = (
    "GC1_NORMAL",
    "GC1_TECHNICAL_FAILURE",
    "GC1_COMMUNICATION_FAILURE",
    "GC1_MULTIPLE_FAILURE",
)


def failure_events(scenario):
    if scenario == "GC1_TECHNICAL_FAILURE":
        return [{"uav_id": 2, "step": 30}]
    if scenario == "GC1_COMMUNICATION_FAILURE":
        return []
    if scenario == "GC1_MULTIPLE_FAILURE":
        return [
            {"uav_id": 2, "step": 30},
            {"uav_id": 4, "step": 60},
        ]
    return []

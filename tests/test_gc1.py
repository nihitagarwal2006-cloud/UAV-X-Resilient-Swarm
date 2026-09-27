from main import build_mission
from scenarios.config import ScenarioConfig


def test_gc1_normal_completes():
    mission, _, _ = build_mission(ScenarioConfig.NORMAL)
    for _ in range(240):
        if mission.is_complete():
            break
        mission.step()
    assert mission.is_complete()
    assert mission.summary()["completion_rate"] == 100.0


if __name__ == "__main__":
    test_gc1_normal_completes()
    print("GC1 test passed")

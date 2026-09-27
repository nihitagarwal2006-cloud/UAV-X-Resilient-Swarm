from scenarios.gc1_config import *


class ScenarioConfig:
    NORMAL = "GC1_NORMAL"
    TECHNICAL_FAILURE = "GC1_TECHNICAL_FAILURE"
    COMMUNICATION_FAILURE = "GC1_COMMUNICATION_FAILURE"
    MULTIPLE_FAILURE = "GC1_MULTIPLE_FAILURE"

    def __init__(self, scenario):
        self.scenario = scenario

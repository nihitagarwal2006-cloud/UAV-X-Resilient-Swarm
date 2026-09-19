class ScenarioConfig:

    # ============================================================
    # AVAILABLE SCENARIOS
    # ============================================================

    NORMAL = "NORMAL"

    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"

    COMMUNICATION_FAILURE = "COMMUNICATION_FAILURE"

    MULTIPLE_FAILURE = "MULTIPLE_FAILURE"


    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self, scenario):

        self.scenario = scenario


    # ============================================================
    # TECHNICAL FAILURE EVENTS
    # ============================================================

    def get_technical_failures(self):

        if self.scenario == self.TECHNICAL_FAILURE:

            return [
                {
                    "uav_id": 2,
                    "step": 6
                }
            ]

        if self.scenario == self.MULTIPLE_FAILURE:

            return [
                {
                    "uav_id": 2,
                    "step": 6
                },
                {
                    "uav_id": 4,
                    "step": 12
                }
            ]

        return []


    # ============================================================
    # COMMUNICATION FAILURE EVENTS
    # ============================================================

    def get_communication_failures(self):

        if self.scenario == self.COMMUNICATION_FAILURE:

            return [
                {
                    "uav_id": 2,
                    "step": 2
                }
            ]

        return []
class ScenarioConfig:

    NORMAL = "NORMAL"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"
    COMMUNICATION_FAILURE = "COMMUNICATION_FAILURE"
    MULTIPLE_FAILURE = "MULTIPLE_FAILURE"

    def __init__(self, scenario=NORMAL):

        valid_scenarios = [
            self.NORMAL,
            self.TECHNICAL_FAILURE,
            self.COMMUNICATION_FAILURE,
            self.MULTIPLE_FAILURE
        ]

        if scenario not in valid_scenarios:
            raise ValueError(
                f"Unknown scenario: {scenario}"
            )

        self.scenario = scenario

    def is_normal(self):

        return self.scenario == self.NORMAL

    def has_technical_failure(self):

        return self.scenario in [
            self.TECHNICAL_FAILURE,
            self.MULTIPLE_FAILURE
        ]

    def has_communication_failure(self):

        return self.scenario == self.COMMUNICATION_FAILURE

    def get_technical_failures(self):

        if not self.has_technical_failure():
            return []

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

        return [
            {
                "uav_id": 2,
                "step": 6
            }
        ]

    def get_communication_failures(self):

        if not self.has_communication_failure():
            return []

        return [
            {
                "uav_id": 3,
                "step": 8
            }
        ]
from mivp_agent.agent import Agent, Model

from .actions import FAKE_ACTION


class FakeAgent(Agent):
    def __init__(self, model) -> None:
        self.model = model

    def build_model(self) -> Model:
        return self.model

    def observation_to_state(self, observation):
        return (
            observation['NAV_X'],
            observation['NAV_Y']
        )

    def state_to_action(self, model: Model, state, observation):
        return FAKE_ACTION
from abc import ABC, abstractmethod
from copy import deepcopy

from mivp_agent.model import Model


class Agent(ABC): 
    @abstractmethod
    def build_model(self) -> Model:
        pass
    
    def start_episode(self):
        pass

    @abstractmethod
    def observation_to_state(self, observation):
        pass
    
    @abstractmethod
    def state_to_action(self, model: Model, state, observation):
        pass

    def duplicate(self):
        return deepcopy(self)

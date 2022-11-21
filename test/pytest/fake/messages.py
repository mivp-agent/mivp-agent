from copy import copy, deepcopy

from mivp_agent.messages import MissionMessage

from .state import FAKE_PAUSE_STATE, FAKE_RUNNING_STATE

def dup_message(msg: MissionMessage):
    '''
    Helper method to provide a copy of a mission message with a deepcopy of the episode_report and observation as these are dicts.

    Deepcopy does not work on MissionMessages because they contain locking primitives
    '''
    m = copy(msg)
    m.episode_report = deepcopy(m.episode_report)
    m.observation = deepcopy(m.observation)

    return m

FAKE_PAUSE_MESSAGE = MissionMessage(
    'fake-addr',
    FAKE_PAUSE_STATE,
    is_transition=False
)

FAKE_RUNNING_MESSAGE = MissionMessage(
    'fake-addr',
    FAKE_RUNNING_STATE,
    is_transition=False
)
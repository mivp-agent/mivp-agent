from dataclasses import dataclass
from typing import Any, Tuple, List
from threading import Lock

from mivp_agent.manager import MissionManager
from mivp_agent.agent import Agent
from mivp_agent.environment import Environment

@dataclass
class VehicleCache:
    # Store the last_episode number to detect episode transitions in new incoming messages
    last_episode: int = None
    # Store the last state to prevent `state_to_action` from being called until the agent arrives in a new state
    last_state: Any = None

    # Because BHV_Agent expects an action with every message and we don't want to call `state_to_action` for every message, we store the existing state
    # TODO: Modify BHV_Agent to replace previous if no action is passed?
    current_action: Any = None


@dataclass
class Transition:
    s1: Any
    action: Any
    s2: Any

Batch = List[Transition]

class Driver:
    def __init__(
        self,
        agent_template: Agent,
        environment: Environment = None,
        expect_agents: int = None,
        log: bool = True,
    ) -> None:
        self._agent_template = agent_template
        self._model = self._agent_template.build_model()

        self._environment = environment
        self._expect_agents = expect_agents
        self._log = log

        # TODO: Why is task name needed?
        self._mgr = MissionManager('driver', log=self._log)

        # Create structure to hold agent instances & vehicle cache
        self._agent_data = {}

        self._context_lock = Lock() # Purpose: Never use 'with Driver' twice
        self._work_lock = Lock() # Purpose: Only call sample / run once... other behavior is undefined

    def __enter__(self):
        if not self._context_lock.acquire(False):
            raise RuntimeError('Only one context acquisition allowed on Driver instances')

        if self._environment:
            self._environment.__enter__()

        self._mgr.__enter__()
        return self
    
    def _pause_all(self):
        # Put every connected vehicle into the paused state
        while not all(self._mgr.episode_state(vid) == 'PAUSED' for vid in self._mgr.get_ids()):
            msg = self._mgr.get_message()
            if msg.episode_state == 'PAUSED':
                msg.request_new()
            else:
                msg.stop()

    def _preflight_check(self):
        # Wait for the number of specified vehicles
        if self._expect_agents is not None:
            self._mgr.wait_for_count(self._expect_agents)

        self._pause_all()

    def _find_or_create_data(self, vid: str) -> Tuple[Agent, VehicleCache]:
        if vid not in self._agent_data:
            self._agent_data[vid] = (
                self._agent_template.duplicate(),
                VehicleCache()
            )

        return self._agent_data[vid]
    
    def _reset_caches(self):
        for vid in self._agent_data.keys():
            agent, _ = self._agent_data[vid]
            self._agent_data[vid] = (agent, VehicleCache())

    def sample(self, batches, episodes_per_batch):
        '''
        This method is used to collect a number of batches of episodes with specified size. It will `yield` the results after each batch is completed and put the vehicles in pause until control is returned for the next batch collection.

        NOTE: To guard against undefined behavior this method will grab a locking primitive to prevent against simultaneous calls.

        Additionally there is a check to make sure the Driver's context has been acquired by at least one source. This assures that the `MissionManager` server thread is started and open for communication. 
        '''
        # Someone has to have acquired the context (not a great guarantee of anything really)
        if self._context_lock.acquire(False):
            self._context_lock.release()
            raise RuntimeError('Please acquire the Driver\'s context before calling `sample(...)`')

        # Prevent simultaneous calls
        if not self._work_lock.acquire(False):
            raise RuntimeError('Unable to acquire the "work lock". Did you call `sample(...)` or `run(...)` ?')

        self._preflight_check()

        completed_batches = 0
        while completed_batches < batches:
            # Collect batches of transitions and yield them one at a time for training
            yield self._collect_batch(episodes_per_batch)

        self._work_lock.release()

    def _collect_batch(self, episodes) -> Batch:
        self._reset_caches()

        collected_episodes = 0
        batch: Batch = []
        while collected_episodes < episodes:
            msg = self._mgr.get_message()

            # Start vehicle if not started
            if msg.episode_state == 'PAUSED':
                msg.mark_transition() # Initial state should be a transition
                msg.start()

                continue # Don't try to use the message to react to

            agent, cache = self._find_or_create_data(msg.vid)
            current_state = agent.observation_to_state(msg.observation)

            if cache.last_state != current_state:
                msg.mark_transition() # For logger

                # If we have the information to fully construct a transition, do so and store
                if cache.last_state is not None and cache.current_action is not None:
                    batch.append(Transition(
                        cache.last_state,
                        cache.current_action,
                        current_state
                    ))

                # Get new action from model and update cache
                #print('yo')
                #print(self._model.rlock())
                with self._model.rlock():
                    cache.current_action = agent.state_to_action(
                        self._model,
                        current_state,
                        msg.observation
                    )

                cache.last_state = current_state

            if cache.last_episode != msg.episode_report['NUM']:
                # If this is not the first episode, increment the count bc we have completed the previous episode
                if cache.last_episode is not None:
                    collected_episodes += 1

                cache.last_episode = msg.episode_report['NUM']
                agent.start_episode()

            # Preform the action specified in the cache
            msg.act(cache.current_action)
        
        # Pause all vehicles and return the collected batch of transitions
        self._pause_all()
        return batch

    def __exit__(self, exc_type, exc_value, traceback):
        if self._environment:
            self._environment.__exit__()

        self._mgr.__exit__()

        self._context_lock.release()
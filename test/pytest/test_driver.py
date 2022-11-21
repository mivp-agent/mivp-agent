import pytest
from copy import copy
from unittest.mock import patch, call, Mock, MagicMock

from fake.actions import FAKE_ACTION
from fake.messages import dup_message, FAKE_PAUSE_MESSAGE, FAKE_RUNNING_MESSAGE
from fake.agent import FakeAgent

from mivp_agent import Driver, Agent, Model
from mivp_agent.messages import MissionMessage

@patch('mivp_agent.Agent.__abstractmethods__', set())
@patch('mivp_agent.driver.MissionManager')
def test_context_manager(mock_manager):
    d = Driver(Agent())

    mock_manager.return_value.__enter__.assert_not_called()

    with d:
        # Grabs the manager context
        mock_manager.return_value.__enter__.assert_called_once()
        # Does not release the context
        mock_manager.return_value.__exit__.assert_not_called()

        # Test that only one context can be acquired
        with pytest.raises(RuntimeError):
            with d:
                pass

    mock_manager.return_value.__exit__.assert_called_once()

@patch('mivp_agent.Agent.__abstractmethods__', set())
@patch('mivp_agent.driver.MissionManager')
def test_locking_rules(mock_manager):
    d = Driver(Agent())

    with pytest.raises(RuntimeError):
        next(d.sample(1,1))

    mock_manager.return_value.get_message = lambda: copy(FAKE_PAUSE_MESSAGE)
    d._collect_batch = lambda _: None
    with d, pytest.raises(RuntimeError):
        next(d.sample(1,1))
        next(d.sample(1,1))


@patch('mivp_agent.Agent.__abstractmethods__', set())
@patch('mivp_agent.driver.MissionManager')
def test_sample_preflight_wait(mock_manager):
    mock_manager = mock_manager.return_value
    mock_manager.wait_for_count.return_value = None
    
    def no_pause_or_collect(d):
        d._pause_all = lambda: None
        d._collect_batch = lambda _: None

    d = Driver(Agent())
    no_pause_or_collect(d)
    with d:
        next(d.sample(1,1))
    mock_manager.wait_for_count.assert_not_called()

    d = Driver(Agent(), expect_agents=2)
    no_pause_or_collect(d)
    with d:
        next(d.sample(1,1))
    mock_manager.wait_for_count.assert_called_once_with(2)


@patch('mivp_agent.Agent.__abstractmethods__', set())
@patch('mivp_agent.driver.MissionManager')
def test_sample_preflight_pause(mock_manager):
    mock_manager = mock_manager.return_value
    mock_manager.get_ids.return_value = (
        'id1',
        'id2'
    )
    episode_state = {
        'id1': 'RUNNING',
        'id2': 'RUNNING'
    }
    mock_manager.episode_state = lambda id: episode_state[id]

    message_mocks = (
        Mock(spec=MissionMessage),
        Mock(spec=MissionMessage)
    )
    for i, m in enumerate(message_mocks):
        m.episode_state = 'RUNNING'

        # Make the stop() method cause the state from `MissionManager.epsiode_state` change
        id = tuple(episode_state.keys())[i] # Order not particular important
        def mutate_state(id=id): # <--- forcing early binding of id (otherwise id2 is bound to both instances of the function)
            episode_state[id] = 'PAUSED'
        m.stop.side_effect = mutate_state
    
    mock_manager.get_message.side_effect = message_mocks

    d = Driver(Agent())
    d._collect_batch = lambda _: None
    with d:
        next(d.sample(1,1))
    for m in message_mocks:
        m.stop.assert_called_once()

@patch('mivp_agent.Agent')
@patch('mivp_agent.driver.MissionManager')
def test_sample_single_batch(mock_manager, mock_agent):
    mock_manager = mock_manager.return_value

    '''
    Message setup
    '''
    # Two messages, one to update the cache last_state from None -> a number the other to end signal the episode has ended.
    message1 = dup_message(FAKE_RUNNING_MESSAGE)
    message2 = dup_message(FAKE_RUNNING_MESSAGE)
    message2.episode_report['NUM'] += 1

    # Alter the state of m2 a little so we can tell the difference
    message2.observation['NAV_X'] = -12.0

    # Wrap in mocks so can track the calls,  return one after another
    def wrap_message(message: MissionMessage):
        m = Mock(spec=MissionMessage)
        m.vid = message.vid
        m.observation = message.observation
        m.episode_state = message.episode_state
        m.episode_report = message.episode_report
        return m
    m1 = wrap_message(message1)
    m2 = wrap_message(message2)
    mock_manager.get_message.side_effect = (m1, m2)

    '''
    Agent setup

    Constructing both a fake and a mock on this one to I can verify that the correct methods have been called
    '''
    mock_model = MagicMock(spec=Model)

    mock_model.rlock.return_value.__exit__.return_value = None
    #mock_model.rlock.return_value = Mock(autospec=True)
    fa = FakeAgent(mock_model)
    mock_agent.build_model.side_effect = fa.build_model
    mock_agent.observation_to_state.side_effect = fa.observation_to_state
    mock_agent.state_to_action.side_effect = fa.state_to_action
    # Make duplication do nothing
    mock_agent.duplicate.return_value = mock_agent

    '''
    Running the thing
    '''
    d = Driver(mock_agent)

    # Disable preflight checks
    d._preflight_check = lambda: None
    with d:
        next(d.sample(1,1))

    # Make sure both observations were passed to the agent
    state_calls = (
        call(m1.observation),
        call(m2.observation)
    )
    mock_agent.observation_to_state.assert_has_calls(state_calls)

    # Assert state -> action has been called properly
    mock_model.rlock.assert_has_calls((call(), call()), any_order=True) # For some reason the calls to __enter__ and __exit__ are showing up here, so any_order is True to prevent double calls
    act_calls = (
        call(mock_model, (98.0, 40.0), m1.observation),
        call(mock_model, (-12.0, 40.0), m2.observation)
    )
    mock_agent.state_to_action.assert_has_calls(act_calls)

    # This will be called for the second call b/c it acts as if it will continue collecting information / episodes
    mock_agent.start_episode.assert_has_calls((call(), call()))

    # Make sure act was called
    m1.act.assert_called_once_with(FAKE_ACTION)
    m2.act.assert_called_once_with(FAKE_ACTION)
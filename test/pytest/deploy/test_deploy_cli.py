import os
import pytest
from argparse import ArgumentParser
from unittest.mock import Mock, patch

from mivp_agent.deploy import Task, Environment
from mivp_agent.cli.deploy import DeployCLI

CURRENT_FILE = os.path.abspath(os.path.realpath(__file__))


class FakeEnvironment(Environment):
    _CUSTOM_ID = 'FAKE_ENVIRONMENT_123023'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_directory(self):
        return None
    
    def get_command(self):
        return None


def fake_callable():
    pass


class FakeTask(Task):
    _CUSTOM_ID = 'FAKE_TASK_123023'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_environment(self, **kwargs) -> Environment:
        return FakeEnvironment(**kwargs)
    
    def get_callable(self):
        return fake_callable

@patch('mivp_agent.deploy.deployments.docker.docker') # MacOS runners don't have a docker client, so mock docker.from_env()
def test_subparser_validation(mock_docker):
    cli = DeployCLI(ArgumentParser())
    with pytest.raises(SystemExit) as e:
        cli.do_it({})
    assert e.value.code == 1

@patch('mivp_agent.deploy.deployments.docker.docker') # MacOS runners don't have a docker client, so mock docker.from_env()
def test_basic(mock_docker):
    setup = Mock()
    teardown = Mock()
    args = {
        'env_args': 'ekey1=evalue1 ekey2=evalue2',
        'task_args': 'tkey1=tvalue1 tkey2=tvalue2',
        'setup': setup,
        'teardown': teardown,
        'task_file': CURRENT_FILE
    }

    parser = ArgumentParser()
    cli = DeployCLI(parser)
    
    def validate(args, task, env):
        '''
        This method is used to validate the construction and initialization of the FakeTask and FakeEnvironment. Because these objects are dynamically imported by the CLI I was finding it difficult to patch / mock them... thus this side effect.
        '''
        assert args == args
        
        '''
        Using duck typing bellow because `isinstance(task, FakeTask)` does not work well with the dynamic imports either. Seems to be something related to different `id(class)`s being returned.

        More here:
        - https://stackoverflow.com/questions/46365996/two-objects-made-from-the-same-class-using-different-import-methods-isinstance
        - https://stackoverflow.com/questions/17179440/python-2-7-isinstance-fails-at-dynamically-imported-module-class
        '''
        assert task._CUSTOM_ID == FakeTask._CUSTOM_ID
        task_args = {
            'tkey1': 'tvalue1',
            'tkey2': 'tvalue2'
        }
        assert set(task_args.items()).issubset(set(task.kwargs.items()))

        assert env._CUSTOM_ID == FakeEnvironment._CUSTOM_ID
        env_args = {
            'ekey1': 'evalue1',
            'ekey2': 'evalue2'
        }
        assert set(env_args.items()).issubset(set(env.kwargs.items()))

    setup.side_effect = validate
    teardown.side_effect = validate

    cli.do_it(args)

    setup.assert_called_once()
    teardown.assert_called_once()
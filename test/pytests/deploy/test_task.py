import os
import pytest

from mivp_agent.deploy import Task

CURRENT_FILE = os.path.realpath(__file__)
CURRENT_DIR = os.path.abspath(os.path.dirname(CURRENT_FILE))


class BadCallable(Task):
    def get_environment(self, **kwargs):
        # Won't be used
        return None
    
    # No run


def test_abc():
    with pytest.raises(TypeError):
        BadCallable()


class ValidTask(Task):
    def get_environment(self, **kwargs):
        # This won't be used so... almost valid ;)
        return None
    
    def run():
        pass


def test_directory():
    t = ValidTask()
    assert t.get_directory() == CURRENT_DIR


def test_command():
    expected_command = 'agnt run test_task.py'
    expected_command += ' {\\"namespace\\":{\\"value\\":5}}'

    config = {
        'namespace': {
            'value': 5
        }
    }

    t = ValidTask(config=config)
    assert t.get_command() == expected_command

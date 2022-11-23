import os
import pytest

from mivp_agent.deploy import Task

CURRENT_FILE = os.path.realpath(__file__)
CURRENT_DIR = os.path.abspath(os.path.dirname(CURRENT_FILE))


class BadCallable(Task):
    def get_environment(self, **kwargs):
        # Won't be used
        return None
    
    def get_callable(self):
        return 'not-a-callable'


def test_callable_validation():
    b = BadCallable()
    with pytest.raises(AssertionError):
        b.get_command()


def my_callable():
    pass


class ValidTask(Task):
    def get_environment(self, **kwargs):
        # This won't be used so... almost valid ;)
        return None
    
    def get_callable(self):
        return my_callable


def test_directory():
    t = ValidTask()
    assert t.get_directory() == CURRENT_DIR


def test_command():
    t = ValidTask()
    expected_command = 'agnt run test_task.py my_callable'
    expected_command += ' --args key1=value1 key2=value2'

    kwargs = {
        'key1': 'value1',
        'key2': 'value2'
    }

    assert t.get_command(**kwargs) == expected_command

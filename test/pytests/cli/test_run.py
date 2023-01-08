import os
from unittest.mock import Mock, patch
from argparse import ArgumentParser

from mivp_agent.cli.run import RunCLI


CURRENT_FILE = os.path.abspath(os.path.realpath(__file__))
CURRENT_DIR = os.path.dirname(CURRENT_FILE)


@patch('mivp_agent.cli.run._load_dynamic_task')
def test_basic(task_loader):
    parser = ArgumentParser()
    cli = RunCLI(parser)

    mock_module = Mock()
    mock_module.mock_callable.return_value = 'Blah'

    args = {
        'python_file': CURRENT_FILE,
        'config': '{"namespace": {"value": 5}}'
    }

    task_loader.return_value = Mock()

    cli.do_it(args)
    task_loader.assert_called_once_with(CURRENT_FILE)


def test_real_file(capsys):
    '''
    This part is testing
    1. A valid callable will be called correctly.
    2. Relative imports will work after sys.path.append(...)
    '''

    args = {
        'python_file': os.path.join(CURRENT_DIR, 'res/valid_task.py'),
        'config': '{"namespace": {"value": 5}}'
    }

    parser = ArgumentParser()
    cli = RunCLI(parser)
    cli.do_it(args)

    captured = capsys.readouterr()
    assert captured.out == 'Hello friend!\n'
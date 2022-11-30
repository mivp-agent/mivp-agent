import os
from unittest.mock import Mock, patch
from argparse import ArgumentParser

from mivp_agent.cli.run import RunCLI


CURRENT_FILE = os.path.abspath(os.path.realpath(__file__))


@patch('mivp_agent.cli.run.importlib.util.module_from_spec')
@patch('mivp_agent.cli.run.importlib.util.spec_from_file_location')
def test_basic(spec_from_file_location, module_from_spec):
    parser = ArgumentParser()
    cli = RunCLI(parser)

    mock_module = Mock()
    mock_module.mock_callable.return_value = 'Blah'

    args = {
        'python_file': CURRENT_FILE,
        'python_callable': 'mock_callable',
        'args': None
    }

    spec_from_file_location.return_value = Mock()
    module_from_spec.return_value = mock_module

    cli.do_it(args)
    spec_from_file_location.assert_called_once_with(
        'dynamic_callable',
        CURRENT_FILE
    )
    mock_module.mock_callable.assert_called_once_with()

    # Again with some args
    args['args'] = ['key1=value1', 'key2=value2']
    cli.do_it(args)
    spec_from_file_location.assert_called_with(
        'dynamic_callable',
        CURRENT_FILE
    )
    mock_module.mock_callable.assert_called_with(
        key1='value1',
        key2='value2'
    )
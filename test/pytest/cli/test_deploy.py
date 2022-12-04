import os
import pytest
from argparse import ArgumentParser
from unittest.mock import Mock

from mivp_agent.cli.deploy import DeployCLI

'''
**IMPORTANT NOTE**

Do not import res/valid_task.py here. This will break the testing of `patch_dynamic_sys_path(..)` and `import relative_import` in `test_real_file(..)`
'''

CURRENT_FILE = os.path.abspath(os.path.realpath(__file__))
CURRENT_DIR = os.path.dirname(CURRENT_FILE)


def test_subparser_validation():
    '''
    This method tests if the deployment command has been set properly. For example `agnt deploy docker task.py` is a valid usage while `agnt deploy task.py` is not.
    '''
    cli = DeployCLI(ArgumentParser())
    with pytest.raises(SystemExit) as e:
        cli.do_it({})
    assert e.value.code == 1


@pytest.mark.parametrize('task_path, expected_error', [
    (os.path.join(CURRENT_DIR, 'not_a_directory'), 'The path specified by `task-path` is not a file, please check the CLI usage.'),
    (os.path.join(CURRENT_DIR, 'res/not_python.txt'), 'No ModuleSpec could be loaded from the `task-file` path specified. This may indicate the file is not a valid python file.'),
    (os.path.join(CURRENT_DIR, 'res/import_issue.py'), "No module named 'not_an_actual_module'"),
    (os.path.join(CURRENT_DIR, 'res/syntax_issue.py'), "invalid syntax")
])
def test_dynamic_import_failure(capsys, task_path, expected_error):
    setup = Mock()
    teardown = Mock()
    args = {
        'task_file': task_path,
        'setup': setup,
        'teardown': teardown
    }
    cli = DeployCLI(ArgumentParser())
    with pytest.raises(SystemExit) as e:
        cli.do_it(args)

    captured = capsys.readouterr()
    print(captured.err) # For ease of debugging when there are errors
    
    # Find error that is specific to type of issue
    issue_message_idx = captured.err.find(expected_error)
    assert issue_message_idx != -1

    exit_message_idx = captured.err.find('Error: Deploy CLI could not load the task specified in your command. Please see the error above.')
    assert exit_message_idx != -1
    assert issue_message_idx < exit_message_idx
    assert e.value.code == 1


def test_real_file():
    setup = Mock()
    teardown = Mock()
    args = {
        'env_args': ['ekey1=evalue1', 'ekey2=evalue2'],
        'task_args': ['tkey1=tvalue1', 'tkey2=tvalue2'],
        'setup': setup,
        'teardown': teardown,
        'task_file': os.path.join(
            CURRENT_DIR,
            'res/valid_task.py'
        )
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
        assert task._CUSTOM_ID == 'VALID_TASK_123023'
        task_args = {
            'tkey1': 'tvalue1',
            'tkey2': 'tvalue2'
        }
        assert set(task_args.items()).issubset(set(task.kwargs.items()))

        assert env._CUSTOM_ID == 'VALID_ENVIRONMENT_123023'
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
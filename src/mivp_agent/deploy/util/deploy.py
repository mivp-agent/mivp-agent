import os, sys
import traceback
import inspect
import importlib.util

from mivp_agent.deploy import Task, Environment
from mivp_agent.deploy.deployment import Deployment

from mivp_agent.tunable.configs import config_from_json


def deploy(
    args: dict,
    deployment: Deployment,
    task_file: str,
    config_path: str,
    skip_setup=True,
    skip_teardown=True
):
    '''
    This function actually deploys a specified task. It is used by both the `agnt deploy` and `agnt tune` commands.
    '''
    if config_path is None:
        config = {}
    else:
        config = config_from_json(config_path)

    task, env = load_task_env(task_file, config)

    # Configure all tunables
    deployment.from_config(config)
    task.from_config(config)
    env.from_config(config)

    if not skip_setup:
        deployment.setup(args, task, env)

    try:
        deployment.start(args, task, env)
    except:  # noqa: E722
        traceback.print_exc()

        print('\nEncountered the exception above while running start()')

    try:
        deployment.stop(args, task, env)
    except:  # noqa: E722
        traceback.print_exc()

        print('\nEncountered the exception above while running stop()')

    if not skip_teardown:
        deployment.teardown(args, task, env)


def load_task_env(task_path: str, config: dict):
    '''
    This helper function loads and constructs instances of a `Task` and `Environment` from a specified task_path and config provided.
    '''
    task_path = os.path.abspath(task_path)
    assert os.path.isfile(task_path), 'The path to the task file is not a valid file path'

    task_cls = _load_dynamic_task(task_path)

    task: Task = task_cls(config=config, file_path=task_path)
    env: Environment = task.get_environment()

    return task, env


def _patch_dynamic_sys_path(file_path):
    '''
    Python will usually add the directory of an executed file to the `sys.path`. Because both `agnt deploy` and `agnt run` are dynamically loading files to be executed / interpreted this is done manually through this function.

    **NOTE:** This should be called before the module is dynamically imported.
    '''
    sys.path.append(os.path.abspath(os.path.dirname(file_path)))


def _load_dynamic_task(task_path):
    '''
    This helper function is used to dynamically import a Task class from a given file.
    '''
    _patch_dynamic_sys_path(task_path)

    task_spec = importlib.util.spec_from_file_location(
        'dynamic_task',
        task_path
    )
    assert task_spec is not None, 'No ModuleSpec could be loaded from the task file path. This may indicate the file is not a valid python file.'

    task_module = importlib.util.module_from_spec(task_spec)
    task_spec.loader.exec_module(task_module)

    # Find the task (Must be subclass)
    task_cls = None
    for attr_name in dir(task_module):
        attr = getattr(task_module, attr_name)
        if inspect.isclass(attr) and issubclass(attr, Task) and attr != Task:
            assert task_cls is None, f'Multiple tasks defined in: {task_path}'
            task_cls = attr
    
    assert task_cls is not None, f'Unable to find task in specified path: {task_path}'

    return task_cls
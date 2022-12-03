import os
import pytest
import subprocess

from mivp_agent.deploy.util.docker import get_or_build


CURRENT_FILE = os.path.realpath(__file__)
CURRENT_DIR = os.path.abspath(os.path.dirname(CURRENT_FILE))


def decode_if_bytes(obj):
    if hasattr(obj, 'decode'):
        return obj.decode()
    return obj


def test_docker_build():
    '''
    This test builds both images required for the following test, don't want to do this in `agnt deploy` for two reasons
    1. Hard to view the output of the image building incrementally via `Popen.communicate` (want to be able to see progress)
    2. The timeout on `Popen.communicate(...)` was causing the GitHub runners to fail as they need to build the image from scratch each time.
    '''
    get_or_build('mivp-agent-task-base')
    get_or_build('mivp-agent-env-base')

@pytest.mark.run(after='test_docker_build')
def test_docker():
    task_file = os.path.join(
        CURRENT_DIR,
        'basic_deployable/task.py'
    )
    package_dir = os.path.abspath(os.path.join(
        CURRENT_DIR,
        '../..'
    ))
    deploy_command = f'agnt deploy docker {task_file} --task-args key=value --dev {package_dir}'

    # The lists below should be ordered, it will be asserted later in the test
    task_output = [
        "Hello from the task!",
        "With args: {'key': 'value'}",
        "!! End of stream received !!"
    ]
    task_output = [f'task | {out}' for out in task_output]
    env_output = [
        "Hello from the environment!",
        "I am an example resource",
        "!! End of stream received !!"
    ]
    env_output = [f'env | {out}' for out in env_output]
    
    p = subprocess.Popen(deploy_command.split(), stdout=subprocess.PIPE)
    stdout, stderr = p.communicate(timeout=360)
    
    stdout = decode_if_bytes(stdout)
    stderr = decode_if_bytes(stderr)
    # For ease of debugging
    print(stdout)
    print(stderr)

    # Make sure there were no errors in the deploy command
    assert p.returncode == 0
    
    def validate_existence_and_order(output_list):
        indices = [stdout.find(out) for out in output_list]
        
        last_position = None
        last_idx = None
        for i, position in enumerate(indices):
            assert position != -1, f'Unable to found expected output: {output_list[i]}'

            if last_idx is not None:
                assert last_position < position, f'Found out of order messages: ("{output_list[last_idx]}" and {output_list[i]})'
            
            last_idx = i
            last_position = position

    validate_existence_and_order(task_output)
    validate_existence_and_order(env_output)
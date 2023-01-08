import relative_import # noqa: F401 Make sure sys.path.append(..) works properly

from mivp_agent.deploy import Task, Environment
from mivp_agent.tunable import IntDim


class ValidEnvironment(Environment):
    _CUSTOM_ID = 'VALID_ENVIRONMENT_123023'

    def feasible_space(self):
        return 'env', {
            'env_param': IntDim(0, 5)
        }

    def get_directory(self):
        return None
    
    def get_command(self):
        return None


class ValidTask(Task):
    _CUSTOM_ID = 'VALID_TASK_123023'

    def feasible_space(self):
        return 'task', {
            'task_param': IntDim(0, 5)
        }

    def get_environment(self) -> Environment:
        return ValidEnvironment()
    
    def run(self):
        print('Hello friend!')
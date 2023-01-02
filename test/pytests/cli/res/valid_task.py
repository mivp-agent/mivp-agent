import relative_import # noqa: F401 Make sure sys.path.append(..) works properly

from mivp_agent.deploy import Task, Environment


class ValidEnvironment(Environment):
    _CUSTOM_ID = 'VALID_ENVIRONMENT_123023'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_directory(self):
        return None
    
    def get_command(self):
        return None


def valid_callable():
    pass


class ValidTask(Task):
    _CUSTOM_ID = 'VALID_TASK_123023'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_environment(self, **kwargs) -> Environment:
        return ValidEnvironment(**kwargs)
    
    def get_callable(self):
        return valid_callable
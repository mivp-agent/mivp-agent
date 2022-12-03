from mivp_agent.deploy import Task, Environment

from env import ExampleEnvironment


def example_callable(**kwargs):
    print('Hello from the task!')
    if kwargs:
        print(f'With args: {kwargs}')


class ExampleTask(Task):
    def get_environment(self, **kwargs) -> Environment:
        return ExampleEnvironment()
    
    def get_callable(self):
        return example_callable

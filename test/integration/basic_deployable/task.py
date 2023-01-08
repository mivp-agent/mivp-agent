from mivp_agent.deploy import Task, Environment
from mivp_agent.tunable import IntDim

from env import ExampleEnvironment


class ExampleTask(Task):
    def feasible_space(self):
        return 'task', {
            'value': IntDim(0, 10)
        }

    def get_environment(self) -> Environment:
        return ExampleEnvironment()
    
    def run(self):
        print('Hello from the task!')
        print(f'With value: {self.get_value("value")}')

from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace

from mivp_agent.deploy import Task, Environment


class Deployment(ABC):
    '''
    The `Deployment` class is meant to provide a framework where compute resources can be provisioned and the `Task` and `Environment` containers can be deployed on those resources.

    The two primary methods required are `setup(...)` and `teardown(...)`. The `setup(...)` method should provision infrastructure, deploy and start `Environment` containers, deploy and start the `Task` container and block until the task has completed.

    The `teardown(...)` method will be called after control has been returned from `startup(...)` to undo the provisioning step and free up compute resources.

    Deployments are intended to be launched through the `agnt deploy` command. As such, they may define custom `argparse` arguments. Parsed args will be passed to both


    **IMPORTANT NOTE:** The `get_command(...)` should be run inside the copy of the directory returned by `get_directory(...)`. This will be expected by the implementors of `Tasks`.
    '''

    def _configure_parser(self, parser: ArgumentParser):
        # Tell the `agnt deploy` command to use this instance of setup and teardown.
        parser.set_defaults(setup=self.setup)
        parser.set_defaults(teardown=self.teardown)

        # Allow user to set further args
        self.configure_parser(parser)

    @abstractmethod
    def configure_parser(self, parser: ArgumentParser):
        pass

    @abstractmethod
    def setup(self, args: Namespace, task: Task, environment: Environment):
        pass

    @abstractmethod
    def teardown(self, args: Namespace, task: Task, environment: Environment):
        pass

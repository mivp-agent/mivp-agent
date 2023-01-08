import json
from argparse import ArgumentParser, Namespace

from mivp_agent.deploy import Task
from mivp_agent.deploy.util.deploy import _load_dynamic_task


class RunCLI:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

        self.parser.set_defaults(func=self.do_it)
        self.parser.add_argument(
            'python_file',
            metavar='python-file',
            default=None,
            help="Path to the python file which the callable is located in."
        )
        self.parser.add_argument(
            'config',
            metavar='python-callable',
            default=None,
            help="Name of the python callable inside the `python-file` file to be called."
        )

    def do_it(self, args: Namespace):
        # See DeployCLI's do_it for comments on this
        if not isinstance(args, dict):
            args = vars(args)
        
        config = json.loads(args['config'])
        
        task_cls = _load_dynamic_task(args['python_file'])

        task: Task = task_cls(config=config, file_path=args['python_file'])
        # Apologies for the eye bleeding here, config is used in the constructor to make is easy on `get_command(...)` before deployment AND config is used below *after* deployment to actually load the config. Technically since the task is deployed we shouldn't need the logic above but right now it is packages together.
        task.from_config(config)

        task.run()
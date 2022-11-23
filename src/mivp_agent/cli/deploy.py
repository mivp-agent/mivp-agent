import os, sys
import inspect
import importlib.util
from argparse import ArgumentParser, Namespace

from mivp_agent.deploy import Task
from mivp_agent.deploy.deployment import Deployment
from mivp_agent.deploy.deployments import DockerDeployment


class DeployCLI:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser
        self.subparsers = self.parser.add_subparsers()

        self.parser.set_defaults(func=self.do_it)
        
        self._setup_subparser('docker', DockerDeployment())
    
    def _setup_subparser(self, name, deployment: Deployment):
        '''
        Without applying the following arguments at the subparser level, they would need to be applied before the sub command is used.

        What we don't want:
        ```
        agnt deploy MyTask k8
        ```

        What we are creating with this method:
        ```
        agnt deploy k8 MyTask
        ```
        '''
        subparser = self.subparsers.add_parser(name)
        subparser.add_argument(
            'task_file',
            metavar='task-file',
            default=None,
            help="Path to the python file containing your task class to deploy."
        )

        subparser.add_argument(
            '--env-args',
            metavar="KEY=VALUE",
            nargs="+",
            required=False,
            default={},
            help="Use --env-args followed by any number of KEY=VALUE pairs which will be passed to the **kwargs of the Environment."
        )

        subparser.add_argument(
            '--task-args',
            metavar="KEY=VALUE",
            nargs="+",
            required=False,
            default={},
            help="Use --task-args followed by any number of KEY=VALUE pairs which will be passed to the **kwargs of the Task."
        )

        # Allow deployment to add arguments
        deployment._configure_parser(subparser)
    
    def _parse_key_value_pair(self, pairs):
        pairs_dict = {}
        if pairs:
            pairs = pairs.split() # Split on white space.
            for pair in pairs:
                items = pair.split('=')
                if len(items) < 0:
                    raise RuntimeError(f'Found non key-value pair: "{pair}" please use "=" to delimit key-value pairs (no spaces allowed in keys or pairs).')
                key = items[0].strip('')
                value = '='.join(items[1:])
                
                pairs_dict[key] = value
        return pairs_dict
    
    def _load_task_cls(self, args):
        '''
        This is a helper method which dynamically loads a subclass of `Task` given the `args.task-file` argument.

        This is needed because tasks are user defined. We do not know the task to launch until runtime. We don't even know the set of tasks which can be run. This forces us to do some semi-complicated things with `importlib` to dynamically load
        '''
        # Because we don't know which task to launch before runtime (or even the set of tasks that can be run)
        task_path = os.path.abspath(args['task_file'])
        task_spec = importlib.util.spec_from_file_location(
            'dynamic_task', # pathlib.Path(task_path).stem,
            task_path
        )
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

        return task_cls, task_path

    def do_it(self, args: Namespace):
        # If a positional argument (subparser) command was specified, then both setup and tear down should be specified. See `Deployment._configure_parser`. If this has not been done, instruct the user to do so.
        if not isinstance(args, dict): # During testing a dict is used
            args = vars(args) # Because Namespaces suck

        if 'setup' not in args or 'teardown' not in args:
            print("Error: please use at least one positional argument\n", file=sys.stderr)

            self.parser.print_help()
            exit(1)

        # Dynamically load the task from specified file (might Error)
        task_cls, task_path = self._load_task_cls(args)

        # Parse out the env and task arguments
        env_args = self._parse_key_value_pair(args['env_args'])
        task_args = self._parse_key_value_pair(args['task_args'])

        # Construct the task and environment
        task: Task = task_cls(file_path=task_path, **task_args)
        env = task.get_environment(**env_args)

        # Run deployment
        args['setup'](args, task, env)
        args['teardown'](args, task, env)

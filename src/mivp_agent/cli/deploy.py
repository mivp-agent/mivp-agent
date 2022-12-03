import os, sys
import inspect
import traceback
import importlib.util
from argparse import ArgumentParser, Namespace

from mivp_agent.deploy import Task
from mivp_agent.deploy.deployment import Deployment
from mivp_agent.deploy.deployments import DockerDeployment

from .util import parse_kv_pairs


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
            default=None,
            help="Use --env-args followed by any number of KEY=VALUE pairs which will be passed to the `**kwargs` of the Environment."
        )

        subparser.add_argument(
            '--task-args',
            metavar="KEY=VALUE",
            nargs="+",
            required=False,
            default=None,
            help="Use --task-args followed by any number of KEY=VALUE pairs which will be passed to the `**kwargs` of the Task."
        )

        # Allow deployment to add arguments
        deployment._configure_parser(subparser)
    
    def _load_task_cls(self, args):
        '''
        This is a helper method which dynamically loads a subclass of `Task` given the `args.task-file` argument.

        This is needed because tasks are user defined. We do not know the task to launch until runtime. We don't even know the set of tasks which can be run. This forces us to do some semi-complicated things with `importlib` to dynamically load
        '''
        # Because we don't know which task to launch before runtime (or even the set of tasks that can be run)
        task_path = os.path.abspath(args['task_file'])
        assert os.path.isfile(task_path), 'The path specified by `task-path` is not a file, please check the CLI usage.'

        task_spec = importlib.util.spec_from_file_location(
            'dynamic_task', # pathlib.Path(task_path).stem,
            task_path
        )
        assert task_spec is not None, 'No ModuleSpec could be loaded from the `task-file` path specified. This may indicate the file is not a valid python file.'
        
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
        try:
            task_cls, task_path = self._load_task_cls(args)
        except: # noqa: E722
            traceback.print_exc()

            print('\nError: Deploy CLI could not load the task specified in your command. Please see the error above.', file=sys.stderr)
            exit(1)

        # Parse out the env and task arguments
        env_args = parse_kv_pairs(args['env_args'])
        task_args = parse_kv_pairs(args['task_args'])

        # Construct the task and environment
        try:
            task: Task = task_cls(file_path=task_path, **task_args)
        except TypeError:
            traceback.print_exc()
            print('\nError: Type error received while calling __init__(). If you have added --task-args this may indicate your __init__ function does not have **kwargs in the parameter list.', file=sys.stderr)
            exit(1)

        try:
            env = task.get_environment(**env_args)
        except TypeError:
            traceback.print_exc()
            print('\nError: Type error received while calling get_environment(). If you have added --env-args this may indicate your function does not have **kwargs in the parameter list.', file=sys.stderr)
            exit(1)

        # Run deployment
        try:
            args['setup'](args, task, env)
        except KeyboardInterrupt:
            print('\nReceived keyboard interrupt, running teardown method...')
        
        args['teardown'](args, task, env)

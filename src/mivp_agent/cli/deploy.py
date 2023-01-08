import sys
import traceback
from argparse import ArgumentParser, Namespace

from mivp_agent.deploy.deployment import Deployment
from mivp_agent.deploy.deployments import DockerDeployment
from mivp_agent.deploy.util.deploy import deploy


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
        agnt deploy MyTask config.json k8
        ```

        What we are creating with this method:
        ```
        agnt deploy k8 MyTask config.json
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
            '--config',
            default=None,
            required=False,
            help='Specify path to the simulation config'
        )

        # Allow deployment to add arguments
        deployment._configure_parser(subparser)

    def do_it(self, args: Namespace):
        # If a positional argument (subparser) command was specified, then both setup and tear down should be specified. See `Deployment._configure_parser`. If this has not been done, instruct the user to do so.
        if not isinstance(args, dict): # During testing a dict is used
            args = vars(args) # Because Namespaces suck

        if 'deployment' not in args:
            print("Error: please use at least one positional argument\n", file=sys.stderr)

            self.parser.print_help()
            exit(1)

        try:
            deploy(args, args['deployment'], args['task_file'], args['config'])
        except:  # noqa: E722
            traceback.print_exc()

            print('\nError: Deploy CLI could not load the task specified in your command. Please see the error above.', file=sys.stderr)
            exit(1)
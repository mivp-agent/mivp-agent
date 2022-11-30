import os, sys
import importlib.util
from argparse import ArgumentParser, Namespace

from .util import parse_kv_pairs


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
            'python_callable',
            metavar='python-callable',
            default=None,
            help="Name of the python callable inside the `python-file` file to be called."
        )
        self.parser.add_argument(
            '--args',
            metavar="KEY=VALUE",
            nargs="+",
            required=False,
            default=None,
            help="Use --args followed by any number of KEY=VALUE pairs which will be passed to the `**kwargs` of the python callable."
        )
    
    def _patch_sys_path(self, file_path):
        '''
        Little bit about the below...

         Usually when executing a `file.py` the directory which the file is in will be added to `sys.path`. Since `agnt run` commands are technically calling the `/usr/local/bin/agnt` script, only that directory is added. This causes imports from the same directory to fail.

         So we add the path manually to the path...

         **NOTE:** This needs to be called before modules are imported as that is what we are patching.
        '''
        sys.path.append(os.path.abspath(os.path.join(
            file_path,
            '..'
        )))

    def do_it(self, args: Namespace):
        # See DeployCLI's do_it for comments on this
        if not isinstance(args, dict):
            args = vars(args)
        
        assert os.path.isfile(args['python_file']), f'Python file provided to `agnt run` does not exist or is directory: {args["python_file"]}'

        file_path = os.path.abspath(args['python_file'])
        file_spec = importlib.util.spec_from_file_location(
            'dynamic_callable',
            file_path
        )
        self._patch_sys_path(file_path)
        file_module = importlib.util.module_from_spec(file_spec)
        file_spec.loader.exec_module(file_module)

        try:
            callable_attr = getattr(file_module, args['python_callable'])
        except AttributeError:
            print(f'Error: python callable "{args["python_callable"]}" does not exist on file "{args["python_file"]}"', file=sys.stderr)
            exit(1)

        callable_attr(**parse_kv_pairs(args['args']))
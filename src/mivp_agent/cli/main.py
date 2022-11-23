import sys
import argparse

from .info import Info
from .log import Log
from .inspect.inspector import Inspector
from .deploy import DeployCLI

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

DeployCLI(subparsers.add_parser('deploy'))
Info(subparsers.add_parser('info'))
Log(subparsers.add_parser('log'))
Inspector(subparsers.add_parser('inspect'))


def main():
    args = parser.parse_args()

    # If no sub command is specified, print help and exit
    if not hasattr(args, 'func'):
        print("Error: please use at least one positional argument\n", file=sys.stderr)

        parser.print_help()
        exit(1)

    # Otherwise trigger sub command
    args.func(args)


if __name__ == 'main':
    main()

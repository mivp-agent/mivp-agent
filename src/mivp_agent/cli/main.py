import argparse

from .info import Info
from .log import Log
from .inspect.inspector import Inspector

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

Info(subparsers.add_parser('info'))
Log(subparsers.add_parser('log'))
Inspector(subparsers.add_parser('inspect'))

def main():
  args = parser.parse_args()

  # If no sub command is specified, print help and exit
  if not hasattr(args, 'func'):
    parser.print_help()
    exit(1)
  
  # Otherwise trigger sub command
  args.func(args)

if __name__ == 'main':
  main()
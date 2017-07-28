#!/usr/bin/env python
"""Zargparse - a tool for generating Zsh completion files."""

import argparse
import runpy
import sys


# pylint: disable=protected-access
# noinspection PyProtectedMember
def inspect_parser(parser: argparse.ArgumentParser, _args=None,
                   _namespace=None) -> None:
    """Inspects the ArgumentParser object."""
    tool_name = parser.prog.rstrip('.py')
    print(tool_name)
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            print('Subparsers: {}'.format(action.choices.keys()))
        print(action.option_strings)

    sys.exit(0)


def main(file_path):
    # Monkey patch parse_args in order to inspect the ArgumentParser object
    argparse.ArgumentParser.parse_args = inspect_parser

    # Run the file as __main__ to emulate usage via the command line
    runpy.run_path(file_path, run_name='__main__')


if __name__ == '__main__':
    _parser = argparse.ArgumentParser(
        description='Zargparse - A Zsh completion file generator')
    _parser.add_argument('file_path', help='File to generate completion')
    _parser.add_argument('--name', help='Name of tool')
    arguments = _parser.parse_args()

    main(arguments.file_path)

#!/usr/bin/env python
"""Zargparse - a tool for generating Zsh completion files."""

import argparse
import os
import runpy
import sys

import jinja2

TEMPLATE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'completion.jinja')


class Argument:
    """A positional argument."""
    def __init__(self, name: str, help_text: str) -> None:
        self.name = name
        self.help_text = help_text


class Flag:
    """A command line flag."""
    def __init__(self, options, help_text: str, has_argument: bool) -> None:
        self.options = options
        self.help_text = help_text
        self.has_argument = has_argument

    @property
    def arg_string(self) -> str:
        """String passed to _arguments function in a Zsh completion file.

        A flag with one option and no arguments:
            '--flag[Description of flag.]'

        The same flag that takes an argument:
            '--flag=[Description of flag.]'

        A flag with multiple options that takes an argument:
            '(--flag -f)'{--flag,-f}'=[Description of flag.]:'
        """
        result = "'"
        if len(self.options) == 1:
            result += self.options[0]
        else:
            result += "(" + ' '.join(self.options) + ")'"
            result += "{" + ','.join(self.options) + "}'"
        if self.has_argument:
            result += '='
        result += "[{}]".format(self.help_text)
        if self.has_argument:
            # This is needed so that completion works for subcommands when a
            # global flag is used.
            result += ':'
        result += "'"
        return result


class Subcommand:
    """A subcommand of a command line tool."""
    def __init__(self, name: str, help_text: str) -> None:
        self.name = name
        self.help_text = help_text
        self.flags = []
        self.arguments = []


class Tool:
    """A command line tool."""
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.subcommands = []
        self.flags = []
        self.arguments = []

    def print(self):
        print('Tool Name: {}'.format(self.name))
        print('Description: {}'.format(self.description))
        print('Flags:')
        for flag in self.flags:
            print('  {}: {}'.format(flag.options, flag.help_text))
        print('Positional arguments:')
        for arg in self.arguments:
            print('  {}: {}'.format(arg.name, arg.help_text))
        print('Subcommands:')
        for subcommand in self.subcommands:
            print('  {}: {}'.format(subcommand.name, subcommand.help_text))
            for flag in subcommand.flags:
                print('    {}: {}'.format(flag.options, flag.help_text))
            for arg in subcommand.arguments:
                print('    {}: {}'.format(arg.name, arg.help_text))


# pylint: disable=protected-access
# noinspection PyProtectedMember
class ParserAnalyzer:
    """Analyze the ArgumentParser object.

    This collects the data needed for autocompletion.
    """
    def __init__(self, parser: argparse.ArgumentParser) -> None:
        self.parser = parser
        tool_name = self.parser.prog
        description = self.parser.description
        self.tool = Tool(tool_name, description)
        self._analyze_parser()

    def _analyze_parser(self):
        for action in self.parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                self._analyze_subparsers(action)
            elif action.option_strings:
                self.tool.flags.append(self._get_flag(action))
            else:
                self.tool.arguments.append(self._get_argument(action))

    def _analyze_subparser(self, subparser: argparse.ArgumentParser,
                           help_text: str, name: str):
        subcommand = Subcommand(name, help_text)
        for action in subparser._actions:
            if isinstance(action, argparse._SubParsersAction):
                # Nested subparsers are not supported
                pass
            elif action.option_strings:
                subcommand.flags.append(self._get_flag(action))
            else:
                subcommand.arguments.append(self._get_argument(action))
        self.tool.subcommands.append(subcommand)

    @staticmethod
    def _get_argument(action: argparse.Action):
        return Argument(action.dest, action.help)

    @staticmethod
    def _get_flag(action: argparse.Action):
        options = action.option_strings
        help_text = action.help
        if isinstance(action, (argparse._HelpAction,
                               argparse._StoreFalseAction,
                               argparse._StoreTrueAction,
                               argparse._CountAction,
                               argparse._AppendConstAction,
                               argparse._VersionAction,
                               argparse._StoreConstAction)):
            has_argument = False
        else:
            has_argument = True
        return Flag(options, help_text, has_argument)

    def _analyze_subparsers(self, action: argparse._SubParsersAction) -> None:
        for index, name in enumerate(action.choices.keys()):
            # The help text for a subcommand is stored in _choices_action
            help_text = action._choices_actions[index].help
            self._analyze_subparser(action.choices[name], help_text, name)


def fake_parse_args(parser: argparse.ArgumentParser, _args=None,
                    _namespace=None) -> None:
    """Used to monkey patch ArgumentParser.parse_args."""
    analyzer = ParserAnalyzer(parser)
    with open(TEMPLATE_FILE) as f:
        template = jinja2.Template(f.read(), trim_blocks=True)

    output_file = '_{}'.format(analyzer.tool.name)
    print('Writing completion file to {}'.format(output_file))
    with open(output_file, 'w') as f:
        f.write(template.render(tool=analyzer.tool))
    sys.exit(0)


def main(file_path: str):
    # Monkey patch parse_args in order to inspect the ArgumentParser object
    argparse.ArgumentParser.parse_args = fake_parse_args

    # Run the file as __main__ to emulate usage via the command line
    runpy.run_path(file_path, run_name='__main__')


if __name__ == '__main__':
    _parser = argparse.ArgumentParser(
        description='Zargparse - A Zsh completion file generator')
    _parser.add_argument('file_path', help='File to generate completion for')
    arguments = _parser.parse_args()

    main(arguments.file_path)

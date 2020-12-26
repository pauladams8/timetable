# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from __future__ import annotations

from ..input import ask
from datetime import date as Date
from firefly import Client, factories
from functools import cached_property
from typing import List, Callable, Any
from argparse import ArgumentParser as ArgumentsParser, Namespace as Arguments

# Interface for a command
class Command():
    # Date parsing help snippet
    INTELLEGENT_DATE_HINT: str = '%(prog)s will attempt to parse any human readable date string, so dates like `tomorrow` and `next monday` are acceptable.'

    # The command name
    name: str = None

    # The command description
    description: str = None

    # The subcommands
    subcommands: List[Command] = None

    # Create an instance
    def __init__(self, parser: ArgumentsParser, parent: Command = None, subcommands: List[Command] = None):
        self.parser: ArgumentsParser = parser
        self.parent: Command = parent
        self._args: Arguments = None

        if subcommands is None:
            subcommands = []

        if self.subcommands:
            subcommands.extend(self.subcommands)

        if subcommands:
            subparsers = self.parser.add_subparsers(help='For help with a specific command, run %(prog)s [COMMAND] --help')

            for command in subcommands:
                subparser: ArgumentsParser = subparsers.add_parser(
                    name=command.name,
                    description=command.description
                )
                command(parser=subparser, parent=self)

        # Register the command
        self.parser.set_defaults(func=self)
        self.register_arguments()

    # Register the command arguments
    def register_arguments(self):
        self.parser.add_argument('-n', '--no-interaction', action='store_true', default=False, help='Prevents %(prog)s from reading stdin, for example. Defaults to false. A config file must be present with this option.')

    # Parse the command arguments
    def parse_arguments(self) -> Arguments:
        self._args: Arguments = self.parser.parse_args()
        return self._args

    # Execute the command
    def __call__(self, args: Arguments):
        self.parser.print_help()

    # Get the command arguments
    @property
    def args(self) -> Arguments:
        return self._args or (self.parent.args if self.parent else None)

    # Get an argument or ask the user for it
    def arg_or_ask(self, arg: str):
        return getattr(self.args, arg, None) or ask(arg.capitalize())

    # Print the client loading state while excuting the callback
    def print_client_state(self, callback: Callable[[Client], [Any]]):
        self.firefly_client.spinner.start()

        try:
            result = callback(self.firefly_client)
        except:
            self.firefly_client.spinner.stop()
            # Continue propagation
            raise

        self.firefly_client.spinner.stop()
        self.firefly_client.spinner.ok('✔️')

        return result

    # Get the Firefly client
    @cached_property
    def firefly_client(self) -> Client:
        return factories.firefly_client(can_ask=not self.args.no_interaction)
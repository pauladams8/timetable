# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from __future__ import annotations

import factories
from firefly import Client
from datetime import date as Date
from typing import List, Callable
from functools import cached_property
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
    def __init__(self, parser: ArgumentsParser, subcommands: List[Command] = None):
        self.parser: ArgumentsParser = parser

        if subcommands is None:
            subcommands = []

        if self.subcommands:
            subcommands.extend(self.subcommands)

        if subcommands:
            subparsers = self.parser.add_subparsers(help='For help with a specific command, run %(prog)s [COMMAND] --help')

            for command in subcommands:
                subparser: ArgumentsParser = subparsers.add_parser(
                    name=command.name,
                    description=command.description,
                    prog=parser.prog
                )
                command(subparser)

        # Register the command
        self.parser.set_defaults(func=self)
        self.register_arguments()

    # Register the command arguments
    def register_arguments(self):
        pass

    # Execute the command
    def __call__(self, args: Arguments):
        pass

    # Print the client loading state while excuting the callback
    def print_client_state(self, callback: Callable):
        self.firefly_client.spinner.start()
        result = callback()
        self.firefly_client.spinner.stop()
        return result

    # Get the Firefly client
    @cached_property
    def firefly_client(self) -> Client:
        return factories.firefly_client()
# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import factories
from firefly import Client
from argparse import ArgumentParser, Namespace as Arguments

# Interface for a command.
class Command():
    # Date parsing help snippet
    INTELLEGENT_DATE_HINT: str = '%(prog)s will attempt to parse any human readable date string, so dates like `tomorrow` and `next monday` are acceptable.'

    # The command description
    description: str = None

    # Create a Command instance
    def __init__(self):
        self.firefly_client: Client = factories.firefly_client()

    # Register the command arguments
    @classmethod
    def register_arguments(self, parser: ArgumentParser):
        pass

    # Execute the command
    def execute(self, args: Arguments):
        pass
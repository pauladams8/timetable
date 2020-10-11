# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from commands import Command
from argparse import ArgumentParser, Namespace as Arguments

# Mark a task as done
class CompleteTask(Command):
    # The task description
    description: str = 'Mark a task as done'

    # Register the command arguments
    @classmethod
    def register_arguments(self, parser: ArgumentParser):
        parser.add_argument('id', action='store_const', help='The ID of the task to mark as done. You can retrieve a list of your tasks using %(prog)s tasks.')

    # Execute the command
    def execute(self, args: Arguments):
        pass # Awaiting mark_as_done impl on the Firefly client
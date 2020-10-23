# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from commands import Command
from argparse import Namespace as Arguments

# Mark a task as done
class CompleteTask(Command):
    # The command name
    name: str = 'done'

    # The command description
    description: str = 'Mark a task as done'

    # Register the command arguments
    def register_arguments(self):
        self.parser.add_argument('id', type=int, help='The ID of the task to mark as done. You can retrieve a list of your tasks by running %(prog)s tasks.')

    # Execute the command
    def __call__(self, args: Arguments):
        self.firefly_client.mark_task_as_done(task_id=args.id)
# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .. import Command
from argparse import Namespace as Arguments

# Mark a task as todo
class UndoTask(Command):
    # The command name
    name: str = 'todo'

    # The command description
    description: str = 'Mark a task as todo'

    # Register the command arguments
    def register_arguments(self):
        self.parser.add_argument('id', type=int, help='The ID of the task to mark as todo. You can retrieve a list of your tasks by running %(prog)s tasks.')

    # Execute the command
    def __call__(self, args: Arguments):
        self.firefly_client.mark_task_as_to_do(task_id=args.id)
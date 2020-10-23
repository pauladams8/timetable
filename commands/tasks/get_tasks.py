# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import re
from .. import Command
from typing import List
from .undo_task import UndoTask
from aenum import AutoNumberEnum
from colorama import Style, Back
from .complete_task import CompleteTask
from argparse import Namespace as Arguments
from parsers import DatePeriodParser, DateRange, TaskSortParser, Sort
from firefly import Task, TaskCompletionStatus, TaskReadStatus, TaskMarkingStatus, TaskSortColumn

# Get the user's set tasks.
class GetTasks(Command):
    # The command name
    name: str = 'tasks'

    # The command description
    description: str = 'Retrieve your set tasks'

    # The subcommands
    subcommands: List[Command] = [
        CompleteTask,
        UndoTask
    ]

    # Register the command arguments
    def register_arguments(self):
        completion_status_group = self.parser.add_mutually_exclusive_group()
        completion_status_group.add_argument('--todo', dest='completion_status', action='store_const', const=TaskCompletionStatus.TO_DO, help='Tasks that are yet to be completed')
        completion_status_group.add_argument('--done', dest='completion_status', action='store_const', const=TaskCompletionStatus.DONE, help='Tasks that are done')
        read_status_group = self.parser.add_mutually_exclusive_group()
        read_status_group.add_argument('--read', dest='read_status', action='store_const', const=TaskReadStatus.READ, help='Tasks that have been read')
        read_status_group.add_argument('--unread', dest='read_status', action='store_const', const=TaskReadStatus.UNREAD, help='Tasks that have not been read')
        marking_status_group = self.parser.add_mutually_exclusive_group()
        marking_status_group.add_argument('--marked', dest='marking_status', action='store_const', const=TaskMarkingStatus.MARKED, help='Tasks that have been marked')
        marking_status_group.add_argument('--unmarked', dest='marking_status', action='store_const', const=TaskMarkingStatus.UNMARKED, help='Tasks that have not been marked')
        self.parser.add_argument('--set', action=DatePeriodParser, nargs='*', metavar=('FROM', '[UNTIL]'), help='Tasks that were set no earlier than FROM, but no later than UNTIL. UNTIL defaults to FROM, so for tasks set yesterday, for example, use --set yesterday. ' + self.INTELLEGENT_DATE_HINT)
        self.parser.add_argument('--due', action=DatePeriodParser, nargs='*', metavar=('FROM', '[UNTIL]'), help='Tasks that are due no earlier than FROM, but no later than UNTIL. UNTIL defaults to FROM, so for tasks due tomorrow, for example, use --due tomorrow. ' + self.INTELLEGENT_DATE_HINT)
        self.parser.add_argument('--set-by', nargs='*', metavar='SETTER', help='Space separated list of task setter GUIDs. You can get a list of your teachers and their GUIDs using `%(prog)s teachers`.')
        self.parser.add_argument('--set-to', nargs='*', metavar='ADDRESEE', help='Space separated list of task addressee GUIDs. You can get a list of your classes and their GUIDs using `%(prog)s classes`.')
        self.parser.add_argument('--sort', action=TaskSortParser, nargs=2, metavar=('COLUMN', '[DIRECTION]'), default=Sort(TaskSortColumn.DUE_DATE), help='Order by which to sort the tasks. Supply a snake_case column (either set_date or due_date; defaults to due_date) and optionally a direction (either asc or desc; defaults to desc).')
        self.parser.add_argument('--offset', type=int, default=0, help='Offset from which to retrieve tasks (defaults to 0). Must be an integer.')
        self.parser.add_argument('--limit', type=int, default=10, help='Limit to retrieve tasks to (defaults to 10). Must be an integer.')

    # Execute the command
    def __call__(self, args: Arguments):
        tasks, total_count = self.print_client_state(
            lambda: self.firefly_client.get_tasks(
                completion_status=args.completion_status or TaskCompletionStatus.ALL,
                read_status=args.read_status or TaskReadStatus.ALL,
                marking_status=args.marking_status or TaskMarkingStatus.ALL,
                sort=args.sort,
                due_date=args.due,
                setters=args.set_by,
                addressees=args.set_to,
                offset=args.offset,
                limit=args.limit
            )
        )

        for task in tasks:
            if task.is_done:
                completion_status = _TaskCompletionStatusDisplay.DONE
            else:
                if task.is_overdue():
                    completion_status = _TaskCompletionStatusDisplay.OVERDUE
                elif task.is_due_soon():
                    completion_status = _TaskCompletionStatusDisplay.DUE_SOON
                else:
                    completion_status = _TaskCompletionStatusDisplay.TO_DO

            # Looks like Firefly's hosted on an IIS server lol
            title: str = re.sub(r'[\r]\n', ' ', task.title)
            title = title[:75] + '...' if len(title) > 75 else title

            print(Style.BRIGHT + title + Style.RESET_ALL, completion_status, Style.DIM + str(task.id) + Style.RESET_ALL)

        print(Style.DIM + 'Showing %r of %r tasks.' % (len(tasks), total_count) + Style.RESET_ALL)

# Holds display props on a task completion status
class _TaskCompletionStatusDisplay(AutoNumberEnum):
    DONE = '✔️ DONE', Back.GREEN
    TO_DO = '⏱ TODO', Back.YELLOW
    DUE_SOON = '⏰ DUE SOON', Back.RED
    OVERDUE = '🚨 OVERDUE', Back.RED

    # Create an instance
    def __init__(self, label: str, color: str):
        self.label: str = label
        self.color: str = color

    # Render the status display as a padded string
    def __str__(self):
        return self.color + ' ' + self.label + ' ' + Style.RESET_ALL
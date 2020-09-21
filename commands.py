# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import sys
import factories
import dateparser
from argparse import ArgumentParser, Namespace as Arguments
from datetime import time as Time, date as Date
from configparser import ConfigParser
from typing import List, Callable, Any
from colorama import Style
from firefly import FireflyClient, SortOrder, TaskSortColumn, TaskCompletionStatus, TaskReadStatus, TaskMarkingStatus

INTELLEGENT_DATE_HINT = '%(prog)s will attempt to parse any human readable date string, so dates like `tomorrow` and `next monday` are acceptable.'

# Interface for a command.
class Command():
    # The command description
    description: str = None

    # Create a Command instance
    def __init__(self):
        self.firefly_client: FireflyClient = factories.firefly_client()

    # Register the command arguments
    def register_arguments(self, parser: ArgumentParser):
        pass

    # Execute the command
    def execute(self, args: Arguments):
        pass

    # Call a method on the FireflyClient while printing its state to the console.
    def _print_client_state(self, callback: Callable[[FireflyClient], Any]):
        self.firefly_client.spinner.start()
        result = callback(self.firefly_client)
        self.firefly_client.spinner.stop()

        return result

# GetTimetable retrieves the user's timetable for a given day.
class GetTimetable(Command):
    description = 'Retrieve your timetable'

    # Register the command arguments
    def register_arguments(self, parser: ArgumentParser):
        parser.add_argument('-d', '--date', help='The timetable date; defaults to today. ' + INTELLEGENT_DATE_HINT, default=Date.today())

    # Execute the command
    def execute(self, args: Arguments):
        if not isinstance(args.date, Date):
            args.date = dateparser.parse(args.date).date()

        lessons = self._print_client_state(lambda client: client.get_lessons(args.date))

        self._print_timetable(lessons)

    # Pretty print the timetable to the console
    def _print_timetable(self, timetable: List):
        if len(timetable) < 1:
            print('🎉 No lessons in timetable')

        for lesson in timetable:
            time_format: Callable[[Time], str] = lambda time: time.strftime('%H:%M')
            time_period = time_format(lesson.start_time) + ' - ' + time_format(lesson.end_time)

            print(Style.DIM + time_period + Style.RESET_ALL, Style.BRIGHT + lesson.subject + Style.RESET_ALL)

            padding = ' ' * (len(time_period) + 1)

            teacher = lesson.teacher
            teacher_name = None
            room = lesson.room

            if teacher:
                teacher_name = teacher.name

            for value in [teacher_name, room]:
                if value:
                    print(padding + value)

# GetTasks retrieves the user's set tasks.
class GetTasks(Command):
    description = 'Retrieve your set tasks'

    # Register the command arguments
    def register_arguments(self, parser: ArgumentParser):
        completion_status_group = parser.add_mutually_exclusive_group()
        completion_status_group.add_argument('--todo', dest='completion_status', action='store_const', const=TaskCompletionStatus.TO_DO, help='Tasks that are yet to be completed')
        completion_status_group.add_argument('--done', dest='completion_status', action='store_const', const=TaskCompletionStatus.DONE, help='Tasks that are done')
        read_status_group = parser.add_mutually_exclusive_group()
        read_status_group.add_argument('--read', dest='read_status', action='store_const', const=TaskReadStatus.READ, help='Tasks that have been read')
        read_status_group.add_argument('--unread', dest='read_status', action='store_const', const=TaskReadStatus.UNREAD, help='Tasks that have not been read')
        marking_status_group = parser.add_mutually_exclusive_group()
        marking_status_group.add_argument('--marked', dest='marking_status', action='store_const', const=TaskMarkingStatus.MARKED, help='Tasks that have been marked')
        marking_status_group.add_argument('--unmarked', dest='marking_status', action='store_const', const=TaskMarkingStatus.UNMARKED, help='Tasks that have not been marked')
        parser.add_argument('--set', nargs=2, metavar='[FROM/UNTIL]', help='Tasks that were set no earlier than FROM, but no later than UNTIL. You may specify one, both or neither. UNTIL defaults to FROM, so for tasks set yesterday, for example, use --set yesterday. ' + INTELLEGENT_DATE_HINT)
        parser.add_argument('--due', nargs=2, metavar='[FROM/UNTIL]', help='Tasks that are due no earlier than FROM, but no later than UNTIL. You may specify one, both or neither. UNTIL defaults to FROM, so for tasks due tomorrow, for example, use --due tomorrow. ' + INTELLEGENT_DATE_HINT)
        parser.add_argument('--set-by', nargs='*', metavar='SETTER', help='Space separated list of task setter GUIDs. You can get a list of your teachers and their GUIDs using `%(prog)s teachers`.')
        parser.add_argument('--set-to', nargs='*', metavar='ADDRESEE', help='Space separated list of task addressee GUIDs. You can get a list of your classes and their GUIDs using `%(prog)s classes`.')
        parser.add_argument('--sort', nargs=2, default=[TaskSortColumn.DUE_DATE, SortOrder.DESCENDING], metavar='[COLUMMN/DIRECTION]', help='Order by which to sort the tasks. Supply a snake_case column (either set_date or due_date; defaults to due_date) and a direction (either asc or desc; defaults to desc).')
        parser.add_argument('--offset', type=int, help='Offset from which to retrieve tasks (minimum index). Must be an integer.')
        parser.add_argument('--limit', type=int, help='Limit to retrieve tasks to (maximum index). Must be an integer.')

    def execute(self, args: Arguments):
        completion_status: TaskCompletionStatus = getattr(args, 'completion_status', None) or TaskCompletionStatus.ALL
        read_status: TaskReadStatus = getattr(args, 'read_status', None) or TaskReadStatus.ALL
        marking_status: TaskMarkingStatus = getattr(args, 'marking_status', None) or TaskMarkingStatus.ALL
        set_date_str: str = getattr(args, 'set', None)
        set_from: Date = None
        set_until: Date = None
        due_date_str: str = getattr(args, 'due', None)
        due_from: Date = None
        due_until: Date = None

        if set_date_str is not None:
            dates = set_date_str.split(' ')

            set_from = dates[0]

            if len(dates) < 2:
                set_until = set_from
            else:
                set_until = dates[1]

# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import sys
import math
import factories
import dateparser
from enum import Enum
from colorama import Style, Back
from configparser import ConfigParser
from typing import List, Dict, Callable, Any
from sort_parsers import TaskSortParser, Sort
from datetime import time as Time, date as Date, timedelta as TimeDelta
from argparse import ArgumentParser, Namespace as Arguments
from date_parsers import DateParser, DatePeriodParser, DateRange
from firefly import FireflyClient, Task, TaskCompletionStatus, TaskReadStatus, TaskMarkingStatus, SortDirection, TaskSortColumn

INTELLEGENT_DATE_HINT = '%(prog)s will attempt to parse any human readable date string, so dates like `tomorrow` and `next monday` are acceptable.'

# Interface for a command.
class Command():
    # The command description
    description: str = None

    # Create a Command instance
    def __init__(self):
        self.firefly_client: FireflyClient = factories.firefly_client()

    # Register the command arguments
    @classmethod
    def register_arguments(self, parser: ArgumentParser):
        pass

    # Execute the command
    def execute(self, args: Arguments):
        pass

# GetTimetable retrieves the user's timetable for a given day.
class GetTimetable(Command):
    description = 'Retrieve your timetable'

    # Register the command arguments
    @classmethod
    def register_arguments(self, parser: ArgumentParser):
        parser.add_argument('-d', '--date', action=DateParser, default=Date.today(), help='The timetable date; defaults to today. ' + INTELLEGENT_DATE_HINT)

    # Execute the command
    def execute(self, args: Arguments):
        # User wants to generate calendar file
        if args.command == 'ics':
            date_range: DateRange = args.date

            diff: TimeDelta = date_range.from_date - date_range.until_date

            if diff.weeks() != 2:
                raise ValueError('KGS timetables rotate every 2 weeks')

        self.firefly_client.spinner.start()
        lessons = self.firefly_client.get_lessons(args.date)
        self.firefly_client.spinner.stop()

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

# Tasks retrieves the user's set tasks.
class Tasks(Command):
    description = 'Retrieve your set tasks'

    # Register the command arguments
    @classmethod
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
        parser.add_argument('--set', action=DatePeriodParser, nargs='*', metavar=('FROM', '[UNTIL]'), help='Tasks that were set no earlier than FROM, but no later than UNTIL. UNTIL defaults to FROM, so for tasks set yesterday, for example, use --set yesterday. ' + INTELLEGENT_DATE_HINT)
        parser.add_argument('--due', action=DatePeriodParser, nargs='*', metavar=('FROM', '[UNTIL]'), help='Tasks that are due no earlier than FROM, but no later than UNTIL. UNTIL defaults to FROM, so for tasks due tomorrow, for example, use --due tomorrow. ' + INTELLEGENT_DATE_HINT)
        parser.add_argument('--set-by', nargs='*', metavar='SETTER', help='Space separated list of task setter GUIDs. You can get a list of your teachers and their GUIDs using `%(prog)s teachers`.')
        parser.add_argument('--set-to', nargs='*', metavar='ADDRESEE', help='Space separated list of task addressee GUIDs. You can get a list of your classes and their GUIDs using `%(prog)s classes`.')
        parser.add_argument('--sort', action=TaskSortParser, nargs=2, metavar=('COLUMN', '[DIRECTION]'), default=Sort(TaskSortColumn.DUE_DATE), help='Order by which to sort the tasks. Supply a snake_case column (either set_date or due_date; defaults to due_date) and optionally a direction (either asc or desc; defaults to desc).')
        parser.add_argument('--offset', type=int, default=0, help='Offset from which to retrieve tasks (defaults to 0). Must be an integer.')
        parser.add_argument('--limit', type=int, default=10, help='Limit to retrieve tasks to (defaults to 10). Must be an integer.')

    # Execute the command
    def execute(self, args: Arguments):
        completion_status: TaskCompletionStatus = args.completion_status or TaskCompletionStatus.ALL
        read_status: TaskReadStatus = args.read_status or TaskReadStatus.ALL
        marking_status: TaskMarkingStatus = args.marking_status or TaskMarkingStatus.ALL
        sort: Sort = args.sort
        offset: int = args.offset
        limit: int = args.limit
        due_date_range: DateRange = args.due or DateRange(None, None)
        setters: List = args.set_by
        addresses: List = args.set_to

        tasks: List[Task]
        total_count: int

        # self.firefly_client.spinner.start()

        tasks, total_count = self.firefly_client.get_tasks(
            completion_status=completion_status,
            read_status=read_status,
            marking_status=marking_status,
            sort_col=sort.column,
            sort_direction=sort.direction,
            min_due_date=due_date_range.from_date,
            max_due_date=due_date_range.until_date,
            setters=setters,
            addressees=addresses,
            offset=offset,
            limit=limit
        )

        # self.firefly_client.spinner.stop()

        self._print_tasks(tasks, total_count)

    # Pretty print the list of tasks to the console
    def _print_tasks(self, tasks: List[Task], total_count: int):
        completion_status: _TaskCompletionStatusDisplay

        for task in tasks:
            if task.is_done:
                completion_status = _TaskCompletionStatusDisplayEnum.DONE.value
            else:
                if task.is_overdue():
                    completion_status = _TaskCompletionStatusDisplayEnum.OVERDUE.value
                elif task.is_due_soon():
                    completion_status = _TaskCompletionStatusDisplayEnum.DUE_SOON.value
                else:
                    completion_status = _TaskCompletionStatusDisplayEnum.TO_DO.value

            print(Style.BRIGHT + task.title + Style.RESET_ALL, completion_status, Style.DIM + str(task.id) + Style.RESET_ALL)
        
        print(Style.DIM + 'Showing %r of %r tasks.' % (len(tasks), total_count))

# _TaskDisplayStatus holds display props on a task completion status.
class _TaskCompletionStatusDisplay():
    # Create a _TaskCompletionStatusDisplay.
    def __init__(self, label: str, color: str):
        self.label: str = label
        self.color: str = color

    # __len__ computes the length of the status' label.
    def __len__(self):
        return len(self.label)

    # __str__ renders the status display as a padded string.
    def __str__(self):
        return self.color + ' ' + self.label + ' ' + Style.RESET_ALL

# _TaskDisplayStatusEnum holds possible _TaskDisplayStatuses
class _TaskCompletionStatusDisplayEnum(Enum):
    DONE = _TaskCompletionStatusDisplay('✔️ DONE', Back.GREEN)
    TO_DO = _TaskCompletionStatusDisplay('⏱ TODO', Back.YELLOW)
    DUE_SOON = _TaskCompletionStatusDisplay('⏰ DUE SOON', Back.RED)
    OVERDUE = _TaskCompletionStatusDisplay('🚨 OVERDUE', Back.RED)

class CompleteTask(Command):
    def register_arguments(self, parser: ArgumentParser):
        parser.add_argument('id')
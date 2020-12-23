# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .. import Command
from colorama import Style
from typing import Callable, List
from firefly.parsers import DateParser
from argparse import Namespace as Arguments
from .export_timetable import ExportToCalendar
from datetime import date as Date, time as Time
from firefly import TimetablePeriod, Lesson, Teacher

# Retrieves the user's timetable
class GetTimetable(Command):
    # The command name
    name: str = 'timetable'

    # The command description
    description: str = 'Retrieve your timetable'

    # The subcommands
    subcommands: List[Command] = [
        ExportToCalendar
    ]

    # Register the command arguments
    def register_arguments(self):
        self.parser.add_argument('-d', '--date', action=DateParser, default=Date.today(), help='The timetable date; defaults to today. ' + self.INTELLEGENT_DATE_HINT)

    # Execute the command
    def __call__(self, args: Arguments):
        timetable: List[Lesson] = self.print_client_state(
            lambda client: client.get_lessons(args.date, TimetablePeriod.DAY)
        )

        if len(timetable) < 1:
            print('🎉 No lessons in timetable')

        for lesson in timetable:
            time_format: Callable[[Time], [str]] = lambda time: time.strftime('%H:%M')
            time_period: str = time_format(lesson.start) + ' - ' + time_format(lesson.end)

            print(Style.DIM + time_period + Style.RESET_ALL, Style.BRIGHT + lesson.subject + Style.RESET_ALL)

            padding: str = ' ' * (len(time_period) + 1)

            teacher: Teacher = lesson.teacher
            teacher_name: str = None
            room: str = lesson.room

            if teacher:
                teacher_name = teacher.name

            for value in [teacher_name, room]:
                if value:
                    print(padding + value)
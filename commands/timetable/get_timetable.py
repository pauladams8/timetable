# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from colorama import Style
from commands import Command
from parsers import DateParser
from typing import Callable, List
from datetime import date as Date, time as Time
from firefly import TimetablePeriod, Lesson, Teacher
from argparse import ArgumentParser, Namespace as Arguments

# Retrieves the user's timetable
class GetTimetable(Command):
    # The command description
    description: str = 'Retrieve your timetable'

    # Register the command arguments
    @classmethod
    def register_arguments(self, parser: ArgumentParser):
        parser.add_argument('-d', '--date', action=DateParser, default=Date.today(), help='The timetable date; defaults to today. ' + self.INTELLEGENT_DATE_HINT)

    # Execute the command
    def execute(self, args: Arguments):
        # self.firefly_client.spinner.start()
        lessons = self.firefly_client.get_lessons(args.date, TimetablePeriod.DAY)
        # self.firefly_client.spinner.stop()

        self._print_timetable(lessons)

    # Pretty print the timetable to the console
    def _print_timetable(self, timetable: List[Lesson]):
        if len(timetable) < 1:
            print('🎉 No lessons in timetable')

        lesson: Lesson

        for lesson in timetable:
            time_format: Callable[[Time], str] = lambda time: time.strftime('%H:%M')
            time_period: str = time_format(lesson.start_time) + ' - ' + time_format(lesson.end_time)

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
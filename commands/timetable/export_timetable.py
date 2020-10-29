# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import sys
# from ics import Event
from .event import Event
from .. import Command
from typing import List
from parsers import DateParser
from argparse import Namespace as Arguments, FileType
from datetime import date as Date, timedelta as TimeDelta
from firefly import Lesson, TimetablePeriod

# Export the user's timetable to an iCalendar file.
class ExportToCalendar(Command):
    # The command name
    name: str = 'export'

    # The command description
    description: str = 'Export your timetable to an iCalendar file'

    # Register the command arguments
    def register_arguments(self):
        self.parser.add_argument('-o', '--output', type=FileType('w'), help='The path to which to write the calendar. Defaults to ./timetable.ics.')
        self.parser.add_argument('--from', action=DateParser, dest='from_date', metavar='FROM', default=Date.today(), help='The date from which to start the calendar; defaults to today. ' + self.INTELLEGENT_DATE_HINT)
        self.parser.add_argument('--until', action=DateParser, dest='until_date', metavar='UNTIL', help='The date at which to end the calendar; defaults to the end of the school year, calculated as the weekday before a holiday of length --timeout. ' + self.INTELLEGENT_DATE_HINT)
        self.parser.add_argument('--timeout', type=int, default=4, help='The activity timeout described in --until. Supply an integer number of minimum holiday weeks after which it is assumed the school year is over. Defaults to 4.')

    # Execute the command
    def __call__(self, args: Arguments):
        timetable: List[Lesson] = self.get_lessons(
            args.from_date,
            args.until_date,
            args.timeout
        )

        events: List[Event] = []

        for lesson in timetable:
            event: Event = Event(
                title=lesson.subject,
                location=lesson.room
            )

            for i, existing_event in enumerate(events):
                if existing_event == event:
                    events[i].events.append(event)
                    break

            else:
                events.append(event)

        sys.exit(len(events))

    # Get the lessons between the from and until dates
    def get_lessons(self, from_date: Date, until_date: Date, timeout: int) -> List[Lesson]:
        # Calculate the first day of the week
        date: Date = from_date - TimeDelta(from_date.weekday())

        lessons: List[Lesson] = []

        while True:
            if until_date and date > until_date:
                break

            last_activity: Date = lessons[-1].end_time.date() if lessons else from_date

            if date - last_activity >= TimeDelta(weeks=timeout):
                break

            lessons += self.print_client_state(lambda: self.firefly_client.get_lessons(
                    date, TimetablePeriod.WEEK
                )
            )

            date += TimeDelta(weeks=1)

        return lessons
# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import sys
from .. import Command
from typing import List
from .event import Event, EventSet
from firefly.parsers import DateParser
from firefly import Lesson, TimetablePeriod
from argparse import Namespace as Arguments, FileType
from datetime import date as Date, timedelta as TimeDelta

# Export the user's timetable to an iCalendar file.
class ExportToCalendar(Command):
    # The command name
    name: str = 'export'

    # The command description
    description: str = 'Export your timetable to an iCalendar file'

    # Register the command arguments
    def register_arguments(self):
        self.parser.add_argument('-o', '--output', type=FileType('w'), help='The path to which to write the calendar. Defaults to timetable-{--from as an ISO timestamp}.ics in the current directory.')
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

        events: EventSet = EventSet(
            Event(
                title=lesson.subject,
                location=lesson.room,
                start=lesson.start,
                end=lesson.end
            ) for lesson in timetable
        )

        del timetable

        # with open(args.output) as output:
        #     output.write('\n'.join(event.to_ical() for event in events))

    # Get the lessons between the from and until dates
    def get_lessons(self, from_date: Date, until_date: Date, timeout: int) -> List[Lesson]:
        lessons: List[Lesson] = []
        last_activity: Date = from_date
        date: Date = from_date - TimeDelta(from_date.weekday())

        while date <= until_date if until_date else True and date - last_activity <= TimeDelta(weeks=timeout):
            lessons += self.print_client_state(
                lambda client: client.get_lessons(
                    date, TimetablePeriod.WEEK
                )
            )

            if lessons:
                last_activity = lessons[-1].end.date()

            date += TimeDelta(weeks=1)

        return lessons
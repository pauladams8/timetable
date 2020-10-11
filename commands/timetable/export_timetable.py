# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from commands import Command
from argparse import ArgumentParser
from parsers import DatePeriodParser

# Export the user's timetable to an iCalendar file.
class ExportToCalendar(Command):
    # The command description
    description: str = 'Export your timetable to an iCalendar file'

    # Register the command arguments
    @classmethod
    def register_arguments(self, parser: ArgumentParser):
        parser.add_argument('--repeat', action=DatePeriodParser)
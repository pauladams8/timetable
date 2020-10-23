# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .. import Command
from parsers import DatePeriodParser
from argparse import Namespace as Arguments

# Export the user's timetable to an iCalendar file.
class ExportToCalendar(Command):
    # The command name
    name: str = 'export'

    # The command description
    description: str = 'Export your timetable to an iCalendar file'

    # Register the command arguments
    def register_arguments(self):
        self.parser.add_argument('--repeat', action=DatePeriodParser)

    # Execute the command
    def __call__(self, args: Arguments):
        pass
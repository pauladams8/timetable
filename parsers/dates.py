# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import dateparser
from typing import List, Type
from datetime import date as Date
from argparse import Action as ArgumentParser, ArgumentParser as ArgumentsParser, Namespace as Arguments

# Parses a date string
class DateParser(ArgumentParser):
    # Invokes the parser function
    def __call__(self, parser: ArgumentsParser, args: Arguments, date_str: str, option_string: str = None):
        setattr(args, self.dest, self._parse_date(date_str))

    # Parse a date string
    def _parse_date(self, date_str: str) -> Date:
        time = dateparser.parse(date_str)

        if not time:
            raise ValueError('Unable to parse date `%s`. Perhaps try rephrasing it?' % date_str)

        return time

# Parses multiple date strings
class DatePeriodParser(DateParser):
    # Invokes the parser function
    def __call__(self, parser: ArgumentsParser, args: Arguments, dates: List[str], option_string: str = None):
        for i, date_str in enumerate(dates):
            dates[i] = self._parse_date(date_str)

        from_date = dates[0]

        try:
            until_date = dates[1]
        except IndexError:
            until_date = None

        setattr(args, self.dest, DateRange(from_date, until_date))

# Encapsulates 2 dates
class DateRange():
    # Create an instance
    def __init__(self, from_date: Date, until_date: Date = None):
        self.from_date: Date = from_date
        self._until_date: Date = until_date

    # Get the until date
    @property
    def until_date(self):
        # Default to single date range
        return self._until_date or self.from_date
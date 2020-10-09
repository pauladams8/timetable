# Copyright Paul Adams <paul@thecoderszone.com>, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import dateparser
from typing import List, Type
from datetime import date as Date
from argparse import Action as ArgumentParser, ArgumentParser as ArgumentsParser, Namespace as Arguments

# DateParser parses a date string
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

# DatePeriodParser parses multiple date strings
class DatePeriodParser(DateParser):
    # Invokes the parser function
    def __call__(self, parser: ArgumentsParser, args: Arguments, dates: List[str], option_string: str = None):
        for i, date_str in enumerate(dates):
            dates[i] = self._parse_date(date_str)

        from_date = dates[0]

        try:
            until_date = dates[1]
        except IndexError:
            # DateRange will determine the default until_date
            until_date = None

        setattr(args, self.dest, DateRange(from_date, until_date))

# DateRange holds two dates
class DateRange():
    # Create a DateRange
    def __init__(self, from_date: Date, until_date: Date):
        # It seems `from` is a reserved Python keyword, so we'll namespace both dates Hungarian style with _date
        self.from_date = from_date
        self.until_date = until_date or from_date
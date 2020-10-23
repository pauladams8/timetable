# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import dateparser
from typing import List
from firefly import DateRange
from datetime import date as Date, datetime as DateTime
from argparse import _StoreAction as StoreAction, ArgumentParser as ArgumentsParser, Namespace as Arguments

# Parse a date string
def parse_date(date_str: str) -> Date:
    time: DateTime = dateparser.parse(date_str)

    if not time:
        raise ValueError('Unable to parse date `%s`. Perhaps try rephrasing it?' % date_str)

    return time.date()

# Parses a date string
class DateParser(StoreAction):
    # Invoke the parser function
    def __call__(self, parser: ArgumentsParser, args: Arguments, date_str: str, option_string: str = None):
        super().__call__(parser, args, parse_date(date_str), option_string)

# Parses multiple date strings
class DatePeriodParser(StoreAction):
    # Invoke the parser function
    def __call__(self, parser: ArgumentsParser, args: Arguments, dates: List[str], option_string: str = None):
        for i, date_str in enumerate(dates):
            dates[i] = parse_date(date_str)

        from_date: Date = dates[0]

        try:
            until_date: Date = dates[1]
        except IndexError:
            until_date = None

        super().__call__(parser, args, DateRange(from_date, until_date), option_string)
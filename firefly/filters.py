# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from datetime import date as Date
from .enums import SortColumn, SortDirection

# Encapsulates the sort column and direction
class Sort():
    # Create an instance
    def __init__(self, column: SortColumn, direction: SortDirection = None):
        self.column: SortColumn = column
        self._direction: SortDirection = direction

    # Get the direction
    @property
    def direction(self):
        # Default to descending as most users won't want to trawl through old homework archives
        return self._direction or SortDirection.DESCENDING

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
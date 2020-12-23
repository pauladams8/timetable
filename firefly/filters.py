# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from datetime import date as Date
from .enums import SortColumn, TaskSortColumn, SortDirection, TaskCompletionStatus

# Defines how to sort results
class Sort():
    # Create an instance
    def __init__(self, column: SortColumn, direction: SortDirection = None):
        self.column: SortColumn = column
        self._direction: SortDirection = direction

    # Get the direction
    def direction(self) -> SortDirection:
        return self._direction or SortDirection.DESCENDING

# Sort for the task endpoint
class TaskSort(Sort):
    # Create an instance
    def __init__(self, column: TaskSortColumn, direction: SortDirection = None):
        super().__init__(column, direction)

    # Get the direction
    def direction(self, completion_status: TaskCompletionStatus = TaskCompletionStatus.ALL) -> SortDirection:
        if self._direction:
            return self._direction

        # Default to ascending if the user wants only uncompleted tasks, so they know what to prioritise
        if self.column == TaskSortColumn.DUE_DATE and completion_status == TaskCompletionStatus.TO_DO:
            return SortDirection.ASCENDING

        return super().direction()

# Period of time between two dates
class DatePeriod():
    # Create an instance
    def __init__(self, from_date: Date, until_date: Date = None):
        self.from_date: Date = from_date
        self._until_date: Date = until_date

    # Get the until date
    @property
    def until_date(self) -> Date:
        # Default to single date range
        return self._until_date or self.from_date
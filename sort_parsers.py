# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from abc import ABC
from typing import List
from output import human_list
from firefly import SortColumn, SortDirection, TaskSortColumn
from argparse import Action as ArgumentParser, ArgumentParser as ArgumentsParser, Namespace as Arguments

# Parses the sort direction and column
class SortParser(ArgumentParser, ABC):
    # String -> Enum sort direction mappings
    DIRECTION_MAPPINGS = {
        'asc': SortDirection.ASCENDING,
        'desc': SortDirection.DESCENDING
    }

    # Invoke the sort parser
    def __call__(self, parser: ArgumentsParser, args: Arguments, values: List[str], option_string: str = None):
        try:
            sort_col: SortColumn = self._parse_sort_column(values[0])
        # This LookupError refers to values[0].
        # It is the responsibility of _parse_sort_column to catch any enum mapping LookupError and raise a more useful error for the user.
        except LookupError:
            raise ValueError('Please specify a sort column')
        # This time, it's our responsibility to catch mapping LookupError, so we'll need 2 try blocks.
        try:
            sort_dir_str: str = values[1]
            try:
                sort_dir = self.DIRECTION_MAPPINGS[sort_dir_str]
            except LookupError:
                raise ValueError('%s is not a valid sort direction. Please choose %s.' % (sort_dir_str, human_list([key for key in self.DIRECTION_MAPPINGS], 'or')))
        except LookupError:
            # The sort directory is optional; Sort.__init__() can determine the default.
            sort_dir: None

        # We'll encapsulate the direction and column in a SortOrder object for better DX.
        setattr(args, self.dest, Sort(sort_col, sort_dir))

    # Parse the sort column (TBI)
    def _parse_sort_column(self, col: str) -> SortColumn:
        pass
    
# TaskSortParser primarily parses the task sort column
class TaskSortParser(SortParser):
    # String -> Enum sort column mappings
    COLUMN_MAPPINGS = {
        'set_date': TaskSortColumn.SET_DATE,
        'due_date': TaskSortColumn.DUE_DATE
    }

    # Parse the sort column (overrides abstract SortParser)
    def _parse_sort_column(self, sort_col: str) -> TaskSortColumn:
        try:
            return self.COLUMN_MAPPINGS[sort_col]
        except LookupError:
            raise ValueError('%s is not a valid task sort column. Please choose %s.' % (sort_col, human_list([key for key in self.COLUMN_MAPPINGS], 'or')))

# Sort is the order to sort results from Firefly APIs
class Sort():
    # Create a new SortOrder
    def __init__(self, column: SortColumn, direction: SortDirection = None):
        self.column = column
        # We'll default the direction to descending as most users won't want to trawl through old homework archives.
        self.direction = direction or SortDirection.DESCENDING
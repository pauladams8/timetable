# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from abc import ABC
from typing import List
from output import human_list
from firefly import SortDirection, SortColumn, TaskSortColumn
from argparse import ArgumentParser as ArgumentsParser, Action as ArgumentParser, Namespace as Arguments

# Parses the sort direction and column
class SortParser(ArgumentParser, ABC):
    # Invoke the sort parser
    def __call__(self, parser: ArgumentsParser, args: Arguments, values: List[str], option_string: str = None):
        try:
            sort_col: SortColumn = self._parse_sort_column(values[0])
        # This LookupError refers to values[0].
        except LookupError:
            raise ValueError('Please specify a sort column')

        sort_dir: SortDirection

        try:
            sort_dir_str: str = values[1]
        except LookupError:
            sort_dir = None

        sort_dir = SortDirection.from_human_name(sort_dir_str)

        if not sort_dir:
            raise ValueError('%s is not a valid sort direction. Please choose %s.' % (sort_dir_str, human_list([value.human_name for value in SortDirection], 'or')))

        setattr(args, self.dest, Sort(sort_col, sort_dir))

    # Parse the sort column (TBI)
    def _parse_sort_column(self, col: str) -> SortColumn:
        pass
    
# TaskSortParser primarily parses the task sort column
class TaskSortParser(SortParser):
    # Parse the sort column
    def _parse_sort_column(self, sort_col_str: str) -> TaskSortColumn:
        sort_col: TaskSortColumn =  TaskSortColumn.from_human_name(sort_col_str)

        if not sort_col:
            raise ValueError('%s is not a valid task sort column. Please choose %s.' % (sort_col_str, human_list([value.human_name for value in TaskSortColumn], 'or')))

        return sort_col

# Encapsulates the sort column and direction for better DX
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
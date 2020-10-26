# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from abc import ABC
from .enum import parse_enum
from output import human_list
from typing import List, Type
from firefly import SortDirection, SortColumn, TaskSortColumn, Sort
from argparse import ArgumentParser as ArgumentsParser, _StoreAction as StoreAction, Namespace as Arguments

# Parses the sort direction and column
class SortParser(StoreAction, ABC):
    # Invoke the sort parser
    def __call__(self, parser: ArgumentsParser, args: Arguments, values: List[str], option_string: str = None):
        try:
            col: SortColumn = self.parse_column(values[0])
        except IndexError:
            raise ValueError('Please specify a sort column')

        try:
            dir: SortDirection = self.parse_direction(values[1])
        except IndexError:
            dir = None

        super().__call__(parser, args, Sort(col, dir), option_string)

    # Parse the sort direction
    def parse_direction(self, dir: str) -> SortDirection:
        return parse_enum(dir, SortDirection)

    # Parse the sort column
    def parse_column(self, col: str) -> SortColumn:
        pass

# Parses the task sort column
class TaskSortParser(SortParser):
    # Parse the sort column
    def parse_column(self, col: str) -> TaskSortColumn:
        return parse_enum(col, TaskSortColumn)
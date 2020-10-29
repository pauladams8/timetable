# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from __future__ import annotations

from typing import Callable
from aenum import AutoNumberEnum
from .events import TaskEvent, MarkAsDoneEvent, MarkAsUndoneEvent

# Enum for filtering
class Enum(AutoNumberEnum):
    # Create an instance
    def __init__(self, foreign_name: str, human_name: str = None, cls: type = None):
        # Name used by server
        self.foreign_name: str = foreign_name
        # Human readable name for lookups
        self._human_name: str = human_name
        # Native class
        self.cls: type = cls

    # Get the human readable name
    @property
    def human_name(self) -> str:
        # Bear in mind spaces need escaping, so snake case is preferable to the user in a CLI
        return self._human_name or self.name.lower()

    # Create a native instance for the enum value
    def create(self, *args, **kwargs) -> object:
        if not self.cls:
            return None

        return self.cls(*args, **kwargs)

    # Filter the enum by a callback
    @classmethod
    def filter(cls, callback: Callable[Enum], default = None) -> Enum:
        try:
            return next(enum for enum in cls if callback(enum))
        except StopIteration:
            return default

    # Get an enum by its human readable name
    @classmethod
    def from_human_name(cls, human_name: str, default: str = None) -> Enum:
        return cls.filter(lambda enum: enum.human_name == human_name, default)

    # Get an enum by its server name
    @classmethod
    def from_foreign_name(cls, foreign_name: str, default: str = None) -> Enum:
        return cls.filter(lambda enum: enum.foreign_name == foreign_name, default)

# Abstract enum for filtering
class FilterEnum(Enum):
    ALL = 'All'

# Enum for filtering tasks by whether the user has completed them
class TaskCompletionStatus(Enum):
    ALL = 'AllIncludingArchived'
    TO_DO = 'Todo'
    DONE = 'DoneOrArchived'

# Enum for filtering tasks by whether the user has read them
class TaskReadStatus(Enum):
    ALL = 'All'
    READ = 'OnlyRead'
    UNREAD = 'OnlyUnread'

# Enum for filtering tasks by whether the teacher has marked them
class TaskMarkingStatus(Enum):
    ALL = 'All'
    MARKED = 'OnlyMarked'
    UNMARKED = 'OnlyUnmarked'

# Enum for sort directions
class SortDirection(Enum):
    ASCENDING = 'Ascending', 'asc'
    DESCENDING = 'Descending', 'desc'

# Abstract enum for sort columns
class SortColumn(Enum):
    pass

# Enum for columns used to sort tasks
class TaskSortColumn(SortColumn):
    DUE_DATE = 'DueDate'
    SET_DATE = 'SetDate'

# Enum for the timetable period
class TimetablePeriod(Enum):
    DAY = 'day'
    WEEK = 'week'

# Enum for the task owner
class TaskOwner(Enum):
    SETTER = 'OnlySetters'

# Enum for a task response event
class TaskEventEnum(Enum):
    DONE = 'mark-as-done', MarkAsDoneEvent
    UNDONE = 'mark-as-undone', MarkAsUndoneEvent

    # Create an instance
    def __init__(self, foreign_name: str, cls: type):
        super().__init__(foreign_name=foreign_name, cls=cls)

    # Create a native instance for the enum value
    def create(self, *args, **kwargs) -> TaskEvent:
        return super().create(*args, **kwargs)

# Enum for a task recipient
class Recipient(Enum):
    USER = 'user'
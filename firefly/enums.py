# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from aenum import AutoNumberEnum

# Enum for filtering
class Enum(AutoNumberEnum):
    # Create an instance
    def __init__(self, foreign_name: str, human_name: str = None):
        # Name used by server
        self.foreign_name: str = foreign_name
        # Human readable name for lookups
        self._human_name: str = human_name

    # Get the human readable name
    @property
    def human_name(self) -> str:
        return self._human_name

    # Get an enum by its human readable name
    @classmethod
    def from_human_name(cls, human_name: str):
        try:
            return next(enum for enum in cls if enum.human_name == human_name)
        except StopIteration:
            return None

# Abstract enum for filtering
class FilterEnum(Enum):
    ALL = 'All'

# Enum for filtering tasks by whether the user has completed them
class TaskCompletionStatus(Enum):
    TO_DO = 'Todo'
    DONE = 'DoneOrArchived'
    ALL = 'AllIncludingArchived'

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
class TaskSortColumn(Enum):
    SET_DATE = 'SetDate'
    DUE_DATE = 'DueDate'

    # Get the human readable name
    @property
    def human_name(self):
        return self.name.lower()

# Enum for the timetable period
class TimetablePeriod(Enum):
    DAY = 'day'
    WEEK = 'week'

# Enum for the task owner
class TaskOwner(Enum):
    SETTER = 'OnlySetters'

# Enum for a task response event
class TaskEvent(Enum):
    DONE = 'mark-as-done'
    UNDONE = 'mark-as-undone'

# Enum for a task recipient
class Recipient(Enum):
    USER = 'user'
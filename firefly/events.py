# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from abc import ABC
from .resources import User
from datetime import datetime as DateTime

# Event occuring on a task
class TaskEvent(ABC):
    def __init__(
        self,
        guid: str,
        user: User,
        sent_at: DateTime,
        version_id: int
    ):
        self.guid = guid
        self.user = user
        self.sent_at = sent_at
        self.version_id = version_id

# Task marked as done event
class MarkAsDoneEvent(TaskEvent):
    pass

# Task marked as undone event
class MarkAsUndoneEvent(TaskEvent):
    pass
# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from abc import ABC
from typing import List
from .times import BREAK, LUNCH
from datetime import datetime as DateTime, date as Date, timedelta as TimeDelta

# User account
class User():
    # Create an instance
    def __init__(
            self,
            guid: str,
            name: str = None,
            is_deleted: bool = False,
            sort_key: str = None
        ):
        self.guid: str = guid
        self.name: str = name
        self.is_deleted: bool = is_deleted
        self.sort_key: str = sort_key

# Owner of a lesson
class Teacher():
    # Create an instance
    def __init__(
            self,
            name: str,
            picture: str = None,
            roles: List[str] = None,
            departments: List[str] = None,
            phone_number: str = None,
            email_address: str = None
        ):
        self.name: str = name
        self.picture: str = picture
        self.roles: List[str] = roles or []
        self.departments: List[str] = departments or []
        self.phone_number: str = phone_number
        self.email_address: str = email_address

# Subject taught by a teacher in a room
class Lesson():
    # Create an instance
    def __init__(
            self,
            start: DateTime,
            end: DateTime,
            subject: str = None,
            teacher: Teacher = None,
            room: str = None
        ):
        self.start: DateTime = start
        self.end: DateTime = end
        self._subject: str = subject
        self.teacher: Teacher = teacher
        self.room: str = room

    # Get the subject
    @property
    def subject(self):
        if self.start.time() == BREAK.start and self.end.time() == BREAK.end:
            return 'Break'

        if self.start.time() == LUNCH.start and self.end.time() == LUNCH.end:
            return 'Lunch'

        return self._subject or 'Free Period'

# Recipient of a task
class Addressee(ABC):
    # Create an instance
    def __init__(self, guid: str, name: str = None):
        self.guid: str = guid
        self.name: str = name

# Group of students
class Class(Addressee):
    pass

# User studying at the school
class Student(User, Addressee):
    pass

# Unit of work to be completed
class Task():
    # Create an instance
    def __init__(
            self,
            id: str,
            title: str,
            addressees: List[Addressee],
            setter: User,
            set: Date,
            due: Date,
            is_done: bool,
            is_read: bool = False,
            is_archived: bool = False,
            description_contains_questions: bool = False,
            file_submission_required: bool = False,
            has_file_submission: bool = False,
            is_excused: bool = False,
            is_personal_task: bool = False,
            is_resubmission_required: bool = False,
            last_marked_as_done_by: User = None
        ):
        self.id: str = id
        self.title: str = title
        self.addressees: List[Addressee] = addressees
        self.setter: User = setter
        self.set: Date = set_date
        self.due: Date = due_date
        self.is_done: bool = is_done
        self.is_read: bool = is_read
        self.is_archived: bool = is_archived
        self.description_contains_questions: bool = description_contains_questions
        self.file_submission_required: bool = file_submission_required
        self.has_file_submission: bool = has_file_submission
        self.is_excused: bool = is_excused
        self.is_personal_task: bool = is_personal_task
        self.is_resubmission_required: bool = is_resubmission_required
        self.last_marked_as_done_by: User = last_marked_as_done_by

    # Determine if the task is overdue
    def is_overdue(self) -> bool:
        return self.due < Date.today()

    # Determine if the task is due soon
    def is_due_soon(self) -> bool:
        return self.due - Date.today() < TimeDelta(days=3)
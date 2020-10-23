# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from abc import ABC
from typing import List
from datetime import time as Time, date as Date, timedelta as TimeDelta

# User account
class User():
    def __init__(
            self,
            guid: str,
            name: str = None,
            is_deleted: bool = False,
            sort_key: str = None
        ):
        self.guid = guid
        self.name = name
        self.is_deleted = is_deleted
        self.sort_key = sort_key

# Owner of a lesson
class Teacher():
    def __init__(
            self,
            name: str,
            picture: str = None,
            roles: List[str] = [],
            departments: List[str] = [],
            phone_number: str = None,
            email_address: str = None
        ):
        self.name = name
        self.picture = picture
        self.roles = roles
        self.departments = departments
        self.phone_number = phone_number
        self.email_address = email_address

# Subject taught by a teacher in a room
class Lesson():
    def __init__(self,
            start_time: Time,
            end_time: Time,
            subject: str,
            teacher: Teacher = None,
            room: str = None
        ):
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.teacher = teacher
        self.room = room

# Recipient of a task
class Addressee(ABC):
    def __init__(self, guid: str, name: str = None):
        self.guid = guid
        self.name = name

# Group of students
class Class(Addressee):
    pass

# User studying at the school
class Student(User, Addressee):
    pass

# Unit of work to be completed
class Task():
    # Create a Task instance
    def __init__(
            self,
            id: str,
            title: str,
            addressees: List[Addressee],
            setter: User,
            set_date: Date,
            due_date: Date,
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
        self.id = id
        self.title = title
        self.addressees = addressees
        self.setter = setter
        self.set_date = set_date
        self.due_date = due_date
        self.is_done = is_done
        self.is_read = is_read
        self.is_archived = is_archived
        self.description_contains_questions = description_contains_questions
        self.file_submission_required = file_submission_required
        self.has_file_submission = has_file_submission
        self.is_excused = is_excused
        self.is_personal_task = is_personal_task
        self.is_resubmission_required = is_resubmission_required
        self.last_marked_as_done_by = last_marked_as_done_by

    # Determine if the task is overdue
    def is_overdue(self):
        return self.due_date < Date.today()

    # Determine if the task is due soon
    def is_due_soon(self):
        return self.due_date - Date.today() < TimeDelta(days=3)
# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorised reproduction is prohibited.

import re
import os
import sys ### REMOVE ME ###
import json
import pickle
import requests
from abc import ABC
from enum import Enum
from pathlib import Path
from http import HTTPStatus
from bs4 import BeautifulSoup
from colorama import Fore, Style
from yaspin import yaspin as Yaspin
from argparse import ArgumentParser
from typing import List, Dict, Callable
from http import cookiejar as CookieJar
from dateutil import parser as timeparser
from datetime import date as Date, time as Time, datetime as DateTime, timedelta

# User is a person's account.
class User():
    def __init__(self, guid: str, name: str, is_deleted: bool = False, sort_key: str = None):
        self.guid = guid
        self.name = name
        self.is_deleted = is_deleted
        self.sort_key = sort_key

# Teacher is the owner of the lesson.
class Teacher():
    def __init__(self, name: str, picture: str = None, roles: List[str] = [], departments: List[str] = [], phone_number: str = None, email_address: str = None):
        self.name = name
        self.picture = picture
        self.roles = roles
        self.departments = departments
        self.phone_number = phone_number
        self.email_address = email_address

# Lesson is a subject taught by a teacher in a room.
class Lesson():
    def __init__(self, start_time: Time, end_time: Time, subject: str, teacher: Teacher = None, room: str = None):
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.teacher = teacher
        self.room = room

# Addressee is the recipient of a task.
class Addressee(ABC):
    def __init__(self, guid: str, name: str = None):
        self.guid = guid
        self.name = name

# Class is a group of students.
class Class(Addressee):
    pass

# Student is a user studying at the school.
class Student(User, Addressee):
    pass

# Task is a piece of work to be completed.
class Task():
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
        return self.due_date - Date.today() < timedelta(days=3)

# TaskFilterEnum is an abstract enum for filtering tasks.
class TaskFilterEnum(Enum):
    ALL = 'All'

# TaskCompletionStatus is an enum for filtering tasks by whether the user has completed them.
class TaskCompletionStatus(Enum):
    TO_DO = 'Todo'
    DONE = 'DoneOrArchived'
    ALL = 'AllIncludingArchived'

# TaskReadStatus is an enum for filtering tasks by whether the user has read them.
class TaskReadStatus(Enum):
    ALL = 'All'
    READ = 'OnlyRead'
    UNREAD = 'OnlyUnread'

# TaskMarkingStatus is an enum for filtering tasks by whether the teacher has marked them.
class TaskMarkingStatus(Enum):
    ALL = 'All'
    MARKED = 'OnlyMarked'
    UNMARKED = 'OnlyUnmarked'

# SortDirection is an enum for sort orders.
class SortDirection(Enum):
    ASCENDING = 'Ascending'
    DESCENDING = 'Descending'

# SortColumn is an abstract enum for sort columns
class SortColumn(Enum):
    pass

# TaskSortColumn is an enum for columns used to sort tasks.
class TaskSortColumn(SortColumn):
    SET_DATE = 'SetDate'
    DUE_DATE = 'DueDate'

# FireflyClient maintains Firefly session state.
class FireflyClient():
    # MIME type constants
    MIME_TYPE_HTML = 'text/html'
    MIME_TYPE_JSON = 'application/json'

    # __init__ creates a new Firefly client. 
    def __init__(self, url: str, username: str, password: str, storage_path: Path):
        self.base_url = url
        self.username = username
        self.password = password
        self.spinner = Yaspin()
        self._client = requests.Session()
        self._client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
            'Accept': self.MIME_TYPE_HTML # Can be overriden on a method basis
        })
        self._attempts = 0
        self._cookie_path = storage_path.joinpath('cookies')

        if self._cookie_path.is_file():
            cookies = pickle.load(self._cookie_path.open('rb'))
            self._client.cookies.update(cookies)

    # _request makes a request to Firefly and checks if we're authenticated.
    # If we're not, it will attempt to login.
    def _request(self, method: str, endpoint: str, **kwargs):
        url = self.base_url + endpoint

        response = self._client.request(method, url, **kwargs)

        # Determine if we need to login
        if response.status_code == HTTPStatus.UNAUTHORIZED or response.url != url and 'login.aspx' in response.url:
            if self._attempts > 1:
                raise Exception('Unable to authenticate with Firefly')

            self.login()

            self._attempts += 1

            # Try again
            return self._request(method, endpoint, **kwargs)

        expected_type = response.request.headers['Accept']

        # Validate the content type against what we requested
        if expected_type not in response.headers['Content-Type']:
            raise Exception('Response content type must be ' + expected_type)

        if expected_type == self.MIME_TYPE_HTML:
            # Create a parser instance on the response for parsing HTML
            response.parser = BeautifulSoup(response.text, 'lxml')

        return response

    # _get makes a GET request
    def _get(self, endpoint: str, **kwargs):
        return self._request('GET', endpoint, **kwargs)

    # _post makes a POST request
    def _post(self, endpoint: str, **kwargs):
        return self._request('POST', endpoint, **kwargs)

    # get_lessons gets the lessons on a given day.
    def get_lessons(self, date: Date) -> List[Lesson]:
        self.spinner.color = 'green'
        self.spinner.text = 'Retrieving timetable'

        response = self._get('/planner/day/' + date.strftime('%Y-%m-%d'))

        regex = re.compile('var PLANNER_INITIAL_STATUS = (.*)')

        javascript = response.parser.find(string=regex)

        if not javascript:
            raise Exception('Failed to locate script tag on planner page')

        planner_json = regex.match(javascript).group(1)

        if not planner_json:
            raise Exception('Failed to extract planner JSON data')

        planner_status = json.loads(planner_json)

        lessons = []

        for lesson in planner_status['events']:
            parse_time: Callable[[str], Time] = lambda iso_date: timeparser.isoparse(iso_date).time()

            start_time = parse_time(lesson.get('isostartdate'))
            end_time = parse_time(lesson.get('isoenddate'))

            p4 = None
            subject = lesson.get('subject')

            if not subject:
                free_period = 'Free Period'

                if start_time == Time(10, 45):
                    subject = 'Break'
                    break_end_time = Time(11, 10)

                    # Firefly does not distinguish between break and free period
                    if end_time != break_end_time:
                        p4_end_time = end_time
                        p4 = Lesson(
                            break_end_time,
                            p4_end_time,
                            free_period
                        )
                        end_time = break_end_time

                elif start_time == Time(12, 55) and end_time == Time(14):
                    subject = 'Lunch'
                else:
                    subject = free_period

            # teacher_name = lesson.get('chairperson')
            # teacher = None

            # if teacher_name:
            #     surname = re.match('.* .* (.*)', teacher_name).group(1)
            #     teacher = self.get_teacher(surname)

            teacher_name = lesson.get('chairperson')
            teacher = None

            if teacher_name:
                teacher = Teacher(teacher_name)

            lessons.append(Lesson(
                start_time,
                end_time,
                subject,
                teacher,
                lesson.get('location')
            ))
            
            if p4:
                lessons.append(p4)

        self.spinner.text = 'Retrieved Timetable'
        self.spinner.ok('✔')

        return lessons

    def get_lessons_by_week(self, start: Date) -> Dict[Date, List[Lesson]]:
        pass

    # get_teachers searches the staff directory by surname.
    def get_teachers(self, surname: str) -> List[Teacher]:
        response = self._get('/school-directory', params={
            'name': surname
        })

        teachers = []

        i = 0

        for row in response.parser.select_one('#StaffResults > table').find_all('tr'):
            # Ignore table header
            if i != 0:
                cells = row.find_all('td')

                teachers.append(Teacher(
                    cells[1].find('h3').text,
                    cells[0].find('img')['src'],
                    [role.strip() for role in cells[2].find_all(text=True)],
                    [department.strip()
                     for department in cells[3].text.split(', ')],
                    cells[4].find(text=True).strip(),
                    cells[4].find('a').text
                ))

            i += 1

        return teachers

    # get_teacher returns the first search result from the staff directory.
    def get_teacher(self, surname: str) -> Teacher:
        return self.get_teachers(surname)[0]

    # get_tasks retrieves the user's set tasks.
    def get_tasks(
            self,
            completion_status: TaskCompletionStatus.TO_DO,
            read_status: TaskReadStatus.ALL,
            marking_status: TaskMarkingStatus = TaskMarkingStatus.ALL,
            min_due_date: Date = None,
            max_due_date: Date = None,
            setters: List[User] = None,
            addressees: List[Addressee] = None,
            sort_col: TaskSortColumn = TaskSortColumn.DUE_DATE,
            sort_direction: SortDirection = SortDirection.ASCENDING,
            offset: int = 0,
            limit: int = 10
        ) -> (List[Task], int):
        self.spinner.text = 'Retrieving tasks'

        params = {
            'ownerType': 'OnlySetters',
            'archiveStatus': TaskFilterEnum.ALL.value,
            'completionStatus': completion_status.value,
            'markingStatus': marking_status.value,
            'readStatus': read_status.value,
            'page': offset,
            'pageSize': limit,
            'sortingCriteria': [
                {
                    'column': sort_col.value,
                    'order': sort_direction.value
                }
            ]
        }

        date_filter: Callable[[Date], str] = lambda date: date.strftime('%Y-%m-%d')

        if min_due_date:
            params['dueDateFrom'] = date_filter(min_due_date)
        if max_due_date:
            params['dueDateTo'] = date_filter(max_due_date)
        if setters:
            params['owners'] = [setter.guid for setter in setters]
        if addressees:
            params['addressees'] = [addressee.guid for addressee in addressees]

        # sys.exit(params)

        response = self._post('/api/v2/taskListing/view/self/tasks/filterBy', json=params, headers={
            'Accept': self.MIME_TYPE_JSON,
            'Referer': 'https://firefly.kgs.org.uk/set-tasks'
        })

        # sys.exit(response.text)

        body = response.json()

        tasks: List = []

        # Helper lambdas for parsing response params
        def date_parser(date_str: str) -> Date:
            if not date_str:
                return date_str

            time = DateTime.strptime(date_str, '%Y-%m-%d')

            if isinstance(time, DateTime):
                return time.date()

            return time

        user_decoder: Callable[[Dict, str], User] = lambda user_dict, user_cls = User: user_cls(
            user_dict.get('guid'),
            user_dict.get('name'),
            user_dict.get('deleted', False),
            user_dict.get('sortKey')
        )

        for task_dict in body['items']:
            addressees: List = []

            for addresee_dict in task_dict['addressees']:
                if addresee_dict.get('isGroup'):
                    addresee_cls = Class
                else:
                    addresee_cls = Student

                addressees.append(addresee_cls(
                    addresee_dict.get('guid'),
                    addresee_dict.get('name')
                ))

            last_marked_as_done_by: Dict = task_dict.get('lastMarkedAsDoneBy')

            if last_marked_as_done_by:
                last_marked_as_done_by: User = user_decoder(last_marked_as_done_by)

            tasks.append(
                Task(
                    id=task_dict.get('id'),
                    title=task_dict.get('title'),
                    addressees=addressees,
                    setter=user_decoder(task_dict['setter'], Student if task_dict['isPersonalTask'] else User),
                    set_date=date_parser(task_dict['setDate']),
                    due_date=date_parser(task_dict['dueDate']),
                    is_done=task_dict.get('isDone'),
                    is_read=task_dict.get('isUnread'),
                    is_archived=task_dict.get('archived'),
                    description_contains_questions=task_dict.get('descriptionContainsQuestions'),
                    file_submission_required=task_dict.get('fileSubmissionRequired'),
                    has_file_submission=task_dict.get('hasFileSubmission'),
                    is_excused=task_dict.get('isExcused'),
                    is_personal_task=task_dict.get('isPersonalTask'),
                    is_resubmission_required=task_dict.get('isResubmissionRequired'),
                    last_marked_as_done_by=last_marked_as_done_by
                )
            )

        self.spinner.text = 'Retrieved tasks'
        self.spinner.ok('✔️')

        return tasks, body.get('totalCount')

    # login requests a session cookie from Firefly and saves it to a file so we don't have to login again until it expires.
    def login(self):
        old_spinner_text = self.spinner.text
        self.spinner.text = 'Logging in'

        response = self._get('/login/login.aspx')

        form = response.parser.select_one('body > div.ff-login-box > div.ff-login-mainsection > form')

        self._post('/login/' + form['action'], data={
            'username': self.username,
            'password': self.password
        }, headers={
            'Referer': response.url
        })

        if not self._cookie_path.is_file():
            self._cookie_path.touch()

        cookie_file = self._cookie_path.open('wb+')

        pickle.dump(self._client.cookies, cookie_file)

        self.spinner.text = old_spinner_text
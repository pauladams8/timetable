# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorised reproduction is prohibited.

import re
import os
import json
import pickle
from pathlib import Path
from colorama import Style
from http import HTTPStatus
from bs4 import BeautifulSoup
from yaspin import yaspin as Yaspin
from argparse import ArgumentParser
from .filters import Sort, DateRange
from requests import Session, Response
from dateutil import parser as dateutil
from http import cookiejar as CookieJar
from typing import List, Dict, Callable, Type
from .events import TaskEvent, MarkAsDoneEvent, MarkAsUndoneEvent
from .resources import User, Teacher, Lesson, Addressee, Class, Student, Task
from .times import BREAK_START_TIME, BREAK_END_TIME, LUNCH_START_TIME, LUNCH_END_TIME
from datetime import date as Date, time as Time, datetime as DateTime, timedelta as TimeDelta
from .enums import (TaskCompletionStatus, TaskReadStatus, TaskMarkingStatus, SortDirection,
                    TaskSortColumn, FilterEnum, TimetablePeriod, TaskOwner, TaskEventEnum, Recipient)

# Type hint the HTML parser
Response.parser: BeautifulSoup

# Maintains Firefly session state
class Client():
    # MIME type constants
    MIME_TYPE_HTML: str = 'text/html'
    MIME_TYPE_JSON: str = 'application/json'

    # Create a new instance
    def __init__(self, url: str, username: str, password: str, storage_path: Path):
        self.base_url: str = url
        self.username: str = username
        self.password: str = password
        self.spinner: Yaspin = Yaspin()
        self._client: Session = Session()
        self._client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
            'Accept': self.MIME_TYPE_HTML # Can be overriden on a method basis
        })
        self._attempts: int = 0
        self._user: User = None
        self._cookie_path = storage_path.joinpath('cookies')

        if self._cookie_path.is_file():
            cookies = pickle.load(self._cookie_path.open('rb'))
            self._client.cookies.update(cookies)

    # Append an endpoint to the base url
    def _url(self, endpoint: str) -> str:
        return self.base_url + endpoint

    # Make a request to Firefly and check if we're authenticated.
    # If we're not, attempt to login.
    def _request(self, method: str, endpoint: str, **kwargs) -> Response:
        url: str = self._url(endpoint)

        response: Response = self._client.request(method, url, **kwargs)

        # Determine if we need to login
        if response.status_code == HTTPStatus.UNAUTHORIZED or response.url != url and 'login.aspx' in response.url:
            if self._attempts > 1:
                raise Exception('Unable to authenticate with Firefly')

            self.login()

            self._attempts += 1

            # Try again
            return self._request(method, endpoint, **kwargs)

        expected_type: str = response.request.headers.get('Accept')

        if expected_type == self.MIME_TYPE_HTML:
            # Create a parser instance on the response for parsing HTML
            response.parser: BeautifulSoup = BeautifulSoup(response.text, 'lxml')

        return response

    # Make a GET request
    def _get(self, endpoint: str, **kwargs) -> Response:
        return self._request('GET', endpoint, **kwargs)

    # Make a POST request
    def _post(self, endpoint: str, **kwargs) -> Response:
        return self._request('POST', endpoint, **kwargs)

    # Get the lessons for a given day
    def get_lessons(self, from_date: Date, period: TimetablePeriod = TimetablePeriod.DAY) -> List[Lesson]:
        day: int = from_date.day
        suffix: str

        # https://stackoverflow.com/questions/739241/date-ordinal-output
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = 'th'
        else:
            suffix = ['st', 'nd', 'rd'][day % 10 - 1]

        indicator: str = ' '.join(['timetable for', ('week beginning ' if period == TimetablePeriod.WEEK else '') + str(day) + suffix, from_date.strftime('%B')])

        self.spinner.color = 'green'
        self.spinner.text = 'Retrieving ' + indicator

        response: Response = self._get('/planner/%s/%s' % (period.foreign_name, from_date.strftime('%Y-%m-%d')))

        regex: re.Pattern = re.compile(r'var PLANNER_INITIAL_STATUS = (.*)')

        javascript: str = response.parser.find(string=regex)

        planner_json: str = regex.search(javascript).group(1)

        planner_status: Dict = json.loads(planner_json)

        lessons: List = []

        for lesson in planner_status['events']:
            # Parse an ISO 8601 compatible time string
            def parse_time(iso_time: str) -> DateTime:
                if not iso_time:
                    return iso_time

                return dateutil.isoparse(iso_time)

            start_time: DateTime = parse_time(lesson.get('isostartdate'))
            end_time: DateTime = parse_time(lesson.get('isoenddate'))
            subject: str = lesson.get('subject')

            p2: Lesson = None
            p4: Lesson = None

            # Firefly does not distinguish between break and free period
            if start_time.time() == BREAK_START_TIME or end_time.time() == BREAK_END_TIME:
                if start_time.time() != BREAK_START_TIME:
                    p2 = Lesson(
                        start_time=start_time,
                        end_time=DateTime.combine(
                            end_time.date(),
                            BREAK_START_TIME
                        )
                    )
                    start_time = DateTime.combine(
                        start_time.date(),
                        BREAK_START_TIME
                    )
                if end_time.time() != BREAK_END_TIME:
                    p4 = Lesson(
                        start_time=DateTime.combine(
                            start_time.date(),
                            BREAK_END_TIME
                        ),
                        end_time=end_time
                    )
                    end_time = DateTime.combine(
                        end_time.date(),
                        BREAK_END_TIME
                    )

            teacher_name: str = lesson.get('chairperson')
            teacher: Teacher = None

            if teacher_name:
                teacher = Teacher(teacher_name)

            if p2:
                lessons.append(p2)

            lessons.append(
                Lesson(
                    start_time=start_time,
                    end_time=end_time,
                    subject=subject,
                    teacher=teacher,
                    room=lesson.get('location')
                )
            )

            if p4:
                lessons.append(p4)

        self.spinner.text = 'Retrieved ' + indicator
        self.spinner.ok('✔')

        return lessons

    # Search the staff directory by surname.
    def get_teachers(self, surname: str) -> List[Teacher]:
        response = self._get('/school-directory', params={
            'name': surname
        })

        teachers = []

        i: int = 0

        for row in response.parser.select_one('#StaffResults > table').find_all('tr'):
            # Ignore table header
            if i != 0:
                cells = row.find_all('td')

                teachers.append(
                    Teacher(
                        name=cells[1].find('h3').text,
                        picture=cells[0].find('img')['src'],
                        roles=[role.strip() for role in cells[2].find_all(text=True)],
                        departments=[department.strip() for department in cells[3].text.split(', ')],
                        phone_number=cells[4].find(text=True).strip(),
                        email_address=cells[4].find('a').text
                    )
                )

            i += 1

        return teachers

    # Get the first search result from the staff directory
    def get_teacher(self, surname: str) -> Teacher:
        return self.get_teachers(surname)[0]

    # Get the user's set tasks
    def get_tasks(
        self,
        completion_status: TaskCompletionStatus.TO_DO,
        read_status: TaskReadStatus.ALL,
        marking_status: TaskMarkingStatus = TaskMarkingStatus.ALL,
        due_date: DateRange = None,
        setters: List[User] = None,
        addressees: List[Addressee] = None,
        sort: Sort = Sort(TaskSortColumn.DUE_DATE),
        offset: int = 0,
        limit: int = 10
    ) -> (List[Task], int):
        self.spinner.text = 'Retrieving tasks'

        params: Dict = {
            'ownerType': TaskOwner.SETTER.foreign_name,
            'archiveStatus': FilterEnum.ALL.foreign_name,
            'completionStatus': completion_status.foreign_name,
            'markingStatus': marking_status.foreign_name,
            'readStatus': read_status.foreign_name,
            'page': offset,
            'pageSize': limit,
            'sortingCriteria': [
                {
                    'column': sort.column.foreign_name,
                    'order': sort.direction(completion_status).foreign_name
                }
            ]
        }

        date_filter: Callable[[Date], str] = lambda date: date.strftime('%Y-%m-%d')

        if due_date:
            params['dueDateFrom'] = date_filter(due_date.from_date)
            params['dueDateTo'] = date_filter(due_date.until_date)
        if setters:
            params['owners'] = [setter.guid for setter in setters]
        if addressees:
            params['addressees'] = [addressee.guid for addressee in addressees]

        response = self._post('/api/v2/taskListing/view/self/tasks/filterBy', json=params, headers={
            'Accept': self.MIME_TYPE_JSON,
            'Referer': self._url('/set-tasks')
        })

        body = response.json()

        tasks: List = []

        # Parse a date from a Firefly style string
        def parse_date(date_str: str) -> Date:
            if not date_str:
                return date_str

            time = DateTime.strptime(date_str, '%Y-%m-%d')

            if not time:
                return time

            return time.date()

        # Create a User instance
        def create_user(user_dict: Dict, user_cls: str = User) -> User:
            return user_cls(
                guid=user_dict.get('guid'),
                name=user_dict.get('name'),
                is_deleted=user_dict.get('deleted', False),
                sort_key=user_dict.get('sortKey')
            )

        for task_dict in body['items']:
            addressees: List = []

            for addressee_dict in task_dict['addressees']:
                addressee_cls: str = Class if addressee_dict.get('isGroup') else Student

                addressees.append(
                    addressee_cls(
                        addressee_dict.get('guid'),
                        addressee_dict.get('name')
                    )
                )

            last_marked_as_done_by: Dict = task_dict.get('lastMarkedAsDoneBy')

            if last_marked_as_done_by:
                last_marked_as_done_by: User = create_user(last_marked_as_done_by)

            tasks.append(
                Task(
                    id=task_dict.get('id'),
                    title=task_dict.get('title'),
                    addressees=addressees,
                    setter=create_user(task_dict.get('setter'), Student if task_dict.get('isPersonalTask') else User),
                    set_date=parse_date(task_dict.get('setDate')),
                    due_date=parse_date(task_dict.get('dueDate')),
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

    # Respond to a task with an event
    def _respond_to_task(self, task_id: int, event_type: TaskEventEnum, feedback: str = None) -> TaskEvent:
        response = self._post('/_api/1.0/tasks/%r/responses' % task_id, headers={
            'Referer': self._url('/set-tasks/' + str(task_id)),
            'Accept': self.MIME_TYPE_JSON
        }, data={
            'data': json.dumps({
                'event': {
                    'author': self.user.guid,
                    'feedback': '' if feedback is None else feedback,
                    # isoformat doesn't include timezone
                    'sent': DateTime.utcnow().isoformat(timespec='milliseconds') + 'Z',
                    'type': event_type.foreign_name
                },
                'recipient': {
                    'guid': self.user.guid,
                    'type': Recipient.USER.foreign_name
                }
            })
        })

        if response.status_code == HTTPStatus.FORBIDDEN:
                raise Exception("Can't mark the task as %s as it's alrady marked as %s" % (
                        event_type.human_name, event_type.human_name
                    )
                )

        event: dict = response.json()['description']

        event_type: TaskEventEnum = TaskEventEnum.from_foreign_name(event['type'])

        return event_type.create(
            guid=event['eventGuid'],
            user=User(
                event['author']
            ),
            sent_at=dateutil.isoparse(event['sent']),
            version_id=event['eventVersionId']
        )

    # Mark a task as done
    def mark_task_as_done(self, task_id: int) -> str:
        return self._respond_to_task(task_id, TaskEventEnum.DONE)

    # Mark a task as to do
    def mark_task_as_to_do(self, task_id: int) -> str:
        return self._respond_to_task(task_id, TaskEventEnum.UNDONE)

    # Get the authenticated user
    @property
    def user(self) -> User:
        if not self._user:
            response: Response = self._get('/pupil-portal')

            regex: re.Pattern = re.compile(r'ff_globals\.initialPageData = (.*);')

            javascript: str = response.parser.find(string=regex)

            json_str: str = regex.search(javascript).group(1)

            user_data: Dict = json.loads(json_str)['page']['user']

            user_cls: str = Student if user_data.get('@role') == 'student' else User

            self._user = user_cls(
                guid=user_data['@guid'],
                name=user_data['@fullname']
            )

        return self._user

    # Request a session cookie from Firefly and save it to a file so we don't have to login again until it expires
    def login(self):
        old_spinner_text: str = self.spinner.text
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

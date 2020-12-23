# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorised reproduction is prohibited.

import re
import json
import pickle
from pathlib import Path
from .times import BREAK
from http import HTTPStatus
from bs4 import BeautifulSoup
from .events import TaskEvent
from yaspin import yaspin as Yaspin
from requests import Session, Response
from dateutil import parser as dateutil
from .filters import TaskSort, DatePeriod
from typing import List, Dict, Callable, Type
from .errors import AuthenticationError, InputError
from datetime import date as Date, time as Time, datetime as DateTime
from .resources import User, Teacher, Lesson, Addressee, Class, Student, Task
from .enums import (TaskCompletionStatus, TaskReadStatus, TaskMarkingStatus, SortDirection,
                    TaskSortColumn, FilterEnum, TimetablePeriod, TaskOwner, TaskEventEnum, Recipient)

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
        self.spinner.color = 'green'
        self._client: Session = Session()
        self._client.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        self._client.headers['Accept'] = self.MIME_TYPE_HTML # Can be overriden on a method basis
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
                raise AuthenticationError('Unable to authenticate with Firefly, check your credentials')

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

        self.spinner.text = 'Retrieving ' + indicator

        response: Response = self._get('/planner/%s/%s' % (period.foreign_name, from_date.strftime('%Y-%m-%d')))

        regex: re.Pattern = re.compile(r'var PLANNER_INITIAL_STATUS = (.*)')

        javascript: str = response.parser.find(string=regex)

        planner_json: str = regex.search(javascript).group(1)

        planner_status: Dict = json.loads(planner_json)

        lessons: List = []

        # Parse an ISO 8601 compatible time string
        def parse_time(iso_time: str) -> DateTime:
            if not iso_time:
                return iso_time

            return dateutil.isoparse(iso_time)

        for lesson in planner_status['events']:
            start: DateTime = parse_time(lesson.get('isostartdate'))
            end: DateTime = parse_time(lesson.get('isoenddate'))
            subject: str = lesson.get('subject')

            p2: Lesson = None
            p4: Lesson = None

            # Firefly does not distinguish between break and free period
            if start.time() == BREAK.start or end.time() == BREAK.end:
                if start.time() != BREAK.start:
                    p2 = Lesson(
                        start=start,
                        end=DateTime.combine(
                            end.date(),
                            BREAK.start
                        )
                    )
                    start = DateTime.combine(
                        start.date(),
                        BREAK.start
                    )
                if end.time() != BREAK.end:
                    p4 = Lesson(
                        start=DateTime.combine(
                            start.date(),
                            BREAK.end
                        ),
                        end=end
                    )
                    end = DateTime.combine(
                        end.date(),
                        BREAK.end
                    )

            teacher_name: str = lesson.get('chairperson')
            teacher: Teacher = None

            if teacher_name:
                teacher = Teacher(teacher_name)

            if p2:
                lessons.append(p2)

            lessons.append(
                Lesson(
                    start=start,
                    end=end,
                    subject=subject,
                    teacher=teacher,
                    room=lesson.get('location')
                )
            )

            if p4:
                lessons.append(p4)

        self.spinner.text = 'Retrieved ' + indicator

        return lessons

    # Search the staff directory by surname.
    def search_directory(self, surname: str) -> List[Teacher]:
        self.spinner.text = 'Searching the school directory'

        response = self._get('/school-directory', params={
            'name': surname
        })

        teachers = []

        table = response.parser.select_one('#StaffResults > table')

        if not table:
            return []

        for i, row in enumerate(table.find_all('tr')):
            # Ignore table header
            if i != 0:
                cells = row.find_all('td')

                phone_number: str = cells[4].find(text=True)
                email_address: str = cells[4].find('a').text

                teachers.append(
                    Teacher(
                        name=cells[1].find('h3').text,
                        picture=cells[0].find('img')['src'],
                        roles=[role.strip() for role in cells[2].find_all(text=True) if role],
                        departments=[department.strip() for department in cells[3].text.split(', ') if department],
                        phone_number=phone_number.strip() if phone_number else phone_number,
                        email_address=email_address.strip() if email_address else email_address
                    )
                )

        return teachers

    # Get the first search result from the staff directory
    def get_teacher(self, surname: str) -> Teacher:
        try:
            return self.search_directory(surname)[0]
        except IndexError:
            return None

    # Get the user's set tasks
    def get_tasks(
        self,
        completion_status: TaskCompletionStatus = TaskCompletionStatus.ALL,
        read_status: TaskReadStatus = TaskReadStatus.ALL,
        marking_status: TaskMarkingStatus = TaskMarkingStatus.ALL,
        due: DatePeriod = None,
        setters: List[User] = None,
        addressees: List[Addressee] = None,
        sort: TaskSort = TaskSort(TaskSortColumn.DUE_DATE),
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

        date_filter: Callable[[Date], [str]] = lambda date: date.strftime('%Y-%m-%d')

        if due:
            params['dueDateFrom'] = date_filter(due.from_date)
            params['dueDateTo'] = date_filter(due.until_date)
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
        def create_user(user_dict: Dict, user_cls: Type[User] = User) -> User:
            return user_cls(
                guid=user_dict.get('guid'),
                name=user_dict.get('name'),
                is_deleted=user_dict.get('deleted', False),
                sort_key=user_dict.get('sortKey')
            )

        for task_dict in body['items']:
            addressees: List = []

            for addressee_dict in task_dict['addressees']:
                addressee_cls: Type[Addressee] = Class if addressee_dict.get('isGroup') else Student

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
                raise InputError("Can't mark the task as %s as it's already marked as %s" % (
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

            user_cls: Type[User] = Student if user_data.get('@role') == 'student' else User

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

        cookie_file = self._cookie_path.open('wb')

        pickle.dump(self._client.cookies, cookie_file)

        self.spinner.text = old_spinner_text

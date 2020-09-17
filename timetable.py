# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorised reproduction is prohibited.

import requests
import pickle
import json
import re
import os
import subprocess
import sys
import shlex
import dateparser
from http import cookiejar
from typing import List, Callable
from bs4 import BeautifulSoup
from pathlib import Path
from yaspin import yaspin
from configparser import ConfigParser
from datetime import date, time, timedelta
from dateutil import parser as timeparser
from colorama import Fore, Style, init as colorinit

PATH = Path.home().joinpath('.ff-timetable')

# Teacher is the owner of the lesson.
class Teacher():
    def __init__(self, name: str, picture: str, roles: List[str], departments: List[str], phone_number: str, email_address: str):
        self.name = name
        self.picture = picture
        self.roles = roles
        self.departments = departments
        self.phone_number = phone_number
        self.email_address = email_address

# Lesson is a subject taught by a teacher in a room.
class Lesson():
    def __init__(self, start_time: time, end_time: time, subject: str, teacher: Teacher = None, room: str = None):
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.teacher = teacher
        self.room = room

# FireflyClient maintains Firefly session state.
class FireflyClient():
    # __init__ creates a new Firefly client. 
    def __init__(self, url: str, username: str, password: str):
        self.base_url = url
        self.username = username
        self.password = password
        self.spinner = yaspin()
        self._client = requests.Session()
        self._client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'en-GB,en;q=0.9'
        })
        self._attempts = 0
        self._path = Path.home().joinpath('.ff-timetable')
        self._cookie_path = self._path.joinpath('cookies')

        if not self._path.is_dir():
            self._path.mkdir()

        if self._cookie_path.is_file():
            cookies = pickle.load(self._cookie_path.open('rb'))
            self._client.cookies.update(cookies)

    # _request makes a request to Firefly and checks if we're authenticated.
    # If we're not, it will attempt to login.
    def _request(self, method: str, endpoint: str, **kwargs):
        url = self.base_url + endpoint

        response = self._client.request(method, url, **kwargs)

        # Determine if we need to login
        if response.url != url and 'login.aspx' in response.url:
            if self._attempts > 1:
                raise Exception('Unable to authenticate with Firefly')

            self.login()

            self._attempts += 1

            # Try again
            return self._request(method, endpoint, **kwargs)

        if 'text/html' not in response.headers['Content-Type']:
            raise Exception('Response content type must be HTML')

        response.parser = BeautifulSoup(response.text, 'lxml')

        return response

    # _get makes a GET request
    def _get(self, endpoint: str, **kwargs):
        return self._request('GET', endpoint, **kwargs)

    # _post makes a POST request
    def _post(self, endpoint: str, **kwargs):
        return self._request('POST', endpoint, **kwargs)

    # get_lessons gets the lessons on a given day.
    def get_lessons(self, date: date) -> List[Lesson]:
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
            parse_time: Callable[[str], time] = lambda iso_date: timeparser.isoparse(iso_date).time()

            start_time = parse_time(lesson.get('isostartdate'))
            end_time = parse_time(lesson.get('isoenddate'))

            p4 = None
            subject = lesson.get('subject')

            if not subject:
                free_period = 'Free Period'

                if start_time == time(10, 45):
                    subject = 'Break'
                    break_end_time = time(11, 10)

                    # Firefly does not distinguish between break and free period
                    if end_time != break_end_time:
                        p4_end_time = end_time
                        p4 = Lesson(
                            break_end_time,
                            p4_end_time,
                            free_period
                        )
                        end_time = break_end_time

                elif start_time == time(12, 55) and end_time == time(14):
                    subject = 'Lunch'
                else:
                    subject = free_period

            # teacher_name = lesson.get('chairperson')
            # teacher = None

            # if teacher_name:
            #     surname = re.match('.* .* (.*)', teacher_name).group(1)
            #     teacher = self.get_teacher(surname)

            lessons.append(Lesson(
                start_time,
                end_time,
                subject,
                lesson.get('chairperson'),
                lesson.get('location')
            ))
            
            if p4:
                lessons.append(p4)

        self.spinner.text = 'Retrieved Timetable'
        self.spinner.ok('✔')

        return lessons

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

    # login requests a session cookie from Firefly and saves it to a file so we don't have to login again until it expires.
    def login(self):
        self._old_spinner_text = self.spinner.text
        self.spinner.text = 'Logging in'

        response = self._get('/login/login.aspx')

        form = response.parser.select_one(
            'body > div.ff-login-box > div.ff-login-mainsection > form')

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

        self.spinner.text = self._old_spinner_text
        self._old_spinner_text = None

# header_str pretty prints a dictionary of headers.
# This function is for debugging purposes. You probably won't need to use it.
def header_str(headers: dict):
    return '\n'.join([k + ': ' + (', '.join(v) if isinstance(v, list) else v) for (k, v) in headers])

# create_client creates a new FireflyClient with the configured URL and credentials.
def create_client():
    config = get_config()
    sections = config.sections()

    if len(sections) < 1:
        raise Exception('Please configure a Firefly hostname')

    hostname = sections[0]
    host_config = config[hostname]

    for key in ['Username', 'Password']:
        if not host_config.get(key, None):
            raise Exception('Please set the {} for {}'.format(key.lower(), hostname))

    protocol = host_config.get('Protocol', 'https')
    username = host_config['Username']
    password = host_config['Password']

    return FireflyClient(protocol + '://' + hostname, username, password)

# get_config retrieves a config value for a key if one is supplied, or the config object.
def get_config(key: str = None):
    config_path = PATH.joinpath('timetable.conf')

    if not config_path.is_file():
        raise Exception('Please create a configuration file at `{}`.'.format(config_path))

    config = ConfigParser()
    config.read(config_path)

    if key:
        return config[key]
    
    return config

# print_timetable pretty prints the user's timetable to the console.
def print_timetable(client: FireflyClient, date: date):
    client.spinner.start()

    lessons = client.get_lessons(date)

    client.spinner.stop()

    for lesson in lessons:
        time_format: Callable[[date],str] = lambda date: date.strftime('%H:%M')
        time_period = time_format(lesson.start_time) + ' - ' + time_format(lesson.end_time)

        print(Style.DIM + time_period + Style.RESET_ALL, Style.BRIGHT + lesson.subject + Style.RESET_ALL)

        padding = len(time_period) + 1

        for key in ['teacher', 'room']:
            value = getattr(lesson, key, None)

            if value is not None:
                print(' ' * padding + value)

colorinit()

client = create_client()

date_input = input('Date (leave blank for today): ')

if date_input:
    parsed_time = dateparser.parse(date_input)

    if parsed_time:
        date = parsed_time.date()
    else:
        raise Exception("Couldn't parse the date `{}`. Perhaps try rephrasing it?".format(date_input))
else:
    date = date.today()

print_timetable(client, date)
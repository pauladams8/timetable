# Timetable

This script retrieves your timetable and other information from Firefly.

[![asciicast](https://asciinema.org/a/qwucsSXemoLbaCgvBsIu7p4VI.svg)](https://asciinema.org/a/qwucsSXemoLbaCgvBsIu7p4VI)

## Requirements
- libxml2 and libxslt
- Python 3.8 or higher
- Python dependencies listed in `requirements.txt` (`pip install -r requirements.txt`)

## Usage
### Timetable
#### Get your timetable
```
usage: ff timetable [-h] [-d DATE] {export} ...

Retrieve your timetable

positional arguments:
  {export}              For help with a specific command, run ff timetable
                        [COMMAND] --help

optional arguments:
  -h, --help            show this help message and exit
  -d DATE, --date DATE  The timetable date; defaults to today. ff timetable
                        will attempt to parse any human readable date string,
                        so dates like `tomorrow` and `next monday` are
                        acceptable.
```
### Tasks
#### Get tasks
```
usage: ff tasks [-h] [--all | --done] [--read | --unread]
                [--marked | --unmarked] [--set FROM [[UNTIL] ...]]
                [--due FROM [[UNTIL] ...]] [--subject SUBJECT [SUBJECT ...]]
                [--set-by [SETTER ...]] [--set-to [ADDRESEE ...]]
                [--sort COLUMN [[DIRECTION] ...]] [--offset OFFSET]
                [--limit LIMIT]
                {done,undo} ...

Retrieve your set tasks

positional arguments:
  {done,undo}           For help with a specific command, run ff tasks
                        [COMMAND] --help

optional arguments:
  -h, --help            show this help message and exit
  --all                 Tasks that are yet to be completed
  --done                Tasks that are done
  --read                Tasks that have been read
  --unread              Tasks that have not been read
  --marked              Tasks that have been marked
  --unmarked            Tasks that have not been marked
  --set FROM [[UNTIL] ...]
                        Tasks that were set no earlier than FROM, but no later
                        than UNTIL. UNTIL defaults to FROM, so for tasks set
                        yesterday, for example, use --set yesterday. ff tasks
                        will attempt to parse any human readable date string,
                        so dates like `tomorrow` and `next monday` are
                        acceptable.
  --due FROM [[UNTIL] ...]
                        Tasks that are due no earlier than FROM, but no later
                        than UNTIL. UNTIL defaults to FROM, so for tasks due
                        tomorrow, for example, use --due tomorrow. ff tasks
                        will attempt to parse any human readable date string,
                        so dates like `tomorrow` and `next monday` are
                        acceptable.
  --subject SUBJECT [SUBJECT ...]
                        The class subject(s). E.g. maths, physics, english.
  --set-by [SETTER ...]
                        Space separated list of task setter GUIDs. You can get
                        a list of your teachers and their GUIDs by running `ff
                        tasks teachers`.
  --set-to [ADDRESEE ...]
                        Space separated list of task addressee GUIDs. You can
                        get a list of your classes and their GUIDs by running
                        `ff tasks classes`.
  --sort COLUMN [[DIRECTION] ...]
                        Order by which to sort the tasks. Supply a snake_case
                        column (either set_date or due_date; defaults to
                        due_date) and optionally a direction (either asc or
                        desc; defaults to desc).
  --offset OFFSET       Offset from which to retrieve tasks (defaults to 0).
                        Must be an integer.
  --limit LIMIT         Limit to retrieve tasks to (defaults to 10). Must be
                        an integer.
```
#### Mark task as done
```
usage: ff tasks done [-h] id

Mark a task as done

positional arguments:
  id          The ID of the task to mark as done. You can retrieve a list of
              your tasks by running ff tasks done tasks.

optional arguments:
  -h, --help  show this help message and exit
```
#### Mark task as todo
```
usage: ff tasks todo [-h] id

Mark a task as todo

positional arguments:
  id          The ID of the task to mark as todo. You can retrieve a list of
              your tasks by running ff tasks todo tasks.

optional arguments:
  -h, --help  show this help message and exit
```
### Teachers
#### Search the school directory
```
usage: ff teachers search [-h] [--surname SURNAME]

Search the school directory by surname

optional arguments:
  -h, --help         show this help message and exit
  --surname SURNAME  The surname to search for
```
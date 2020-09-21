import factories
from typing import List
from pathlib import Path
from configparser import ConfigParser, SectionProxy

AUTHOR = 'Paul Adams'
PATH = Path.home().joinpath('.ff-timetable')

# get retrieves a config value for a dot separated key.
def get(key: str) -> str:
    parser = factories.config_parser()

    fragments = key.split('.')
    section_key = fragments.pop()

    section = parser[section_key]

    for fragment in fragments:
        value = section.get(fragment)

        if value is None:
            return value

    return value

# sections gets the sections from the config file.
def sections() -> List:
    return factories.config_parser().sections()

# section gets a section for a section key.
def section(key: str) -> SectionProxy:
    return factories.config_parser()[key]
# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import os
from .input import ask
from pathlib import Path
from . import fmt, factories
from .errors import ConfigError
from configparser import ConfigParser, NoSectionError, NoOptionError, _UNSET

# The program author
AUTHOR: str = 'Paul Adams'
# The repository URL
REPO_URL: str = 'https://github.com/pauladams8/timetable'
# The storage path
PATH: Path = Path.home().joinpath('.ff-timetable')
# The config file path
CONFIG_PATH: Path = PATH.joinpath('timetable.conf')
# The Sentry DSN
SENTRY_DSN = 'https://bd151808309343b7b8cc0338021a2722@o490264.ingest.sentry.io/5553897'

# Create the storage directory if it doesn't exist
if not PATH.is_dir():
    PATH.mkdir()

# Create the config file if it doesn't exist
if not CONFIG_PATH.is_file():
    CONFIG_PATH.touch()

# Create the config parser singleton
Parser: ConfigParser = factories.config_parser()

# Determine if debug mode is on
def debug_mode() -> bool:
    return Parser.getboolean('general', 'debug', fallback=False) or os.getenv('ENVIRONMENT') == 'dev'

# Get a value from the config file or ask the user if it doesn't exist
def get(section: str, key: str, default = _UNSET, can_ask: bool = True):
    try:
        value = Parser.get(section, key, fallback=default)
    except (NoSectionError, NoOptionError) as e:
        if can_ask:
            value = ask(section.capitalize() + ' ' + key)
            if isinstance(e, NoSectionError):
                Parser.add_section(section)
            Parser.set(section, key, value)
            commit()
            return value

        if isinstance(e, NoSectionError):
            raise ConfigError('Please create a `%s` section in the config file' % section)
        raise ConfigError('Please set the %s `%s` key in the config file' % (section.capitalize(), key))

    return value

# Write any changes to the config file
def commit():
    with open(CONFIG_PATH, 'w') as f:
        Parser.write(f)
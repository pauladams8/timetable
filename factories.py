# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import config
from firefly import Client
from typing import Callable
from configparser import ConfigParser, SectionProxy

# Create a new configparser.ConfigParser
def config_parser():
    config_path = config.PATH.joinpath('timetable.conf')

    if not config_path.is_file():
        raise Exception('Please create a configuration file at `%s`.' % config_path)

    config_parser = ConfigParser()
    config_parser.read(config_path)

    return config_parser

# Create a new FireflyClient
def firefly_client():
    section: SectionProxy = config.section('firefly')

    # Get a config value from the Firefly section
    def get_config(key: str, default: str = None) -> str:
        value: str = section.get(key, default)

        if not value:
            raise Exception('Please set the Firefly ' + key)

        return value

    url: str = get_config('protocol', 'https') + '://' + get_config('hostname')

    return Client(
        url=url,
        username=get_config('username'),
        password=get_config('password'),
        storage_path=config.PATH
    )
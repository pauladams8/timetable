# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from . import config
from .client import Client
from .errors import ConfigError
from configparser import ConfigParser, SectionProxy

# Create a new configparser.ConfigParser
def config_parser():
    config_parser = ConfigParser()
    config_parser.read(config.CONFIG_PATH)

    return config_parser

# Create a new Client
def firefly_client(can_ask: bool = True):
    section: str = 'firefly'

    # Get a config value from the Firefly section
    def get_config(key: str, default = config._UNSET) -> str:
        return config.get(section, key, default, can_ask)

    url: str = get_config('protocol', 'https') + '://' + get_config('hostname')

    return Client(
        url=url,
        username=get_config('username'),
        password=get_config('password'),
        storage_path=config.PATH
    )
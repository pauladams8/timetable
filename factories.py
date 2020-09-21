import config
from firefly import FireflyClient
from configparser import ConfigParser

_config_parser: ConfigParser = None

# config_parser creates a new configparser.ConfigParser
def config_parser():
    config_path = config.PATH.joinpath('timetable.conf')

    if not config_path.is_file():
        raise Exception('Please create a configuration file at `{}`.'.format(config_path))

    config_parser = ConfigParser()
    config_parser.read(config_path)

    return config_parser

# create_client creates a new FireflyClient.
def firefly_client():
    sections = config.sections()

    if len(sections) < 1:
        raise Exception('Please configure a Firefly hostname')

    hostname = sections[0]
    host_config = config.section(hostname)

    for key in ['Username', 'Password']:
        if not host_config.get(key):
            raise Exception('Please set the {} for {}'.format(key.lower(), hostname))

    protocol = host_config.get('Protocol', 'https')
    username = host_config['Username']
    password = host_config['Password']

    return FireflyClient(protocol + '://' + hostname, username, password, config.PATH)
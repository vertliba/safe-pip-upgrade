import configparser
import logging.config
from typing import Callable


class Config:
    # MAIN PARAMETERS
    INI_FILE = 'pip_upgrade.ini'
    WORKING_DIRECTORY = r'./'
    LOCAL_REQUIREMENTS_FILE = r'./requirements.txt'
    IGNORE_LINE_STARTS = '# -r https:// http:// git+'.split()

    RUNNER = 'compose'

    # COMPOSE PARAMETERS
    COMPOSE_PROJECT_FOLDER = WORKING_DIRECTORY
    COMPOSE_REQUIREMENTS_FILE = LOCAL_REQUIREMENTS_FILE
    COMPOSE_SERVICE_NAME = 'django'
    COMPOSE_WORK_DIR = None  # remote working directory

    command_handler: Callable


LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'myFormatter',
            'filename': 'pip_upgrade.log'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'myFormatter',
        },
    },
    'formatters': {
        'myFormatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}

logging.config.dictConfig(LOGGING)


class ConfigFile(configparser.ConfigParser):
    """ Ini file config parser. """
    MAP = {
        'MAIN': {'INI_FILE': str,
                 'WORKING_DIRECTORY': str,
                 'LOCAL_REQUIREMENTS_FILE': str,
                 'IGNORE_LINE_STARTS': str},
        'COMPOSE RUNNER': {'COMPOSE_PROJECT_FOLDER': str,
                           'COMPOSE_REQUIREMENTS_FILE': str,
                           'COMPOSE_SERVICE_NAME': str,
                           'COMPOSE_WORK_DIR': str}
    }

    def write_to_file(self):
        for section, keys in self.MAP.items():
            self[section] = {key: getattr(Config, key) for key in keys}

        with open(Config.INI_FILE, 'w') as file:
            self.write(file)

    def read_from_file(self):
        self.read(Config.INI_FILE)
        GETTERS = {str: self.get, int: self.getint, bool: self.getboolean}
        for section, keys in self.MAP.items():
            for key, value_type in keys.items():
                getter = GETTERS[value_type]
                # noinspection PyArgumentList
                value = getter(section, key, raw=True, fallback=None)
                if value is not None:
                    setattr(Config, key, value)


config_file = ConfigFile()
config_file.read_from_file()

import logging.config

class Config:
    INI_FILE = 'pip_upgrade.ini'
    WORKING_DIRECTORY = r'./'
    LOCAL_REQUIREMENTS_FILE = r'./requirements.txt'

    RUNNER = 'compose'

    # Compose parameters
    COMPOSE_PROJECT_FOLDER = WORKING_DIRECTORY
    COMPOSE_REQUIREMENTS_FILE = LOCAL_REQUIREMENTS_FILE
    COMPOSE_SERVICE_NAME = 'django'
    COMPOSE_WORK_DIR = './',  # remote working directory
    IGNORE_LINE_STARTS = ('# -r https:// http:// git+').split()

LOGGING = {
    'version': 1,
    'handlers': {
        'fileHandler': {
            'class': 'logging.FileHandler',
            'formatter': 'myFormatter',
            'filename': 'main.log'
        },
        'fullHandler': {
            'class': 'logging.FileHandler',
            'formatter': 'myFormatter',
            'filename': 'full.log'
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
            'handlers': ['fullHandler'],
            'level': 'INFO',
        },
    },
}

logging.config.dictConfig(LOGGING)


import logging.config

REQUIREMENTS_FILE = 'deploy/requirements.txt'
LOCAL_REQUIREMENTS_FILE = r'C:\work\big-project\deploy\requirements\requirements.txt'

PYTHON_RUNNER = 'compose'
PROJECT_FOLDER = r'C:\work\big-project'
COMPOSE_SERVICE_NAME = 'django'
REMOTE_WORK_DIR = '/app'  # remote working directory
IGNORE_LINE_STARTS = ('#', '-r', 'https://', 'http://')

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

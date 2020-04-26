Pip-safe-upgrade
==================

Pip-safe-upgrade automatically updates your pip requirements to the highest versions the tests pass.

![build](https://github.com/VVyacheslav/safe-pip-upgrade/workflows/build/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/VVyacheslav/safe-pip-upgrade/branch/master/graph/badge.svg)](https://codecov.io/gh/VVyacheslav/safe-pip-upgrade)
[![PyPI version](https://badge.fury.io/py/safe-pip-upgrade.svg)](https://badge.fury.io/py/safe-pip-upgrade)

Overview
--------

This package can works only with docker-compose projects for now. 

Installation
------------

```shell script
pip install safe-pip-upgrade
```

Work algorithm
----------------------

After that you run the program with requirement parameters safe_pip_upgrade will do:

1. starts the container in daemon mode (runs `docker-compose run project sleep 3590`).
1. read the next package in requirements.
1. check comment. if the comment is `'# the latest working version'` go to p. 2.
1. check comment. if the comment is `'# error on the version x.x.x'`:
    1. check if the is version between current and x.x.x
    2. if there is update requirements file to version in the middle between the current and x.x.x and go to p. 3
    1. if there is not, add comment `'# the latest working version'` and go to p. 2
1. check if there is newer version
    1. if there is not go to p. 2
    1. if there is, update requirements file to the newest version
1. starts the tests
1. if tests fail set version back, add comment `'# error on the version x.x.x'` and go to p. 4.
1. otherwise, go to p. 2

Usage
-----


### The main parameters

```python
REQUIREMENTS_FILE = 'deploy/requirements.txt' # path to the requirements file in docker container
LOCAL_REQUIREMENTS_FILE = r'C:\work\big-project\deploy\requirements\requirements.txt' # the local path to the requirements file 

PROJECT_FOLDER = r'C:\work\big-project' # the local project path
COMPOSE_SERVICE_NAME = 'django' # the docker-compose service name
REMOTE_WORK_DIR = '/app'  # remote working directory
```

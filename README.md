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

Using safe-pip-upgrade is basically a two-step process.

1. Define your app's parameters with a `pip_upgrade.ini`
2. Run ```pip-upgrade.py UPGRADE``` to start the upgrade of your requirements 

A `pip_upgrade.ini` looks like this:

```ini
[MAIN]
working_directory = ./  # change it if you want to start upgrade from other directory.
local_requirements_file = requirements.txt # path and name of the requirements file relative to the working directory
ignore_line_starts = ['#', '-r', 'https://', 'http://', 'git+'] # list of the line beginnings you want to ignore 

[COMPOSE RUNNER]
compose_project_folder = . # path to your docker-compose file
compose_requirements_file = requirements.txt # path and name of the requirements file in docker container relative to CWD in your Dockerfile 
compose_service_name = django # name of the docker-compose service
compose_work_dir = # set it if you want to change working directory in container 
```

You can run ```pip_upgrade.py CREATE-INI``` so that pip-upgrade automatically creates an ini-file for you 

All ini-files option can also be defined with command keys. Type ```pip_upgrade.py``` to see a detailed description.

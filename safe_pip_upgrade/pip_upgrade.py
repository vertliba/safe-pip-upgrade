#!/usr/bin/python3
"""
Pip-safe-upgrade automatically updates your pip requirements.

It tries to gradually upgrade your requirements one by one while the tests
pass.
"""
import argparse
import os
import sys

from safe_pip_upgrade.config import Config, config_file
from safe_pip_upgrade.upgrade import start_upgrade


class ManagementUtility:
    """ Encapsulate the logic of the django-admin and manage.py utilities. """

    def __init__(self):
        self.argv = sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])

    def execute(self):
        # noinspection PyTypeChecker
        parser = argparse.ArgumentParser(
            description=__doc__,  # printed with -h/--help
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # COMMANDS
        subparsers = parser.add_subparsers(help='Command')

        # upgrade
        parser_upgrade = subparsers.add_parser('UPGRADE', help='start upgrade')
        parser_upgrade.set_defaults(command_handler=start_upgrade)

        # create ini file
        parser_create_ini = subparsers.add_parser(
            'CREATE-INI', help='create example ini file in current directory')
        parser_create_ini.set_defaults(
            command_handler=config_file.write_to_file)

        # GENERAL SETTINGS
        general_group = parser.add_argument_group('MAIN PARAMETERS')

        # ini file
        general_group.add_argument(
            "-f", "--file", metavar="INI FILE", dest='INI_FILE',
            help='Specify alternate config file. (default: "pip_upgrade.ini)')

        # working directory
        general_group.add_argument(
            "-d", "--work-directory", metavar="DIR", dest='WORKING_DIRECTORY',
            help='Specify working directory. (default: current directory)')

        # local requirements file
        general_group.add_argument(
            "-r", "--requirement", metavar="FILE",
            dest='LOCAL_REQUIREMENTS_FILE',
            help='Specify local requirements file  '
                 '(default: requirements.txt)')

        # runner
        general_group.add_argument(
            "-u", "--runner", metavar="RUNNER", dest='RUNNER',
            help='Specify runner (only "compose" is available now).')

        # COMPOSE RUNNER SETTINGS
        compose_group = parser.add_argument_group('COMPOSE RUNNER PARAMETERS')

        # compose project directory
        compose_group.add_argument(
            "-cd", "--compose-project-directory", metavar="DIR",
            dest='COMPOSE_PROJECT_FOLDER',
            help='Specify an alternate project directory (default: '
                 'work-directory if defined, otherwise current directory')

        # compose requirements file
        compose_group.add_argument(
            "-cr", "--compose-requirements", metavar="FILE",
            dest='COMPOSE_REQUIREMENTS_FILE',
            help='Specify compose requirements file '
                 '(default: compose working directory.')

        # compose service name
        compose_group.add_argument(
            "-cs", "--compose-service", metavar="DIR",
            dest='COMPOSE_SERVICE_NAME',
            help='Specify compose service name '
                 '(default: "django".')

        # compose work directory
        compose_group.add_argument(
            "-crd", "--compose-work-dir", metavar="DIR",
            dest='COMPOSE_WORK_DIR',
            help='Specify an alternate compose working directory in '
                 'container (default: CWD form Dockerfile)'),

        args = parser.parse_args(namespace=Config)
        if not hasattr(args, 'command_handler'):
            parser.print_help()
        else:
            args.command_handler()


utility = ManagementUtility()
utility.execute()

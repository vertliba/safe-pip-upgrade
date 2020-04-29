import logging
import os
from logging import INFO

from safe_pip_upgrade.config import Config as Config
from safe_pip_upgrade.requirements import Requirement, RecognizeException
from safe_pip_upgrade.requirements_file import RequirementsLocal
from safe_pip_upgrade.runners.python_compose import (ComposeRunner,
                                                     DockerException)

logger = logging.getLogger(__name__)


def get_requirements():
    """ Get requirements file handler.

    Now there is only a file handler. Perhaps there will be more later.
    """
    return RequirementsLocal(os.path.join(Config.WORKING_DIRECTORY,
                                          Config.LOCAL_REQUIREMENTS_FILE))


def get_client():
    if Config.RUNNER == 'compose':
        runner = ComposeRunner(
            project_folder=Config.COMPOSE_PROJECT_FOLDER,
            service_name=Config.COMPOSE_SERVICE_NAME,
            requirements_file_name=Config.COMPOSE_REQUIREMENTS_FILE,
            remote_work_dir=Config.COMPOSE_WORK_DIR
        )
        runner.up()
        return runner


class Upgrade:
    """ The main class that performs the upgrade. """

    def __init__(self, client, req_file):
        self.client = client
        self.req_file = req_file
        self.req_lines = self.req_file.read_lines()

    def start_upgrade(self):
        """ Upgrade all requirements. """
        self.req_file.make_backup()
        for i, r_line in enumerate(self.req_lines):
            r_line = r_line.strip()
            if (not r_line or
                    list(
                        filter(r_line.startswith, Config.IGNORE_LINE_STARTS))):
                continue

            try:
                self.try_upgrade_requirement(i)
            except DockerException:
                self.req_lines[i] = r_line
                break

            except RecognizeException as ex:
                logger.log(INFO, ex)
                continue

        self.req_file.write_lines(self.req_lines)
        logger.info('All done!')

    def try_upgrade_requirement(self, i):
        """ Upgrade requirements.

        if there is no version marked as failed try the newest version. If
        there is already a failed version, try find version between the current
        and latest.
        """
        req = Requirement(self.req_lines[i])
        while req.increase_version():
            self.req_lines[i] = req.get_line()
            self.req_file.write_lines(self.req_lines)

            logger.info(f'try upgrade requirements: {req.get_line().strip()}')
            if self.client.run_tests():
                logger.info(f'requirements was upgraded: {req.get_line()}')
                self.req_file.copy_file('', '_last_pass')
            else:
                logger.info(f'upgrade failed: {req.get_line()}')
                req.fix_error_version()
        self.req_lines[i] = req.get_line()


def start_upgrade():
    Upgrade(get_client(), get_requirements()).start_upgrade()


if __name__ == '__main__':
    start_upgrade()

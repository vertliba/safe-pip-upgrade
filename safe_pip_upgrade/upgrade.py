import logging
from logging import INFO
from safe_pip_upgrade.defaults import (
    REQUIREMENTS_FILE, PYTHON_RUNNER,
    PROJECT_FOLDER, COMPOSE_SERVICE_NAME,
    REMOTE_WORK_DIR, IGNORE_LINE_STARTS,
    LOCAL_REQUIREMENTS_FILE)

from safe_pip_upgrade.pythons.python_compose import (ComposeRunner,
                                                     DockerException)
from safe_pip_upgrade.requirements import Requirement, RecognizeException
from safe_pip_upgrade.requirements_file import RequirementsLocal

logger = logging.getLogger(__name__)


def get_requirements():
    """ Get requirements file handler.

    Now there is only a file handler. Perhaps there will be more later.
    """
    return RequirementsLocal(LOCAL_REQUIREMENTS_FILE)


def get_client():
    if PYTHON_RUNNER == 'compose':
        runner = ComposeRunner(PROJECT_FOLDER, COMPOSE_SERVICE_NAME)
        runner.remote_work_dir = REMOTE_WORK_DIR
        runner.requirements_file_name = REQUIREMENTS_FILE
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
                    list(filter(r_line.startswith, IGNORE_LINE_STARTS))):
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

            logger.info(f'try upgrade requirements: {req.get_line()}')
            if self.client.run_tests():
                logger.info(f'requirements was upgraded: {req.get_line()}')
                self.req_file.copy_file('', '_last_pass')
            else:
                logger.info(f'upgrade failed: {req.get_line()}')
                req.fix_error_version()
        self.req_lines[i] = req.get_line()

if __name__ == '__main__':
    Upgrade(get_client(), get_requirements()).start_upgrade()
    # client = get_client()
    # client.run_tests()

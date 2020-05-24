import logging
from logging import INFO

from safe_pip_upgrade.config import Config
from safe_pip_upgrade.core.packages import Requirement, RecognizeException

logger = logging.getLogger(__name__)


class SafeUpgradeException(Exception):
    pass


class RunnerException(SafeUpgradeException):
    pass


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
            except RunnerException:
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

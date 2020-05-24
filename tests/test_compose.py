from unittest.case import TestCase
from unittest.mock import patch

from safe_pip_upgrade.runners.compose import ComposeRunner


class FakeConfig:
    COMPOSE_WORK_DIR = 'COMPOSE_WORK_DIR'
    COMPOSE_PROJECT_FOLDER = 'COMPOSE_PROJECT_FOLDER'
    COMPOSE_SERVICE_NAME = 'COMPOSE_SERVICE_NAME'
    COMPOSE_REQUIREMENTS_FILE = 'COMPOSE_REQUIREMENTS_FILE'


class ComposeTestCase(TestCase):
    """ TestCase of the docker runner.

    It is need to be finished.
    """
    runner_path = ComposeRunner.__module__ + '.' + ComposeRunner.__name__ + '.'

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.up_patcher = patch(cls.runner_path + '_docker_up')
        cls.up_patcher.start()
        cls.run_docker = patch(cls.runner_path + '_run_docker')
        cls._check_or_run_daemon_patcher = patch(cls.runner_path +
                                                 '_check_or_run_daemon')

    def test_check_daemon(self):
        runner = ComposeRunner(FakeConfig)
        with self.run_docker as run_docker:
            run_docker.reset_mock()

            # service is started
            run_docker.return_value.stdout = runner.daemon_name.encode()
            result = runner._check_daemon()

            run_docker.assert_called_once_with(
                'ps', '-f',
                'name=COMPOSE_SERVICE_NAME_upgrade',
                capture_output=True
            )
            self.assertTrue(result)

            # service is not started
            run_docker.return_value.stdout = b''
            result = runner._check_daemon()
            self.assertFalse(result)

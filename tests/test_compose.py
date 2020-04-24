from unittest import skip
from unittest.case import TestCase

from safe_pip_upgrade.defaults import (REMOTE_WORK_DIR, REQUIREMENTS_FILE,
                                       PROJECT_FOLDER)
from safe_pip_upgrade.pythons.python_compose import ComposeRunner


@skip
class ComposeTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.runner = ComposeRunner(PROJECT_FOLDER, 'django')

    def test_docker(self):
        self.runner.remote_work_dir = REMOTE_WORK_DIR
        self.runner.requirements_file_name = REQUIREMENTS_FILE
        self.runner.up()
        self.assertTrue(self.runner.run_tests())

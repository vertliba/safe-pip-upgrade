from unittest import skip
from unittest.case import TestCase

from safe_pip_upgrade.config import Config as Config
from safe_pip_upgrade.runners.python_compose import ComposeRunner


@skip
class ComposeTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.runner = ComposeRunner(
            project_folder=Config.COMPOSE_PROJECT_FOLDER,
            service_name='django',
            requirements_file_name=Config.COMPOSE_REQUIREMENTS_FILE,
            remote_work_dir=Config.COMPOSE_WORK_DIR
        )

    def test_docker(self):
        self.runner.up()
        self.assertTrue(self.runner.run_tests())

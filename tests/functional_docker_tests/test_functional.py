import os
import shutil
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from tests.helpers import get_package_last_version

EXPECTED_REQUIREMENTS_TXT = (
    f'ppci==0.5.7 # the latest working version\n'
    f'rules==2.1 # the latest working version\n'
    f'Faker=={get_package_last_version("Faker")}\n'
    f'\n'
    f'# Next lines will be ignored because of comments\n'
    f'requests==2.24.0 # the latest working version\n'
    f'packaging==20.4 # the latest working version\n'
)


class DockerIntegrationTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.cur_dir = Path(__file__).parent
        os.chdir(cls.cur_dir)
        cls.test_project_path = cls.cur_dir.parent.parent / 'test_project'
        cls.requirements_file = (cls.test_project_path / 'requirements.txt')
        super().setUpClass()

    def test_upgrade(self):
        self.copy_requirements()
        import safe_pip_upgrade.pip_upgrade as pip_upgrade
        with patch.object(sys, 'argv', ['pip-upgrade', 'UPGRADE']):
            pip_upgrade.main()
        actual_requirements = self.requirements_file.read_text()
        self.assertEqual(EXPECTED_REQUIREMENTS_TXT, actual_requirements)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.clean_backups()
        super().tearDownClass()

    @classmethod
    def clean_backups(cls):
        for f in cls.test_project_path.glob('requirements_backup_*.txt'):
            f.unlink()

    def copy_requirements(self):
        orig_req = (self.test_project_path / 'requirements.original.txt')
        shutil.copyfile(orig_req, self.requirements_file)

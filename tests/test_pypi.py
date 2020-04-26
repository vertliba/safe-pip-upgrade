from unittest import mock
from unittest.case import TestCase

import requests

from safe_pip_upgrade.requirements import RequirementType, Requirement
from safe_pip_upgrade.pypi import PypiPackage, Packages
from tests.fixtures.pypi_fixtures import PYPI_ANSWER


class PypiPackageTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        with mock.patch('safe_pip_upgrade.pypi.requests.get', ) as req:
            req.return_value.status_code = requests.codes.ok
            req.return_value.text = PYPI_ANSWER
            cls.package = PypiPackage('ppci')

    def test_get_latest_version(self):
        version = self.package.last_version

        self.assertEqual('0.5.7', version)

    def test_next_version(self):
        version = self.package.next_version('0.5.1')

        self.assertEqual('0.5.2', version)

    def test_get_middle_version_next_versions(self):
        version = self.package.get_middle_version('0.5.5', '0.5.6')
        self.assertFalse(version)

    def test_get_middle_version(self):
        version = self.package.get_middle_version('0.5', '0.5.5')
        self.assertEqual('0.5.2', version)

    def test_get_middle_version_from_last(self):
        version = self.package.get_middle_version(self.package.last_version)
        self.assertFalse(version)


class PackagesTestCase(TestCase):

    @mock.patch('safe_pip_upgrade.pypi.PypiPackage._get_versions', mock.Mock())
    def test_packages(self):
        packages = Packages()

        # test package adding
        package = packages.get_package('django')
        self.assertEqual('django', package.name)

        # test other package adding
        other_package = packages.get_package('djangorestframework')
        self.assertEqual('djangorestframework', other_package.name)

        # test trying to add package existed return doesn't create new object
        same_package = packages.get_package('django')
        self.assertIs(package, same_package)


@mock.patch('safe_pip_upgrade.pypi.Packages.get_package', mock.Mock())
class RequirementTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        with mock.patch('safe_pip_upgrade.pypi.requests.get', ) as req:
            req.return_value.status_code = requests.codes.ok
            req.return_value.text = PYPI_ANSWER
            cls.package = PypiPackage('ppci')

    def test_split_line(self):
        TEST_EXAMPLES = {
            'ppci~=2.1.1 # the latest working version': (
                'ppci~=2.1.1', 'the latest working version'),
            'ppci>0.3.0,<0.4.0': (
                'ppci>0.3.0,<0.4.0', ''),
        }
        req = Requirement('ppci')
        for line, params in TEST_EXAMPLES.items():
            result = req.split_line(line)
            with self.subTest(line):
                self.assertEqual(params, result)

    def test_recognize_comment(self):
        TEST_EXAMPLES = {
            '': (
                RequirementType.LATEST_VERSION, None),
            'the latest working version': (
                RequirementType.FINAL_LATEST_VERSION, None),
            'error on the version 2.1.1': (
                RequirementType.NOT_LATEST_VERSION, '2.1.1'),
        }
        req = Requirement('ppci')
        for line, params in TEST_EXAMPLES.items():
            result = req.recognize_comment(line)
            with self.subTest(line):
                self.assertEqual(params[0], req.type)
                self.assertEqual(params[1], req.error_version)

    def test_recognize_package_and_version(self):
        TEST_EXAMPLES = {
            'ppci': (
                'ppci', None),
            'ppci~=2.1.1': (
                'ppci', '2.1.1'),
            'ppci>0.3.0,<0.4.0': (
                'ppci', '0.3.0'),
        }
        req = Requirement('ppci')
        for line, params in TEST_EXAMPLES.items():
            result = req.recognize_package_and_version(line)
            with self.subTest(line):
                self.assertEqual(params[0], req.name, 'name')
                self.assertEqual(params[1], req.version, 'version')

    def test_recognize_all(self):
        TEST_EXAMPLES = {
            'ppci==2.1.1': (
                'ppci', '2.1.1', RequirementType.LATEST_VERSION, None),
            'ppci~=2.1.1 # the latest working version': (
                'ppci', '2.1.1', RequirementType.FINAL_LATEST_VERSION, None),
            'ppci>=0.3.0,<0.4.0 # error on the version 2.1.1': (
                'ppci', '0.3.0', RequirementType.NOT_LATEST_VERSION, '2.1.1'),
            'ppci>0.3.0,<0.4.0': (
                'ppci', '0.3.0', RequirementType.LATEST_VERSION, None),
            'ppci>=4.0.7,<4.1.0': (
                'ppci', '4.0.7', RequirementType.LATEST_VERSION, None),
        }
        for line, params in TEST_EXAMPLES.items():
            with self.subTest(line):
                req = Requirement(line)
                self.assertEqual(params[0], req.name, 'name')
                self.assertEqual(params[1], req.version, 'version')
                self.assertEqual(params[2], req.type, 'type')
                self.assertEqual(params[3], req.error_version, 'err version')

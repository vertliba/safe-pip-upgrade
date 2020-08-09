from unittest import mock
from unittest.case import TestCase

import requests

from safe_pip_upgrade import pypi
from safe_pip_upgrade.pypi import PypiPackage, PypiPackages, pypi_packages
from safe_pip_upgrade.core.packages import RequirementType, Requirement
from .fixtures.pypi_fixtures import PYPI_ANSWER


class PypiPackageTestCase(TestCase):
    """ Pypi parser test case. """

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

    @mock.patch('safe_pip_upgrade.pypi.PypiPackage._get_versions')
    def test_packages(self, get_versions):
        packages = PypiPackages()

        # get package
        package = packages.get_package('django')
        # get other package
        other_package = packages.get_package('djangorestframework')

        # the package names is correct
        self.assertEqual('django', package.name)
        self.assertEqual('djangorestframework', other_package.name)

        # trying to add package existed return doesn't create new object
        # and doesn't get versions from pypi again
        get_versions.reset_mock()
        same_package = packages.get_package('django')
        self.assertIs(package, same_package)
        get_versions.assert_not_called()


class RequirementTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        with mock.patch('requests.get') as req:
            req.return_value.status_code = requests.codes.ok
            req.return_value.text = PYPI_ANSWER
            cls.package = pypi_packages.get_package('ppci')

    def test_split_line(self):
        test_examples = {
            'ppci~=2.1.1 # the latest working version': (
                'ppci~=2.1.1', 'the latest working version'),
            'ppci>0.3.0,<0.4.0': (
                'ppci>0.3.0,<0.4.0', ''),
        }
        req = Requirement('ppci')
        for line, params in test_examples.items():
            result = req.split_line(line)
            with self.subTest(line):
                self.assertEqual(params, result)

    def test_recognize_comment(self):
        test_examples = {
            '': (
                RequirementType.LATEST_VERSION, None),
            'the latest working version': (
                RequirementType.FINAL_LATEST_VERSION, None),
            'error on the version 2.1.1': (
                RequirementType.NOT_LATEST_VERSION, '2.1.1'),
        }
        req = Requirement('ppci')
        for line, params in test_examples.items():
            req.recognize_comment(line)
            with self.subTest(line):
                self.assertEqual(params[0], req.type)
                self.assertEqual(params[1], req.error_version)

    def test_recognize_package_and_version(self):
        test_examples = {
            # if requirements.txt doesn't specify version - use
            # the latest one
            'ppci': ('ppci', '0.5.7'),
            'ppci~=2.1.1': ('ppci', '2.1.1'),
            'ppci>0.3.0,<0.4.0': ('ppci', '0.3.0'),
        }
        req = Requirement('ppci')
        for line, params in test_examples.items():
            req.recognize_package_and_version(line)
            with self.subTest(line):
                self.assertEqual(params[0], req.name, 'name')
                self.assertEqual(params[1], req.version, 'version')

    def test_recognize_all(self):
        test_examples = {
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
        for line, params in test_examples.items():
            with self.subTest(line):
                req = Requirement(line)
                self.assertEqual(params[0], req.name, 'name')
                self.assertEqual(params[1], req.version, 'version')
                self.assertEqual(params[2], req.type, 'type')
                self.assertEqual(params[3], req.error_version, 'err version')

import copy
import json
import re
from unittest.case import TestCase
from unittest.mock import MagicMock, patch, _patch, Mock

import requests

from safe_pip_upgrade.pypi import URL_PATTERN
from safe_pip_upgrade.upgrade import Upgrade
from tests.fixtures.pypi_fixtures import PYPI_ANSWER

try:
    from packaging.version import parse
except ImportError:
    # noinspection PyProtectedMember
    from pip._vendor.packaging.version import parse


class PypiPatcherMixin(TestCase):
    """ Mixin for patch request to Pypi to fixtures. """
    req_patcher: _patch

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.req_patcher = patch('safe_pip_upgrade.pypi.requests.get', )
        get = cls.req_patcher.start()
        get.return_value.status_code = requests.codes.ok
        get.return_value.text = PYPI_ANSWER

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.req_patcher.stop()


class TryUpgradeRequirementsTestCase(PypiPatcherMixin):

    def test_try_upgrade_requirements_failure(self):
        """ There is no working upgrades. """
        client = MagicMock()
        client.run_tests.return_value = False
        req_file = CopyArgsMagicMock()

        upgrade = Upgrade(client, req_file)
        upgrade.req_lines = ['ppci~=0.5\n']

        upgrade.try_upgrade_requirement(0)

        # version 0.5 was fixed
        self.assertEqual('ppci==0.5 # the latest working version\n',
                         upgrade.req_lines[0])
        # the last was an attempt to upgrade to next version
        last_call = req_file.write_lines.call_args_list[-1].args[0][0]
        self.assertTrue(last_call.startswith('ppci==0.5.1'))
        # the first was an attempt to upgrade to the latest version
        first_call = req_file.write_lines.call_args_list[0].args[0][0]
        self.assertTrue(first_call.startswith('ppci==0.5.7'))
        # there were more than 2 attempts
        call_number = len(req_file.write_lines.call_args_list)
        self.assertGreater(call_number, 2)

    def test_try_upgrade_requirements_success(self):
        """ All available upgrades work. """
        client = MagicMock()
        client.run_tests.return_value = True
        req_file = CopyArgsMagicMock()

        upgrade = Upgrade(client, req_file)
        upgrade.req_lines = ['ppci~=0.5\n']

        upgrade.try_upgrade_requirement(0)

        # the version was upgraded to 0.5
        self.assertEqual('ppci==0.5.7\n', upgrade.req_lines[0])
        # there were one attempt
        call_number = len(req_file.write_lines.call_args_list)
        self.assertEqual(call_number, 1)

    def test_try_upgrade_from_latest_version(self):
        """ The latest version is already installed. """
        client = MagicMock()
        client.run_tests.return_value = False
        req_file = CopyArgsMagicMock()

        upgrade = Upgrade(client, req_file)
        upgrade.req_lines = ['ppci<=0.5.7\n']

        upgrade.try_upgrade_requirement(0)

        # version 0.5 is a latest
        self.assertEqual('ppci==0.5.7\n', upgrade.req_lines[0])

        # there were no attempts to upgrade
        call_number = len(req_file.write_lines.call_args_list)
        self.assertEqual(0, call_number)


class StartUpgradeTestCase(TestCase):
    # list format: {package_name: ((releases), max_working)}
    FAKE_RELEASES = {
        'p-1': (('0.0.1', '0.0.2', '0.0.3', '0.0.4'), '0.0.3'),
        'p-2': (('0.0.1', '0.0.2', '0.0.3', '0.0.4'), '0.0.4'),
        'p-3': (('0.0.1', '0.0.2', '0.0.3', '0.0.4'), '0.0.3'),
        'p-4': (('0.0.1', '0.0.2', '0.0.3', '0.0.4'), '0.0.4'),
    }

    ORIGINAL_REQUIREMENTS = '''
        p-1==0.0.2
        p-2==0.0.2
        p-3==0.0.1 # error on the version 0.0.3  
        p-4==0.0.4
    '''
    EXPECTED_REQUIREMENTS = '''
p-1==0.0.3 # the latest working version
p-2==0.0.4
p-3==0.0.2 # the latest working version
p-4==0.0.4
    '''

    get_patcher: _patch

    @classmethod
    def fake_get(cls, url):
        template = URL_PATTERN.replace('{package}', '(.*)')
        package = re.search(template, url).group(1)
        response = json.dumps(
        {'releases': {r: [] for r in cls.FAKE_RELEASES[package][0]}})
        result = Mock()
        result.status_code = requests.codes.ok
        result.text = response
        return result

    def fake_test(self):
        lines = self.req_file.write_lines.call_args[0][0]
        for line in lines:
            result = re.search('(p-\d)==(\d\.\d\.\d)', line)
            if not result:
                continue
            package = result[1]
            version = parse(result[2])
            max_version = parse(self.FAKE_RELEASES[package][1])
            if version>max_version:
                return False
        return True

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.get_patcher = patch('safe_pip_upgrade.pypi.requests.get',
                                cls.fake_get)
        get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.get_patcher.stop()

    # @patch('safe_pip_upgrade.requirements.Requirement')
    def test_start_upgrade(self):
        client = MagicMock()
        client.run_tests = self.fake_test
        self.req_file = CopyArgsMagicMock()

        upgrade = Upgrade(client, self.req_file)
        upgrade.req_lines = self.str_to_list(self.ORIGINAL_REQUIREMENTS)
        upgrade.start_upgrade()

        last_call = self.req_file.write_lines.call_args_list[-1].args[0]
        exp = self.str_to_list(self.EXPECTED_REQUIREMENTS)
        self.assertEqual(exp, last_call)

        client = MagicMock()

    def str_to_list(self, string):
        return [s+'\n' for s in string.split('\n')]

class CopyArgsMagicMock(MagicMock):
    """ Overrides MagicMock to store copies of arguments passed into calls. """

    def __call__(self, *args, **kwargs):
        args = copy.deepcopy(args)
        kwargs = copy.deepcopy(kwargs)
        return super().__call__(*args, **kwargs)

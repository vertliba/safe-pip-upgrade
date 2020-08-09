from typing import Tuple
from unittest import TestCase

import pkg_resources

MAX_WORKING_VERSION = {
    'ppci': (0, 5, 7),
    'rules': (2, 1),
}


class FakeTestCase(TestCase):
    """ Fail if the version installed is more than in MAX_WORKING_VERSION. """

    def test_version(self):
        for package, max_version in MAX_WORKING_VERSION.items():
            installed_version = get_package_installed_version(package)

            self.assertLessEqual(installed_version, max_version)


def get_package_installed_version(package_name: str) -> Tuple[int]:
    """ Return installed package version as tuple. """
    return pkg_resources.get_distribution(package_name).parsed_version.release

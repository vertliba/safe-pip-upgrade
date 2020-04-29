import json
import logging
import pprint

import requests
from requests import RequestException

logger = logging.getLogger(__name__)

try:
    from packaging.version import parse
except ImportError:
    # noinspection PyProtectedMember,PyCompatibility
    from pip._vendor.packaging.version import parse


class Packages:
    """ Pypi packages cache. """

    def __init__(self):
        self.packages = {}

    def get_package(self, name):
        if name in self.packages:
            return self.packages[name]
        else:
            # setdefault evaluates default value even if the key exists
            return self.packages.setdefault(name, PypiPackage(name))


packages = Packages()


class PypiPackage:
    """ Pypi packages parser. """
    URL_PATTERN = 'https://pypi.python.org/pypi/{package}/json'

    def __init__(self, name):
        self.name = name
        self._get_versions()

    @property
    def last_version(self):
        return str(self.releases[-1])

    def next_version(self, version):
        version = parse(version)
        if version == self.last_version:
            return None
        return str(self.releases[self.releases.index(version) + 1])

    def get_middle_version(self, gt, lt=None):
        """ get version between """
        gt_ind = self.releases.index(parse(gt))
        if lt:
            lt_ind = self.releases.index(parse(lt))
        else:
            lt_ind = len(self.releases)

        if lt_ind - gt_ind <= 1:
            # there are no versions between
            return None

        middle_pos = (gt_ind + lt_ind) // 2
        return str(self.releases[middle_pos])

    def _get_versions(self):
        """Return version of package on pypi.python.org using json."""
        try:
            req = requests.get(self.URL_PATTERN.format(package=self.name))
            req.raise_for_status()
        except RequestException as e:
            logger.exception('Can not get access to pypi API: %s',
                             pprint.saferepr(e))
            raise ConnectionError(e)

        j = json.loads(req.text)
        raw_releases = j.get('releases', [])
        all_releases = sorted([parse(r) for r in raw_releases])
        self.releases = [r for r in all_releases if not r.is_prerelease]

import json

import requests
from packaging.version import parse
PYPI_API_URL_PATTERN = 'https://pypi.python.org/pypi/{package}/json'


def get_package_last_version(package_name: str) -> str:

    req = requests.get(PYPI_API_URL_PATTERN.format(package=package_name))
    req.raise_for_status()
    j = json.loads(req.text)
    raw_releases = j.get('releases', [])
    all_releases = sorted([parse(r) for r in raw_releases
                           if not parse(r).is_prerelease])
    return all_releases[-1].base_version

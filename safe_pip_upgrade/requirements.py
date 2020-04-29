import re
from enum import Enum, auto

from safe_pip_upgrade import SafeUpgradeException
from safe_pip_upgrade.pypi import packages


# Comments for packages that having been analyzed.
# "# the latest working version" - there are newer versions, but they don`t
# work
# "# error on the version x.x.x" - version x.x.x calls error, but there are
# versions between current and x.x.x to test"
# if the latest version is already installed the comment is not added


class RequirementType(Enum):
    LATEST_VERSION = auto()  # the latest version
    FINAL_LATEST_VERSION = auto()  # the latest version that works
    NOT_LATEST_VERSION = auto()  # there may be next versions to test


TEMPLATES = {
    RequirementType.FINAL_LATEST_VERSION: r'the latest working version',
    RequirementType.NOT_LATEST_VERSION: r'error on the version (\S*)',
}


class RecognizeException(SafeUpgradeException):
    pass


class Requirement:
    """ Package in requirements. """
    type = None
    error_version = None
    package = None
    version = None
    previous_version = None
    name: str

    def __init__(self, line):
        self.recognize(line)

    def recognize(self, line):
        # type: (str) -> None
        """ Parse requirement line. """
        package, comment = self.split_line(line)

        if not package:
            raise RecognizeException('can\'t find package name')

        self.recognize_package_and_version(package)

        # recognise comment
        self.recognize_comment(comment)

    def increase_version(self):
        # type: (...) -> bool
        """ Try find newer version for test.

        if next version has already been failed, stop further upgrades.
        """
        if self.type == RequirementType.FINAL_LATEST_VERSION:
            return False

        self.package = packages.get_package(self.name)

        # get the latest version that may work
        if self.type == RequirementType.NOT_LATEST_VERSION:
            # get version between the current and last
            version_to_test = self.package.get_middle_version(
                self.version, self.error_version)
            if not version_to_test:
                self.type = RequirementType.FINAL_LATEST_VERSION
                return False
        else:
            version_to_test = self.package.last_version
            if version_to_test == self.version:
                # The latest version is already installed
                return False

        self.previous_version = self.version
        self.version = version_to_test
        return True

    def get_line(self):
        # type: () -> str
        """ get requirements file line."""
        line = "{}=={}".format(self.name, self.version)
        if self.type != RequirementType.LATEST_VERSION:
            line += ' # ' + TEMPLATES[self.type]
            if self.type == RequirementType.NOT_LATEST_VERSION:
                line = line.replace(r'(\S*)', self.error_version)

        return line + '\n'

    def fix_error_version(self):
        self.type = RequirementType.NOT_LATEST_VERSION
        self.error_version = self.version
        self.version = self.previous_version

    def recognize_comment(self, comment):
        # if there is no comment the latest version was installed
        if not comment:
            self.type = RequirementType.LATEST_VERSION
            return

        for requirement_type, template in TEMPLATES.items():
            search = re.search(template, comment)
            if search:
                self.type = requirement_type
                if search.groups():
                    self.error_version = search.group(1)
                break
        else:
            raise RecognizeException('can\'t recognize comment')

    def recognize_package_and_version(self, package):
        match = re.split(r'[>=<~\s,]+', package)
        self.name = match[0]
        if len(match) > 1:
            self.version = match[1]

    def split_line(self, line):
        # type: (str) -> tuple
        """ Split line on text and comment """

        parts = [s.strip() for s in line.split('#', 1)]
        package = parts[0]
        comment = parts[1] if len(parts) >= 2 else ''

        return package, comment

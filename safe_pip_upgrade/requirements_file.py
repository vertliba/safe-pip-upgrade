import logging
import os
from shutil import copy

logger = logging.getLogger(__name__)


class RequirementsLocal:
    """ Local requirements file manager. """

    def __init__(self, file_name):
        self.full_name = file_name
        self.path, tail = os.path.split(self.full_name)
        self.name, self.extension = tail.split('.')

    def read_lines(self):
        """ Read requirements file. """
        logger.debug(f'read requirements')
        with open(self.full_name, newline='\n', encoding='utf-8') as file:
            return file.readlines()

    def write_lines(self, requirements):
        """ Write requirements file. """
        # type (list) -> None
        logger.debug(f'write requirements')
        with open(self.full_name, 'w', newline='\n', encoding='utf-8') as f:
            f.writelines(requirements)

    def copy_file(self, from_suffix, to_suffix):
        """ Copy requirements file with an other suffix. """
        copy(self.file_with_suffix(from_suffix),
             self.file_with_suffix(to_suffix))

    def file_with_suffix(self, suffix):
        """ Give file name with a suffix. """
        return os.path.join(self.path,
                            self.name + suffix + '.' + self.extension)

    def make_backup(self):
        """ Make backup. """
        i = 1
        while os.path.exists(self.file_with_suffix(f'_backup_{i}')):
            i += 1
        logger.debug(f'make backup')
        self.copy_file('', f'_backup_{i}')

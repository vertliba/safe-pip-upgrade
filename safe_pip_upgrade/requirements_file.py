import logging
import os
from shutil import copy

logger = logging.getLogger(__name__)

class RequirementsLocal:
    def __init__(self, file_name):
        self.full_name = file_name
        self.path, tail = os.path.split(self.full_name)
        self.name, self.extension = tail.split('.')

    def read_lines(self):
        logger.debug(f'read requirements')
        with open(self.full_name) as file:
            return file.readlines()

    def write_lines(self, requirements):
        # type (list) -> None
        logger.debug(f'write requirements')
        with open(self.full_name, 'w') as f:
            f.writelines(requirements)
            # f.write('\n'.join(requirements))


    def copy_file(self, from_suffix, to_suffix):
        copy(self.file_with_suffix(from_suffix),
             self.file_with_suffix(to_suffix))

    def file_with_suffix(self, suffix):
        return os.path.join(self.path,
                            self.name + suffix + '.' + self.extension)

    def make_backup(self):
        i=1
        while os.path.exists(self.file_with_suffix(f'_backup_{i}')):
            i += 1

        logger.debug(f'make backup')
        self.copy_file('', f'_backup_{i}')
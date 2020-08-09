import logging
import subprocess

from safe_pip_upgrade.core.upgrade import RunnerException

logger = logging.getLogger(__name__)


class ComposeRunner:
    requirements_file_name = 'requirements.txt'

    def __init__(self, config):
        self.config = config
        self.remote_work_dir = config.COMPOSE_WORK_DIR
        self.project_folder = config.COMPOSE_PROJECT_FOLDER
        self.service_name = config.COMPOSE_SERVICE_NAME
        self.requirements_file_name = config.COMPOSE_REQUIREMENTS_FILE.replace(
            r'\\', '/')
        self.daemon_name = self.service_name + '_upgrade'
        self._docker_up()

    def run_tests(self):
        self._check_or_run_daemon()
        params = (f'exec {self.daemon_name} pip install -r '
                  f'{self.requirements_file_name}').split(' ')
        code = self._run_docker(*params).returncode

        logger.info(f'docker: install requirements, return code {code}')
        if code:
            logger.error('docker: failed to install requirements.')
            return False

        self._check_or_run_daemon()
        logger.info(f'docker: start tests')
        code = self._run_docker(
            'exec', self.daemon_name, *self.config.TEST_START_COMMAND.split()
        ).returncode
        logger.info(f'docker: tests done, return code {code}')
        return code == 0

    def _docker_up(self):
        self._delete_test_container()
        params = ['-d', '--name', self.daemon_name]
        if self.remote_work_dir:
            params.extend(['-w', self.remote_work_dir])
        code = self._run_compose(
            'run',
            params,
            args=['sleep', str(60 * 60 * 10)]).returncode
        logger.info(f'docker: up, return code {code}')
        return code == 0

    def _delete_test_container(self):
        self._run_docker('rm', self.daemon_name, '-f')

    def _check_daemon(self):
        options = ['-f', f'name={self.daemon_name}']
        result = self._run_docker('ps', *options, capture_output=True)
        return self.daemon_name.encode() in result.stdout

    def _check_or_run_daemon(self):
        if not self._check_daemon():
            logger.info('docker: check container: stopped, restart.')
            self._docker_up()
            if not self._check_daemon():
                logger.error('docker: container is stopped after restart!')
                raise DockerException()

    def _run_compose(self, command, options=(), args=()):
        run_params = ['docker-compose']
        run_params.append(command)
        run_params.extend(options)
        run_params.append(self.service_name)
        run_params.extend(args)
        logger.info(f'>>{" ".join(run_params)}')
        sp = subprocess.run(run_params, check=True, timeout=20,
                            cwd=self.project_folder)
        return sp

    def _run_docker(self, *options, capture_output=False):
        run_params = ['docker', *options]
        logger.info(f'>>{" ".join(run_params)}')
        daemon = subprocess.run(run_params, timeout=60 * 10,
                                capture_output=capture_output)
        return daemon


class DockerException(RunnerException):
    pass

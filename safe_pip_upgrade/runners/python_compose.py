import logging
import subprocess

logger = logging.getLogger(__name__)


class DockerException(Exception):
    pass


class ComposeRunner:
    requirements_file_name = 'requirements.txt'

    def __init__(self, project_folder: str, service_name: str,
                 requirements_file_name: str,
                 remote_work_dir: str):
        self.remote_work_dir = remote_work_dir
        self.project_folder = project_folder
        self.service_name = service_name
        self.requirements_file_name = requirements_file_name.replace('\\', '/')
        self.daemon_name = service_name + '_upgrade'

    def run_tests(self):
        self.check_or_run_daemon()
        params = (f'exec {self.daemon_name} pip install -r '
                  f'{self.requirements_file_name}').split(' ')
        code = self.run_docker(*params).returncode

        logger.info(f'docker: install requirements, return code {code}')
        if code:
            logger.error('docker: failed to install requirements.')
            return False

        self.check_or_run_daemon()
        logger.info(f'docker: start tests')
        code = self.run_docker(
            'exec', self.daemon_name, 'python', 'manage.py', 'test',
            '--failfast', '--keepdb', '--no-input'
        ).returncode
        logger.info(f'docker: tests done, return code {code}')
        return code == 0

    def up(self):
        self.run_docker('rm', self.daemon_name, '-f')
        params = ['-d', '--name', self.daemon_name]
        if self.remote_work_dir:
            params.extend(['-w', self.remote_work_dir])
        code = self.run_compose(
            'run',
            params,
            args=['sleep', str(60 * 60 * 10)]).returncode
        logger.info(f'docker: up, return code {code}')
        return code == 0

    def check_daemon(self):
        options = ['-f', f'name={self.daemon_name}']
        result = self.run_docker('ps', *options, capture_output=True)
        return self.daemon_name.encode() in result.stdout

    def check_or_run_daemon(self):
        if not self.check_daemon():
            logger.info('docker: check container: stopped, restart.')
            self.up()
            if not self.check_daemon():
                logger.error('docker: container is stopped after restart!')
                raise DockerException('')

    def run_compose(self, command, options=(), args=()):
        run_params = ['docker-compose']
        run_params.extend(['--project-directory', self.project_folder])
        run_params.append(command)
        run_params.extend(options)
        run_params.append(self.service_name)
        run_params.extend(args)
        logger.info(f'>>{" ".join(run_params)}')
        sp = subprocess.run(run_params, check=True, timeout=20,
                            cwd=self.project_folder)
        return sp

    def run_docker(self, *options, capture_output=False):
        run_params = ['docker', *options]
        logger.info(f'>>{" ".join(run_params)}')
        daemon = subprocess.run(run_params, timeout=60 * 10,
                                capture_output=capture_output)
        return daemon

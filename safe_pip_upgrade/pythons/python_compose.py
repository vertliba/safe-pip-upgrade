import os
import subprocess
import logging

logger = logging.getLogger(__name__)


class DockerException(Exception):
    pass


class ComposeRunner:
    remote_work_dir = '/app'  # remote working directory
    requirements_file_name = 'requirements.txt'

    def __init__(self, project_folder, service_name):
        self.project_folder = project_folder
        self.project_name = os.path.split(project_folder)[-1]
        self.service_name = service_name
        self.daemon_name = self.project_name + '_upgrade'

    def run_tests(self):
        self.check_or_run_daemon()
        logger.info(f'docker: install requirements start')
        code = self.run_docker(
            'exec', self.daemon_name, 'pip', 'install',
            '-r', self.requirements_file_name
        ).returncode

        logger.info(f'docker: install requirements, return code {code}')
        if code:
            logger.error('docker: failed to install requirements.')
            raise DockerException('failed to install requirements')

        self.check_or_run_daemon()
        logger.info(f'docker: start tests')
        code = self.run_docker(
            'exec', self.daemon_name, 'python', 'manage.py', 'test',
            '--keepdb', '--no-input'
        ).returncode
        logger.info(f'docker: tests done, return code {code}')
        return code == 0

    def up(self):
        self.run_docker('rm', self.daemon_name, '-f')
        code = self.run_compose(
            'run',
            ['-d', '--name', self.daemon_name, '-w', self.remote_work_dir],
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
        sp = subprocess.run(run_params, check=True, timeout=20,
                            cwd=self.project_folder)
        return sp

    def run_docker(self, *options, capture_output=False):
        run_params = ['docker', *options]
        daemon = subprocess.run(run_params, timeout=60 * 10,
                                capture_output=capture_output)
        return daemon

from mivp_agent.deploy import Task, Environment
from mivp_agent.deploy.deployment import Deployment
from mivp_agent.deploy.util.docker import get_or_build

import os
import docker
from argparse import ArgumentParser, Namespace

DEPLOYABLE_DIRECTORY = "~/deployable"


class DockerDeployment(Deployment):
    '''
    The `DockerDeployment`
    '''
    def __init__(self) -> None:
        self.client = docker.from_env()
    
    def configure_parser(self, parser: ArgumentParser):
        return super().configure_parser(parser)
  
    def _create_task_container(self, task: Task):
        image = get_or_build(task.get_image())

        abs_directory = os.path.abspath(task.get_directory())

        command = "export AGENT_SERVER_HOST 0.0.0.0"
        command += f"&& cd {DEPLOYABLE_DIRECTORY}"
        command += f"&& {task.get_command()}"
        
        container = self.client.containers.create(
            image,
            command,
            volumes=f'{abs_directory}:~/deployable'
        )

        ip = container.attrs['NetworkSettings']['IPAddress']

        return container, ip
    
    def _create_env_container(self, env: Environment, task_ip):
        image = get_or_build(env.get_image())

        abs_directory = os.path.abspath(env.get_directory())

        command = f"export AGENT_SERVER_HOST {task_ip}"
        command += f"&& cd {DEPLOYABLE_DIRECTORY}"
        command += f"&& {env.get_command()}"
    
        return self.client.containers.create(
            image,
            command,
            volumes=f'{abs_directory}:~/deployable'
        )

    def setup(self, args: Namespace, task: Task, environment: Environment):
        task_container, task_ip = self._create_task_container(task)
        env_container = self._create_env_container(environment, task_ip)

        # Start environment container detached
        env_container.start(detach=True)
        
        # Start task container and block
        task_container.start()

    def teardown(self, args: Namespace, task: Task, environment: Environment):
        pass
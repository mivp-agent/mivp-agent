from mivp_agent.deploy import Task, Environment
from mivp_agent.deploy.deployment import Deployment
from mivp_agent.deploy.util.docker import get_or_build
from mivp_agent.util.log_presenter import LogPresenter

import os
import time
from queue import Queue, Empty
from threading import Thread
import docker
from docker.client import DockerClient
from argparse import ArgumentParser, Namespace

DEPLOYABLE_DIRECTORY = "/data/deployable"


class DockerDeployment(Deployment):
    '''
    The `DockerDeployment`
    '''
    def __init__(self) -> None:
        self.client: DockerClient = docker.from_env()
        self._presenter = LogPresenter()
        self._log_queue = Queue()
        self._shutdown_signal = False

    def configure_parser(self, parser: ArgumentParser):
        return super().configure_parser(parser)

    def _get_ip(self, container) -> str:
        '''
        This method is required because it seems that the attributes are not updated after `container.start()` calls are made.
        '''
        updated_container = self.client.containers.get(container.id)
        
        ip = updated_container.attrs['NetworkSettings']['IPAddress']
        if ip == '':
            raise RuntimeError(f'Failed to get IP from container {container.id}')

    def _create_task_container(self, task: Task):
        image = get_or_build(task.get_image())

        abs_directory = os.path.abspath(task.get_directory())

        command = f"sleep 5 && cd {DEPLOYABLE_DIRECTORY}"
        command += f" && {task.get_command()}"

        container = self.client.containers.create(
            image,
            f"sh -c '{command}'",
            environment={
                'AGENT_SERVER_HOST': '0.0.0.0'
            },
            volumes=[f'{abs_directory}:{DEPLOYABLE_DIRECTORY}',],
            tty=True
        )

        return container
    
    def _create_env_container(self, env: Environment, task_ip):
        image = get_or_build(env.get_image())

        abs_directory = os.path.abspath(env.get_directory())

        command = f"sleep 5 && cd {DEPLOYABLE_DIRECTORY}"
        command += f"&& {env.get_command()}"

        return self.client.containers.create(
            image,
            f"sh -c '{command}'",
            environment={
                'AGENT_SERVER_HOST': task_ip
            },
            volumes=[f'{abs_directory}:{DEPLOYABLE_DIRECTORY}',],
            tty=True
        )
    
    def _log_consumer(self, name, container):
        '''
        This function is used within a thread to provide a non-blocking way to get the `next(generator)` value. Messages are put in the `_log_queue` to be read by the main thread.
        '''
        generator = container.attach(logs=True, stream=True)
        while not self._shutdown_signal:
            try:
                text = next(generator)
                self._log_queue.put((name, text.decode()))
            except StopIteration:
                self._log_queue.put((name, '!! End of stream received !!\n'))
                break

    def setup(self, args: Namespace, task: Task, environment: Environment):
        task_container = self._create_task_container(task)
        task_container.start()
        task_ip = self._get_ip(task_container)

        env_container = self._create_env_container(environment, task_ip)
        env_container.start()

        task_log_consumer = Thread(
            target=self._log_consumer,
            args=(
                'task',
                task_container
            ),
            daemon=True
        )
        env_log_consumer = Thread(
            target=self._log_consumer,
            args=(
                'env',
                env_container,
            ),
            daemon=True
        )
        task_log_consumer.start()
        env_log_consumer.start()

        threads_alive = lambda: task_log_consumer.is_alive() or env_log_consumer.is_alive()

        with self._presenter as p:
            while threads_alive() or not self._log_queue.empty():
                try:
                    source, text = self._log_queue.get(timeout=0.1)
                    p.add(source, text)
                except Empty:
                    time.sleep(0.1)

    def teardown(self, args: Namespace, task: Task, environment: Environment):
        pass
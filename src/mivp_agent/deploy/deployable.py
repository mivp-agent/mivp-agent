from abc import ABC, abstractmethod


class Deployable(ABC):
    '''
    The `Deployable` construct provides an common interface used by subclasses of `Deployment`. It has two primary purposes.
    
    1. Provide the details required to start a docker container
        - `get_image(...)`
        - `get_command(...)`
    2. Provide path to a directory of resource to bring with the docker container. The method of "bringing" (volume mounting, scp, etc..) is defined by the `Deployment` subclasses.
        - `get_directory(...)`
    
    The __init__(self, **kwargs) method may be overridden without any calls to this super class. The tooling provided by `agnt deploy <deploy_type>`.
    '''

    def __init__(self, **kwargs) -> None:
        '''
        This method is just a stub which can be overridden by implementors without any need to call this super method.

        The `agnt deploy <deploy_type>` will drop and key value pairs provided by `--env-args` or `--task-args` into the `Environment` and `Task` init methods respectively.
        '''
        pass

    @abstractmethod
    def get_image(self) -> str:
        '''
        This method should point to one of two things.

        1. A image that is maintained and managed by mivp-agent
        2. A custom pre built docker image.

        You may provide this in the format of `image` or `image:tag` if no provided `image` will be translated to `image:latest`
        '''
        pass

    @abstractmethod
    def get_directory(self) -> str:
        '''
        This method should provide the directory which should be copied onto the deployment and which all user-provided commands will be run in by the deployment.
        '''
        pass

    @abstractmethod
    def get_command(self) -> str:
        '''
        This method should provide the shell command to be used when the container is started. It should be run inside the deployments copy of the directory provided by `get_directory()`
        '''
        pass
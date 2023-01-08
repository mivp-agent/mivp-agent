import os
import json
import inspect
from abc import abstractmethod

from mivp_agent.deploy.deployable import Deployable
from mivp_agent.deploy import Environment


class Task(Deployable):
    '''
    `Tasks` are the primary part of a deployment. While different deployments may choose to scale up as many `Environments` as it can handle, there should only be one `Task`.

    The main function of this type of executable is to run the `ModelBridgeServer` class and any associated `Agent`s, `Model`s, and `Driver`s.
    '''

    def __new__(cls, *args, **kwargs):
        '''
        This method will apply set the `_file_path` attribute to be equal to the `file_path` key word if provided.
        
        This is used by the `agnt deploy` script because there are confusing issues with the `inspect.getfile(self.__class__)` call. Namely, it complains about the dynamically imported class being a "built-in". As the CLI already has the file path, we can set it here without requiring the subclasses to call super().__init__(blah).
        '''
        instance = super(Task, cls).__new__(cls)
        if 'file_path' in kwargs:
            instance._file_path = kwargs['file_path']
            # Don't need to pass this to `agnt run`
            del kwargs['file_path']
        else:
            instance._file_path = None
        
        if 'config' in kwargs:
            instance._config = kwargs['config']
        else:
            instance._config = {}

        # Store kwargs for `get_command()`
        instance.kwargs = kwargs

        return instance
    
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_environment(self) -> Environment:
        '''
        This method should provide a constructed `Environment` deployable that is associated with this task.

        Configuration of the `Tunable`'s space will be handled immediately after it is returned.
        '''
        pass

    @abstractmethod
    def run(self):
        '''
        This method will be called inside of the deployment.
        '''
        pass

    def _get_subclass_file(self):
        '''
        Can not use __file__ directly as that would return this file not the file of the subclass.
        '''
        # If we have dynamically loaded this class and set _file_path in __new__, use that as the inspect call is currently failing.
        if self._file_path is not None:
            return self._file_path
        
        return inspect.getfile(self.__class__)

    def _args_dumps(self, dict):
        string = None

        for key in dict:
            value = dict[key]
            if string is not None:
                string += f' {key}={value}'
            else:
                string = f'{key}={value}'
        
        return string

    def get_command(self) -> str:
        '''
        This method constructs a command through the use of the `agnt run` helper command. It should be run inside the directory provided by `get_directory(...)` in the deployment.

        **NOTE:** This should not be overridden unless you know what you are doing.
        '''

        file_name = os.path.basename(self._get_subclass_file())
        configs = json.dumps(self._config, separators=(',', ':')) # Make the seperators not include whitespace so the shell can interpret correctly
        configs = configs.replace('"', '\\"') # Add single backslash so the shell does not interpret and remove the quotes will end up with '\"' output after python removes the `\\` and inserts a single `\`.

        command = f'agnt run {file_name} {configs}'

        return command
    
    def get_directory(self) -> str:
        '''
        This method provides the default functionality of `Task` instances. Namely, the deployment will be instructed to include the directory of the file which `Task` is defined in.

        For example:
        my_directory/
            - myfile.py # Implements Task
            - mymodel.py
        
        With this layout `get_directory()` will return `my_directory`. This will be directory which deployments will move the remote location and execute commands within.
        '''
        subclass_file = self._get_subclass_file()
        subclass_dir = os.path.abspath(
            os.path.dirname(subclass_file)
        )
        return subclass_dir

    def get_image(self) -> str:
        '''
        This method can be overridden to provide a custom container image to deploy the task in. By default `mivp-agent-task-base` is provided.

        If you override this method there are two types of images you can provide.

        1. A image that is maintained and managed by mivp-agent
        2. A custom pre built docker image.

        You may provide this in the format of `image` or `image:tag` if no provided `image` will be translated to `image:latest`
        '''

        return 'mivp-agent-task-base'
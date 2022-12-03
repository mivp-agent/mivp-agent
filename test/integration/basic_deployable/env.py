import os
from mivp_agent.deploy import Environment

class ExampleEnvironment(Environment):
    def get_directory(self) -> str:
        '''Most of the time you will want to bring some resources into the docker container, all commands will be run in the path specified by this function.
        
        The following return statement will target the directory which the current file is inside of. That directory will be mounted inside the `/data/deployable` directory.
        '''
        return os.path.abspath(os.path.join(os.path.realpath(__file__), '..'))
    
    def get_command(self) -> str:
        return 'echo "Hello from the environment!" && cat resource.txt'
from mivp_agent.deploy.deployable import Deployable


class Environment(Deployable):
    '''
    The `Environment` is an extremely small wrapper around the `Deployable` construct. It provides the `mivp-agent-env-base` as the default image. If you have a mission which does not require complex utilities & environment this can be used. Otherwise, think about overriding it.

    **NOTE:** Any customer environment must correctly install both the `moos-ivp-agent` and `mivp-agent` packages. You will most likely want to base your image off of MOOS-IvP's official images. Take a look at the `mivp-agent-env-base` docker file for how to do this.
    '''

    def get_image(self) -> str:
        '''
        This method can be overridden to provide a custom container image to deploy the task in. By default `mivp-agent-env-base` is provided.

        If you override this method there are two types of images you can provide.

        1. A image that is maintained and managed by mivp-agent
        2. A custom pre built docker image.

        You may provide this in the format of `image` or `image:tag` if no provided `image` will be translated to `image:latest`
        '''

        return 'mivp-agent-env-base'
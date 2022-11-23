import os, sys
import docker
from halo import Halo

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DOCKERFILES_DIR = os.path.join(CURRENT_DIR, '../dockerfiles')
# Remove .. from path
DOCKERFILES_DIR = os.path.abspath(DOCKERFILES_DIR)

DOCKERFILES = [file for file in os.listdir(DOCKERFILES_DIR)]
DOCKERFILE_NAMES = [name.split('.')[1] for name in DOCKERFILES]


def parse_name(name, default_tag='latest'):
    split = name.split(':')
    if len(split) == 1:
        return name, default_tag
    if len(split) == 2:
        return split[0], split[1]
    raise RuntimeError('Expected format "name" or "name:tag" not found.')


def get_or_build(name):
    client = docker.from_env()
    raw_name, tag = parse_name(name)
    try:
        return client.images.get(f'{raw_name}:{tag}')
    except docker.errors.ImageNotFound:
        if raw_name not in DOCKERFILE_NAMES:
            raise RuntimeError(f'Unable to find either pre-built image, or a dockerfile managed by mivp-agent called "{raw_name}:{tag}". If this is your docker file please make sure to build it')
    return build_image(name)


def build_image(name):
    client = docker.from_env()
    raw_name, tag = parse_name(name)
    dockerfile = f'Dockerfile.{raw_name}'
    full_path = os.path.join(DOCKERFILES_DIR, dockerfile)
    spinner = Halo(text=f'Building {full_path}...', spinner='dots')

    try:
        spinner.start()
        image = client.images.build(
            path=DOCKERFILES_DIR,
            dockerfile=dockerfile,
            tag=f'{raw_name}:{tag}'
        )
        return image
    except docker.errors.BuildError as e:
        print(f'\n\nFailed to build docker image. You can see more detailed output by running `docker build -f {dockerfile} {DOCKERFILES_DIR}` manually', file=sys.stderr)
        raise e
    finally:
        spinner.stop()
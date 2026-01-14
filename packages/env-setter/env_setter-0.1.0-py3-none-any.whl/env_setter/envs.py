"""Get and set environments."""

import logging
import os
import shlex
from pathlib import Path

from env_setter.constants import DEFAULT_ENV_DIRECTORY, ENV_DIRECTORY_OVERRIDE
from env_setter.exceptions import EnvironmentDirectoryIsAFileError, EnvironmentNotFoundError
from env_setter.parser import TOMLParser

logger = logging.getLogger(__name__)


def _get_dir() -> Path:
    """Get the environment files directory.

    We check ENV_DIRECTORY_OVERRIDE environment variable, if set.
    Otherwise, default to DEFAULT_ENV_DIRECTORY
    """
    dir_to_check = os.getenv(ENV_DIRECTORY_OVERRIDE, DEFAULT_ENV_DIRECTORY)
    env_folder = Path(dir_to_check).expanduser()

    # create empty folder if not exists
    env_folder.mkdir(parents=True, exist_ok=True)

    if not env_folder.is_dir():
        raise EnvironmentDirectoryIsAFileError

    return env_folder


def get_parsed_envs() -> dict[str, dict]:
    """Parse available toml files to load an env."""
    env_dir = _get_dir()
    envs = {}

    for item in env_dir.iterdir():
        if item.is_dir():
            logger.warning("Nested directories are not supported. Skipping %s", item)

        envs[item.stem] = TOMLParser.parse(f=item)

    return envs


def set_env(env_name: str) -> str:
    """Set the environment with the given name."""
    envs = get_parsed_envs()

    if env_name not in envs:
        raise EnvironmentNotFoundError(env_name=env_name, available_environments=envs)

    command = ""
    for key, val in envs[env_name].items():
        command += f"export {key}={shlex.quote(val)}\n"

    return command

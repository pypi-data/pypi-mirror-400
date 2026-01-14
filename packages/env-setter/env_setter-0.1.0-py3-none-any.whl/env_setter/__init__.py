"""Init for the package."""

import logging

from rich.logging import RichHandler

from env_setter import cli
from env_setter.envs import get_parsed_envs, set_env
from env_setter.exceptions import EnvironmentNotFoundError, InvalidEnvironmentError
from env_setter.parser import TOMLParser

__all__ = [
    "EnvironmentNotFoundError",
    "InvalidEnvironmentError",
    "TOMLParser",
    "cli",
    "get_parsed_envs",
    "set_env",
]

__version__ = "0.1.0"


logging.basicConfig(level="NOTSET", handlers=[RichHandler()])

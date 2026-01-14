"""Parser to parse environment files."""

import tomllib
from pathlib import Path

from env_setter.exceptions import IncorrectFileTypeError, InvalidEnvironmentError


# only toml for now, expand to yaml, json and unknown formats too
class TOMLParser:
    """Parses toml files into envs."""

    @staticmethod
    def verify(f: Path) -> bool:
        """Verify if the file type is correct for this parser."""
        return not (f.is_dir() or not f.name.endswith(".toml"))

    @staticmethod
    def parse(f: Path) -> dict:
        """Parse a TOML file at a given path."""
        if not TOMLParser.verify(f=f):
            raise IncorrectFileTypeError(filename=f.name)

        try:
            return tomllib.loads(f.read_text())
        except tomllib.TOMLDecodeError as e:
            raise InvalidEnvironmentError(filename=f.name) from e

"""Util to add alias to the host shell's profile."""

import logging
import os
from pathlib import Path
from typing import ClassVar

from env_setter.exceptions import ShellNotFoundError

logger = logging.getLogger(__name__)


SHELL_FUNCTION = """
# this is required as we cannot set environment variables from spawned processes.
function env_set() {
    eval $(envo command $@)
}
alias envo-set="env_set"
"""


class InitalizeShell:
    """Runs a custom shell command after installation."""

    _TO_ADD: ClassVar = """export env-set=eval $(envo set "$@")"""

    _BASH_FILES: ClassVar = [".bash_profile", ".profile", ".bashrc"]
    _ZSH_FILES: ClassVar = [".zprofile", ".zshrc"]
    _FISH_FILES: ClassVar = [".config/fish/config.fish"]

    @staticmethod
    def _get_default_shell() -> str:
        shell = os.environ.get("SHELL")
        if not shell:
            raise ShellNotFoundError

        return shell

    @classmethod
    def _get_shell_profile(cls) -> Path:
        home_dir = Path.home()
        shell_name = str(Path(cls._get_default_shell()).expanduser())

        if "bash" in shell_name:
            files_to_check = cls._BASH_FILES
        elif "zsh" in shell_name:
            files_to_check = cls._ZSH_FILES
        elif "fish" in shell_name:
            files_to_check = cls._FISH_FILES
        else:
            files_to_check = []

        file_path = None

        for file in files_to_check:
            if Path(Path.home() / file).exists():
                file_path = home_dir / file

        if file_path is None:
            raise ShellNotFoundError

        return file_path

    @classmethod
    def _write_alias_to_shell_file(cls) -> bool:
        shell_file = cls._get_shell_profile()
        file_data = shell_file.read_text()
        if SHELL_FUNCTION not in file_data:
            shell_file.write_text(f"{file_data}\n{SHELL_FUNCTION}\n")
            return True
        return False

    @classmethod
    def _print_alias_message(cls) -> None:
        logger.info("Adding the following lines to %s:", cls._get_shell_profile())
        logger.info("\n\n%s\n\n", SHELL_FUNCTION)
        logger.info("Please restart the shell or export it in your current environment.")
        logger.info("The shell was detected automatically and you may need to add it to other profiles if necessary.")

    @classmethod
    def run(cls) -> None:
        """Add an alias to run the envo commands."""
        if cls._write_alias_to_shell_file():
            cls._print_alias_message()
        else:
            logger.info("Shell already initialized.")

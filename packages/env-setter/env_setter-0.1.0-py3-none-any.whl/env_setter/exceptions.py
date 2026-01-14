"""Exceptions for this library."""

ENVIRONMENT_DIRECTORY_IS_A_FILE_EXCEPTION = "Env directory should not be a file."


class EnvironmentDirectoryIsAFileError(Exception):
    """Raised when the environment directory is a file."""

    def __init__(self) -> None:
        """Init of the class."""
        super().__init__(ENVIRONMENT_DIRECTORY_IS_A_FILE_EXCEPTION)


class IncorrectFileTypeError(Exception):
    """Raise when a file type does not match a parser."""

    def __init__(self, filename: str) -> None:
        """Init of the class."""
        message = f"File type is not correct for file {filename}."
        super().__init__(message)


class InvalidEnvironmentError(Exception):
    """For any issues being faced when parsing an environment file."""

    def __init__(self, filename: str) -> None:
        """Init of the class."""
        message = f"Error parsing file {filename}"
        super().__init__(message)


class EnvironmentNotFoundError(Exception):
    """When a given environment is not found."""

    def __init__(self, env_name: str, available_environments: dict) -> None:
        """Init of the class."""
        message = (
            f"Environment {env_name} not found in the list of environments {','.join(available_environments.keys())}"
        )
        super().__init__(message)


class ShellNotFoundError(Exception):
    """In case we cannot determine the shell of the os."""

    message = """Could not determine shell of the operating system.
                 Only base, fish and zsh are supported for now."""

    def __init__(self) -> None:
        """Init for the class."""
        super().__init__(self.message)

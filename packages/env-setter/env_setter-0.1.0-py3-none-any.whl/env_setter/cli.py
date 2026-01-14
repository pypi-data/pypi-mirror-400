"""CLI interface for the package."""

import logging

import typer

from env_setter.envs import get_parsed_envs, set_env
from env_setter.exceptions import EnvironmentNotFoundError
from env_setter.initialize_shell import InitalizeShell

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.callback()
def _main_app_callback(
    ctx: typer.Context,
    verbose: bool | None = typer.Option(None, "--verbose", "-v", help="Enable verbose mode."),
) -> None:
    ctx.ensure_object(object)

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


@app.command("init")
def initialize_shell() -> None:
    """Initialize the shell with some needed aliases."""
    InitalizeShell.run()


@app.command("list")
def list_environments() -> None:
    """List all the environments."""
    for key in get_parsed_envs():
        typer.echo(key)


@app.command("command")
def get_environment_command(environment_name: str) -> None:
    """Get the export commands for a given environment."""
    typer.echo(set_env(env_name=environment_name))


@app.command("show")
def show_environment(environment_name: str) -> None:
    """Show an environment."""
    envs = get_parsed_envs()
    if environment_name not in envs:
        raise EnvironmentNotFoundError(env_name=environment_name, available_environments=envs)

    typer.echo("\n".join(f"{key}={val}" for key, val in envs[environment_name].items()))


def main() -> None:
    """Invoke it from cli."""
    app()


if __name__ == "__main__":
    main()

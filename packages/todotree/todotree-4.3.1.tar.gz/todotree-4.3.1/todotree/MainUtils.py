from functools import wraps
from pathlib import Path

import click

from todotree.Errors.ConfigFileNotFoundError import ConfigFileNotFoundError
from todotree.Config.Config import Config


class MainUtils:
    """
    Class containing static methods which are useful in the main class.
    """

    @staticmethod
    def initialize(config, **kwargs):
        """
        Finalizes configuration and does some setup which is applicable for all commands.
        """
        # Parse options.
        MainUtils.parse_common_options(config, **kwargs)

        # Git pull if needed.
        config.git.git_pull()
        # Logging
        config.console.verbose(f"Read configuration from {config.config_file}")
        config.console.verbose(f"The todo file is supposed to be at {config.paths.todo_file}")
        config.console.verbose(f"The done file is supposed to be at {config.paths.done_file}")

    @staticmethod
    def common_options(function):
        """
        Wrapper that defines common click options.

        It should be used as a decorator: `@common_options`

        This function is used to support both
        `todotree cd --verbose` and `todotree --verbose cd`
        """

        @wraps(function)
        @click.option('--config-file', default=None, help="Path to the configuration file.")
        @click.option('--todo-file', default=None, help="Path to the todo.txt file, overrides --config.")
        @click.option('--done-file', default=None, help="Path to the done.txt file, overrides --config.")
        @click.option('--verbose', is_flag=True, help="Increases verbosity in messages.", is_eager=True)
        @click.option('--quiet', is_flag=True, help="Do not print messages, only output. Useful in scripts.",
                      is_eager=True)
        @click.pass_context
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    @staticmethod
    def parse_common_options(config: Config, **kwargs):
        """
        Parses the options from `common_options`.
        @param config: current config.
        @param kwargs: new options.
            :param config_file: `Optional[Path]` Path to the configuration file from the command line.
            :param done_file: `Optional[Path]` Path to the configuration file from the command line.
            :param todo_file: `Optional[Path]` Path to the configuration file from the command line.
            :param quiet: --quiet value
            :param verbose: --verbose value.
        """
        try:
            config.read(kwargs["config_file"])
        except ConfigFileNotFoundError as e:
            e.echo_and_exit(Config(), kwargs["config_file"], kwargs["verbose"])
        if kwargs["verbose"] and not config.console.is_quiet():
            config.console.set_verbose()
        if kwargs["quiet"]:
            config.console.set_quiet()
        if kwargs["todo_file"] is not None:
            config.paths.todo_file = Path(kwargs["todo_file"])
        if kwargs["done_file"] is not None:
            config.paths.done_file = Path(kwargs["done_file"])

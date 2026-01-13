from pathlib import Path

import click

from todotree.Commands.AbstractCommand import AbstractCommand


class Cd(AbstractCommand):

    def run(self):
        config_path: Path = Path(self.config.paths.todo_folder)
        self.config.console.verbose("The location to the data folder is: ")

        if config_path.is_absolute():
            # Then the configured path is printed.
            click.echo(str(config_path))
            exit()
        # Then the relative path is resolved to be absolute.
        base_path: Path = Path.home()
        full_path: Path = base_path / config_path
        click.echo(str(full_path))
        exit()

    def __call__(self, *args, **kwargs):
        raise NotImplemented
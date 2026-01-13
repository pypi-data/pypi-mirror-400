import subprocess
import sys
from pathlib import Path

import click

from todotree.Config.Config import Config


# Addons https://click.palletsprojects.com/en/8.1.x/commands/#custom-multi-commands

class Addons:
    # Note: Does not inherit AbstractCommand!

    def __init__(self, config: Config = Config()):
        self.rv: list = []
        """List of programs."""

        self.config: Config = config
        """Configuration"""

    def run(self, invocation: tuple[str]):

        """Run the addon with the invocation. The invocation also contains any number of arguments."""
        name, *arguments = invocation
        file = Path(self.config.paths.addons_folder / name)
        if not file.exists():
            self.config.console.error(f"There is no script at {file}")
            exit(1)

        self.config.console.verbose(f"Running script at {file}")
        try:
            if name.endswith(".py"):
                result = subprocess.run([sys.executable, file, str(self.config.paths.todo_file)] + arguments, capture_output=True, text=True)
            else:
                result = subprocess.run([file, str(self.config.paths.todo_file)], capture_output=True, text=True)
        except Exception as e:
            self.config.console.error(f"Error while running the addon {name}.")
            self.config.console.error(f"The error is {e}")
            raise e

        click.echo(result.stdout, nl=False)
        if result.returncode != 0:
            click.echo(result.stderr)
        self.config.git.commit_and_push(f"addons {invocation}")

    def __call__(self, *args, **kwargs):
        raise NotImplemented # Too lazy.
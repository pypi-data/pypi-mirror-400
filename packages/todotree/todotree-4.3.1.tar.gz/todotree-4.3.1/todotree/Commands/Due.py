import click

from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError


class Due(AbstractCommand):
    def __call__(self):
        # Disable fancy imports, because they do not have due dates.
        self.config.enable_project_folder = False
        self.taskManager.import_tasks()
        return self.taskManager.print_tree("due")

    def run(self):
        try:
            click.echo(self())
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)

import click

from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError


class PrintRaw(AbstractCommand):

    def run(self):
        try:
            click.echo(self.taskManager.config.paths.todo_file.read_text())
        except FileNotFoundError:
            TodoFileNotFoundError("").echo_and_exit(self.config)

    def __call__(self, *args, **kwargs):
        raise NotImplemented
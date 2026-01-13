import click

from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError


class List(AbstractCommand):
    def run(self):
        try:
            message = self()
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)
        self.config.console.info("Todos")
        click.echo(message)

    def __call__(self, *args, **kwargs):
        self.taskManager.import_tasks()
        return self.taskManager
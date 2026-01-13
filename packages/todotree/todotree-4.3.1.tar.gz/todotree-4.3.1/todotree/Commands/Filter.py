import click

from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError


class Filter(AbstractCommand):

    def run(self, search_term=None):
        try:
            self.config.console.info(f"Todos for term '{search_term}'")
            click.echo(self(search_term))
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)

    def __call__(self, search_term=None):
        self.taskManager.import_tasks()
        return self.taskManager.filter(search_term)
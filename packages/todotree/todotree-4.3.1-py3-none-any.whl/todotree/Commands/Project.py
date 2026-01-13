import click

from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError


class Project(AbstractCommand):

    def run(self):
        try:
            click.echo(self())
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)

    def __call__(self, *args, **kwargs):
        self.taskManager.import_tasks()
        return self.taskManager.print_tree("projects")
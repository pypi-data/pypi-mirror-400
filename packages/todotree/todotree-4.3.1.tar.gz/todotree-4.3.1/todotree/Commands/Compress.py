from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError


class Compress(AbstractCommand):

    def __call__(self):
        self.taskManager.import_tasks()
        self.taskManager.compress()

    def run(self) -> None:
        try:
            return self()
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)
            exit(1)  # ide hinting.

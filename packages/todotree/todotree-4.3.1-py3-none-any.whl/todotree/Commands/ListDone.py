from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.DoneFileNotFoundError import DoneFileNotFoundError
from todotree.Managers.DoneManager import DoneManager


class ListDone(AbstractCommand):
    def run(self):
        try:
            self.config.console.info(self())
        except DoneFileNotFoundError as e:
            e.echo_and_exit(self.config)

    def __call__(self):
        done_manager = DoneManager(self.config)
        done_manager.import_tasks()
        return done_manager
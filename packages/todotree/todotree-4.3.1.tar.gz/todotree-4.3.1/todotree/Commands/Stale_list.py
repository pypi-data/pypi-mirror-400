from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.StaleFileNotFoundError import StaleFileNotFoundError
from todotree.Managers.StaleManager import StaleManager


class StaleList(AbstractCommand):

    def run(self):
        try:
            self.config.console.info(self())
        except StaleFileNotFoundError as e:
            e.echo_and_exit(self.config)

    def __call__(self):
        stale_manager = StaleManager(self.config)
        stale_manager.import_tasks()
        return str(stale_manager)
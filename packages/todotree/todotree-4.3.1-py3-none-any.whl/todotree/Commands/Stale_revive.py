from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.NoSuchTaskError import NoSuchTaskError
from todotree.Errors.StaleFileNotFoundError import StaleFileNotFoundError
from todotree.Managers.StaleManager import StaleManager
from todotree.Task.Task import Task


class StaleRevive(AbstractCommand):

    def run(self, task_number: int):
        try:
            result = self(task_number)
        except StaleFileNotFoundError as e:
            e.echo_and_exit(self.config)
            exit(1) # IDE hinting.
        except NoSuchTaskError as e:
            self.config.console.error(e.message)
            exit(1)

        self.config.console.info("Revived the following task:")
        for task in result:
            self.config.console.info(task)
        self.config.git.commit_and_push("Stale Revive")

    def __call__(self, task_number: int) -> list[Task]:
        stale_manager = StaleManager(self.config)
        stale_manager.import_tasks()
        revived_task = stale_manager.remove_task_from_file(task_number)
        self.taskManager.import_tasks()
        return self.taskManager.add_tasks_to_file([revived_task])
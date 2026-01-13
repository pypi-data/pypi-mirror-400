from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.NoSuchTaskError import NoSuchTaskError
from todotree.Errors.StaleFileNotFoundError import StaleFileNotFoundError
from todotree.Managers.StaleManager import StaleManager
from todotree.Task.Task import Task


class StaleAdd(AbstractCommand):

    def run(self, task_number: int):
        try:
            task_to_add = self(task_number)
        except StaleFileNotFoundError as e:
            e.echo_and_exit(self.config)
            exit(1)  # IDE hinting.
        except NoSuchTaskError as e:
            self.config.console.error(e.message)
            exit(1)
        self.config.console.info("Added the following tasks to the stale list.")
        for task in task_to_add:
            self.config.console.info(str(task))
        self.config.git.commit_and_push("Stale Add")

    def __call__(self, task_number: int) -> list[Task]:
        stale_manager = StaleManager(self.config)
        stale_manager.import_tasks()
        self.taskManager.import_tasks()
        task_to_add = self.taskManager.remove_task_from_file(task_number)
        return stale_manager.add_tasks_to_file([task_to_add])
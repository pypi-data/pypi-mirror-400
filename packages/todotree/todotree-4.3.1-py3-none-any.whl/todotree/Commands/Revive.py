import click

from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.DoneFileNotFoundError import DoneFileNotFoundError
from todotree.Errors.NoSuchTaskError import NoSuchTaskError
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError
from todotree.Managers.DoneManager import DoneManager
from todotree.Task.Task import Task


class Revive(AbstractCommand):
    def run(self, done_number: int):
        try:
            new_tasks = self(done_number)
        except DoneFileNotFoundError as e:
            e.echo_and_exit(self.config)
            exit(1)  # IDE hinting.
        except NoSuchTaskError as e:
            self.config.console.error(e.message)
            exit(1)  # IDE hinting.
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)
            exit(1)  # IDE hinting.
        self.config.console.info("The newly revived tasks:")
        for task in new_tasks:
            self.config.console.info(str(task))
        self.config.git.commit_and_push("revive")

    def __call__(self, done_number: int) -> list[Task]:
        done_manager = DoneManager(self.config)
        done_manager.import_tasks()
        revived_task = done_manager.get_task_by_task_number(done_number)
        if not revived_task:
            raise NoSuchTaskError(f"DoneTask {done_number} is not found.")
        self.taskManager.import_tasks()
        return self.taskManager.add_tasks_to_file([Task(revived_task.i, revived_task.task_string)])
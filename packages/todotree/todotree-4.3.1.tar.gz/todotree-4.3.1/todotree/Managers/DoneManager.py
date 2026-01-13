from todotree.Config.Config import Config

from todotree.Errors.DoneFileNotFoundError import DoneFileNotFoundError
from todotree.Managers.AbstractManager import AbstractManager
from todotree.Task.ConsoleTask import ConsoleTask
from todotree.Task.DoneTask import DoneTask


class DoneManager(AbstractManager):
    """Manages the tasks which are done."""

    not_found_error = DoneFileNotFoundError

    def __init__(self, configuration: Config):
        super().__init__()

        self.task_list: list[DoneTask] = []
        """List of the tasks."""

        self.config: Config = configuration
        """Configuration settings for the application."""

        self.file = self.config.paths.done_file
        """txt file location."""

    def import_tasks(self):
        """Imports the tasks from the database file."""
        try:
            with self.file.open('r') as f:
                content = f.readlines()
                for i, task in enumerate(content):
                    # Skip empty lines.
                    if task.strip() == "":
                        continue
                    # The only line that is different compared to the abstract one.
                    self.task_list.append(DoneTask(i + 1, task.strip()))
        except FileNotFoundError as e:
            raise self.not_found_error("") from e

    def __str__(self):
        self.task_list.reverse()
        s = ""
        for tsk in [ConsoleTask.from_done_task(task, self.number_of_digits) for task in self.task_list]:
            s += str(tsk) + "\n"
        return s

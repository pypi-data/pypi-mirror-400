from todotree.Errors.InvalidPriorityError import InvalidPriorityError
from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError
from todotree.Task.Task import Task


class Priority(AbstractCommand):
    def run(self, task_number: int, new_priority: str):
        try:
            new_task = self(task_number, new_priority)
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)
        except InvalidPriorityError as e:
            e.echo_and_exit(self.config)
        self.config.console.info("The new task is: ")
        self.config.console.info(new_task)
        self.config.git.commit_and_push("priority")

    def __call__(self, task_number: int, new_priority: str):
        # Disable fancy imports.
        self.config.enable_project_folder = False
        self.taskManager.import_tasks()
        return self.taskManager.add_or_update_task(task_number, Task.add_or_update_priority, new_priority.upper())

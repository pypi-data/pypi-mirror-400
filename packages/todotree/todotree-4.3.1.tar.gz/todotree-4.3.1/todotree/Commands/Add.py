from todotree.Errors.TaskParseError import TaskParseError
from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError
from todotree.Task.Task import Task


class Add(AbstractCommand):

    def run(self, task: tuple):
        # Convert tuple to string
        try:
            task = self(" ".join(map(str, task)))
            self.config.console.info("Task added:")
            self.config.console.info(str(task))
            self.config.git.commit_and_push("add")
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)

    def __call__(self, task: str) -> Task:
        """Adds the new task to taskmanager and return the new task."""
        if not task:
            raise TaskParseError("Task is empty!")
        self.config.enable_project_folder = False
        self.taskManager.import_tasks()
        return self.taskManager.add_tasks_to_file([Task(0, task)])[0]

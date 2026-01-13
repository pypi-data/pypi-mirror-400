from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.NoSuchTaskError import NoSuchTaskError
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError


class Append(AbstractCommand):
    def __call__(self, task_nr: int, append_string: str):
        # Disable fancy imports, because they are not needed.
        self.config.enable_project_folder = False
        self.taskManager.import_tasks()
        return self.taskManager.append_to_task(task_number=task_nr, task_string=append_string)

    def run(self, task_nr: int, append_string: tuple[str]):
        # Append task.
        try:
            new_task = self(task_nr, " ".join(append_string))
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)
        except NoSuchTaskError as e:
            self.config.console.error(e.message)
            exit(1)
        self.config.console.info("The new task is: ")
        self.config.console.info(new_task)
        self.config.git.commit_and_push("append")

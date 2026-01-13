from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.DoneFileNotFoundError import DoneFileNotFoundError
from todotree.Errors.NoSuchTaskError import NoSuchTaskError
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError
from todotree.Managers.DoneManager import DoneManager
from todotree.Task.DoneTask import DoneTask


class Do(AbstractCommand):

    def __call__(self, task_numbers: list[int]) -> list[DoneTask]:
        # Marking something as Done cannot be done with fancy imports
        # So we disable them.
        self.config.enable_project_folder = False
        self.taskManager.import_tasks()
        completed_tasks = self.taskManager.remove_tasks_from_file(task_numbers)
        done_manager = DoneManager(self.config)
        done_manager.import_tasks()
        done_tasks = [DoneTask.task_to_done(task) for task in completed_tasks]
        done_manager.add_tasks_to_file(done_tasks)
        return done_tasks

    def run(self, task_numbers: list[tuple]):
        # Convert to ints. Task numbers is a list of tuples. Each tuple contains one digit of the number.
        new_numbers: list[int] = []
        for task_tuple in task_numbers:
            new_number: str = ""
            for task_digit in task_tuple:
                new_number += task_digit
            new_numbers.append(int(new_number))
        try:
            done_tasks = self(new_numbers)
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)
            exit(1)  # IDE hinting.
        except NoSuchTaskError as e:
            self.config.console.error(e.message)
            exit(1) # IDE hinting.
        except DoneFileNotFoundError as e:
            e.echo_and_exit(self.config)
            exit(1)  # IDE hinting.
        # Print the results
        self.config.console.info("Tasks marked as done:")
        for task in done_tasks:
            self.config.console.info(str(task))
        self.config.git.commit_and_push("do")

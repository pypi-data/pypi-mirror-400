import math
import shutil
from abc import ABC
from pathlib import Path
# https://docs.python.org/3/library/tempfile.html
from tempfile import NamedTemporaryFile

from todotree.Errors.NoSuchTaskError import NoSuchTaskError
from todotree.Task.ConsoleTask import ConsoleTask
from todotree.Task.Task import Task


class AbstractManager(ABC):
    not_found_error = FileNotFoundError
    """Error to raise when the database file is not found."""

    @property
    def max_task_number(self) -> int:
        """Property which defines the highest number in the task list."""
        try:
            return max([x.i for x in self.task_list])
        except ValueError:
            # Then the list is empty
            return 0

    @property
    def number_of_digits(self) -> int:
        """Property which defines the number of digits of the task in the task list with the highest number."""
        return int(math.ceil(math.log(self.max_task_number + 1, 10)))

    def __init__(self):
        self.file: Path = Path("/")
        """Path to the 'database' file. Must be set in the subclass."""

        self.task_list: list[Task] = []
        """Task list"""

    def remove_task_from_file(self, task_number: int) -> Task:
        # Remove task.
        try:
            removed_task = self.task_list.pop(task_number - 1)
        except IndexError as e:
            raise NoSuchTaskError(f"Task {task_number} does not exist in {self.file.name}.") from e
        self.write_to_file()
        return removed_task

    def remove_tasks_from_file(self, task_numbers: list[int]) -> list[Task]:
        removed_tasks = []
        task_numbers.sort()
        task_numbers.reverse()
        for task_number in task_numbers:
            t = self.get_by_task_number(task_number)
            self.task_list.remove(t)
            removed_tasks.append(t)
        self.write_to_file()
        return removed_tasks

    def write_to_file(self):
        """Writes the entire list to the file."""
        #  Delete=false is needed for windows, I hope that somebodies temp folder won't be clobbered with this...
        try:
            with NamedTemporaryFile("w+t", newline="", delete=False) as temp_file:
                # may strip new lines by using task list.
                for counter in range(1, self.max_task_number + 1):
                    try:
                        temp_file.write(self.get_by_task_number(counter).to_file())
                    except NoSuchTaskError:
                        temp_file.write("\n")
                temp_file.flush()
                shutil.copy(temp_file.name, self.file)
        except FileNotFoundError as e:
            raise self.not_found_error from e

    def get_task_by_task_number(self, task_number: int) -> Task | None:
        for task in self.task_list:
            if task.i == task_number:
                return task
        return None

    def add_tasks_to_file(self, tasks: list[Task]) -> list[Task]:
        """Adds multiple tasks to the file. Returns the added tasks."""
        if len(self.task_list) != 0:
            numbers = set(x.i for x in self.task_list)
            blanks = list(set(range(1, self.max_task_number)) - numbers)
            blanks.sort()
            if len(blanks) >= len(tasks):
                for task in tasks:
                    task.i = blanks.pop(0)
            else:
                # Fill in the blanks.
                i = 0 # Warning, is modified in the following loop.
                for i, blank in enumerate(blanks):
                    tasks[i].i = blank
                # Add the remaining to the end of the list.
                for j, task in enumerate(tasks[i:], start=1):
                    task.i = j + self.max_task_number
        else:
            # Empty file, no tasks yet.
            for j, task in enumerate(tasks, start=1):
                task.i = j

        # Final housekeeping.
        self.task_list.extend(tasks)
        self.write_to_file()
        return tasks

    def import_tasks(self):
        """Imports the tasks from the database file."""
        try:
            with self.file.open('r') as f:
                content = f.readlines()
                for i, task in enumerate(content, start=1):
                    # Skip empty lines.
                    if task.strip() == "":
                        continue
                    self.task_list.append(Task(i, task.strip()))
        except FileNotFoundError as e:
            raise self.not_found_error() from e

    def __str__(self):
        """List the tasks."""
        s = ""
        for tsk in [ConsoleTask(task.i, task.task_string, self.number_of_digits) for task in self.task_list]:
            s += str(tsk) + "\n"
        return s

    def get_by_task_number(self, num: int):
        """
        Gets a task with number :num:
        :raise: NoSuchTaskError if the task is not found.
        """
        for task in self.task_list:
            if task.i == num:
                return task
        raise NoSuchTaskError(f"Task {num} does not exist.")
    def __repr__(self):
        return f"AbstractManager({self.max_task_number} Tasks)"

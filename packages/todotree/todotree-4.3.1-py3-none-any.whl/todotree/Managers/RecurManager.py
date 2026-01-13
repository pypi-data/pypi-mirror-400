import datetime
import re
from itertools import chain
from pathlib import Path

from todotree.Config.Config import Config
from todotree.Errors.RecurDateStampError import RecurDateStampError
from todotree.Errors.RecurParseError import RecurParseError
from todotree.Task.RecurTask import RecurTask
from todotree.Managers.TaskManager import TaskManager


class RecurManager:
    """Manages the recur.txt tasks."""

    comment_regex = re.compile(r"^\s*#")
    """Regular expression to detect comments."""

    recur_timestamp_filename = ".recur.timestamp"
    """Name of the timestamp file."""

    def __init__(self, config: Config):
        self.config: Config = config
        self.task_list: list[RecurTask] = []
        self.task_manager: TaskManager = TaskManager(self.config)
        self.last_date: datetime.date | None = None
        self.timestamp_file: Path = self.config.paths.todo_folder / self.recur_timestamp_filename
        self.is_manual = False
        # If supplied with the

    def import_tasks(self):
        """Import the tasks from recur.txt."""
        error = False
        with self.config.paths.recur_file.open("r") as f:
            for line_number, recur_task in enumerate(f.readlines()):
                if not recur_task.strip():
                    # Empty line, continue.
                    continue
                if self.comment_regex.match(recur_task):
                    # Comment, continue.
                    continue
                try:
                    task = RecurTask(recur_task)
                    self.task_list.append(task)
                except RecurParseError as e:
                    self.config.console.error(f"Error parsing Recur on line {line_number}.")
                    self.config.console.error(str(e))
                    error = True
                    continue
                if task.end_date < task.start_date:
                    self.config.console.warning(f"Recur task on line {line_number} is ending before it is starting.")
                    self.config.console.warning("This task will never get added.")
        if error:
            raise RecurParseError("One or more tasks were invalid, aborted adding recur tasks.")
        # Also import the tasks itself to compare later.
        self.task_manager.import_tasks()

    def add_to_todo(self):
        """Add the imported tasks to todo.txt"""
        # Check time of last time recur ran.
        self._check_last_time_run()
        # If already run, just exit.
        if self.last_date == datetime.date.today():
            self.config.console.info("Recur has already run today.")
            return

        # Filter the tasks that need to be added.
        self.filter_by_date()
        self.filter_by_existing()
        # Add the remaining Recur Tasks to the task list.
        added_tasks = self.task_manager.add_tasks_to_file([x.to_task(i) for i, x in enumerate(self.task_list, start=1)])
        if added_tasks:
            self.config.console.info("Added the following tasks:")
        else:
            self.config.console.info("No recurring task to add.")
        for i, task in enumerate(added_tasks):
            self.config.console.info(f"{task}")

    def filter_by_date(self):
        """Removes tasks that are not allowed to be added because of their date information."""
        new_list = []
        for task in self.task_list:
            if task.start_date > datetime.date.today():
                # Recur task has not started yet.
                continue
            if task.end_date < datetime.date.today():
                # Recur task has ended.
                continue
            match task.interval:
                case RecurTask.Recurrence.Never:
                    if self.last_date < task.start_date < datetime.date.today():
                        new_list.append(task)
                    elif self.last_date < task.end_date < datetime.date.today():
                        new_list.append(task)
                case RecurTask.Recurrence.Daily:
                    # Then it should always be added.
                    new_list.append(task)
                case RecurTask.Recurrence.Weekly:
                    self.__match_week(new_list, task, datetime.date.today())
                case RecurTask.Recurrence.Monthly:
                    self.__match_month(new_list, task, datetime.date.today())
                case RecurTask.Recurrence.Yearly:
                    self.__match_year(new_list, task, datetime.date.today())
        # End loop
        self.task_list = new_list

    def __match_week(self, new_list, task, today):
        # Count up until the week is further than last date.
        date = task.start_date
        while date < self.last_date:
            date = date + datetime.timedelta(days=7)
        if date < today:
            new_list.append(task)

    def __match_month(self, new_list, task, today):
        if self.last_date.day < today.day:
            # case: 12 13 14 15
            if task.start_date.day in range(self.last_date.day, today.day):
                new_list.append(task)
        else:
            # case: 30 31 1 2 3 4 5
            if task.start_date.day in chain(range(self.last_date.day, 31), range(1, today.day)):
                new_list.append(task)

    def __match_year(self, new_list, task, today):
        if self.last_date.year < today.year:
            # case: 2022 2023
            if task.start_date.month in range(self.last_date.month):
                # Check in last year
                if self.last_date < datetime.date(self.last_date.year, task.start_date.month,
                                                  task.start_date.day) < today:
                    new_list.append(task)
            else:
                # Check in new year.
                if self.last_date < datetime.date(today.year, task.start_date.month, task.start_date.day) < today:
                    new_list.append(task)
        else:
            # Both in same year.
            if self.last_date < datetime.date(self.last_date.year, task.start_date.month, task.start_date.day) < today:
                new_list.append(task)

    def filter_by_existing(self):
        """Removes tasks that already exist in todo.txt"""
        existing_tasks = [x.task_string for x in self.task_manager.task_list]
        self.task_list = [item for item in self.task_list if item.task_string not in existing_tasks]

    def _check_last_time_run(self):
        if self.last_date is not None:
            # Then it was already checked.
            return
        if not self.timestamp_file.exists():
            # Then run from the beginning of time.
            self.last_date = datetime.date(1, 1, 1)
            return
        timestamp = self.timestamp_file.read_text()
        try:
            self.last_date = datetime.date.fromisoformat(timestamp.strip())
        except ValueError as e:
            RecurDateStampError().echo_and_exit(self.config, timestamp)
            exit(1)
        if self.config.console.is_verbose():
            self.config.console.verbose(f"Last run was at date {self.last_date}")

    def _set_last_time_run(self):
        if not self.timestamp_file.exists():
            self.timestamp_file.touch()
        # This changes the mtime.
        self.timestamp_file.write_text(datetime.date.today().isoformat())

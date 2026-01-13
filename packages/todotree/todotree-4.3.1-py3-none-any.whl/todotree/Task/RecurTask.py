import datetime
import re
from enum import Enum

from todotree.Errors.RecurParseError import RecurParseError
from todotree.Task.Task import Task


class RecurTask:
    recur_pattern = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})\s*;"  # Start Date.
                               r"\s*(\d{4}-\d{2}-\d{2})?\s*;"  # End date. 
                               r"\s*(\w+)\s*-"  # interval.
                               r"\s*(.*)$")  # Task.

    class Recurrence(Enum):
        Never = 0
        Daily = 1
        Weekly = 2
        Monthly = 3
        Yearly = 4

    def __init__(self, recur_line: str):
        """Parses `recur_line` to create a RecurTask."""
        self.start_date = datetime.date(1, 1, 1)
        self.end_date = datetime.date(9999, 1, 1)
        self.interval: RecurTask.Recurrence = RecurTask.Recurrence.Never
        self.task_string: str = ""
        self.recur_line: str = recur_line
        if recur_line.strip():
            # Parse each part
            match = self.recur_pattern.match(recur_line)
            if not match:
                raise RecurParseError(f"This string does not match regex: {recur_line}")
            start, end, interval, task_string = match.groups()
            self.task_string = task_string.strip()
            self.__parse_start_date(start)
            self.__parse_end_date(end)
            self.__parse_interval(interval)

    def __repr__(self):
        return f"RecurTask({self.recur_line.strip()})"

    def to_task(self, i: int = -1) -> Task:
        """Returns a Task representation of the RecurTask."""
        return Task(i, self.task_string)

    def __parse_interval(self, interval):
        try:
            self.interval = RecurTask.Recurrence[interval.capitalize()]
        except KeyError as e:
            raise RecurParseError(f"Error parsing interval: {e}. "
                                  f"It must be one of the following {', '.join([x.name for x in RecurTask.Recurrence])}")

    def __parse_end_date(self, end):
        if end:
            try:
                self.end_date = datetime.date.fromisoformat(end)
            except ValueError as e:
                raise RecurParseError(f"Error parsing end date: {e}")

    def __parse_start_date(self, start):
        try:
            self.start_date = datetime.date.fromisoformat(start)
        except ValueError as e:
            raise RecurParseError(f"Error parsing start date: {e}")

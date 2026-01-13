import datetime
import re
from datetime import datetime, date, timedelta
from enum import EnumType, Enum, StrEnum

from dateutil.utils import today

from todotree.Errors.InvalidPriorityError import InvalidPriorityError
from todotree.Errors.TaskParseError import TaskParseError


class DueDateBand(StrEnum):
    a = "Overdue"
    b = "Due today"
    c = "Due tomorrow"
    d = "Due in the next 7 days"
    e = "Due date further than the next 7 days"
    z = "No due date"


class Task:
    """
    Base class that represents a task.
    """

    t_date_pattern = re.compile(r"t:(\d{4})-(\d{2})-(\d{2})\s?")
    """Regex pattern which defines t:dates in a task string."""

    project_pattern = re.compile(r"\+\S+\s?")
    """Regex pattern which defines projects in a task string."""

    context_pattern = re.compile(r"@\w+\s?")
    """Regex pattern which defines contexts in a task string."""

    priority_pattern = re.compile(r"^\([a-zA-Z]\)\s?")
    """Regex pattern which defines the priority in a task string."""

    due_date_pattern = re.compile(r"due:(\d{4})-(\d{2})-(\d{2})\s?")
    """Regex pattern which defines due dates in a string.
    
    The format is due:yyyy-mm-dd.
    This is a due date for a single time.
    """

    due_month_pattern = re.compile(r"duy:(\d{2})-(\d{2})\s?")
    """Regex pattern which defines dum dates in a string.

    The format is due:mm-dd.
    This is a due date which recurs each year.
    
    An example case would be doing taxes. Each year you have to them before a certain date.
    """

    due_day_pattern = re.compile(r"dum:(\d{2})\s?")
    """Regex pattern which defines dum dates in a string.

    The format is due:dd.
    This is a due date for a deadline which recurs each month.
    """

    block_pattern = re.compile(r"(bl:)(\w+)\s?")
    """Regex pattern which defines a block key. format: bl:string"""

    blocked_by_pattern = re.compile(r"(by:)(\w+)\s?")
    """Regex pattern which defines a blocked by key. format: by:string"""

    @property
    def t_date(self) -> date | None:
        """Property which returns the latest t date of the task."""
        return max(self.t_date_all) if len(self.t_date_all) > 0 else None

    # FUTURE: t_date Setter.

    @property
    def due_date(self) -> date | None:
        """Property which returns the earliest due date."""
        return min(self.due_date_all) if len(self.due_date_all) > 0 else None

    # FUTURE: due_date setter. https://mathspp.com/blog/pydonts/properties

    @property
    def due_date_band(self) -> DueDateBand:
        """
        Property which returns the time until the due date lapses in human-readable language.
        """
        if self.due_date is None:
            return DueDateBand.z
        # List with options.
        difference = self.due_date - datetime.today().date()
        if difference < timedelta(days=0):
            return DueDateBand.a
        if difference < timedelta(days=1):
            return DueDateBand.b
        if difference < timedelta(days=2):
            return DueDateBand.c
        if difference < timedelta(days=7):
            return DueDateBand.d
        return DueDateBand.e

    @property
    def priority(self) -> int:
        """
        Property which defines the priority of a `Task` as an integer.
        """
        return ord(self.priority_string.upper()) - 65 if self.priority_string != "" else 684

    def __init__(self, i: int, task_string: str):
        """
        Initializes a single task from a string.
        :param i: The task identifier.
        :param task_string: The string containing the task.
        """
        self.date_marked_done: str | None = None
        """Date that this task was marked as done."""

        self.t_date_all: list[datetime.date] = []
        """All t dates of a task."""

        self.due_date_all: list[datetime.date] = []
        """All due dates of a task"""

        self.task_string: str = ""
        """raw un formatted string"""

        self.other_string: str = task_string
        """String containing any part which is not captured in another variable."""

        self.i: int = i
        """The task identifier"""

        self.priority_string: str = ""  # FUTURE: Convert to property instead.
        """priority as a String."""

        self.projects: list[str] = []
        """List of all projects"""

        self.contexts: list[str] = []
        """List of all contexts"""

        self.blocks: list[str] = []
        """List of all block identifiers."""

        self.blocked: list[str] = []
        """List of all blocked by identifiers"""

        # Parse the various properties from the task.
        if task_string:  # task is not empty
            self.task_string = task_string.strip()  # Remove whitespace and the \n.
            self.write_string = task_string

            # Parse the various items.
            self.__parse_priority(task_string)

            self.__parse_project(task_string)
            self.__parse_context(task_string)
            self.__parse_t_date(task_string)
            self.__parse_due_date(task_string)
            self.__parse_due_month(task_string)
            self.__parse_due_day(task_string)
            self.__parse_block_list(task_string)
            self.__parse_blocked_by_list(task_string)

            # Final cleanup of other_string.
            self.other_string = self.other_string.strip()

    def to_file(self):
        return self.task_string + "\n"

    def __parse_priority(self, task_string):
        """
        Parse the priority from the `task_string`.
        """
        if self.priority_pattern.match(task_string):
            with_parentheses = self.priority_pattern.match(task_string).group(0)
            self.priority_string = with_parentheses[1]
            self.other_string = self.priority_pattern.sub("", self.other_string).lstrip()

    def __parse_project(self, task_string):
        """
        Parse the projects from the `task_string`.
        """
        if self.project_pattern.search(task_string):
            projects_with_plus = self.project_pattern.findall(task_string)
            for p in projects_with_plus:
                # strip is for the trailing whitespace.
                self.projects.append(re.sub(r"\+", "", p).strip())
        self.other_string = self.project_pattern.sub("", self.other_string)

    def __parse_context(self, task_string):
        """
        Parse the contexts from the `task_string`.
        """
        if self.context_pattern.search(task_string):
            context_with_at = self.context_pattern.findall(task_string)
            for c in context_with_at:
                self.contexts.append(re.sub(r"@", "", c).strip())
        self.other_string = self.context_pattern.sub("", self.other_string)

    def __parse_t_date(self, task_string):
        """
        Parse the t_dates from the `task_string`.
        """
        for year, month, day in self.t_date_pattern.findall(task_string):
            try:
                # Add t:date to the t date list.
                self.t_date_all.append(datetime(int(year), int(month), int(day)).date())
            except ValueError:
                raise TaskParseError(f"This task has an incorrect t:date.{year}-{month}-{day}, task: {task_string}")
        self.other_string = self.t_date_pattern.sub("", self.other_string)

    def __parse_due_date(self, task_string):
        """
        Parse the due date from the `task_string`.
        """
        for year, month, day in self.due_date_pattern.findall(task_string):
            try:
                self.due_date_all.append(datetime(int(year), int(month), int(day)).date())
            except ValueError:
                raise TaskParseError(
                    f"This task has an incorrect due:date. date: {year}-{month}-{day}, task: {task_string}")
        self.other_string = self.due_date_pattern.sub("", self.other_string)

    def __parse_due_month(self, task_string):
        """
        Parse the duy date from the `task_string`.
        """
        for month, day in self.due_month_pattern.findall(task_string):
            try:
                date_next_year = datetime(datetime.today().year + 1, int(month), int(day))
                if date_next_year - today() < timedelta(weeks=4):
                    self.due_date_all.append(date_next_year.date())
                else:
                    self.due_date_all.append(datetime(datetime.today().year, int(month), int(day)).date())
            except ValueError:
                raise TaskParseError(f"This task has an incorrect dum:date. date: {month} {day}, task: {task_string}")
        self.other_string = self.due_month_pattern.sub("", self.other_string)

    def __parse_due_day(self, task_string):
        """
        Parses the dum date from `task_string`.
        """
        for day in self.due_day_pattern.findall(task_string):
            try:
                # Also take care of rollover near Christmas.
                date_next_month = datetime(
                    datetime.today().year if datetime.today().month < 12 else datetime.today().year + 1,
                    datetime.today().month + 1 if (datetime.today().month + 1) <= 12 else 1,
                    int(day))
                if date_next_month - today() < timedelta(days=7):
                    # The deadline in the next month is less than 7 days away.
                    self.due_date_all.append(date_next_month.date())
                else:
                    self.due_date_all.append(datetime(datetime.today().year, datetime.today().month, int(day)).date())
            except ValueError:
                raise TaskParseError(f"This task has an incorrect duy:date : {task_string}")
        self.other_string = self.due_day_pattern.sub("", self.other_string)

    def __parse_blocked_by_list(self, task_string):
        """
        Parse the blocked by list.
        """
        for blocked_item in self.blocked_by_pattern.finditer(task_string):
            self.blocked.append(str(blocked_item.group(2)))
        self.other_string = self.blocked_by_pattern.sub("", self.other_string)

    def __parse_block_list(self, task_string):
        """
        Parse the block list.
        """
        for item in self.block_pattern.finditer(task_string):
            self.blocks.append(str(item.group(2)))
        self.other_string = self.block_pattern.sub("", self.other_string)

    def add_or_update_priority(self, new_priority: str) -> bool:
        """
        Adds or updates the priority.
        :param new_priority: the new priority
        :return: A value indicating whether it was added or updated.
        True means it was added. False that it was updated.
        """
        if len(new_priority) > 1:
            # Then the string is not a single character.
            raise InvalidPriorityError(f"{new_priority} is not a valid priority.")
        if self.priority < 600:
            # Then there is already a priority defined.
            self.priority_string = new_priority
            self.task_string = self.priority_pattern.sub("(" + new_priority + ") ", self.task_string)
            return False
        else:
            # There was no priority defined.
            self.priority_string = new_priority
            self.task_string = "(" + new_priority + ") " + self.task_string
            return True

    def add_or_update_due(self, new_due: datetime) -> bool:
        """
        Updates the due date, or adds it if it does not exist.
        :param new_due: the new due date.
        :return: True if it was added. False if the due date is updated.
        """
        if self.due_date is not None:
            # There already are due dates, overwrite any other due dates.
            self.task_string = self.due_date_pattern.sub(
                "due:" + new_due.strftime("%Y-%m-%d"), self.task_string
            )
            self.due_date_all = [new_due.date()]
            return False
        # There was no due_date, substitute the default.
        self.task_string += " due:" + new_due.strftime("%Y-%m-%d")
        self.due_date_all.append(new_due.date())
        return True

    def add_or_update_t_date(self, new_t_date: str):
        """
        Adds or updates the t:date
        :param new_t_date: The new `t_date` in the format yyyy-mm-dd.
        """
        if self.t_date is not None:
            self.task_string = self.t_date_pattern.sub("t:" + new_t_date, self.task_string)
        else:
            self.task_string += " t:" + new_t_date
        self.t_date_all = [datetime.strptime(new_t_date, "%Y-%m-%d").date()]

    def __add__(self, other):
        """
        :param other: the string or task to append to this task.
        """
        match other:
            case str():
                return Task(self.i, self.task_string + " " + other.strip())
            case Task():
                return Task(self.i, self.task_string + " " + other.task_string)
            case _:
                return NotImplemented

    def __str__(self):
        prefix = self.i if self.i > 0 else ""
        task = self.task_string
        return str(prefix) + " " + task

    def __repr__(self):
        return f"Task({self.i}, {self.task_string})"

    def __lt__(self, other) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        # Sort by priority.
        if self.priority != other.priority:
            # Return < or > version.
            return self.priority < other.priority
        # Priority is the same, sort by task number.
        return self.i <= other.i

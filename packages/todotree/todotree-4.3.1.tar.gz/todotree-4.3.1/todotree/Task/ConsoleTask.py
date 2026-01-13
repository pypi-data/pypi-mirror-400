from todotree.Task.DoneTask import DoneTask
from todotree.Task.Task import Task


class ConsoleTask(Task):
    """
    Task class for printing to the console.
    """

    @staticmethod
    def from_done_task(task: DoneTask, total_digits) -> 'ConsoleTask':
        ct = ConsoleTask(task.i, task.task_string, total_digits)
        ct.date_marked_done = task.date_marked_done
        return ct

    def __init__(self, i: int, task_string: str, total_digits=1):
        super().__init__(i, task_string)
        self.total_digits = total_digits
        """Represents the total number of digits that `i` must have."""

        self.parts: list = []
        """The parts of the final string for printing."""

    def __str__(self):
        """Base representation."""
        self.__add_i()
        self.__add_date_marked_done()
        self.__add_priority()
        self.__add_other()
        self.__add_due_date()
        self.__add_projects()
        self.__add_context()
        self.__add_blocks()
        return " ".join(self.parts)

    def print_due(self):
        """
        Print the task for task manager due dates.
        :return: the string suitable for printing the due date tree.
        """
        self.__add_i()
        self.__add_priority()
        self.__add_other()
        self.__add_projects()
        self.__add_context()
        self.__add_blocks()
        self.__add_due_date()
        return " ".join(self.parts)

    def print_project(self, excluded_project=None):
        """
        Strips the string for task_manager.project_tree
        :return: a string useful for printing the project tree.
        """
        self.__add_i()
        self.__add_priority()
        self.__add_other()
        self.__add_due_date()
        self.__add_projects(excluded_project)
        self.__add_context()
        self.__add_blocks()
        return " ".join(self.parts)

    def print_context(self, excluded_context=None):
        """
        Strips the string for task_manager.project_tree
        :return: a string useful for printing the project tree.
        """
        self.__add_i()
        self.__add_priority()
        self.__add_other()
        self.__add_due_date()
        self.__add_projects()
        self.__add_context(excluded_context)
        self.__add_blocks()
        return " ".join(self.parts)

    def __add_i(self):
        """Add the number to `parts`."""
        if self.i > 0:
            self.parts.extend([str(self.i).zfill(self.total_digits)])

    def __add_context(self, excluded_context=None):
        """
        Add the contexts to `parts`.
        :param excluded_context: The context to exclude.
        """
        self.parts.extend([f"@{c}" for c in self.contexts if c != excluded_context])

    def __add_projects(self, excluded_project=None):
        """
        Add the projects to `parts`.
        :param excluded_project: The project to exclude.
        """
        self.parts.extend([f"+{p}" for p in self.projects if p != excluded_project])

    def __add_other(self):
        """Add the non-parsed material to `parts`"""
        if self.other_string:
            self.parts.extend([self.other_string])

    def __add_priority(self):
        """Add the formatted priority to `parts`."""
        if self.priority_string:
            self.parts.extend([f"({self.priority_string})"])

    def __add_blocks(self):
        """Add the blocks to `parts`."""
        self.parts.extend([f"bl:{bl}" for bl in self.blocks])

    def __add_due_date(self):
        """Add the due date to `parts`."""
        if self.due_date is not None:
            self.parts.extend(["due:" + self.due_date.strftime("%Y-%m-%d")])

    def __add_date_marked_done(self):
        if self.date_marked_done is not None:
            self.parts.extend(["x " + self.date_marked_done])

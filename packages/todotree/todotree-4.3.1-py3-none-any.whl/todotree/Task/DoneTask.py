from datetime import date

from todotree.Task.Task import Task


class DoneTask(Task):

    @staticmethod
    def task_to_done(tsk: Task) -> 'DoneTask':
        """
        Format the task String to a done state, by adding x 2020-02-02 in front of it.
        :param tsk: A task_string.
        :return: A done_string with a today's time stamp.
        """
        return DoneTask(tsk.i, "x " + str(date.today()) + " " + tsk.task_string)

    def to_file(self):
        """Returns a string useful for writing to a file."""
        return f"x {self.date_marked_done} {self.task_string}\n"

    @staticmethod
    def task_to_undone(tsk):
        """
        Removes the x 2020-02-02 part so the task can be added to the task file list
        :param tsk: A done string.
        :return: A task string.
        """
        # 13 is the number of chars of "x 2020-02-02 "
        return str.strip(tsk[13:])

    @staticmethod
    def chop(tsk):
        """Chops into a tuple containing the date and the task."""
        return str.strip(tsk[2:12]), str.strip(tsk[13:])

    def __init__(self, i: int, task_string: str):
        """
        Initializes a single task from a string.
        :param i: The task number.
        :param task_string: x 2020-02-02 The string containing the task.
        """
        date_marked_done, task_string = self.chop(task_string)
        super().__init__(i, task_string)
        self.date_marked_done = date_marked_done

    def __str__(self):
        return f"x {self.date_marked_done} {self.task_string}"

    def __repr__(self):
        return f"DoneTask(x {self.date_marked_done} {self.task_string})"

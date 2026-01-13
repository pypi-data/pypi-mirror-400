import abc
from abc import ABC

from todotree.Config.Config import Config
from todotree.Managers.TaskManager import TaskManager


class AbstractCommand(ABC):
    """Abstract Command class to be used as a base class for all command."""

    def __init__(self, config: Config, task_manager: TaskManager):
        """
        Initializes a new AbstractCommand.
        :param config: The configuration of the application.
        :param task_manager: The task manager.
        """
        self.taskManager = task_manager
        self.config = config

    @abc.abstractmethod
    def run(self) -> None:
        """Runs the command. Results are emitted through click.echo."""
        pass

    @abc.abstractmethod
    def __call__(self):
        """
        Runs the command and returns the result.
        """
        pass

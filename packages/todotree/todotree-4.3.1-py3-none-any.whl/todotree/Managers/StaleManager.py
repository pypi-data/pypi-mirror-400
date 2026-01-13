from todotree.Config.Config import Config
from todotree.Errors.StaleFileNotFoundError import StaleFileNotFoundError

from todotree.Managers.AbstractManager import AbstractManager
from todotree.Task.Task import Task


class StaleManager(AbstractManager):
    """Manages the stale.txt file"""
    not_found_error = StaleFileNotFoundError

    def __init__(self, configuration: Config):
        """Initializes a task manager, which manages the tasks."""

        super().__init__()
        self.task_list: list[Task] = []
        """List Without empty lines"""

        self.config: Config = configuration
        """Configuration settings for the application."""

        self.file = self.config.paths.stale_file
        """txt file location."""

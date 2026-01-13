import platform
import re
import subprocess

from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.TodoFileNotFoundError import TodoFileNotFoundError
from todotree.Task.Task import Task


class Schedule(AbstractCommand):
    def run(self, new_date=None, task_number=None):
        # Disable fancy imports, because they do not have t dates.
        self.config.enable_project_folder = False
        # Convert
        date = " ".join(new_date)
        date_pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
        if not date_pattern.match(date):
            date = self.fuzzy_match_date(date)
        try:
            self.taskManager.import_tasks()
            self.config.console.info(f"Task {task_number} hidden until {date}")
            updated_task = self.taskManager.add_or_update_task(task_number, Task.add_or_update_t_date, date)
            self.config.console.info(str(updated_task))
        except TodoFileNotFoundError as e:
            e.echo_and_exit(self.config)
        self.config.git.commit_and_push("schedule")

    def fuzzy_match_date(self, date):
        """Fuzzy Matching of the date."""
        match platform.system().lower():
            case "windows":
                self.config.console.error("Windows is not supported.")
                exit(1)
            case "linux":
                self.config.console.verbose(f"Attempt to parse {date} with the `date` program.")
                # Try to use the `date` utility.
                dat = subprocess.run(
                    ["date", "-d " + date, "+%F "],
                    capture_output=True,
                    encoding="utf-8"
                )
                if dat.returncode > 0:
                    self.config.console.error(f"The date {date} could not be parsed.")
                    exit(1)
                date = dat.stdout.strip()
                return date
            case "darwin":
                self.config.console.verbose(f"Attempt to parse {date} with the `date` program.")
                # Try to use the `date` utility.
                dat = subprocess.run(
                    ["gdate", "-d " + date, "+%F "],
                    capture_output=True,
                    encoding="utf-8"
                )
                # FUTURE: gdate detection and error messaging.
                # self.config.console.error("gdate was not found, this can be installed with `brew install coreutils`.")
                if dat.returncode > 0:
                    self.config.console.error(f"The date {date} could not be parsed.")
                    exit(1)
                date = dat.stdout.strip()
                return date
            case _:
                self.config.console.error(f"The platform {platform.system()} could not be parsed.")
                exit(1)

    def __call__(self, *args, **kwargs):
        raise NotImplemented("Schedule() is not implemented.")
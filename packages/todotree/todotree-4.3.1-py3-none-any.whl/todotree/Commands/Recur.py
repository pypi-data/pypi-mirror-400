import datetime

from todotree.Commands.AbstractCommand import AbstractCommand
from todotree.Errors.RecurParseError import RecurParseError
from todotree.Managers.RecurManager import RecurManager


class Recur(AbstractCommand):

    def run(self, date: str | None = None):
        if not self.config.paths.recur_file.exists():
            self.config.console.error("recur.txt not found, nothing to add.")
            self.config.console.error("It should be at the following location:")
            self.config.console.error(self.config.paths.recur_file)
            exit(1)
        if date is not None:
            # Parse the date into a proper date.
            try:
                date_proper = datetime.date.fromisoformat(date.strip())
            except ValueError:
                self.config.console.error(f"date {date} is not a valid iso date.")
                exit(1)
        else:
            date_proper = None

        try:
            self(date_proper)
        except RecurParseError as e:
            self.config.console.error(str(e))
            exit(1)
        self.config.git.commit_and_push("recur")

    def __call__(self, date: datetime.date | None = None, *args, **kwargs):
        rm = RecurManager(self.config)
        if date is not None:
            # This will override the timestamp file checking.
            rm.last_date = date
        rm.import_tasks()
        rm.add_to_todo()
        rm._set_last_time_run()

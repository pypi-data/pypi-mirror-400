import click
from todotree.Errors.TodotreeError import TodotreeError

from todotree.Commands.AbstractCommand import AbstractCommand


class Edit(AbstractCommand):
    def run(self, filename: str):
        # Disable fancy imports.
        self.config.enable_project_folder = False
        # Run based on which file is actually there.
        match filename:
            case "todo":
                click.edit(filename=str(self.config.paths.todo_file))
            case "done":
                click.edit(filename=str(self.config.paths.done_file))
            case "stale":
                click.edit(filename=str(self.config.paths.stale_file))
            case "recur":
                click.edit(filename=str(self.config.paths.recur_file))
            case _:
                raise TodotreeError(f"{filename} is not a correct file name to edit.")
        # Push the results to Git.
        self.config.git.commit_and_push("edit")

    def __call__(self, *args, **kwargs):
        raise NotImplemented
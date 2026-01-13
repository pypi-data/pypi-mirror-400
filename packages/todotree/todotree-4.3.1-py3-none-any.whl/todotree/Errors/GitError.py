from todotree.Config.ConsolePrefixes import ConsolePrefixes
from todotree.Errors.TodotreeError import TodotreeError


class GitError(TodotreeError):
    """
    Represents an error indicating that something is wrong with the git repo.
    """
    def warn_and_continue(self, console: ConsolePrefixes):
        console.warning("An error occurred while trying to git pull.")
        console.warning("If this was unexpected, try again with the --verbose flag.")



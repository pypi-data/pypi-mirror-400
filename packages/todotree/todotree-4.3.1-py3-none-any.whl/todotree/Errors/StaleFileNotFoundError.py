from todotree.Config.Config import Config

from todotree.Errors.TodotreeError import TodotreeError


class StaleFileNotFoundError(TodotreeError):
    """Represents an error indicating that the stale.txt file is not found."""

    def echo_and_exit(self, config: Config):
        config.console.error("The stale.txt file could not be found.")
        config.console.error(f"It searched at the following location: {config.paths.stale_file}")
        config.console.verbose(str(self))
        exit(1)

from pathlib import Path

from todotree.Errors.TodotreeError import TodotreeError


class ConfigFileNotFoundError(TodotreeError):
    """
    Represents an error indicating that the config.yaml file is not found.
    """
    def echo_and_exit(self, config, config_path: Path, verbose: bool):
        """
        @param config: Config object for defaults. (This is here to prevent a circular import).
        @param config_path: The path that did not have the config.yaml
        @param verbose: Whether to add more information.
        """
        cp = config.console
        cp.warning(f"The config.yaml file could not be found at {config_path}.")
        if verbose:
            cp.warning(f"The config file should be located at {config_path}")
            cp.warning(str(self))
        cp.warning("The default options are now used.")
        exit(1)
